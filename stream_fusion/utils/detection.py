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


def detect_french_languages(torrent_name):
    french_patterns = {
        "VFF": r"\b(?:VFF|TRUEFRENCH)\b",
        "VF2": r"\b(?:VF2)\b",
        "VFQ": r"\b(?:VFQ)\b",
        "VFI": r"\b(?:VFI)\b",
        "VOSTFR  ": r"\b(?:VOSTFR|SUBFRENCH)\b",
    }

    myfrench = ""
    for french, pattern in french_patterns.items():
        if re.search(pattern, torrent_name, re.IGNORECASE):
            myfrench = french

    if len(myfrench) == 0:
        return "VF"

    return myfrench


def detect_hdr(torrent_name):
    hdr_patterns = {
        "HDR": r"\bHDR(?:10\+?|10Plus|10p?)?\b",
        "DV": r"\bDV|DoVi\b",
        "IMAX": r"\bIMAX\b",
    }

    hdrs = []
    for hdr, pattern in hdr_patterns.items():
        if re.search(pattern, torrent_name, re.IGNORECASE):
            hdrs.append(hdr)

    if len(hdrs) == 0:
        return [""]

    return hdrs