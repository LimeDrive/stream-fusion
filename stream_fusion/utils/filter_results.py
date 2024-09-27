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

quality_order = {"2160p": 0, "1080p": 1, "720p": 2, "480p": 3}


def sort_quality(item: TorrentItem):
    logger.debug(f"Evaluating quality for item: {item.raw_title}")
    if not item.parsed_data.resolution:
        return float("inf"), True
    resolution = item.parsed_data.resolution
    priority = quality_order.get(resolution, float("inf"))
    return priority, item.parsed_data.resolution is None


def items_sort(items, config):
    logger.info(f"Starting item sorting. Sort method: {config['sort']}")
    # settings = SettingsModel(
    #     require=[],
    #     exclude=config["exclusionKeywords"] + config["exclusion"],
    #     preferred=[],
    # )

    # rtn = RTN(settings=settings, ranking_model=DefaultRanking())
    # logger.debug("Applying RTN ranking to items")
    # torrents = [rtn.rank(item.raw_title, item.info_hash) for item in items]
    # sorted_torrents = sort_torrents(set(torrents))

    # for key, value in sorted_torrents.items():
    #     index = next((i for i, item in enumerate(items) if item.info_hash == key), None)
    #     if index is not None:
    #         items[index].parsed_data = value

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
    year_min = str(int(year) - 1)
    year_max = str(int(year) + 1)
    year_pattern = re.compile(rf'\b{year_max}|{year}|{year_min}\b')
    filtered_items = []
    for item in items:
        if year_pattern.search(item.raw_title):
            logger.debug(f"Match found for year {year} in item: {item.raw_title}")
            filtered_items.append(item)
        else:
            logger.debug(f"No match found for year {year} in item: {item.raw_title}")
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

    integrale_pattern = re.compile(r'\b(INTEGRALE|COMPLET|COMPLETE|INTEGRAL)\b', re.IGNORECASE)

    for item in items:
        if len(item.parsed_data.seasons) == 0 and len(item.parsed_data.episodes) == 0:
            if integrale_pattern.search(item.raw_title):
                logger.debug(f"Integrale match found for item: {item.raw_title}")
                filtered_items.append(item)
            logger.debug(f"No season or episode information found for item: {item.raw_title}")
            continue
        if (
            len(item.parsed_data.episodes) == 0
            and numeric_season in item.parsed_data.seasons
        ):
            logger.debug(f"Exact season match found for item: {item.raw_title}")
            filtered_items.append(item)
            continue
        if (
            numeric_season in item.parsed_data.seasons
            and numeric_episode in item.parsed_data.episodes
        ):
            logger.debug(f"Exact season and episode match found for item: {item.raw_title}")
            filtered_items.append(item)
            continue

    logger.info(
        f"Filtering complete. {len(filtered_items)} matching items found out of {len(items)} total"
    )
    return filtered_items


def clean_tmdb_title(title):
    # Dictionnaire des caractères à filtrer, groupés par catégorie
    characters_to_filter = {
        'ponctuation': r'<>"/\\|?*',
        'controle': r'\x00-\x1F',
        'symboles': r'\u2122\u00AE\u00A9\u2120\u00A1\u00BF\u2013\u2014\u2018\u2019\u201C\u201D\u2022\u2026',
        'espaces': r'\s+'
    }
    
    filter_pattern = ''.join([f'[{chars}]' for chars in characters_to_filter.values()])   
    cleaned_title = re.sub(r':(\S)', r' \1', title)
    cleaned_title = re.sub(r'\s*:\s*', ' ', cleaned_title)
    cleaned_title = re.sub(filter_pattern, ' ', cleaned_title)
    cleaned_title = cleaned_title.strip()
    cleaned_title = re.sub(characters_to_filter['espaces'], ' ', cleaned_title)
    
    return cleaned_title

def remove_non_matching_title(items, titles):
    filtered_items = []
    integrale_pattern = re.compile(r'\b(INTEGRALE|COMPLET|COMPLETE|INTEGRAL)\b', re.IGNORECASE)
    cleaned_titles = [clean_tmdb_title(title) for title in titles]
    cleaned_titles = [integrale_pattern.sub('', title).strip() for title in cleaned_titles]
    logger.info(f"Removing items not matching titles: {cleaned_titles}")
    
    def is_ordered_subset(subset, full_set):
        subset_words = subset.lower().split()
        full_set_words = full_set.lower().split()
        subset_index = 0
        for word in full_set_words:
            if subset_index < len(subset_words) and word == subset_words[subset_index]:
                subset_index += 1
        return subset_index == len(subset_words)
    
    for item in items:
        cleaned_item_title = integrale_pattern.sub('', item.parsed_data.parsed_title).strip()
        for title in cleaned_titles:
            logger.debug(f"Comparing item title: {cleaned_item_title} with title: {title}")
            
            if is_ordered_subset(cleaned_item_title, title):
                logger.debug(f"Ordered subset match found. Item accepted: {cleaned_item_title}")
                filtered_items.append(item)
                break
            elif is_ordered_subset(title, cleaned_item_title):
                logger.debug(f"Reverse ordered subset match found. Item accepted: {cleaned_item_title}")
                filtered_items.append(item)
                break
            else:
                logger.debug(f"No ordered subset match. Trying title_match()")
                if title_match(title, cleaned_item_title):
                    logger.debug(f"title_match() succeeded. Item accepted: {cleaned_item_title}")
                    filtered_items.append(item)
                    break
        else:
            logger.debug(f"No match found, item skipped: {cleaned_item_title}")
    
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
    logger.info(
        f"Merging cached items ({len(cache_items)}) and search items ({len(search_items)})"
    )
    merged_dict = {}

    def add_to_merged(item: TorrentItem):
        key = (item.raw_title, item.size)
        if key not in merged_dict or item.seeders > merged_dict[key].seeders:
            merged_dict[key] = item

    for item in cache_items:
        add_to_merged(item)
    for item in search_items:
        add_to_merged(item)

    merged_items = list(merged_dict.values())
    logger.info(f"Merging complete. Total unique items: {len(merged_items)}")
    return merged_items
