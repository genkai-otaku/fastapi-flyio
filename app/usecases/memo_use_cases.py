"""メモのアプリケーションサービス（ユースケース）。リポジトリに依存する。"""

from typing import Optional

from app.domain.memo import Memo
from app.usecases.memo_repository import MemoRepository


class CreateMemoUseCase:
    """メモを1件作成するユースケース。"""

    def __init__(self, repository: MemoRepository) -> None:
        self._repo = repository

    async def execute(self, title: str, content: str) -> Memo:
        return await self._repo.create(title=title, content=content)


class ListMemosUseCase:
    """メモ一覧を取得するユースケース。"""

    def __init__(self, repository: MemoRepository) -> None:
        self._repo = repository

    async def execute(self) -> list[Memo]:
        result = await self._repo.find_all()
        return list(result)


class GetMemoUseCase:
    """IDでメモを1件取得するユースケース。"""

    def __init__(self, repository: MemoRepository) -> None:
        self._repo = repository

    async def execute(self, memo_id: str) -> Optional[Memo]:
        return await self._repo.find_by_id(memo_id)


class UpdateMemoUseCase:
    """メモを更新するユースケース。"""

    def __init__(self, repository: MemoRepository) -> None:
        self._repo = repository

    async def execute(
        self,
        memo_id: str,
        *,
        title: Optional[str] = None,
        content: Optional[str] = None,
    ) -> Optional[Memo]:
        existing = await self._repo.find_by_id(memo_id)
        if existing is None:
            return None
        updated = existing
        if title is not None:
            updated = updated.with_title(title)
        if content is not None:
            updated = updated.with_content(content)
        return await self._repo.update(updated)


class DeleteMemoUseCase:
    """メモを1件削除するユースケース。"""

    def __init__(self, repository: MemoRepository) -> None:
        self._repo = repository

    async def execute(self, memo_id: str) -> bool:
        return await self._repo.delete_by_id(memo_id)
