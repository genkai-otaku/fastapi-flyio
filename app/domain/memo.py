"""メモのドメインエンティティ。DB・フレームワークに依存しない。"""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Memo:
    """メモエンティティ。ID・タイトル・本文・作成/更新日時を持つ。"""

    id: str
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

    def with_title(self, title: str) -> "Memo":
        """タイトルを変更した新しいメモを返す（不変のため）。"""
        return Memo(
            id=self.id,
            title=title,
            content=self.content,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    def with_content(self, content: str) -> "Memo":
        """本文を変更した新しいメモを返す（不変のため）。"""
        return Memo(
            id=self.id,
            title=self.title,
            content=content,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
