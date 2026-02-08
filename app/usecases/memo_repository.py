"""メモの永続化インターフェース。実装はインフラ層に依存する。"""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Optional

from app.domain.memo import Memo


class MemoRepository(ABC):
    """メモのリポジトリインターフェース。"""

    @abstractmethod
    async def create(self, title: str, content: str) -> Memo:
        """メモを1件作成し、生成されたエンティティを返す。"""
        ...

    @abstractmethod
    async def find_all(self) -> Sequence[Memo]:
        """全メモを作成日時の昇順で返す。"""
        ...

    @abstractmethod
    async def find_by_id(self, memo_id: str) -> Optional[Memo]:
        """IDでメモを1件取得する。存在しなければ None。"""
        ...

    @abstractmethod
    async def update(self, memo: Memo) -> Memo:
        """メモを更新する。更新後のエンティティを返す。"""
        ...

    @abstractmethod
    async def delete_by_id(self, memo_id: str) -> bool:
        """IDでメモを1件削除する。削除した場合 True、存在しなければ False。"""
        ...
