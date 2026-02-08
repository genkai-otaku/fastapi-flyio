# FastAPI Fly.io（メモアプリ）

FastAPI を Fly.io にデプロイする練習用リポジトリ。汎用メモアプリの CRUD API を実装している。

## 技術スタック

- FastAPI / uvicorn
- PostgreSQL（Docker / Prisma）
- prisma-client-py（async）
- uv

## 開発

### 仮想環境・依存

venv を使うため、Python 系のコマンドは `uv run` で実行する（`activate` は不要）。

```zsh
uv sync
uv sync --extra dev         # テスト用
```

### DB（PostgreSQL）

```zsh
docker compose up -d
cp .env.example .env        # 必要なら編集
```

`.env` に `DATABASE_URL` を設定する（例: `postgresql://app:app@localhost:5432/memo_dev`）。

### Prisma

```zsh
uv run prisma generate
uv run prisma migrate dev   # 初回またはスキーマ変更時
```

### DB を閲覧（Prisma Studio）

```zsh
uv run prisma studio
```

ブラウザで http://localhost:5555 が開き、テーブルの中身を確認・編集できる。

### 起動

```zsh
uv run uvicorn app.main:app --reload
```

- API: http://localhost:8000
- ドキュメント: http://localhost:8000/docs

### メモ API

| メソッド | パス | 説明 |
|----------|------|------|
| POST | /memos | メモ作成 |
| GET | /memos | 一覧取得 |
| GET | /memos/{id} | 1件取得 |
| PATCH | /memos/{id} | 更新 |
| DELETE | /memos/{id} | 削除 |

### テスト

```zsh
uv run pytest
```

- ドメイン・ユースケースのテストは DB 不要。
- `tests/api/` の E2E は `DATABASE_URL` が設定されている場合のみ実行される。

## デプロイ（Fly.io）

- `fly launch` / `fly deploy`
- `DATABASE_URL` は Fly の Secrets で設定する。
