# FastAPI Fly.io（メモアプリ）

FastAPI を Fly.io にデプロイする練習用リポジトリ。汎用メモアプリの CRUD API を実装している。

## 技術スタック

- FastAPI / uvicorn
- PostgreSQL（Docker / Prisma）
- prisma-client-py（async）
- uv

## クリーンアーキテクチャ（概要）

このプロジェクトは **ドメインベースのクリーンアーキテクチャ** を採用している。依存の向きは **外側 → 内側** のみで、ドメインはフレームワークや DB に依存しない。

| 層 | 役割 | 配置（`app/`） |
|----|------|----------------|
| **ドメイン** | エンティティ・値オブジェクト。ビジネスルールのみ。 | `domain/` |
| **ユースケース** | アプリの振る舞い。リポジトリの**インターフェース**を定義。 | `usecases/` |
| **インフラ** | DB（Prisma）など具体的な実装。リポジトリの**実装**。 | `infrastructure/` |
| **インターフェース** | FastAPI ルーター・スキーマ。ユースケースを呼び出し HTTP に変換。 | `interfaces/` |

- **ドメイン** は何にも依存しない。エンティティ（データの形）を置く層で、「呼び出しの一歩」ではない（下記の実行時の流れ参照）。
- **ユースケース** はドメインの型とリポジトリの**インターフェース**だけに依存し、リポジトリの**実装**（インフラ）には直接依存しない。
- **インフラ** がリポジトリを実装し、**インターフェース** がルーターでユースケースにリポジトリを注入して組み立てる。

### 実行時の流れ（リクエストが来たとき）

HTTP リクエストが届いてから DB に触るまで、実際の呼び出し順は次のとおり。

```
  HTTP リクエスト
        │
        ▼
  ┌─────────────────────┐
  │ インターフェース層   │  ルーターがリクエストを受け、ユースケースを呼ぶ
  │ (interfaces/)        │  （リポジトリは DI で渡されている）
  └──────────┬──────────┘
             │
             ▼
  ┌─────────────────────┐
  │ ユースケース層       │  repo.create() / find_all() などを呼ぶ
  │ (usecases/)          │  ※ ここで呼ばれる「リポジトリ」の実体はインフラ層
  └──────────┬──────────┘
             │
             ▼
  ┌─────────────────────┐
  │ インフラ層           │  リポジトリの実装。Prisma で DB にアクセスし、
  │ (infrastructure/)   │  結果をドメインの Memo に変換して返す
  └──────────┬──────────┘
             │
             ▼
        PostgreSQL
```

**ドメイン層について**: ドメインは「呼び出しの一歩」ではなく、**エンティティ（例: Memo）を定義する層**。ユースケースやインフラがこの型を使ってデータをやりとりする。このアプリでは Memo が中心で、`with_title` / `with_content` など更新時の不変操作もドメインに置いている。ルールが増えればドメインサービスなどが増える。

### 設計上の依存（コードの参照関係）

「A → B」＝ A が B を参照する（外側が内側に依存）。内側の層は外側のことを知らない。

```mermaid
flowchart TB
  IF["インターフェース層\ninterfaces/"]
  INF["インフラ層\ninfrastructure/"]
  UC["ユースケース層\nusecases/"]
  DM["ドメイン層\ndomain/"]

  IF --> UC
  IF -.->|"DI で注入"| INF
  INF --> UC
  UC --> DM
```

**表（誰が誰に依存するか）**

| 依存する層（呼び出し元） | 依存される層（参照先） |
|--------------------------|------------------------|
| インターフェース         | ユースケース、インフラ（リポジトリを new してユースケースに渡す） |
| インフラ                 | ユースケース（リポジトリ IF を実装） |
| ユースケース             | ドメイン、リポジトリの**インターフェース** |
| ドメイン                 | なし |

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
