"""メモ API の E2E テスト。DATABASE_URL が設定され DB が利用可能な場合に実行する。"""

import os

import pytest
from fastapi.testclient import TestClient

from app.main import app

# DB が無い環境では E2E をスキップする
pytestmark = pytest.mark.skipif(
    not os.getenv("DATABASE_URL"),
    reason="DATABASE_URL が未設定のため E2E をスキップ",
)


@pytest.fixture
def api_client() -> TestClient:
    return TestClient(app)


class TestメモAPI正常系:
    """正常系: メモの作成・一覧・取得・更新・削除ができること。"""

    def test_メモを作成した場合_201とメモが返ること(self, api_client: TestClient) -> None:
        """メモを作成した場合、201 と作成されたメモが返ること。"""
        res = api_client.post(
            "/memos",
            json={"title": "E2Eタイトル", "content": "E2E本文"},
        )
        assert res.status_code == 201
        data = res.json()
        assert data["title"] == "E2Eタイトル"
        assert data["content"] == "E2E本文"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_メモ一覧を取得した場合_200とリストが返ること(self, api_client: TestClient) -> None:
        """メモ一覧を取得した場合、200 とリストが返ること。"""
        res = api_client.get("/memos")
        assert res.status_code == 200
        assert isinstance(res.json(), list)

    def test_存在するIDで取得した場合_200とメモが返ること(self, api_client: TestClient) -> None:
        """存在する ID で取得した場合、200 とメモが返ること。"""
        create = api_client.post(
            "/memos",
            json={"title": "取得用", "content": "内容"},
        )
        assert create.status_code == 201
        memo_id = create.json()["id"]
        res = api_client.get(f"/memos/{memo_id}")
        assert res.status_code == 200
        assert res.json()["id"] == memo_id
        assert res.json()["title"] == "取得用"

    def test_存在するIDで更新した場合_200と更新後のメモが返ること(
        self, api_client: TestClient
    ) -> None:
        """存在する ID で更新した場合、200 と更新後のメモが返ること。"""
        create = api_client.post(
            "/memos",
            json={"title": "更新前", "content": "内容"},
        )
        assert create.status_code == 201
        memo_id = create.json()["id"]
        res = api_client.patch(
            f"/memos/{memo_id}",
            json={"title": "更新後"},
        )
        assert res.status_code == 200
        assert res.json()["title"] == "更新後"

    def test_存在するIDで削除した場合_204が返ること(self, api_client: TestClient) -> None:
        """存在する ID で削除した場合、204 が返ること。"""
        create = api_client.post(
            "/memos",
            json={"title": "削除用", "content": "内容"},
        )
        assert create.status_code == 201
        memo_id = create.json()["id"]
        res = api_client.delete(f"/memos/{memo_id}")
        assert res.status_code == 204
        get_res = api_client.get(f"/memos/{memo_id}")
        assert get_res.status_code == 404


class TestメモAPI異常系:
    """異常系: 存在しない ID の場合は 404 であること。"""

    def test_存在しないIDで取得した場合_404であること(self, api_client: TestClient) -> None:
        """存在しない ID で取得した場合、404 であること。"""
        res = api_client.get("/memos/non-existent-id")
        assert res.status_code == 404

    def test_存在しないIDで更新した場合_404であること(self, api_client: TestClient) -> None:
        """存在しない ID で更新した場合、404 であること。"""
        res = api_client.patch(
            "/memos/non-existent-id",
            json={"title": "無効"},
        )
        assert res.status_code == 404

    def test_存在しないIDで削除した場合_404であること(self, api_client: TestClient) -> None:
        """存在しない ID で削除した場合、404 であること。"""
        res = api_client.delete("/memos/non-existent-id")
        assert res.status_code == 404
