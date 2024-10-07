import os
import threading

from typing import List, Dict
from RTN import parse

from stream_fusion.utils.debrid.alldebrid import AllDebrid
from stream_fusion.utils.debrid.premiumize import Premiumize
from stream_fusion.utils.debrid.realdebrid import RealDebrid
from stream_fusion.utils.debrid.torbox import Torbox
from stream_fusion.utils.torrent.torrent_item import TorrentItem
from stream_fusion.utils.cache.cache import cache_public
from stream_fusion.utils.general import season_episode_in_filename
from stream_fusion.logging_config import logger


class TorrentSmartContainer:
    def __init__(self, torrent_items: List[TorrentItem], media):
        self.logger = logger
        self.logger.info(
            f"Initializing TorrentSmartContainer with {len(torrent_items)} items"
        )
        self.__itemsDict: Dict[TorrentItem] = self._build_items_dict_by_infohash(
            torrent_items
        )
        self.__media = media

    def get_unaviable_hashes(self):
        hashes = []
        for hash, item in self.__itemsDict.items():
            if item.availability is False:
                hashes.append(hash)
        self.logger.debug(
            f"TorrentSmartContainer: Retrieved {len(hashes)} hashes to process"
        )
        return hashes

    def get_items(self):
        items = list(self.__itemsDict.values())
        self.logger.debug(f"TorrentSmartContainer: Retrieved {len(items)} items")
        return items

    def get_direct_torrentable(self):
        self.logger.info("TorrentSmartContainer: Retrieving direct torrentable items")
        direct_torrentable_items = []
        for torrent_item in self.__itemsDict.values():
            if torrent_item.privacy == "public" and torrent_item.file_index is not None:
                direct_torrentable_items.append(torrent_item)
        self.logger.info(
            f"TorrentSmartContainer: Found {len(direct_torrentable_items)} direct torrentable items"
        )
        return direct_torrentable_items

    def get_best_matching(self):
        self.logger.info("TorrentSmartContainer: Finding best matching items")
        best_matching = []
        self.logger.debug(
            f"TorrentSmartContainer: Total items to process: {len(self.__itemsDict)}"
        )
        for torrent_item in self.__itemsDict.values():
            self.logger.debug(
                f"TorrentSmartContainer: Processing item: {torrent_item.raw_title} - Has torrent: {torrent_item.torrent_download is not None}"
            )
            if torrent_item.torrent_download is not None:
                self.logger.debug(
                    f"TorrentSmartContainer: Has file index: {torrent_item.file_index is not None}"
                )
                if torrent_item.file_index is not None:
                    best_matching.append(torrent_item)
                    self.logger.debug(
                        "TorrentSmartContainer: Item added to best matching (has file index)"
                    )
                else:
                    matching_file = self._find_matching_file(
                        torrent_item.full_index,
                        self.__media.season,
                        self.__media.episode,
                    )
                    if matching_file:
                        torrent_item.file_index = matching_file["file_index"]
                        torrent_item.file_name = matching_file["file_name"]
                        torrent_item.size = matching_file["size"]
                        best_matching.append(torrent_item)
                        self.logger.debug(
                            f"TorrentSmartContainer: Item added to best matching (found matching file: {matching_file['file_name']})"
                        )
                    else:
                        self.logger.debug(
                            "TorrentSmartContainer: No matching file found, item not added to best matching"
                        )
            else:
                best_matching.append(torrent_item)
                self.logger.debug(
                    "TorrentSmartContainer: Item added to best matching (magnet link)"
                )
        self.logger.info(
            f"TorrentSmartContainer: Found {len(best_matching)} best matching items"
        )
        return best_matching

    def _find_matching_file(self, full_index, season, episode):
        self.logger.info(
            f"TorrentSmartContainer: Searching for matching file: Season {season}, Episode {episode}"
        )

        if not full_index:
            self.logger.warning(
                "TorrentSmartContainer: Full index is empty, cannot find matching file"
            )
            return None
        try:
            target_season = int(season.replace("S", ""))
            target_episode = int(episode.replace("E", ""))
        except ValueError:
            self.logger.error(
                f"TorrentSmartContainer: Invalid season or episode format: {season}, {episode}"
            )
            return None

        best_match = None
        for file_entry in full_index:
            if (
                target_season in file_entry["seasons"]
                and target_episode in file_entry["episodes"]
            ):
                if best_match is None or file_entry["size"] > best_match["size"]:
                    best_match = file_entry
                    self.logger.debug(
                        f"TorrentSmartContainer: Found potential match: {file_entry['file_name']}"
                    )

        if best_match:
            self.logger.info(
                f"TorrentSmartContainer: Best matching file found: {best_match['file_name']}"
            )
            return best_match
        else:
            self.logger.warning(
                f"TorrentSmartContainer: No matching file found for Season {season}, Episode {episode}"
            )
            return None

    def cache_container_items(self):
        self.logger.info(
            "TorrentSmartContainer: Starting cache process for container items"
        )
        threading.Thread(target=self._save_to_cache).start()

    def _save_to_cache(self):
        self.logger.info("TorrentSmartContainer: Saving public items to cache")
        public_torrents = list(
            filter(lambda x: x.privacy == "public", self.get_items())
        )
        self.logger.debug(
            f"TorrentSmartContainer: Found {len(public_torrents)} public torrents to cache"
        )
        cache_public(public_torrents, self.__media)
        self.logger.info("TorrentSmartContainer: Caching process completed")

    def update_availability(self, debrid_response, debrid_type, media):
        if not debrid_response or debrid_response == {} or debrid_response == []:
            self.logger.debug(
                "TorrentSmartContainer: Debrid response is empty : "
                + str(debrid_response)
            )
            return
        self.logger.info(
            f"TorrentSmartContainer: Updating availability for {debrid_type.__name__}"
        )
        if debrid_type is RealDebrid:
            self._update_availability_realdebrid(debrid_response, media)
        elif debrid_type is AllDebrid:
            self._update_availability_alldebrid(debrid_response, media)
        elif debrid_type is Torbox:
            self._update_availability_torbox(debrid_response, media)
        elif debrid_type is Premiumize:
            self._update_availability_premiumize(debrid_response)
        else:
            self.logger.error(
                f"TorrentSmartContainer: Unsupported debrid type: {debrid_type.__name__}"
            )
            raise NotImplementedError(
                f"TorrentSmartContainer: Debrid type {debrid_type.__name__} not implemented"
            )

    def _update_availability_realdebrid(self, response, media):
        self.logger.info("TorrentSmartContainer: Updating availability for RealDebrid")
        for info_hash, details in response.items():
            if "rd" not in details:
                self.logger.debug(
                    f"TorrentSmartContainer: Skipping hash {info_hash}: no RealDebrid data"
                )
                continue
            torrent_item: TorrentItem = self.__itemsDict[info_hash]
            self.logger.debug(
                f"Processing {torrent_item.type}: {torrent_item.raw_title}"
            )
            files = []
            if torrent_item.type == "series":
                self._process_series_files(
                    details, media, torrent_item, files, debrid="RD"
                )
            else:
                self._process_movie_files(details, files)
            self._update_file_details(torrent_item, files, debrid="RD")
        self.logger.info(
            "TorrentSmartContainer: RealDebrid availability update completed"
        )

    def _process_series_files(
        self, details, media, torrent_item, files, debrid: str = "??"
    ):
        for variants in details["rd"]:
            file_found = False
            for file_index, file in variants.items():
                clean_season = media.season.replace("S", "")
                clean_episode = media.episode.replace("E", "")
                numeric_season = int(clean_season)
                numeric_episode = int(clean_episode)
                if season_episode_in_filename(
                    file["filename"], numeric_season, numeric_episode
                ):
                    self.logger.debug(f"Matching file found: {file['filename']}")
                    torrent_item.file_index = file_index
                    torrent_item.file_name = file["filename"]
                    torrent_item.size = file["filesize"]
                    torrent_item.availability = debrid
                    file_found = True
                    files.append(
                        {
                            "file_index": file_index,
                            "title": file["filename"],
                            "size": file["filesize"],
                        }
                    )
                    break
            if file_found:
                break

    def _process_movie_files(self, details, files):
        for variants in details["rd"]:
            for file_index, file in variants.items():
                self.logger.debug(
                    f"TorrentSmartContainer: Adding movie file: {file['filename']}"
                )
                files.append(
                    {
                        "file_index": file_index,
                        "title": file["filename"],
                        "size": file["filesize"],
                    }
                )

    def _update_availability_alldebrid(self, response, media):
        self.logger.info("TorrentSmartContainer: Updating availability for AllDebrid")
        if response == {}:
            self.logger.error("TorrentSmartContainer: AllDebrid response is empty")
            return
        if response["status"] != "success":
            self.logger.error(f"TorrentSmartContainer: AllDebrid API error: {response}")
            return
        for data in response["data"]["magnets"]:
            if not data["instant"]:
                self.logger.debug(
                    f"TorrentSmartContainer: Skipping non-instant magnet: {data['hash']}"
                )
                continue
            torrent_item: TorrentItem = self.__itemsDict[data["hash"]]
            files = []
            self._explore_folders_alldebrid(
                data["files"], files, 1, torrent_item.type, media
            )
            self._update_file_details(torrent_item, files, debrid="AD")
        self.logger.info(
            "TorrentSmartContainer: AllDebrid availability update completed"
        )

    def _update_availability_torbox(self, response, media):
        self.logger.info("TorrentSmartContainer: Updating availability for Torbox")
        if response["success"] is False:
            self.logger.error(f"TorrentSmartContainer: Torbox API error: {response}")
            return

        for data in response["data"]:
            torrent_item: TorrentItem = self.__itemsDict[data["hash"]]
            files = self._process_torbox_files(data["files"], torrent_item.type, media)
            self._update_file_details(torrent_item, files, debrid="TB")

        self.logger.info("TorrentSmartContainer: Torbox availability update completed")

    def _process_torbox_files(self, files, type, media):
        processed_files = []
        for index, file in enumerate(files):
            if type == "series":
                if self._is_matching_episode_torbox(file["name"], media):
                    processed_files.append(
                        {
                            "file_index": index,
                            "title": file["name"],
                            "size": file["size"],
                        }
                    )
            elif type == "movie":
                processed_files.append(
                    {
                        "file_index": index,
                        "title": file["name"],
                        "size": file["size"],
                    }
                )
        return processed_files

    def _is_matching_episode_torbox(self, filepath, media):
            # Extract only the filename from the full path
            filename = os.path.basename(filepath)
            
            clean_season = media.season.replace("S", "")
            clean_episode = media.episode.replace("E", "")
            numeric_season = int(clean_season)
            numeric_episode = int(clean_episode)
            
            return season_episode_in_filename(filename, numeric_season, numeric_episode)

    def _update_availability_premiumize(self, response):
        self.logger.info("TorrentSmartContainer: Updating availability for Premiumize")
        if response["status"] != "success":
            self.logger.error(
                f"TorrentSmartContainer: Premiumize API error: {response}"
            )
            return
        torrent_items = self.get_items()
        for i, is_available in enumerate(response["response"]):
            if bool(is_available):
                torrent_items[i].availability = response["transcoded"][i]
                self.logger.debug(
                    f"TorrentSmartContainer: Updated availability for item {i}: {torrent_items[i].availability}"
                )
        self.logger.info(
            "TorrentSmartContainer: Premiumize availability update completed"
        )

    def _update_file_details(self, torrent_item, files, debrid: str = "??"):
        if not files:
            self.logger.debug(
                f"TorrentSmartContainer: No files to update for {torrent_item.raw_title}"
            )
            return
        file = max(files, key=lambda file: file["size"])
        torrent_item.availability = debrid
        torrent_item.file_index = file["file_index"]
        torrent_item.file_name = file["title"]
        torrent_item.size = file["size"]
        self.logger.debug(
            f"TorrentSmartContainer: Updated file details for {torrent_item.raw_title}: {file['title']}"
        )

    def _build_items_dict_by_infohash(self, items: List[TorrentItem]):
        self.logger.info(
            f"TorrentSmartContainer: Building items dictionary by infohash ({len(items)} items)"
        )
        items_dict = {}
        for item in items:
            if item.info_hash is not None:
                if item.info_hash not in items_dict:
                    self.logger.debug(f"Adding {item.info_hash} to items dict")
                    items_dict[item.info_hash] = item
                else:
                    self.logger.debug(
                        f"TorrentSmartContainer: Skipping duplicate info hash: {item.info_hash}"
                    )
        self.logger.info(
            f"TorrentSmartContainer: Built dictionary with {len(items_dict)} unique items"
        )
        return items_dict

    def _explore_folders_alldebrid(self, folder, files, file_index, type, media):

        if type == "series":
            for file in folder:
                if "e" in file:
                    file_index = self._explore_folders_alldebrid(
                        file["e"], files, file_index, type, media
                    )
                    continue
                parsed_file = parse(file["n"])
                clean_season = media.season.replace("S", "")
                clean_episode = media.episode.replace("E", "")
                numeric_season = int(clean_season)
                numeric_episode = int(clean_episode)
                if (
                    numeric_season in parsed_file.seasons
                    and numeric_episode in parsed_file.episodes
                ):
                    self.logger.debug(
                        f"TorrentSmartContainer: Matching series file found: {file['n']}"
                    )
                    files.append(
                        {
                            "file_index": file_index,
                            "title": file["n"],
                            "size": file["s"] if "s" in file else 0,
                        }
                    )
                file_index += 1
        elif type == "movie":
            file_index = 1
            for file in folder:
                if "e" in file:
                    file_index = self._explore_folders_alldebrid(
                        file["e"], files, file_index, type, media
                    )
                    continue
                self.logger.debug(
                    f"TorrentSmartContainer: Adding movie file: {file['n']}"
                )
                files.append(
                    {
                        "file_index": file_index,
                        "title": file["n"],
                        "size": file["s"] if "s" in file else 0,
                    }
                )
                file_index += 1
        return file_index
