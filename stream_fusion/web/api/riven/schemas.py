import enum
from typing import List, Optional
from pydantic import BaseModel, Field

class MediaTypes(str, enum.Enum):
    """Enum defining possible media types for search."""
    movie = "movie"
    tv = "tv"

class RivenResult(BaseModel):
    """
    Model representing a single torrent search result.
    
    Attributes:
        raw_title (str): Original title of the torrent
        size (Optional[int]): Size of the torrent in bytes
        link (Optional[str]): Direct download link (requires passkey)
        seeders (Optional[int]): Number of seeders
        magnet (Optional[str]): Magnet link (requires passkey)
        info_hash (Optional[str]): Torrent info hash
        privacy (Optional[str]): Privacy status ("private" or "public")
        languages (Optional[List[str]]): List of languages available
        type (Optional[str]): Media type ("movie" or "tv")
        source (str): Source of the torrent, defaults to "yggflix"
    """
    raw_title: str = Field(..., description="Original title of the torrent")
    size: Optional[int] = Field(None, description="Size in bytes")
    link: Optional[str] = Field(None, description="Direct download link")
    seeders: Optional[int] = Field(None, description="Number of seeders")
    magnet: Optional[str] = Field(None, description="Magnet link")
    info_hash: Optional[str] = Field(None, description="Torrent info hash")
    privacy: Optional[str] = Field(None, description="Privacy status")
    languages: Optional[List[str]] = Field(default=["fr"], description="Available languages")
    type: Optional[str] = Field(None, description="Media type (movie/tv)")
    source: str = Field(default="yggflix", description="Torrent source")

class RivenResponse(BaseModel):
    """
    Model representing the complete search response.
    
    Attributes:
        query (str): Original search query or identifier used
        tmdb_id (Optional[str]): TMDB ID if available
        imdb_id (Optional[str]): IMDB ID if available
        total_results (int): Total number of results found
        results (List[RivenResult]): List of torrent results
    """
    query: str = Field(..., description="Original search query")
    tmdb_id: Optional[str] = Field(None, description="TMDB ID")
    imdb_id: Optional[str] = Field(None, description="IMDB ID")
    total_results: int = Field(..., description="Total number of results")
    results: List[RivenResult] = Field(..., description="List of torrent results")

class ErrorResponse(BaseModel):
    """Model representing an error response."""
    detail: str = Field(..., description="Error description")