import re

from stream_fusion.utils.filter.base_filter import BaseFilter
from stream_fusion.logging_config import logger


class LanguageFilter(BaseFilter):
    def __init__(self, config):
        super().__init__(config)
        self.fr_regex_patterns = [
            r"(?<=[.\s\-\[])(BlackAngel|Choco|Sicario|Tezcat74|TyrellCorp|Zapax)(?=[.\s\-$$]|$)",
            r"(?<=[.\s\-\[])(FtLi|Goldenyann|MUSTANG|Obi|PEPiTE|QUEBEC63|QC63|ROMKENT)(?=[.\s\-$$]|$)",
            r"(?<=[.\s\-\[])(FLOP|FRATERNiTY|QTZ|PopHD|toto70300|GHT|EXTREME)(?=[.\s\-$$]|$)",
            r"(?<=[.\s\-\[])(DUSTiN|QUALiTY|Tsundere-Raws|LAZARUS|ALFA|SODAPOP)(?=[.\s\-$$]|$)",
            r"(?<=[.\s\-\[])(BDHD|MAX|SowHD|SN2P|RG|BTT|KAF|AwA|MULTiViSiON|FERVEX)(?=[.\s\-$$]|$)",
            r"(?<=[.\s\-\[])(FUJiSAN|HDForever|MARBLECAKE|MYSTERiON|ONLY|UTT)(?=[.\s\-$$]|$)",
            r"(?<=[.\s\-\[])(BONBON|FCK|FW|FoX|FrIeNdS|MOONLY|MTDK|PATOPESTO|Psaro|T3KASHi|TFA)(?=[.\s\-$$]|$)",
            r"(?<=[.\s\-\[])(ALLDAYiN|ARK01|HANAMi|HeavyWeight|NEO|NoNe|ONLYMOViE|Slay3R|TkHD)(?=[.\s\-$$]|$)",
            r"(?<=[.\s\-\[])(4FR|AiR3D|AiRDOCS|AiRFORCE|AiRLiNE|AiRTV|AKLHD|AMB3R)(?=[.\s\-$$]|$)",
            r"(?<=[.\s\-\[])(ANMWR|AVON|AYMO|AZR|BANKAi|BAWLS|BiPOLAR|BLACKPANTERS|BODIE|BOOLZ|BRiNK|CARAPiLS|CiELOS)(?=[.\s\-$$]|$)",
            r"(?<=[.\s\-\[])(CiNEMA|CMBHD|CoRa|COUAC|CRYPT0|D4KiD|DEAL|DiEBEX|DUPLI|DUSS|ENJOi|EUBDS|FHD|FiDELiO|FiDO|ForceBleue)(?=[.\s\-$$]|$)",
            r"(?<=[.\s\-\[])(FREAMON|FRENCHDEADPOOL2|FRiES|FUTiL|FWDHD|GHOULS|GiMBAP|GLiMMER|Goatlove|HERC|HiggsBoson|HiRoSHiMa)(?=[.\s\-$$]|$)",
            r"(?<=[.\s\-\[])(HYBRiS|HyDe|JMT|JoKeR|JUSTICELEAGUE|KAZETV|L0SERNiGHT|LaoZi|LeON|LOFiDEL|LOST|LOWIMDB|LYPSG|MAGiCAL)(?=[.\s\-$$]|$)",
            r"(?<=[.\s\-\[])(MANGACiTY|MAXAGAZ|MaxiBeNoul|McNULTY|MELBA|MiND|MORELAND|MUNSTER|MUxHD|NERDHD|NERO|NrZ|NTK|OBSTACLE)(?=[.\s\-$$]|$)",
            r"(?<=[.\s\-\[])(OohLaLa|OOKAMI|PANZeR|PiNKPANTERS|PKPTRS|PRiDEHD|PROPJOE|PURE|PUREWASTEOFBW|ROUGH|RUDE|Ryotox|SAFETY)(?=[.\s\-$$]|$)",
            r"(?<=[.\s\-\[])(SASHiMi|SEiGHT|SESKAPiLE|SHEEEiT|SHiNiGAMi(UHD)?|SiGeRiS|SILVIODANTE|SLEEPINGFOREST|SODAPOP|S4LVE|SPINE)(?=[.\s\-$$]|$)",
            r"(?<=[.\s\-\[])(SPOiLER|STRINGERBELL|SUNRiSE|tFR|THENiGHTMAREiNHD|THiNK|THREESOME|TiMELiNE|TSuNaMi|UKDHD|UKDTV|ULSHD|Ulysse)(?=[.\s\-$$]|$)",
            r"(?<=[.\s\-\[])(USUNSKiLLED|URY|VENUE|VFC|VoMiT|Wednesday29th|ZEST|ZiRCON)(?=[.\s\-$$]|$)",
        ]
        self.fr_regex = re.compile("|".join(self.fr_regex_patterns))

    def filter(self, data):
        filtered_data = []
        for torrent in data:
            if not torrent.languages:
                continue

            languages = torrent.languages.copy()

            if torrent.from_cache and "multi" in languages:
                regex = self.fr_regex.search(torrent.raw_title)
                logger.debug(f"Regex match for {torrent.raw_title} : {regex}")
                if not regex:
                    languages.remove("multi")
            
            if torrent.from_cache and "fr" in languages:
                regex = self.fr_regex.search(torrent.raw_title)
                logger.debug(f"Regex match for {torrent.raw_title} : {regex}")
                if not regex:
                    languages.remove("fr")

            if "multi" in languages or any(
                lang in self.config["languages"] for lang in languages
            ):
                torrent.languages = languages
                logger.debug(f"Keeping {torrent.raw_title} with lang : {languages} ")
                filtered_data.append(torrent)

        return filtered_data

    def can_filter(self):
        return self.config["languages"] is not None
