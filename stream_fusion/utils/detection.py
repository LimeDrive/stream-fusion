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
