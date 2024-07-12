import re


def detect_languages(torrent_name):
    language_patterns = {
        "fr": r"\b(?:FR(?:ench|a|e|anc[eê]s)?|V(?:O?F(?:F|I|i)?|O?Q)|TRUEFRENCH|VOST(?:FR)?|SUBFRENCH)\b",
        "en": r"\b(?:EN(?:G(?:LISH)?)?|VOST(?:EN)?|SUBBED)\b",
        "es": r"\b(?:ES(?:P(?:ANISH)?)?|VOSE|SUBESP)\b",
        "de": r"\b(?:DE(?:UTSCH|RMAN)?|GER(?:MAN)?|SUBGER)\b",
        "it": r"\b(?:IT(?:A(?:LIAN)?)?|SUBITA)\b",
        "pt": r"\b(?:PT(?:-BR)?|POR(?:TUGUESE)?|LEGENDADO)\b",
        "ru": r"\b(?:RU(?:S(?:SIAN)?)?|SUBSRUS)\b",
        "in": r"\b(?:INDIAN|HINDI|TELUGU|TAMIL|KANNADA|MALAYALAM|PUNJABI|MARATHI|BENGALI|GUJARATI|URDU|ODIA|ASSAMESE|KONKANI|MANIPURI|NEPALI|SANSKRIT|SINHALA|SINDHI|TIBETAN|BHOJPURI|DHIVEHI|KASHMIRI|KURUKH|MAITHILI|NEWARI|RAJASTHANI|SANTALI|SINDHI|TULU)\b",
        "nl": r"\b(?:NL(?:D)?|DUTCH|SUBSNL)\b",
        "hu": r"\b(?:HU(?:N(?:GARIAN)?)?|SUBHUN)\b",
        "la": r"\b(?:LA(?:TIN(?:O)?)?)\b",
        "multi": r"\b(?:MULTI(?:LANG(?:UE)?)?|DUAL(?:AUDIO)?|VF2)\b",
    }

    languages = []
    for language, pattern in language_patterns.items():
        if re.search(pattern, torrent_name, re.IGNORECASE):
            languages.append(language)

    if len(languages) == 0:
        return ["en"]

    return languages


def detect_audios_type(raw_title, languages):
    language_specific_patterns = {
        "fr": {
            "VFF": r"\b(?:VFF|TRUEFRENCH)\b",
            "VF2": r"\b(?:VF2)\b",
            "VFQ": r"\b(?:VFQ)\b",
            "VFI": r"\b(?:VFI)\b",
            "VOF": r"\b(?:VOF)\b",
            "VQ": r"\b(?:VOQ|VQ)\b",
            "VOSTFR": r"\b(?:VOSTFR|SUBFRENCH)\b",
            "FRENCH": r"\b(?:FRENCH|FR)\b"
        },
        "en": {
            "ENG": r"\b(?:ENG|ENGLISH)\b",
            "VO": r"\b(?:VO|OV)\b",
            "SUBBED": r"\b(?:SUB|SUBBED|SUBTITLE[SD])\b"
        },
        "es": {
            "ESP": r"\b(?:ESP|SPANISH)\b"
        },
        "de": {
            "GER": r"\b(?:GER|GERMAN|DEUTSCH)\b"
        },
        "it": {
            "ITA": r"\b(?:ITA|ITALIAN)\b"
        },
        "ja": {
            "JAP": r"\b(?:JAP|JAPANESE)\b"
        },
        "ko": {
            "KOR": r"\b(?:KOR|KOREAN)\b"
        },
        "zh": {
            "CHI": r"\b(?:CHI|CHINESE|MANDARIN)\b"
        },
        "ru": {
            "RUS": r"\b(?:RUS|RUSSIAN)\b"
        },
        "pt": {
            "POR": r"\b(?:POR|PORTUGUESE)\b"
        },
        "nl": {
            "DUT": r"\b(?:DUT|DUTCH)\b"
        },
        "sv": {
            "SWE": r"\b(?:SWE|SWEDISH)\b"
        },
        "da": {
            "DAN": r"\b(?:DAN|DANISH)\b"
        },
        "no": {
            "NOR": r"\b(?:NOR|NORWEGIAN)\b"
        },
        "fi": {
            "FIN": r"\b(?:FIN|FINNISH)\b"
        }
    }
    
    if not languages:
        return "VF"
    
    if isinstance(languages, str):
        languages = [languages]

    if "multi" in languages:
        for lang_patterns in language_specific_patterns.values():
            for audio_type, pattern in lang_patterns.items():
                if re.search(pattern, raw_title, re.IGNORECASE):
                    return audio_type
    else:
        for language in languages:
            patterns = language_specific_patterns.get(language, {})
            for audio_type, pattern in patterns.items():
                if re.search(pattern, raw_title, re.IGNORECASE):
                    return audio_type

    default_types = {
        "fr": "VF",
        "en": "VO",
        "multi": "MULTI"
    }
    return default_types.get(languages[0], "VO")