"""Prisma を使ったメモリポジトリの実装。"""

from typing import Optional

from app.domain.memo import Memo
from app.usecases.memo_repository import MemoRepository
from prisma import Prisma


def _to_domain(row: object) -> Memo:
    """Prisma の Memo レコードをドメインの Memo に変換する。"""
    return Memo(
        id=row.id,
        title=row.title,
        content=row.content,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


class PrismaMemoRepository(MemoRepository):
    """Prisma を用いた MemoRepository の実装。"""

    def __init__(self, db: Prisma) -> None:
        self._db = db

    async def create(self, title: str, content: str) -> Memo:
        row = await self._db.memo.create(data={"title": title, "content": content})
        return _to_domain(row)

    async def find_all(self) -> list[Memo]:
        rows = await self._db.memo.find_many(order={"created_at": "asc"})
        return [_to_domain(r) for r in rows]

    async def find_by_id(self, memo_id: str) -> Optional[Memo]:
        row = await self._db.memo.find_unique(where={"id": memo_id})
        if row is None:
            return None
        return _to_domain(row)

    async def update(self, memo: Memo) -> Memo:
        row = await self._db.memo.update(
            where={"id": memo.id},
            data={
                "title": memo.title,
                "content": memo.content,
            },
        )
        return _to_domain(row)

    async def delete_by_id(self, memo_id: str) -> bool:
        try:
            await self._db.memo.delete(where={"id": memo_id})
            return True
        except Exception:
            # 存在しない ID の場合は Prisma が例外を投げる想定
            return False
