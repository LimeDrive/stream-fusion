from itertools import islice
import uuid
import tenacity
from urllib.parse import unquote

from fastapi import HTTPException
from stream_fusion.utils.debrid.base_debrid import BaseDebrid
from stream_fusion.utils.general import get_info_hash_from_magnet, season_episode_in_filename, is_video_file
from stream_fusion.logging_config import logger
from stream_fusion.settings import settings

class Torbox(BaseDebrid):
    def __init__(self, config):
        super().__init__(config)
        self.base_url = f"{settings.tb_base_url}/{settings.tb_api_version}/api"
        self.token = settings.tb_token if settings.tb_unique_account else self.config["TBToken"]
        logger.info(f"Torbox: Initialized with base URL: {self.base_url}")

    def get_headers(self):
        if settings.tb_unique_account:
            if not settings.proxied_link:
                logger.warning("TorBox: Unique account enabled, but proxied link is disabled. This may lead to account ban.")
                logger.warning("TorBox: Please enable proxied link in the settings.")
                raise HTTPException(status_code=500, detail="Proxied link is disabled.")
            if settings.tb_token:
                return {"Authorization": f"Bearer {settings.tb_token}"}
            else:
                logger.warning("TorBox: Unique account enabled, but no token provided. Please provide a token in the env.")
                raise HTTPException(status_code=500, detail="AllDebrid token is not provided.")
        else:
            return {"Authorization": f"Bearer {self.config["TBToken"]}"}

    def add_magnet(self, magnet, ip=None, privacy="private"):
        logger.info(f"Torbox: Adding magnet: {magnet[:50]}...")
        url = f"{self.base_url}/torrents/createtorrent"
        seed = 2 if privacy == "private" else 1
        data = {
            "magnet": magnet,
            "seed": seed,
            "allow_zip": "false"
        }
        response = self.json_response(url, method='post', headers=self.get_headers(), data=data)
        logger.info(f"Torbox: Add magnet response: {response}")
        return response

    def add_torrent(self, torrent_file, privacy="private"):
        logger.info("Torbox: Adding torrent file")
        url = f"{self.base_url}/torrents/createtorrent"
        seed = 2 if privacy == "private" else 1
        data = {
            "seed": seed,
            "allow_zip": "false"
        }
        files = {
            "file": (str(uuid.uuid4()) + ".torrent", torrent_file, 'application/x-bittorrent')
        }
        response = self.json_response(url, method='post', headers=self.get_headers(), data=data, files=files)
        logger.info(f"Torbox: Add torrent file response: {response}")
        return response

    def get_torrent_info(self, torrent_id):
        logger.info(f"Torbox: Getting info for torrent ID: {torrent_id}")
        url = f"{self.base_url}/torrents/mylist?bypass_cache=true&id={torrent_id}"
        response = self.json_response(url, headers=self.get_headers())
        logger.debug(f"Torbox: Torrent info response: {response}")
        return response

    def control_torrent(self, torrent_id, operation):
        logger.info(f"Torbox: Controlling torrent ID: {torrent_id}, operation: {operation}")
        url = f"{self.base_url}/torrents/controltorrent"
        data = {
            "torrent_id": torrent_id,
            "operation": operation
        }
        response = self.json_response(url, method='post', headers=self.get_headers(), data=data)
        logger.info(f"Torbox: Control torrent response: {response}")
        return response

    @tenacity.retry(
        stop=tenacity.stop_after_attempt(3),
        wait=tenacity.wait_fixed(2),
        retry=tenacity.retry_if_exception_type((HTTPException, TimeoutError))
    )
    def request_download_link(self, torrent_id, file_id=None, zip_link=False):
        logger.info(f"Torbox: Requesting download link for torrent ID: {torrent_id}, file ID: {file_id}, zip link: {zip_link}")
        url = f"{self.base_url}/torrents/requestdl?token={self.token}&torrent_id={torrent_id}&file_id={file_id}&zip_link={str(zip_link).lower()}"
        logger.info(f"Torbox: Requesting URL: {url}")
        response = self.json_response(url, headers=self.get_headers())
        logger.info(f"Torbox: Request download link response: {response}")
        return response

    def get_stream_link(self, query, config, ip=None):
        magnet = query['magnet']
        stream_type = query['type']
        file_index = int(query['file_index']) if query['file_index'] is not None else None
        season = query['season']
        episode = query['episode']
        torrent_download = unquote(query["torrent_download"]) if query["torrent_download"] is not None else None

        info_hash = get_info_hash_from_magnet(magnet)
        logger.info(f"Torbox: Getting stream link for {stream_type} with hash: {info_hash}")

        # Check if the torrent is already added
        existing_torrent = self._find_existing_torrent(info_hash)
        
        if existing_torrent:
            logger.info(f"Torbox: Found existing torrent with ID: {existing_torrent['id']}")
            torrent_info = existing_torrent
            if not torrent_info or "id" not in torrent_info:
                logger.error("Torbox: Failed to add or find torrent.")
                return None
            torrent_id = torrent_info["id"]
        else:
            # Add the magnet or torrent file
            torrent_info = self.add_magnet_or_torrent(magnet, torrent_download)
            if not torrent_info or "torrent_id" not in torrent_info:
                logger.error("Torbox: Failed to add or find torrent.")
                return None
            torrent_id = torrent_info["torrent_id"]

        logger.info(f"Torbox: Working with torrent ID: {torrent_id}")

        # Wait for the torrent to be ready
        if not self._wait_for_torrent_completion(torrent_id):
            logger.warning("Torbox: Torrent not ready, caching in progress.")
            return settings.no_cache_video_url

        # Select the appropriate file
        file_id = self._select_file(torrent_info, stream_type, file_index, season, episode)
        
        if file_id == None:
            logger.error("Torbox: No matching file found.")
            return settings.no_cache_video_url

        # Request the download link
        download_link_response = self.request_download_link(torrent_id, file_id)
        
        if not download_link_response or "data" not in download_link_response:
            logger.error("Torbox: Failed to get download link.")
            return settings.no_cache_video_url

        logger.info(f"Torbox: Got download link: {download_link_response['data']}")
        return download_link_response['data']

    def get_availability_bulk(self, hashes_or_magnets, ip=None):
        logger.info(f"Torbox: Checking availability for {len(hashes_or_magnets)} hashes/magnets")
        
        all_results = []
        
        for i in range(0, len(hashes_or_magnets), 50):
            batch = list(islice(hashes_or_magnets, i, i + 50))
            logger.info(f"Torbox: Checking batch of {len(batch)} hashes/magnets (batch {i//50 + 1})")
            url = f"{self.base_url}/torrents/checkcached?hash={','.join(batch)}&format=list&list_files=true"
            logger.trace(f"Torbox: Requesting URL: {url}")
            response = self.json_response(url, headers=self.get_headers())
            
            if response and response.get("success") and response["data"]:
                all_results.extend(response["data"])
            else:
                logger.debug(f"Torbox: No cached avaibility for batch {i//50 + 1}")
                return None
            
        logger.info(f"Torbox: Availability check completed for all {len(hashes_or_magnets)} hashes/magnets")
        return {
            "success": True,
            "detail": "Torrent cache status retrieved successfully.",
            "data": all_results
        }

    def _find_existing_torrent(self, info_hash):
        logger.info(f"Torbox: Searching for existing torrent with hash: {info_hash}")
        torrents = self.json_response(f"{self.base_url}/torrents/mylist", headers=self.get_headers())
        if torrents and "data" in torrents:
            for torrent in torrents["data"]:
                if torrent["hash"].lower() == info_hash.lower():
                    logger.info(f"Torbox: Found existing torrent with ID: {torrent['id']}")
                    return torrent
        logger.info("Torbox: No existing torrent found")
        return None

    def add_magnet_or_torrent(self, magnet, torrent_download=None, ip=None, privacy="private"):
        if torrent_download is None:
            logger.info("Torbox: Adding magnet")
            response = self.add_magnet(magnet, ip, privacy)
        else:
            logger.info("Torbox: Downloading and adding torrent file")
            torrent_file = self.download_torrent_file(torrent_download)
            response = self.add_torrent(torrent_file, privacy)

        logger.info(f"Torbox: Add torrent response: {response}")

        if not response or "data" not in response or response["data"] is None:
            logger.error("Torbox: Failed to add magnet/torrent")
            return None

        return response["data"]

    def _wait_for_torrent_completion(self, torrent_id, timeout=60, interval=10):
        logger.info(f"Torbox: Waiting for torrent completion, ID: {torrent_id}")
        def check_status():
            torrent_info = self.get_torrent_info(torrent_id)
            if torrent_info and "data" in torrent_info:
                files = torrent_info["data"].get("files", [])
                logger.info(f"Torbox: Current torrent status: {torrent_info['data']['download_state']}")
                return True if len(files) > 0 else False
            return False

        result = self.wait_for_ready_status(check_status, timeout, interval)
        if result:
            logger.info("Torbox: Torrent is ready")
        else:
            logger.warning("Torbox: Torrent completion timeout")
        return result

    def _select_file(self, torrent_info, stream_type, file_index, season, episode):
        logger.info(f"Torbox: Selecting file for {stream_type}, file_index: {file_index}, season: {season}, episode: {episode}")
        files = torrent_info.get("files", [])
        
        if stream_type == "movie":
            if file_index is not None:
                logger.info(f"Torbox: Selected file index {file_index} for movie")
                return file_index
            largest_file = max(files, key=lambda x: x["size"])
            logger.info(f"Torbox: Selected largest file (ID: {largest_file['id']}, Size: {largest_file['size']}) for movie")
            return largest_file["id"]
        
        elif stream_type == "series":
            if file_index is not None:
                logger.info(f"Torbox: Selected file index {file_index} for series")
                return file_index
            
            matching_files = [
                file for file in files
                if season_episode_in_filename(file["short_name"], season, episode) and is_video_file(file["short_name"])
            ]
            
            if matching_files:
                largest_matching_file = max(matching_files, key=lambda x: x["size"])
                logger.info(f"Torbox: Selected largest matching file (ID: {largest_matching_file['id']}, Name: {largest_matching_file['name']}, Size: {largest_matching_file['size']}) for series")
                return largest_matching_file["id"]
            else:
                logger.warning(f"Torbox: No matching files found for S{season}E{episode}")
        
        logger.error(f"Torbox: Failed to select appropriate file for {stream_type}")
        return None