"""メモ API のリクエスト・レスポンススキーマ。"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class MemoCreateRequest(BaseModel):
    """メモ作成リクエスト。"""
    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., max_length=100_000)


class MemoUpdateRequest(BaseModel):
    """メモ更新リクエスト。タイトル・本文は任意指定。"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    content: Optional[str] = Field(None, max_length=100_000)


class MemoResponse(BaseModel):
    """メモ1件のレスポンス。"""
    id: str
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
