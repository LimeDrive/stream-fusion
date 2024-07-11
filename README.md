# StreamFusion

## Description

StreamFusion is an advanced plugin for Stremio that significantly enhances its streaming capabilities. It leverages torrent indexers and Jackett to integrate cached torrent sources from popular debrid services, offering a smooth and comprehensive streaming experience. This application acts as a bridge between Stremio, torrent indexers, and debrid services, providing users with a wide range of content options.

## Key Features

- **Torrent Indexer Integration**: Utilizes various torrent indexers and Jackett to source content.
- **Debrid Service Integration**: Adds cached torrents from RealDebrid, AllDebrid, and Premiumize as sources for Stremio.
- **Direct Streaming**: Uses indexers for direct streaming when cached torrents are unavailable.
- **Advanced Cache Management**: 
  - Utilizes Redis for efficient caching.
  - Community cache for sharing cached torrent searches.
- **Zilean API**: Integration of the DMM Zilean API to obtain cached torrent hashes.
- **Stream Proxification**: All streams originate from a single IP address.
- **Download Management**: Capable of managing torrent downloads on debrid services.

## Installation (WIP)

[Installation instructions to be added]

## Configuration (WIP)

[Configuration details to be added]

## Usage (WIP)

[Usage guide to be added]

## Contributing

Contributions are welcome! Please refer to our contribution guidelines for more details.

```bash
tree -I '*.pyc' -I '__pycache__'
.
├── Dockerfile
├── README.md
├── deploy
│   └── docker-compose.yml
├── poetry.lock
├── poetry.toml
├── pyproject.toml
└── stream_fusion
    ├── __init__.py
    ├── __main__.py
    ├── constants.py
    ├── gunicorn_runner.py
    ├── logging_config.py
    ├── services
    │   ├── redis
    │   │   └── redis_config.py
    │   └── security_db
    │       ├── __init__.py
    │       └── _sqlite_access.py
    ├── settings.py
    ├── static
    ├── templates
    │   ├── config.js
    │   └── index.html
    ├── utils
    │   ├── cache
    │   │   ├── cache_base.py
    │   │   └── local_redis.py
    │   ├── cache.py
    │   ├── debrid
    │   │   ├── alldebrid.py
    │   │   ├── base_debrid.py
    │   │   ├── get_debrid_service.py
    │   │   ├── premiumize.py
    │   │   └── realdebrid.py
    │   ├── detection.py
    │   ├── filter
    │   │   ├── base_filter.py
    │   │   ├── language_filter.py
    │   │   ├── max_size_filter.py
    │   │   ├── quality_exclusion_filter.py
    │   │   ├── results_per_quality_filter.py
    │   │   └── title_exclusion_filter.py
    │   ├── filter_results.py
    │   ├── general.py
    │   ├── jackett
    │   │   ├── jackett_indexer.py
    │   │   ├── jackett_result.py
    │   │   └── jackett_service.py
    │   ├── metdata
    │   │   ├── cinemeta.py
    │   │   ├── metadata_provider_base.py
    │   │   └── tmdb.py
    │   ├── models
    │   │   ├── media.py
    │   │   ├── movie.py
    │   │   └── series.py
    │   ├── parse_config.py
    │   ├── security
    │   │   ├── __init__.py
    │   │   ├── security_api_key.py
    │   │   └── security_secret.py
    │   ├── string_encoding.py
    │   ├── torrent
    │   │   ├── torrent_item.py
    │   │   ├── torrent_service.py
    │   │   └── torrent_smart_container.py
    │   └── zilean
    │       ├── zilean_result.py
    │       └── zilean_service.py
    ├── version.py
    ├── videos
    │   └── nocache.mp4
    └── web
        ├── __init__.py
        ├── api
        │   ├── __init__.py
        │   ├── auth
        │   │   ├── __init__.py
        │   │   ├── schemas.py
        │   │   └── views.py
        │   ├── docs
        │   │   ├── __init__.py
        │   │   └── views.py
        │   ├── monitoring
        │   │   ├── __init__.py
        │   │   └── views.py
        │   └── router.py
        ├── application.py
        ├── lifetime.py
        ├── playback
        │   ├── __init__.py
        │   ├── router.py
        │   └── stream
        │       ├── __init__.py
        │       ├── schemas.py
        │       └── views.py
        └── root
            ├── __init__.py
            ├── config
            │   ├── __init__.py
            │   ├── schemas.py
            │   └── views.py
            ├── router.py
            └── search
                ├── __init__.py
                ├── schemas.py
                ├── stremio_parser.py
                └── views.py

29 directories, 81 files
```

## License

[License information to be added]

## Disclaimer

This project is intended for educational and research purposes only. Users are responsible for their use of the software and must comply with local copyright and intellectual property laws.

## Contact

[![Discord](https://img.shields.io/badge/Discord-Rejoignez%20nous%20sur%20SSD!-7289DA?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/jcMYfrz3sr)

---

StreamFusion is a project derived from Stremio-Jackett, rewritten and improved to offer a better user experience and extended functionalities.