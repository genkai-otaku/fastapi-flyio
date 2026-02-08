"""メモユースケースのテスト（リポジトリをモック）。"""
from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from typing import Optional

from app.domain.memo import Memo
from app.usecases.memo_repository import MemoRepository
from app.usecases.memo_use_cases import (
    CreateMemoUseCase,
    DeleteMemoUseCase,
    GetMemoUseCase,
    ListMemosUseCase,
    UpdateMemoUseCase,
)


class _FakeRepo(MemoRepository):
    """テスト用のインメモリリポジトリ。"""

    def __init__(self) -> None:
        self.memos: dict[str, Memo] = {}
        self._next_id = 1

    async def create(self, title: str, content: str) -> Memo:
        now = datetime(2025, 2, 8, 12, 0, 0)
        memo_id = f"memo-{self._next_id}"
        self._next_id += 1
        memo = Memo(
            id=memo_id,
            title=title,
            content=content,
            created_at=now,
            updated_at=now,
        )
        self.memos[memo_id] = memo
        return memo

    async def find_all(self) -> list[Memo]:
        return sorted(self.memos.values(), key=lambda m: m.created_at)

    async def find_by_id(self, memo_id: str) -> Optional[Memo]:
        return self.memos.get(memo_id)

    async def update(self, memo: Memo) -> Memo:
        if memo.id not in self.memos:
            raise KeyError(memo.id)
        self.memos[memo.id] = memo
        return memo

    async def delete_by_id(self, memo_id: str) -> bool:
        if memo_id in self.memos:
            del self.memos[memo_id]
            return True
        return False


class TestCreateMemoUseCase正常系:
    """正常系: メモ作成の場合。"""

    @pytest.mark.asyncio
    async def test_タイトルと本文を渡した場合_メモが作成されること(self) -> None:
        """タイトルと本文を渡した場合、メモが作成されること。"""
        repo = _FakeRepo()
        use_case = CreateMemoUseCase(repo)
        memo = await use_case.execute(title="買い物", content="牛乳を買う")
        assert memo.title == "買い物"
        assert memo.content == "牛乳を買う"
        assert memo.id.startswith("memo-")
        assert len(repo.memos) == 1


class TestListMemosUseCase正常系:
    """正常系: 一覧取得の場合。"""

    @pytest.mark.asyncio
    async def test_メモが複数ある場合_作成順で返ること(self) -> None:
        """メモが複数ある場合、作成順で返ること。"""
        repo = _FakeRepo()
        await repo.create("1本目", "内容1")
        await repo.create("2本目", "内容2")
        use_case = ListMemosUseCase(repo)
        memos = await use_case.execute()
        assert len(memos) == 2
        assert memos[0].title == "1本目"
        assert memos[1].title == "2本目"


class TestGetMemoUseCase正常系:
    """正常系: 1件取得の場合。"""

    @pytest.mark.asyncio
    async def test_存在するIDを指定した場合_該当メモが返ること(self) -> None:
        """存在する ID を指定した場合、該当メモが返ること。"""
        repo = _FakeRepo()
        created = await repo.create("タイトル", "本文")
        use_case = GetMemoUseCase(repo)
        found = await use_case.execute(created.id)
        assert found is not None
        assert found.id == created.id
        assert found.title == "タイトル"


class TestGetMemoUseCase異常系:
    """異常系: 1件取得で見つからない場合。"""

    @pytest.mark.asyncio
    async def test_存在しないIDを指定した場合_Noneが返ること(self) -> None:
        """存在しない ID を指定した場合、None が返ること。"""
        repo = _FakeRepo()
        use_case = GetMemoUseCase(repo)
        found = await use_case.execute("not-exist")
        assert found is None


class TestUpdateMemoUseCase正常系:
    """正常系: 更新の場合。"""

    @pytest.mark.asyncio
    async def test_タイトルだけ更新した場合_タイトルのみ変わること(self) -> None:
        """タイトルだけ更新した場合、タイトルのみが変わること。"""
        repo = _FakeRepo()
        created = await repo.create("旧タイトル", "本文")
        use_case = UpdateMemoUseCase(repo)
        updated = await use_case.execute(created.id, title="新タイトル")
        assert updated is not None
        assert updated.title == "新タイトル"
        assert updated.content == "本文"

    @pytest.mark.asyncio
    async def test_本文だけ更新した場合_本文のみ変わること(self) -> None:
        """本文だけ更新した場合、本文のみが変わること。"""
        repo = _FakeRepo()
        created = await repo.create("タイトル", "旧本文")
        use_case = UpdateMemoUseCase(repo)
        updated = await use_case.execute(created.id, content="新本文")
        assert updated is not None
        assert updated.title == "タイトル"
        assert updated.content == "新本文"


class TestUpdateMemoUseCase異常系:
    """異常系: 更新で見つからない場合。"""

    @pytest.mark.asyncio
    async def test_存在しないIDを指定した場合_Noneが返ること(self) -> None:
        """存在しない ID を指定した場合、None が返ること。"""
        repo = _FakeRepo()
        use_case = UpdateMemoUseCase(repo)
        updated = await use_case.execute("not-exist", title="無効")
        assert updated is None


class TestDeleteMemoUseCase正常系:
    """正常系: 削除の場合。"""

    @pytest.mark.asyncio
    async def test_存在するIDを指定した場合_Trueが返りメモが消えること(self) -> None:
        """存在する ID を指定した場合、True が返りメモが消えること。"""
        repo = _FakeRepo()
        created = await repo.create("削除する", "内容")
        use_case = DeleteMemoUseCase(repo)
        result = await use_case.execute(created.id)
        assert result is True
        assert created.id not in repo.memos


class TestDeleteMemoUseCase異常系:
    """異常系: 削除で見つからない場合。"""

    @pytest.mark.asyncio
    async def test_存在しないIDを指定した場合_Falseが返ること(self) -> None:
        """存在しない ID を指定した場合、False が返ること。"""
        repo = _FakeRepo()
        use_case = DeleteMemoUseCase(repo)
        result = await use_case.execute("not-exist")
        assert result is False
