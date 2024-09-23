import threading

from typing import List, Dict
from RTN import parse

from stream_fusion.utils.debrid.alldebrid import AllDebrid
from stream_fusion.utils.debrid.premiumize import Premiumize
from stream_fusion.utils.debrid.realdebrid import RealDebrid
from stream_fusion.utils.torrent.torrent_item import TorrentItem
from stream_fusion.utils.cache.cache import cache_public
from stream_fusion.utils.general import season_episode_in_filename
from stream_fusion.logging_config import logger

class TorrentSmartContainer:
    def __init__(self, torrent_items: List[TorrentItem], media):
        self.logger = logger
        self.logger.info(f"Initializing TorrentSmartContainer with {len(torrent_items)} items")
        self.__itemsDict: Dict[TorrentItem] = self.__build_items_dict_by_infohash(torrent_items)
        self.__media = media

    def get_unaviable_hashes(self):
        hashes = []
        for hash, item in self.__itemsDict.items():
            if item.availability is False:
                hashes.append(hash)
        self.logger.debug(f"Retrieved {len(hashes)} hashes to process for RealDebrid")
        return hashes

    def get_items(self):
        items = list(self.__itemsDict.values())
        self.logger.debug(f"Retrieved {len(items)} items")
        return items

    def get_direct_torrentable(self):
        self.logger.info("Retrieving direct torrentable items")
        direct_torrentable_items = []
        for torrent_item in self.__itemsDict.values():
            if torrent_item.privacy == "public" and torrent_item.file_index is not None:
                direct_torrentable_items.append(torrent_item)
        self.logger.info(f"Found {len(direct_torrentable_items)} direct torrentable items")
        return direct_torrentable_items

    def get_best_matching(self):
        self.logger.info("Finding best matching items")
        best_matching = []
        self.logger.debug(f"Total items to process: {len(self.__itemsDict)}")
        for torrent_item in self.__itemsDict.values():
            self.logger.debug(f"Processing item: {torrent_item.raw_title} - Has torrent: {torrent_item.torrent_download is not None}")
            if torrent_item.torrent_download is not None:
                self.logger.debug(f"Has file index: {torrent_item.file_index is not None}")
                if torrent_item.file_index is not None:
                    best_matching.append(torrent_item)
                    self.logger.debug("Item added to best matching (has file index)")
                else:
                    matching_file = self.__find_matching_file(torrent_item.full_index, self.__media.season, self.__media.episode)
                    if matching_file:
                        torrent_item.file_index = matching_file['file_index']
                        torrent_item.file_name = matching_file['file_name']
                        torrent_item.size = matching_file['size']
                        best_matching.append(torrent_item)
                        self.logger.debug(f"Item added to best matching (found matching file: {matching_file['file_name']})")
                    else:
                        self.logger.debug("No matching file found, item not added to best matching")
            else:
                best_matching.append(torrent_item)
                self.logger.debug("Item added to best matching (magnet link)")
        self.logger.info(f"Found {len(best_matching)} best matching items")
        return best_matching

    def __find_matching_file(self, full_index, season, episode):
        self.logger.info(f"Searching for matching file: Season {season}, Episode {episode}")
        
        if not full_index:
            self.logger.warning("Full index is empty, cannot find matching file")
            return None
        try:
            target_season = int(season.replace('S', ''))
            target_episode = int(episode.replace('E', ''))
        except ValueError:
            self.logger.error(f"Invalid season or episode format: {season}, {episode}")
            return None

        best_match = None
        for file_entry in full_index:
            if target_season in file_entry['seasons'] and target_episode in file_entry['episodes']:
                if best_match is None or file_entry['size'] > best_match['size']:
                    best_match = file_entry
                    self.logger.debug(f"Found potential match: {file_entry['file_name']}")

        if best_match:
            self.logger.info(f"Best matching file found: {best_match['file_name']}")
            return best_match
        else:
            self.logger.warning(f"No matching file found for Season {season}, Episode {episode}")
            return None

    def cache_container_items(self):
        self.logger.info("Starting cache process for container items")
        threading.Thread(target=self.__save_to_cache).start()

    def __save_to_cache(self):
        self.logger.info("Saving public items to cache")
        public_torrents = list(filter(lambda x: x.privacy == "public", self.get_items()))
        self.logger.debug(f"Found {len(public_torrents)} public torrents to cache")
        cache_public(public_torrents, self.__media)
        self.logger.info("Caching process completed")

    def update_availability(self, debrid_response, debrid_type, media):
        self.logger.info(f"Updating availability for {debrid_type.__name__}")
        if debrid_type is RealDebrid:
            self.__update_availability_realdebrid(debrid_response, media)
        elif debrid_type is AllDebrid:
            self.__update_availability_alldebrid(debrid_response, media)
        elif debrid_type is Premiumize:
            self.__update_availability_premiumize(debrid_response)
        else:
            self.logger.error(f"Unsupported debrid type: {debrid_type.__name__}")
            raise NotImplementedError(f"Debrid type {debrid_type.__name__} not implemented")

    def __update_availability_realdebrid(self, response, media):
        self.logger.info("Updating availability for RealDebrid")
        for info_hash, details in response.items():
            if "rd" not in details:
                self.logger.debug(f"Skipping hash {info_hash}: no RealDebrid data")
                continue
            torrent_item: TorrentItem = self.__itemsDict[info_hash]
            self.logger.debug(f"Processing {torrent_item.type}: {torrent_item.raw_title}")
            files = []
            if torrent_item.type == "series":
                self.__process_series_files(details, media, torrent_item, files, debrid="RD")
            else:
                self.__process_movie_files(details, files)
            self.__update_file_details(torrent_item, files, debrid="RD")
        self.logger.info("RealDebrid availability update completed")

    def __process_series_files(self, details, media, torrent_item, files, debrid: str = "??"):
        for variants in details["rd"]:
            file_found = False
            for file_index, file in variants.items():
                clean_season = media.season.replace("S", "")
                clean_episode = media.episode.replace("E", "")
                numeric_season = int(clean_season)
                numeric_episode = int(clean_episode)
                if season_episode_in_filename(file["filename"], numeric_season, numeric_episode):
                    self.logger.debug(f"Matching file found: {file['filename']}")
                    torrent_item.file_index = file_index
                    torrent_item.file_name = file["filename"]
                    torrent_item.size = file["filesize"]
                    torrent_item.availability = debrid
                    file_found = True
                    files.append({
                        "file_index": file_index,
                        "title": file["filename"],
                        "size": file["filesize"]
                    })
                    break
            if file_found:
                break

    def __process_movie_files(self, details, files):
        for variants in details["rd"]:
            for file_index, file in variants.items():
                self.logger.debug(f"Adding movie file: {file['filename']}")
                files.append({
                    "file_index": file_index,
                    "title": file["filename"],
                    "size": file["filesize"]
                })

    def __update_availability_alldebrid(self, response, media):
        self.logger.info("Updating availability for AllDebrid")
        if response["status"] != "success":
            self.logger.error(f"AllDebrid API error: {response}")
            return
        for data in response["data"]["magnets"]:
            if not data["instant"]:
                self.logger.debug(f"Skipping non-instant magnet: {data['hash']}")
                continue
            torrent_item: TorrentItem = self.__itemsDict[data["hash"]]
            files = []
            self.__explore_folders(data["files"], files, 1, torrent_item.type, media)
            self.__update_file_details(torrent_item, files, debrid="AD")
        self.logger.info("AllDebrid availability update completed")

    def __update_availability_premiumize(self, response):
        self.logger.info("Updating availability for Premiumize")
        if response["status"] != "success":
            self.logger.error(f"Premiumize API error: {response}")
            return
        torrent_items = self.get_items()
        for i, is_available in enumerate(response["response"]):
            if bool(is_available):
                torrent_items[i].availability = response["transcoded"][i]
                self.logger.debug(f"Updated availability for item {i}: {torrent_items[i].availability}")
        self.logger.info("Premiumize availability update completed")

    def __update_file_details(self, torrent_item, files, debrid: str = "??"):
        if not files:
            self.logger.debug(f"No files to update for {torrent_item.raw_title}")
            return
        file = max(files, key=lambda file: file["size"])
        torrent_item.availability = debrid
        torrent_item.file_index = file["file_index"]
        torrent_item.file_name = file["title"]
        torrent_item.size = file["size"]
        self.logger.debug(f"Updated file details for {torrent_item.raw_title}: {file['title']}")

    def __build_items_dict_by_infohash(self, items: List[TorrentItem]):
        self.logger.info(f"Building items dictionary by infohash ({len(items)} items)")
        items_dict = {}
        for item in items:
            if item.info_hash is not None:
                if item.info_hash not in items_dict:
                    self.logger.debug(f"Adding {item.info_hash} to items dict")
                    items_dict[item.info_hash] = item
                else:
                    self.logger.debug(f"Skipping duplicate info hash: {item.info_hash}")
        self.logger.info(f"Built dictionary with {len(items_dict)} unique items")
        return items_dict

    def __explore_folders(self, folder, files, file_index, type, media):
        
        if type == "series":
            for file in folder:
                if "e" in file:
                    file_index = self.__explore_folders(file["e"], files, file_index, type, media)
                    continue
                parsed_file = parse(file["n"])
                clean_season = media.season.replace("S", "")
                clean_episode = media.episode.replace("E", "")
                numeric_season = int(clean_season)
                numeric_episode = int(clean_episode)
                if numeric_season in parsed_file.seasons and numeric_episode in parsed_file.episodes:
                    self.logger.debug(f"Matching series file found: {file['n']}")
                    files.append({
                        "file_index": file_index,
                        "title": file["n"],
                        "size": file["s"] if "s" in file else 0
                    })
                file_index += 1
        elif type == "movie":
            file_index = 1
            for file in folder:
                if "e" in file:
                    file_index = self.__explore_folders(file["e"], files, file_index, type, media)
                    continue
                self.logger.debug(f"Adding movie file: {file['n']}")
                files.append({
                    "file_index": file_index,
                    "title": file["n"],
                    "size": file["s"] if "s" in file else 0
                })
                file_index += 1
        return file_index