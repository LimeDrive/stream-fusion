# Installation Prerequisites - Stremio Trakt Addon

Before installing the Stremio Trakt Addon, make sure you have met the following prerequisites:

## 1. StreamFusion Installation

!!! important "Mandatory"
    An existing installation of Stream Fusion is required, as the Stremio Trakt Addon shares the PostgreSQL database and Redis instance with Stream Fusion.

## 2. Dedicated Domain

* Create a specific domain for the Stremio Trakt Addon.

## 3. TMDB (The Movie Database) Account

!!! warning "API Key required"
    A TMDB account is necessary to obtain an API Key, which is mandatory for the addon to function.

* Create an account on [TMDB](https://www.themoviedb.org/)
* Obtain an API Key in your account settings

## 4. Trakt.tv Account

!!! important "Mandatory"
    A Trakt.tv account is essential for using this addon.

* Create an account on [Trakt.tv](https://trakt.tv/)
* Create an OAuth application in your Trakt account settings
* Note down the Client ID and Client Secret of your Trakt application

## 5. Rating Poster Database (RPDB) Account (Optional)

!!! note "Recommended"
    An RPDB account is necessary if you wish to use the poster display and rating features.

* Create an account on [Rating Poster Database](https://ratingposterdb.com)
* Obtain an API Key in your account settings

## 6. FanArt.tv Account (Optional)

!!! note "Recommended"
    A FanArt.tv account is necessary if you want to use logos to replace content titles.

* Create an account on [FanArt.tv](https://fanart.tv/)
* Obtain an API Key in your account settings

---

Once you have fulfilled all these prerequisites, you are ready to proceed with the installation of the Stremio Trakt Addon. Make sure to keep all the API Keys you have obtained in a safe place, as they will be necessary during the addon configuration.