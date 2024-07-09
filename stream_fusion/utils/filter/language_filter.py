import re

from stream_fusion.utils.filter.base_filter import BaseFilter


class LanguageFilter(BaseFilter):
    def __init__(self, config):
        super().__init__(config)
        self.fr_regex_patterns = [
            r"^(BlackAngel|Choco|HDForever|MAX|ONLY|Psaro|Sicario|Tezcat74|TyrellCorp|Zapax)$",
            r"^(BDHD|FtLi|Goldenyann|HeavyWeight|MARBLECAKE|MUSTANG|Obi|PEPiTE|QUEBEC63|QC63|ROMKENT)$",
            r"^(FLOP|FRATERNiTY|FoX|Psaro)$",
            r"^(DUSTiN|FCK|FrIeNdS|QUALiTY)$",
            r"^(BDHD|FoX|FRATERNiTY|FrIeNdS|MAX|Psaro|T3KASHi)$",
            r"^(FUJiSAN|HANAMi|HDForever|HeavyWeight|MARBLECAKE|MYSTERiON|NoNE|ONLY|ONLYMOViE|TkHD|UTT)$",
            r"^(BONBON|FCK|FW|FoX|FRATERNiTY|FrIeNdS|MOONLY|MTDK|PATOPESTO|Psaro|T3KASHi|TFA)$",
            r"^(ALLDAYiN|ARK01|FUJiSAN|HANAMi|HeavyWeight|NEO|NoNe|ONLYMOViE|Slay3R|TkHD)$",
            r"^(4FR|AiR3D|AiRDOCS|AiRFORCE|AiRLiNE|AiRTV|AKLHD|AMB3R)$",
            r"^(ANMWR|AVON|AYMO|AZR|BANKAi|BAWLS|BiPOLAR|BLACKPANTERS|BODIE|BOOLZ|BRiNK|CARAPiLS|CiELOS)$",
            r"^(CiNEMA|CMBHD|CoRa|COUAC|CRYPT0|D4KiD|DEAL|DiEBEX|DUPLI|DUSS|ENJOi|EUBDS|FHD|FiDELiO|FiDO|ForceBleue)$",
            r"^(FREAMON|FRENCHDEADPOOL2|FRiES|FUTiL|FWDHD|GHOULS|GiMBAP|GLiMMER|Goatlove|HERC|HiggsBoson|HiRoSHiMa)$",
            r"^(HYBRiS|HyDe|JMT|JoKeR|JUSTICELEAGUE|KAZETV|L0SERNiGHT|LaoZi|LeON|LOFiDEL|LOST|LOWIMDB|LYPSG|MAGiCAL)$",
            r"^(MANGACiTY|MAXAGAZ|MaxiBeNoul|McNULTY|MELBA|MiND|MORELAND|MUNSTER|MUxHD|NERDHD|NERO|NrZ|NTK|OBSTACLE)$",
            r"^(OohLaLa|OOKAMI|PANZeR|PiNKPANTERS|PKPTRS|PRiDEHD|PROPJOE|PURE|PUREWASTEOFBW|ROUGH|RUDE|Ryotox|SAFETY)$",
            r"^(SASHiMi|SEiGHT|SESKAPiLE|SHEEEiT|SHiNiGAMi(UHD)?|SiGeRiS|SILVIODANTE|SLEEPINGFOREST|SODAPOP|S4LVE|SPINE)$",
            r"^(SPOiLER|STRINGERBELL|SUNRiSE|tFR|THENiGHTMAREiNHD|THiNK|THREESOME|TiMELiNE|TSuNaMi|UKDHD|UKDTV|ULSHD|Ulysse)$",
            r"^(USUNSKiLLED|URY|VENUE|VFC|VoMiT|Wednesday29th|ZEST|ZiRCON)$",
        ]
        self.fr_regex = re.compile("|".join(self.fr_regex_patterns))

    def filter(self, data):
        filtered_data = []
        for torrent in data:
            if not torrent.languages:
                continue

            languages = torrent.languages.copy()

            if torrent.from_cache and "multi" in languages:
                if self.fr_regex.search(torrent.raw_title):
                    languages.remove("multi")

            if "multi" in languages or any(
                lang in self.config["languages"] for lang in languages
            ):
                torrent.languages = languages
                filtered_data.append(torrent)

        return filtered_data

    def can_filter(self):
        return self.config["languages"] is not None
