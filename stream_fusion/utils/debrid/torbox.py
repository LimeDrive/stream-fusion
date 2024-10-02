from urllib.parse import unquote
from stream_fusion.constants import NO_CACHE_VIDEO_URL
from stream_fusion.utils.debrid.base_debrid import BaseDebrid
from stream_fusion.utils.general import get_info_hash_from_magnet, season_episode_in_filename, is_video_file
from stream_fusion.logging_config import logger
from stream_fusion.settings import settings

class Torbox(BaseDebrid):
    def __init__(self, config):
        super().__init__(config)
        self.base_url = f"https://api.torbox.app/v1/api"
        logger.info(f"Torbox: Initialized with base URL: {self.base_url}")

    def get_headers(self):
        # TODO: Add support for unique account and check for token conn
        return {"Authorization": f"Bearer {settings.torbox_api_key}"}

    def add_magnet(self, magnet, ip=None):
        logger.info(f"Torbox: Adding magnet: {magnet[:50]}...")
        url = f"{self.base_url}/torrents/createtorrent"
        data = {
            "magnet": magnet,
            "seed": 1,  # Auto seeding
            "allow_zip": "true"
        }
        response = self.json_response(url, method='post', headers=self.get_headers(), data=data)
        logger.info(f"Torbox: Add magnet response: {response}")
        return response

    def add_torrent(self, torrent_file):
        logger.info("Torbox: Adding torrent file")
        url = f"{self.base_url}/torrents/createtorrent"
        files = {"file": torrent_file}
        data = {
            "seed": 1,  # Auto seeding
            "allow_zip": "true"
        }
        response = self.json_response(url, method='post', headers=self.get_headers(), data=data, files=files)
        logger.info(f"Torbox: Add torrent file response: {response}")
        return response

    def get_torrent_info(self, torrent_id):
        logger.info(f"Torbox: Getting info for torrent ID: {torrent_id}")
        url = f"{self.base_url}/torrents/mylist?id={torrent_id}"
        response = self.json_response(url, headers=self.get_headers())
        logger.info(f"Torbox: Torrent info response: {response}")
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

    def request_download_link(self, torrent_id, file_id=None, zip_link=False):
        logger.info(f"Torbox: Requesting download link for torrent ID: {torrent_id}, file ID: {file_id}, zip link: {zip_link}")
        url = f"{self.base_url}/torrents/requestdl"
        params = {
            "torrent_id": torrent_id,
            "zip_link": str(zip_link).lower()
        }
        if file_id:
            params["file_id"] = file_id
        response = self.json_response(url, headers=self.get_headers(), method='get', data=params)
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
        else:
            # Add the magnet or torrent file
            torrent_info = self._add_magnet_or_torrent(magnet, torrent_download)

        if not torrent_info or "id" not in torrent_info:
            logger.error("Torbox: Failed to add or find torrent.")
            return "Error: Failed to add or find torrent."

        torrent_id = torrent_info["id"]
        logger.info(f"Torbox: Working with torrent ID: {torrent_id}")

        # Wait for the torrent to be ready
        if not self._wait_for_torrent_completion(torrent_id):
            logger.warning("Torbox: Torrent not ready, caching in progress.")
            return NO_CACHE_VIDEO_URL

        # Select the appropriate file
        file_id = self._select_file(torrent_info, stream_type, file_index, season, episode)
        
        if not file_id:
            logger.error("Torbox: No matching file found.")
            return NO_CACHE_VIDEO_URL

        # Request the download link
        download_link_response = self.request_download_link(torrent_id, file_id)
        
        if not download_link_response or "data" not in download_link_response:
            logger.error("Torbox: Failed to get download link.")
            return NO_CACHE_VIDEO_URL

        logger.info(f"Torbox: Got download link: {download_link_response['data']}")
        return download_link_response['data']

    def get_availability_bulk(self, hashes_or_magnets, ip=None):
        logger.info(f"Torbox: Checking availability for {len(hashes_or_magnets)} hashes/magnets")
        url = f"{self.base_url}/torrents/checkcached"
        params = {"hash": ",".join(hashes_or_magnets), "format": "object"}
        response = self.json_response(url, headers=self.get_headers(), method='get', data=params)
        logger.info(f"Torbox: Availability check response: {response}")
        return response

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

    def _add_magnet_or_torrent(self, magnet, torrent_download=None):
        if torrent_download is None:
            logger.info("Torbox: Adding magnet")
            response = self.add_magnet(magnet)
        else:
            logger.info("Torbox: Downloading and adding torrent file")
            torrent_file = self.download_torrent_file(torrent_download)
            response = self.add_torrent(torrent_file)

        logger.info(f"Torbox: Add torrent response: {response}")

        if not response or "data" not in response or response["data"] is None:
            logger.error("Torbox: Failed to add magnet/torrent")
            return None

        return response["data"]

    def _wait_for_torrent_completion(self, torrent_id, timeout=300, interval=10):
        logger.info(f"Torbox: Waiting for torrent completion, ID: {torrent_id}")
        def check_status():
            torrent_info = self.get_torrent_info(torrent_id)
            if torrent_info and "data" in torrent_info:
                status = torrent_info["data"].get("download_state", "")
                logger.info(f"Torbox: Current torrent status: {status}")
                return status in ["uploading", "completed", "cached"]
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
                if season_episode_in_filename(file["name"], season, episode) and is_video_file(file["name"])
            ]
            
            if matching_files:
                largest_matching_file = max(matching_files, key=lambda x: x["size"])
                logger.info(f"Torbox: Selected largest matching file (ID: {largest_matching_file['id']}, Name: {largest_matching_file['name']}, Size: {largest_matching_file['size']}) for series")
                return largest_matching_file["id"]
            else:
                logger.warning(f"Torbox: No matching files found for S{season}E{episode}")
        
        logger.error(f"Torbox: Failed to select appropriate file for {stream_type}")
        return None