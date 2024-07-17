import re
from typing import List

from RTN import title_match, RTN, DefaultRanking, SettingsModel, sort_torrents

from stream_fusion.utils.filter.language_filter import LanguageFilter
from stream_fusion.utils.filter.max_size_filter import MaxSizeFilter
from stream_fusion.utils.filter.quality_exclusion_filter import QualityExclusionFilter
from stream_fusion.utils.filter.results_per_quality_filter import ResultsPerQualityFilter
from stream_fusion.utils.filter.title_exclusion_filter import TitleExclusionFilter
from stream_fusion.utils.torrent.torrent_item import TorrentItem
from stream_fusion.logging_config import logger

quality_order = {"4k": 0, "2160p": 0, "1080p": 1, "720p": 2, "480p": 3}


def sort_quality(item):
    logger.debug(f"Evaluating quality for item: {item.raw_title}")
    if len(item.parsed_data.data.resolution) == 0:
        return float("inf"), True
    resolution = item.parsed_data.data.resolution[0]
    priority = quality_order.get(resolution, float("inf"))
    return priority, item.parsed_data.data.resolution is None


def items_sort(items, config):
    logger.info(f"Starting item sorting. Sort method: {config['sort']}")
    settings = SettingsModel(
        require=[],
        exclude=config["exclusionKeywords"] + config["exclusion"],
        preferred=[],
    )

    rtn = RTN(settings=settings, ranking_model=DefaultRanking())
    logger.debug("Applying RTN ranking to items")
    torrents = [rtn.rank(item.raw_title, item.info_hash) for item in items]
    sorted_torrents = sort_torrents(set(torrents))

    for key, value in sorted_torrents.items():
        index = next((i for i, item in enumerate(items) if item.info_hash == key), None)
        if index is not None:
            items[index].parsed_data = value

    logger.info(f"Sorting items by method: {config['sort']}")
    if config["sort"] == "quality":
        sorted_items = sorted(items, key=sort_quality)
    elif config["sort"] == "sizeasc":
        sorted_items = sorted(items, key=lambda x: int(x.size))
    elif config["sort"] == "sizedesc":
        sorted_items = sorted(items, key=lambda x: int(x.size), reverse=True)
    elif config["sort"] == "qualitythensize":
        sorted_items = sorted(items, key=lambda x: (sort_quality(x), -int(x.size)))
    else:
        logger.warning(
            f"Unrecognized sort method: {config['sort']}. No sorting applied."
        )
        sorted_items = items

    logger.info(f"Sorting complete. Number of sorted items: {len(sorted_items)}")
    return sorted_items

def filter_out_non_matching_movies(items, year):
    logger.info(f"Filtering non-matching movies for year : {year}")
    year_pattern = re.compile(rf'\b{year}\b')
    filtered_items = []
    for item in items:
        logger.debug(f"Checking item: {item.raw_title}")
        if year_pattern.search(item.raw_title):
            logger.debug("Match found")
            filtered_items.append(item)
        else:
            logger.debug("No match found")
    return filtered_items

def filter_out_non_matching_series(items, season, episode):
    logger.info(
        f"Filtering non-matching items for season {season} and episode {episode}"
    )
    filtered_items = []
    clean_season = season.replace("S", "")
    clean_episode = episode.replace("E", "")
    numeric_season = int(clean_season)
    numeric_episode = int(clean_episode)

    for item in items:
        logger.debug(f"Checking item: {item.raw_title}")
        if len(item.parsed_data.season) == 0 and len(item.parsed_data.episode) == 0:
            logger.debug("Item with no season and episode, skipped")
            continue
        if (
            len(item.parsed_data.episode) == 0
            and numeric_season in item.parsed_data.season
        ):
            logger.debug("Season match found, episode not specified")
            filtered_items.append(item)
            continue
        if (
            numeric_season in item.parsed_data.season
            and numeric_episode in item.parsed_data.episode
        ):
            logger.debug("Exact season and episode match found")
            filtered_items.append(item)
            continue

    logger.info(
        f"Filtering complete. {len(filtered_items)} matching items found out of {len(items)} total"
    )
    return filtered_items


def clean_tmdb_title(title):
    characters_to_filter = r'[<>:"/\\|?*\x00-\x1F™®©℠¡¿–—''""•…]'
    cleaned_title = re.sub(characters_to_filter, ' ', title)
    cleaned_title = cleaned_title.strip()
    cleaned_title = re.sub(r'\s+', ' ', cleaned_title)
    return cleaned_title

def remove_non_matching_title(items, titles):
    logger.info(f"Removing items not matching titles: {titles}")
    filtered_items = []
    cleaned_titles = [clean_tmdb_title(title) for title in titles]
    
    for item in items:
        for cleaned_title in cleaned_titles:
            if title_match(cleaned_title, item.parsed_data.parsed_title):
                filtered_items.append(item)
                break
        else:
            logger.debug("No title match found, item skipped")

    logger.info(
        f"Title filtering complete. {len(filtered_items)} items kept out of {len(items)} total"
    )
    return filtered_items


def filter_items(items, media, config):
    logger.info(f"Starting item filtering for media: {media.titles[0]}")
    filters = {
        "languages": LanguageFilter(config),
        "maxSize": MaxSizeFilter(config, media.type),
        "exclusionKeywords": TitleExclusionFilter(config),
        "exclusion": QualityExclusionFilter(config),
        "resultsPerQuality": ResultsPerQualityFilter(config),
    }

    logger.info(f"Initial item count: {len(items)}")

    if media.type == "series":
        logger.info(f"Filtering out non-matching series torrents")
        items = filter_out_non_matching_series(items, media.season, media.episode)
        logger.info(f"Item count after season/episode filtering: {len(items)}")

    if media.type == "movie":
        logger.info(f"Filtering out non-matching movie torrents")
        items = filter_out_non_matching_movies(items, media.year)
        logger.info(f"Item count after year filtering: {len(items)}")

    items = remove_non_matching_title(items, media.titles)
    logger.info(f"Item count after title filtering: {len(items)}")

    for filter_name, filter_instance in filters.items():
        try:
            logger.info(f"Applying {filter_name} filter: {config[filter_name]}")
            items = filter_instance(items)
            logger.info(f"Item count after {filter_name} filter: {len(items)}")
        except Exception as e:
            logger.error(f"Error while applying {filter_name} filter", exc_info=e)

    logger.info(f"Filtering complete. Final item count: {len(items)}")
    return items


def sort_items(items, config):
    if config["sort"] is not None:
        logger.info(f"Sorting items according to config: {config['sort']}")
        return items_sort(items, config)
    else:
        logger.info("No sorting specified, returning items in original order")
        return items


def merge_items(
    cache_items: List[TorrentItem], search_items: List[TorrentItem]
) -> List[TorrentItem]:
    # Log the number of items being merged
    logger.info(
        f"Merging cached items ({len(cache_items)}) and search items ({len(search_items)})"
    )
    merged_dict = {}

    def add_to_merged(item):
        key = (item.info_hash, item.size)
        if key not in merged_dict or item.seeders > merged_dict[key].seeders:
            merged_dict[key] = item

    # Process cache items
    for item in cache_items:
        add_to_merged(item)
    # Process search items
    for item in search_items:
        add_to_merged(item)

    # Convert the dictionary values to a list
    merged_items = list(merged_dict.values())
    # Log the total number of unique items after merging
    logger.info(f"Merging complete. Total unique items: {len(merged_items)}")
    return merged_items
