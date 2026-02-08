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

## CI/CD（GitHub Actions）

| ワークフロー | トリガー | 内容 |
|-------------|----------|------|
| **CI** | `main` への push、`main` 向け PR | Lint（ruff check / format）、テスト（pytest） |
| **Delete branch** | PR がマージされたとき | マージ元ブランチを自動削除（main は保護） |
| **Deploy** | `main` への push | Fly.io へデプロイ（`fly deploy`） |

### デプロイに必要な GitHub Secrets

- **FLY_API_TOKEN**: Fly.io のデプロイ用トークン。  
  `fly tokens create deploy -x 999999h` で発行し、GitHub の Settings → Secrets and variables → Actions に `FLY_API_TOKEN` として登録する。

### ローカルで Lint を回す

```zsh
uv sync --extra dev
uv run ruff check .
uv run ruff format --check .
```

## デプロイ（Fly.io）

- 手動: `fly launch`（初回） / `fly deploy`
- 自動: `main` にマージすると Deploy ワークフローが走り、Fly.io にデプロイされる。
- リポジトリに `fly.toml` と `Dockerfile` を含めている。既存アプリに合わせる場合は `fly config save -a <アプリ名>` で上書きできる。

### Fly Managed Postgres（MPG）を使う場合

**1. アプリを DB にアタッチ**

Managed Postgres クラスタ作成後、アプリに `DATABASE_URL` を渡す。

```bash
fly mpg list
fly mpg attach <クラスタID> -a <アプリ名>
```

例: `fly mpg attach 82ylg01nykzozx19 -a fastapi-flyio-cjrs7a`

アタッチするとアプリが再起動し、Secrets に `DATABASE_URL` が設定される。

**2. 本番 DB にマイグレーションを実行**

本番の Postgres は Fly のプライベートネットワーク内にあるため、ローカルからは **proxy** 経由で接続する。

- **ターミナル 1**: proxy を起動し、**起動したまま**にする。

  ```bash
  fly mpg proxy
  ```

  クラスタを選ぶと、例えば次のように表示される:

  ```text
  Proxying localhost:16380 to remote [fdaa:...]:5432
  ```

  この **16380** が「proxy のポート」なのでメモする（環境によって番号は変わる）。

- **ターミナル 2**（新しいターミナルを開く）: ここからが「proxy をやった後」の手順。

  1. **パスワードを用意する**  
     [Fly ダッシュボード](https://fly.io/dashboard) → 左の **Managed Postgres** → クラスタ **memo** をクリック → **Connection** タブ。  
     表示されている接続文字列の中の **パスワード**（`fly-user:` の次から `@` の前まで）をコピーする。クラスタ作成時にターミナルに表示されていたパスワードと同じ。

  2. **接続先を「localhost + proxy のポート」にする**  
     本来の接続文字列は `...@pgbouncer.82ylg01nykzozx19.flympg.net/fly-db` のようになっている。  
     proxy 経由でつなぐときは、ホストを `localhost`、ポートをターミナル 1 でメモした番号（例: 16380）に変える。

  3. **次の 2 行を実行する**（`16380` を自分の proxy ポートに、`ここにパスワード` を実際のパスワードに置き換える）。proxy 経由では TLS 不要なので `?sslmode=disable` を付ける:

  ```bash
  export DATABASE_URL="postgresql://fly-user:ここにパスワード@localhost:16380/fly-db?sslmode=disable"
  uv run prisma migrate deploy
  ```

  - 成功すると `Applying migration ...` のような表示が出て終了する。
  - 終わったらターミナル 1 で `Ctrl+C` して proxy を止めてよい。

**3. 動作確認**

```bash
curl https://<アプリ名>.fly.dev/memos
```

空配列 `[]` が返れば OK。メモを作成・取得できるかも試す。

- 今後スキーマを変更したときは、同様に `fly mpg proxy` のうえで `uv run prisma migrate deploy` を実行する。
- `DATABASE_URL` を手動で設定する場合は `fly secrets set DATABASE_URL="..."` で行う（MPG アタッチ済みなら上書きになるので通常は不要）。

### DB クライアントで本番 DB を閲覧する

TablePlus・DBeaver・pgAdmin などで本番の Postgres を見るには、上記と同様に **proxy 経由**で接続する。

1. **ターミナルで proxy を起動**（接続している間は起動したままにする）

   ```bash
   fly mpg proxy
   ```

   クラスタを選ぶと `Proxying localhost:16380 to remote ...` のように表示される。**ポート番号**（例: 16380）をメモする。

2. **接続情報を用意する**

   - [Fly ダッシュボード](https://fly.io/dashboard) → **Managed Postgres** → クラスタ **memo** → **Connection** タブで接続文字列を確認する。
   - proxy 用に次のようにする:
     - **ホスト**: `localhost`
     - **ポート**: 手順 1 のポート（例: 16380）
     - **ユーザー**: `fly-user`
     - **パスワード**: Connection タブに表示されているパスワード
     - **データベース**: `fly-db`
   - SSL/TLS は **無効**（proxy 経由のため。クライアントで「SSL を使わない」や `sslmode=disable` を指定する）。

3. **DB クライアントで新規接続を作成**し、上記のホスト・ポート・ユーザー・パスワード・DB 名を入力して接続する。

4. 使い終わったらターミナルで `Ctrl+C` して proxy を止める。
