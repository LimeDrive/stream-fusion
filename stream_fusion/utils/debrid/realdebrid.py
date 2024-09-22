import re
import json
import time
from urllib.parse import unquote

from fastapi import HTTPException
import requests

from stream_fusion.constants import NO_CACHE_VIDEO_URL
from stream_fusion.services.rd_conn.token_manager import RDTokenManager
from stream_fusion.utils.debrid.base_debrid import BaseDebrid
from stream_fusion.utils.general import get_info_hash_from_magnet
from stream_fusion.utils.general import is_video_file
from stream_fusion.utils.general import season_episode_in_filename
from stream_fusion.settings import settings
from stream_fusion.logging_config import logger


class RealDebrid(BaseDebrid):
    def __init__(self, config):
        super().__init__(config)
        self.base_url = "https://api.real-debrid.com"
        if not settings.rd_unique_account:
            self.token_manager = RDTokenManager(config)

    def get_headers(self):
        if settings.rd_unique_account:
            if not settings.proxied_link:
                logger.warning("Real-Debrid unique account is enabled, but proxied link is disabled. "
                               "This may lead to account ban.")
                logger.warning("Please enable proxied link in the settings.")
                raise HTTPException(status_code=500, detail="Proxied link is disabled.")
            if settings.rd_token:
                return {"Authorization": f"Bearer {settings.rd_token}"}
            else:
                logger.warning("Real-Debrid unique account is enabled, but no token is provided. "
                               "Please provide a token in the env.")
                raise HTTPException(status_code=500, detail="Real-Debrid token is not provided.")
        else:
            return {"Authorization": f"Bearer {self.token_manager.get_access_token()}"}

    def add_magnet(self, magnet, ip=None):
        url = f"{self.base_url}/rest/1.0/torrents/addMagnet"
        data = {"magnet": magnet}
        logger.info(f"Adding magnet to RD: {magnet}")
        return self.json_response(url, method='post', headers=self.get_headers(), data=data)

    def add_torrent(self, torrent_file):
        url = f"{self.base_url}/rest/1.0/torrents/addTorrent"
        return self.json_response(url, method='put', headers=self.get_headers(), data=torrent_file)

    def delete_torrent(self, id):
        url = f"{self.base_url}/rest/1.0/torrents/delete/{id}"
        return self.json_response(url, method='delete', headers=self.get_headers())

    def get_torrent_info(self, torrent_id):
        logger.info(f"Getting torrent info for: {torrent_id}")
        url = f"{self.base_url}/rest/1.0/torrents/info/{torrent_id}"
        torrent_info = self.json_response(url, headers=self.get_headers())
        if not torrent_info or 'files' not in torrent_info:
            return None
        return torrent_info

    def select_files(self, torrent_id, file_id):
        logger.info(f"Selecting file(s): {file_id}")
        self._torrent_rate_limit()
        url = f"{self.base_url}/rest/1.0/torrents/selectFiles/{torrent_id}"
        data = {"files": str(file_id)}
        requests.post(url, headers=self.get_headers(), data=data)

    def unrestrict_link(self, link):
        url = f"{self.base_url}/rest/1.0/unrestrict/link"
        data = {"link": link}
        return self.json_response(url, method='post', headers=self.get_headers(), data=data)

    def is_already_added(self, magnet):
        hash = magnet.split("urn:btih:")[1].split("&")[0].lower()
        url = f"{self.base_url}/rest/1.0/torrents"
        torrents = self.json_response(url, headers=self.get_headers())
        for torrent in torrents:
            if torrent['hash'].lower() == hash:
                return torrent['id']
        return False

    def wait_for_link(self, torrent_id, timeout=60, interval=5):
        start_time = time.time()
        while time.time() - start_time < timeout:
            torrent_info = self.get_torrent_info(torrent_id)
            if torrent_info and 'links' in torrent_info and len(torrent_info['links']) > 0:
                return torrent_info['links']
            time.sleep(interval)

        return None

    def get_availability_bulk(self, hashes_or_magnets, ip=None):
        self._torrent_rate_limit()
        if len(hashes_or_magnets) == 0:
            logger.info("No hashes to be sent to Real-Debrid.")
            return dict()

        url = f"{self.base_url}/rest/1.0/torrents/instantAvailability/{'/'.join(hashes_or_magnets)}"
        return self.json_response(url, headers=self.get_headers())

    def get_stream_link(self, query, config, ip=None):

        magnet = query['magnet']
        stream_type = query['type']
        file_index = int(query['file_index']) if query['file_index'] is not None else None
        season = query['season']
        episode = query['episode']
        torrent_download = unquote(query["torrent_download"]) if query["torrent_download"] is not None else None
        info_hash = get_info_hash_from_magnet(magnet)
        logger.info(f"RealDebrid get stream link for {stream_type} with hash: {info_hash}")

        cached_torrent_ids = self.__get_cached_torrent_ids(info_hash)
        logger.info(f"Found {len(cached_torrent_ids)} cached torrents with hash: {info_hash}")

        torrent_info = None
        if len(cached_torrent_ids) > 0:
            if stream_type == "movie":
                torrent_info = self.get_torrent_info(cached_torrent_ids[0])
            elif stream_type == "series":
                torrent_info = self.__get_cached_torrent_info(cached_torrent_ids, file_index, season, episode)
            else:
                return "Error: Unsupported stream type."

        # The torrent is not yet added
        if torrent_info is None:
            torrent_info = self.__add_magnet_or_torrent(magnet, torrent_download)
            if not torrent_info or 'files' not in torrent_info:
                return "Error: Failed to get torrent info."

            logger.info("Selecting file")
            self.__select_file(torrent_info, stream_type, file_index, season, episode)

            # == operator, to avoid adding the season pack twice and setting 5 as season pack treshold
            if len(cached_torrent_ids) == 0 and stream_type == "series" and len(torrent_info["files"]) > 5:
                logger.info("Prefetching season pack")
                prefetched_torrent_info = self.__prefetch_season_pack(magnet, torrent_download)
                if len(prefetched_torrent_info["links"]) > 0:
                    self.delete_torrent(torrent_info["id"])
                    torrent_info = prefetched_torrent_info

        torrent_id = torrent_info["id"]
        logger.info(f"Waiting for the link(s) to be ready for torrent ID: {torrent_id}")
        # Waiting for the link(s) to be ready
        links = self.wait_for_link(torrent_id)
        if links is None:
            return NO_CACHE_VIDEO_URL

        if len(links) > 1:
            logger.info("Finding appropiate link")
            download_link = self.__find_appropiate_link(torrent_info, links, file_index, season, episode)
        else:
            download_link = links[0]

        logger.info(f"Unrestricting the download link: {download_link}")
        # Unrestricting the download link
        unrestrict_response = self.unrestrict_link(download_link)
        if not unrestrict_response or 'download' not in unrestrict_response:
            return "Error: Failed to unrestrict link."

        logger.info(f"Got download link: {unrestrict_response['download']}")
        return unrestrict_response['download']

    def __get_cached_torrent_ids(self, info_hash):
        self._torrent_rate_limit()
        url = f"{self.base_url}/rest/1.0/torrents"
        torrents = self.json_response(url, headers=self.get_headers())

        logger.info(f"Searching users real-debrid downloads for {info_hash}")
        torrent_ids = []
        for torrent in torrents:
            if torrent['hash'].lower() == info_hash:
                torrent_ids.append(torrent['id'])

        return torrent_ids

    def __get_cached_torrent_info(self, cached_ids, file_index, season, episode):
        cached_torrents = []
        for cached_torrent_id in cached_ids:
            cached_torrent_info = self.get_torrent_info(cached_torrent_id)
            if self.__torrent_contains_file(cached_torrent_info, file_index, season, episode):
                if len(cached_torrent_info["links"]) > 0:  # If the links are ready
                    return cached_torrent_info

                cached_torrents.append(cached_torrent_info)

        if len(cached_torrents) == 0:
            return None

        return max(cached_torrents, key=lambda x: x['progress'])

    def __torrent_contains_file(self, torrent_info, file_index, season, episode):
        if not torrent_info or "files" not in torrent_info:
            return False

        if file_index is None:
            for file in torrent_info["files"]:
                if file["selected"] and season_episode_in_filename(file['path'], season, episode):
                    return True
        else:
            for file in torrent_info["files"]:
                if file['id'] == file_index:
                    return file["selected"] == 1

        return False

    def __add_magnet_or_torrent(self, magnet, torrent_download=None, anon_magnet=False):
        torrent_id = ""
        if torrent_download is None:
            logger.info(f"Adding magnet to RealDebrid")
            if anon_magnet:
                magnet = re.sub(r'&tr=[^&]*', '', magnet)
            magnet_response = self.add_magnet(magnet)
            logger.info(f"RealDebrid add magnet response: {magnet_response}")

            if not magnet_response or 'id' not in magnet_response:
                return "Error: Failed to add magnet."

            torrent_id = magnet_response['id']
        elif anon_magnet and torrent_download:
            logger.info(f"Adding magnet to RealDebrid")
            clean_magnet = re.sub(r'&tr=[^&]*', '', magnet)
            magnet_response = self.add_magnet(clean_magnet)
            logger.info(f"RealDebrid add magnet response: {magnet_response}")

            if not magnet_response or 'id' not in magnet_response:
                return "Error: Failed to add magnet."

            torrent_id = magnet_response['id']
        else:
            logger.info(f"Downloading torrent file from Jackett")
            torrent_file = self.download_torrent_file(torrent_download)
            logger.info(f"Torrent file downloaded from Jackett")

            logger.info(f"Adding torrent file to RealDebrid")
            upload_response = self.add_torrent(torrent_file)
            logger.info(f"RealDebrid add torrent file response: {upload_response}")

            if not upload_response or 'id' not in upload_response:
                return "Error: Failed to add torrent file."

            torrent_id = upload_response['id']

        logger.info(f"New torrent ID: {torrent_id}")
        return self.get_torrent_info(torrent_id)

    def __prefetch_season_pack(self, magnet, torrent_download):
        torrent_info = self.__add_magnet_or_torrent(magnet, torrent_download)
        video_file_indexes = []

        for file in torrent_info["files"]:
            if is_video_file(file["path"]):
                video_file_indexes.append(str(file["id"]))

        self.select_files(torrent_info["id"], ",".join(video_file_indexes))
        time.sleep(10)
        return self.get_torrent_info(torrent_info["id"])

    def __select_file(self, torrent_info, stream_type, file_index, season, episode):
        torrent_id = torrent_info["id"]
        if file_index is not None:
            logger.info(f"Selecting file_index: {file_index}")
            self.select_files(torrent_id, file_index)
            return

        files = torrent_info["files"]
        if stream_type == "movie":
            largest_file_id = max(files, key=lambda x: x['bytes'])['id']
            logger.info(f"Selecting file_index: {largest_file_id}")
            self.select_files(torrent_id, largest_file_id)
        elif stream_type == "series":
            matching_files = []
            for file in files:
                if season_episode_in_filename(file["path"], season, episode):
                    matching_files.append(file)

            largest_file_id = max(matching_files, key=lambda x: x['bytes'])['id']
            logger.info(f"Selecting file_index: {largest_file_id}")
            self.select_files(torrent_id, largest_file_id)

    def __find_appropiate_link(self, torrent_info, links, file_index, season, episode):
        selected_files = list(filter(lambda file: file["selected"] == 1, torrent_info["files"]))

        index = 0
        if file_index is not None:
            for file in selected_files:
                if file["id"] == file_index:
                    break
                index += 1
        else:
            matching_indexes = []
            for file in selected_files:
                if season_episode_in_filename(file["path"], season, episode):
                    matching_indexes.append({"index": index, "file": file})
                index += 1

            index = max(matching_indexes, lambda x: x["file"]["bytes"])["index"]

        if len(links) - 1 < index:
            logger.debug(f"From selected files {selected_files}, index: {index} is out of range for {links}.")
            return NO_CACHE_VIDEO_URL

        return links[index]
