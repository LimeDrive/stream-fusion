from stream_fusion.utils.models.media import Media


class Movie(Media):
    def __init__(self, id, tmdb_id, titles, year, languages):
        super().__init__(id, tmdb_id, titles, languages, "movie")
        self.year = year
