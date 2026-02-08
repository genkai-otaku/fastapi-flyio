"""メモエンティティのテスト。"""

from datetime import datetime

from app.domain.memo import Memo


class TestMemo正常系:
    """正常系: メモの生成・不変操作が期待どおりであること。"""

    def test_メモを生成した場合_idとタイトルと本文と日時が保持されること(self) -> None:
        """メモを生成した場合、id・title・content・created_at・updated_at が保持されること。"""
        now = datetime(2025, 2, 8, 12, 0, 0)
        memo = Memo(
            id="memo-1",
            title="タイトル",
            content="本文",
            created_at=now,
            updated_at=now,
        )
        assert memo.id == "memo-1"
        assert memo.title == "タイトル"
        assert memo.content == "本文"
        assert memo.created_at == now
        assert memo.updated_at == now

    def test_with_titleを呼んだ場合_タイトルだけ変わった新しいメモが返ること(self) -> None:
        """with_title を呼んだ場合、タイトルだけが変わった新しいメモが返ること。"""
        memo = Memo(
            id="memo-1",
            title="旧タイトル",
            content="本文",
            created_at=datetime(2025, 2, 8),
            updated_at=datetime(2025, 2, 8),
        )
        new_memo = memo.with_title("新タイトル")
        assert new_memo.id == memo.id
        assert new_memo.title == "新タイトル"
        assert new_memo.content == memo.content
        assert memo.title == "旧タイトル"

    def test_with_contentを呼んだ場合_本文だけ変わった新しいメモが返ること(self) -> None:
        """with_content を呼んだ場合、本文だけが変わった新しいメモが返ること。"""
        memo = Memo(
            id="memo-1",
            title="タイトル",
            content="旧本文",
            created_at=datetime(2025, 2, 8),
            updated_at=datetime(2025, 2, 8),
        )
        new_memo = memo.with_content("新本文")
        assert new_memo.id == memo.id
        assert new_memo.title == memo.title
        assert new_memo.content == "新本文"
        assert memo.content == "旧本文"
