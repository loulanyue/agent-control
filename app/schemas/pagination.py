import math
from typing import Generic, TypeVar, List, Optional, Any, Callable
from pydantic import BaseModel, Field
from sqlalchemy.orm import Query

T = TypeVar("T")

class PageResult(BaseModel, Generic[T]):
    items: List[T] = Field(..., description="当前页数据列表")
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码 (1-indexed)")
    page_size: int = Field(..., description="每页记录数")
    total_pages: int = Field(..., description="总页数")

def paginate_query(
    query: Query,
    page: int = 1,
    page_size: int = 20,
    serializer: Optional[Callable[[Any], Any]] = None
) -> dict:
    """
    通用 SQLAlchemy Query 分页执行器
    """
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 20
    if page_size > 200:
        page_size = 200

    total = query.count()
    total_pages = math.ceil(total / page_size) if total > 0 else 1

    records = query.offset((page - 1) * page_size).limit(page_size).all()

    if serializer:
        items = [serializer(r) for r in records]
    else:
        items = records

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }
