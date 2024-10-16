import re
from typing import Dict
from stream_fusion.constants import FR_RELEASE_GROUPS, FRENCH_PATTERNS

INSTANTLY_AVAILABLE = "⚡"
DOWNLOAD_REQUIRED = "⬇️​​"
DIRECT_TORRENT = "🏴‍☠️"

def get_emoji(language: str) -> str:
    emoji_dict = {
        "fr": "🇫🇷 FR", "en": "🇬🇧 EN", "es": "🇪🇸 ES",
        "de": "🇩🇪 GR", "it": "🇮🇹 IT", "pt": "🇵🇹 PO",
        "ru": "🇷🇺 RU", "in": "🇮🇳 IN", "nl": "🇳🇱 DU",
        "hu": "🇭🇺 HU", "la": "🇲🇽 LA", "multi": "🌍 MULTi",
    }
    return emoji_dict.get(language, "🇬🇧")

def filter_by_availability(item: Dict) -> int:
    return 0 if item["name"].startswith(INSTANTLY_AVAILABLE) else 1

def filter_by_direct_torrent(item: Dict) -> int:
    return 1 if item["name"].startswith(DIRECT_TORRENT) else 0

def extract_release_group(title: str) -> str:
    combined_pattern = "|".join(FR_RELEASE_GROUPS)
    match = re.search(combined_pattern, title)
    return match.group(0) if match else None

def detect_french_language(title: str) -> str:
    for language, pattern in FRENCH_PATTERNS.items():
        if re.search(pattern, title, re.IGNORECASE):
            return language
    return None