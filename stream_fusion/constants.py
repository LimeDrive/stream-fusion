from typing import Any


NO_CONFIG = {'streams': [{'url': "#", 'title': "No configuration found"}]}
JACKETT_ERROR = {'streams': [{'url': "#", 'title': "An error occured"}]}

# CACHER_URL = "https://stremio-jackett-cacher.elfhosted.com/"

NO_CACHE_HEADERS = {
    "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
    "Pragma": "no-cache",
    "Expires": "0",
}

NO_CACHE_VIDEO_URL = "https://github.com/aymene69/stremio-jackett/raw/main/source/videos/nocache.mp4"

EXCLUDED_TRACKERS = ['0day.kiev', '1ptbar', '2 Fast 4 You', '2xFree', '3ChangTrai', '3D Torrents', '3Wmg', '4thD',
                     '52PT', '720pier', 'Abnormal', 'ABtorrents', 'Acid-Lounge', 'Across The Tasman', 'Aftershock',
                     'AGSVPT', 'Aidoru!Online', 'Aither (API)', 'AlphaRatio', 'Amigos Share Club', 'AniDUB',
                     'Anime-Free', 'AnimeBytes', 'AnimeLayer', 'AnimeTorrents', 'AnimeTorrents.ro', 'AnimeWorld (API)',
                     'AniToons', 'Anthelion (API)', 'ArabaFenice', 'ArabP2P', 'ArabTorrents', 'ArenaBG', 'AsianCinema',
                     'AsianDVDClub', 'Audiences', 'AudioNews', 'Aussierul.es', 'AvistaZ', 'Azusa', 'Back-ups', 'BakaBT',
                     'BeiTai', 'Beload', 'Best-Core', 'Beyond-HD (API)', 'Bibliotik', 'Bit-Bázis', 'BIT-HDTV', 'Bitded',
                     'Bithorlo', 'BitHUmen', 'BitPorn', 'Bitspyder', 'Bittorrentfiles', 'BiTTuRK', 'BJ-Share',
                     'BlueBird', 'Blutopia (API)', 'BookTracker', 'BootyTape', 'Borgzelle', 'Boxing Torrents',
                     'BrasilTracker', 'BroadcasTheNet', 'BroadCity', 'BrokenStones', 'BrSociety (API)', 'BTArg',
                     'BTNext', 'BTSCHOOL', 'BwTorrents', 'BYRBT', 'Carp-Hunter', 'Carpathians', 'CarPT', 'CartoonChaos',
                     'Cathode-Ray.Tube', 'Catorrent', 'Central Torrent', 'CeskeForum', 'CGPeers', 'CHDBits', 'cheggit',
                     'ChileBT', 'Cinemageddon', 'CinemaMovieS_ZT', 'Cinematik', 'CinemaZ', 'Classix', 'Coastal-Crew',
                     'Concertos', 'CrazySpirits', 'CrnaBerza', 'CRT2FA', 'Dajiao', 'DanishBytes (API)', 'Dark-Shadow',
                     'DataScene (API)', 'Deildu', 'Demonoid', 'DesiTorrents (API)', 'Devil-Torrents', 'Diablo Torrent',
                     'DICMusic', 'DigitalCore', 'DimeADozen', 'DiscFan', 'DivTeam', 'DocsPedia', 'Dream Tracker',
                     'DreamingTree', 'Drugari', 'DXP', 'Ebooks-Shares', 'Electro-Torrent', 'Empornium', 'Empornium2FA',
                     'EniaHD', 'Enthralled', 'Enthralled2FA', 'Erai-Raws', 'eShareNet', 'eStone', 'Ex-torrenty',
                     'exitorrent.org', 'ExKinoRay', 'ExoticaZ', 'ExtremeBits', 'ExtremlymTorrents',
                     'Falkon Vision Team', 'FANO.IN', 'Fantastiko', 'Fappaizuri', 'FastScene', 'FearNoPeer',
                     'Femdomcult', 'File-Tracker', 'FileList', 'FinElite', 'FinVip', 'Flux-Zone', 'Free Farm', 'FSM',
                     'FunFile', 'FunkyTorrents', 'FutureTorrent', 'Fuzer', 'Gamera', 'Gay-Torrents.net',
                     'gay-torrents.org', 'GAYtorrent.ru', 'GazelleGames', 'GazelleGames (API)', 'Generation-Free (API)',
                     'Genesis-Movement', 'GigaTorrents', 'GimmePeers', 'Girotorrent', 'GreatPosterWall', 'GreekDiamond',
                     'HaiDan', 'Haitang', 'HappyFappy', 'Hares Club', 'hawke-uno', 'HD-CLUB', 'HD-CzTorrent',
                     'HD-Forever', 'HD-Olimpo (API)', 'HD-Only', 'HD-Space', 'HD-Torrents', 'HD-UNiT3D (API)',
                     'HD4FANS', 'HDArea', 'HDAtmos', 'HDBits (API)', 'HDC', 'HDDolby', 'HDFans', 'HDFun', 'HDGalaKtik',
                     'HDHome', 'HDMaYi', 'HDPT', 'HDRoute', 'HDSky', 'HDtime', 'HDTorrents.it', 'HDTurk', 'HDU',
                     'hdvbits', 'HDVIDEO', 'Hebits', 'HellasHut', 'HellTorrents', 'HHanClub', 'HomePornTorrents',
                     'House of Devil', 'HQMusic', 'HunTorrent', 'iAnon', 'ICC2022', 'Il Corsaro Blu', 'ilDraGoNeRo',
                     'ImmortalSeed', 'Immortuos', 'Indietorrents', 'Infire', 'Insane Tracker', 'IPTorrents',
                     'ItaTorrents', 'JME-REUNIT3D (API)', 'JoyHD', 'JPopsuki', 'JPTV (API)', 'KamePT', 'Karagarga',
                     'Keep Friends', 'KIMOJI', 'Kinorun', 'Kinozal', 'Kinozal (M)', 'Korsar', 'KrazyZone', 'Kufei',
                     'Kufirc', 'LaidBackManor (API)', 'Last Digital Underground', 'LastFiles', 'Lat-Team (API)',
                     'Le-Cinephile', 'LearnBits', 'LearnFlakes', 'leech24', 'Les-Cinephiles', 'LeSaloon', 'Lesbians4u',
                     'Libble', 'LibraNet', 'LinkoManija', 'Locadora', 'LosslessClub', 'LostFilm.tv', 'LST',
                     'M-Team - TP', 'M-Team - TP (2FA)', 'MaDs Revolution', 'Magnetico (Local DHT)', 'Majomparádé',
                     'Making Off', 'Marine Tracker', 'Masters-TB', 'Mazepa', 'MDAN', 'MegamixTracker',
                     'Mendigos da WEB', 'MeseVilág', 'Metal Tracker', 'MetalGuru', 'Milkie', 'MIRCrew', 'MMA-torrents',
                     'MNV', 'MOJBLiNK', 'MonikaDesign (API)', 'MoreThanTV (API)', 'MouseBits', 'Movie-Torrentz',
                     'MovieWorld', 'MuseBootlegs', 'MVGroup Forum', 'MVGroup Main', 'MyAnonamouse', 'MySpleen', 'nCore',
                     'NebulanceAPI', 'NetHD', 'NewStudioL', 'NicePT', 'NoNaMe ClubL', 'NorBits', 'NORDiCHD',
                     'Ntelogo (API)', 'OKPT', 'Old Toons World', 'OnlyEncodes (API)', 'OpenCD', 'Orpheus', 'OshenPT',
                     'Ostwiki', 'OurBits', 'P2PBG', 'Panda', 'Party-Tracker', 'PassThePopcorn', 'Peeratiko', 'Peers.FM',
                     'PigNetwork', 'PixelCove', 'PixelCove2FA', 'PiXELHD', 'PolishSource', 'PolishTracker (API)',
                     'Pornbay', 'PornoLab', 'Portugas (API)', 'PotUK', 'PreToMe', 'PrivateHD', 'ProAudioTorrents',
                     'PTCafe', 'PTChina', 'PTerClub', 'PTFiles', 'PThome', 'PTLSP', 'PTSBAO', 'PTTime', 'PT分享站',
                     "Punk's Horror Tracker", 'PuntoTorrent', 'PussyTorrents', 'PuTao', 'PWTorrents', 'R3V WTF!',
                     'Racing4Everyone (API)', 'RacingForMe', 'Rainbow Tracker', 'RareShare2 (API)', 'Red Leaves',
                     'Red Star Torrent', 'Redacted', 'RedBits (API)', 'ReelFLiX (API)', 'Resurrect The Net',
                     'RetroFlix', 'RevolutionTT', 'RGFootball', 'RinTor', 'RiperAM', 'RM-HD', 'RockBox',
                     'Romanian Metal Torrents', 'Rousi', 'RPTScene', 'RUDUB', 'Rustorka', 'RuTracker', 'SATClubbing',
                     'SceneHD', 'SceneLinks', 'SceneRush', 'SceneTime', 'Secret Cinema', 'SeedFile', 'seleZen',
                     'Shadowflow', 'Shareisland (API)', 'Sharewood', 'Sharewood API', 'SharkPT', 'Shazbat', 'SiamBIT',
                     'SkipTheCommercials (API)', 'SkipTheTrailers', 'SkTorrent', 'SkTorrent-org', 'slosoul', 'SnowPT',
                     'SoulVoice', 'Speed.cd', 'SpeedApp', 'Speedmaster HD', 'SpeedTorrent Reloaded',
                     'Spirit of Revolution', 'SportsCult', 'SpringSunday', 'SugoiMusic', 'Superbits', 'Swarmazon (API)',
                     'Tapochek', 'Tasmanit', 'Team CT Game', 'TeamHD', 'TeamOS', 'TEKNO3D', 'teracod', 'The Crazy Ones',
                     'The Empire', 'The Falling Angels', 'The Geeks', 'The New Retro', 'The Occult',
                     'The Old School (API)', 'The Place', 'The Shinning (API)', 'The Show', 'The Vault', 'The-New-Fun',
                     'TheLeachZone', 'themixingbowl', 'TheRebels (API)', 'TheScenePlace', "Thor's Land", 'TJUPT',
                     'TLFBits', 'TmGHuB', 'Toca Share', 'Toloka.to', 'ToonsForMe', 'Tornado', 'Torrent Heaven',
                     'Torrent Network', 'Torrent Sector Crew', 'Torrent Trader', 'Torrent-Explosiv', 'Torrent-Syndikat',
                     'TOrrent-tuRK', 'Torrent.LT', 'TorrentBD', 'TorrentBytes', 'TorrentCCF', 'TorrentDay', 'TorrentDD',
                     'Torrenteros (API)', 'TorrentHeaven', 'TorrentHR', 'Torrenting', 'Torrentland',
                     'Torrentland (API)', 'TorrentLeech', 'Torrentleech.pl', 'TorrentMasters', 'Torrents-Local',
                     'TorrentSeeds (API)', 'TotallyKids', 'ToTheGlory', 'ToTheGloryCookie', 'TrackerMK',
                     'TranceTraffic', 'Trellas', 'TreZzoR', 'TreZzoRCookie', 'TribalMixes', 'TurkTorrent', 'TV Store',
                     'TVChaosUK', 'TvRoad', 'Twisted-Music', 'U2', 'UBits', 'UHDBits', 'UltraHD', 'Union Fansub',
                     'UnionGang', 'UniOtaku', 'Universal-Torrents', 'Unlimitz', 'upload.cx', 'UTOPIA', 'WDT',
                     'White Angel', 'WinterSakura', 'World-In-HD', 'World-of-Tomorrow', 'Wukong', 'x-ite.me',
                     'XbytesV2', 'Xider-Torrent', 'XSpeeds', 'Xthor (API)', 'xTorrenty', 'Xtreme Bytes', 'XWT-Classics',
                     'XWtorrents', 'YDYPT', 'YGGcookie', 'YGGtorrent', 'Zamunda.net', 'Zelka.org', 'ZmPT (织梦)',
                     'ZOMB', 'ZonaQ', 'Ztracker']


FR_RELEASE_GROUPS = [
            r"(?<=[.\s\-\[])(BlackAngel|Choco|Sicario|Tezcat74|TyrellCorp|Zapax)(?=[.\s\-$$]|$)",
            r"(?<=[.\s\-\[])(FtLi|Goldenyann|MUSTANG|Obi|PEPiTE|QUEBEC63|QC63|ROMKENT|R3MiX)(?=[.\s\-$$]|$)",
            r"(?<=[.\s\-\[])(FLOP|FRATERNiTY|QTZ|PopHD|toto70300|GHT|EXTREME|AvALoN|KFL|mHDgz)(?=[.\s\-$$]|$)",
            r"(?<=[.\s\-\[])(DUSTiN|QUALiTY|Tsundere-Raws|LAZARUS|ALFA|SODAPOP|Tetine|DREAM|Winks)(?=[.\s\-$$]|$)",
            r"(?<=[.\s\-\[])(BDHD|MAX|SowHD|SN2P|RG|BTT|KAF|AwA|MULTiViSiON|FERVEX|Foxhound|K7)(?=[.\s\-$$]|$)",
            r"(?<=[.\s\-\[])(FUJiSAN|HDForever|MARBLECAKE|MYSTERiON|ONLY|UTT|ZiT|JP48|SEL|PATOMiEL)(?=[.\s\-$$]|$)",
            r"(?<=[.\s\-\[])(BONBON|FCK|FW|FoX|FrIeNdS|MOONLY|MTDK|PATOPESTO|Psaro|T3KASHi|TFA)(?=[.\s\-$$]|$)",
            r"(?<=[.\s\-\[])(ALLDAYiN|ARK01|HANAMi|HeavyWeight|NEO|NoNe|ONLYMOViE|Slay3R|TkHD)(?=[.\s\-$$]|$)",
            r"(?<=[.\s\-\[])(4FR|AiR3D|AiRDOCS|AiRFORCE|AiRLiNE|AiRTV|AKLHD|AMB3R|SERQPH|Elcrackito)(?=[.\s\-$$]|$)",
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

FRENCH_PATTERNS = {
    "VFF": r"\b(?:VFF|TRUEFRENCH)\b",
    "VF2": r"\b(?:VF2)\b",
    "VFQ": r"\b(?:VFQ)\b",
    "VFI": r"\b(?:VFI)\b",
    "VOF": r"\b(?:VOF)\b",
    "VQ": r"\b(?:VOQ|VQ)\b",
    "VOSTFR": r"\b(?:VOSTFR|SUBFRENCH)\b",
    "FRENCH": r"\b(?:FRENCH|FR)\b",
}

# REDIS_HOST = 'redis'
# REDIS_PORT = 6379

class CustomException(Exception):
    def __init__(self, status_code: int, message: Any):
        self.status_code = status_code
        self.message = message