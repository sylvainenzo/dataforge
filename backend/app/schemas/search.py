from pydantic import BaseModel


class SearchResult(BaseModel):
    type: str
    title: str
    subtitle: str | None
    slug: str | None
    external_url: str | None
