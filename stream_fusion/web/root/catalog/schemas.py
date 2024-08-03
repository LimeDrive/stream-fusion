from pydantic import BaseModel, Field, model_validator


class ErrorResponse(BaseModel):
    detail: str


class Catalog(BaseModel):
    id: str
    name: str
    type: str


class Video(BaseModel):
    id: str
    title: str
    released: str
    season: int | None = None
    episode: int | None = None


class Meta(BaseModel):
    id: str  # = Field(alias="_id")
    name: str = Field(alias="title")
    type: str = Field(default="movie")
    poster: str | None = None
    background: str | None = None
    videos: list[Video] | None = None
    country: str | None = None
    language: str | None = Field(None, alias="tv_language")
    logo: str | None = None
    genres: list[str] | None = None
    description: str | None = None
    runtime: str | None = None
    website: str | None = None
    stream: dict | None = None
    imdbRating: str | float | None = Field(None, alias="imdb_rating")
    releaseInfo: str | int | None = Field(None, alias="year")

    @model_validator(mode="after")
    def parse_meta(self) -> "Meta":
        if self.releaseInfo:
            self.releaseInfo = (
                f"{self.releaseInfo}-"
                if self.type == "series"
                else str(self.releaseInfo)
            )
        if self.imdbRating:
            self.imdbRating = str(self.imdbRating)

        return self


class MetaItem(BaseModel):
    meta: Meta


class Metas(BaseModel):
    metas: list[Meta] = []
