from pydantic import BaseModel
from typing import List, Optional, Any


class Link(BaseModel):
    """HATEOAS link model"""
    rel: str        # Relationship: self, collection, next, prev, create, update, delete
    href: str       # URL
    method: str     # HTTP method: GET, POST, PUT, DELETE


class PaginatedResponse(BaseModel):
    """Paginated collection with HATEOAS links"""
    data: List[Any]
    links: List[Link]
    page: int
    per_page: int
    total: Optional[int] = None
