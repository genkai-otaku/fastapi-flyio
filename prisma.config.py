"""Prisma の設定（Python 用）。パスや DATABASE_URL を参照する場合に利用。"""
import os
from pathlib import Path

# .env を読む（python-dotenv があれば。なければ環境変数のみ）
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# このファイルがあるディレクトリ（プロジェクトルート）基準
ROOT = Path(__file__).resolve().parent

schema_path = ROOT / "prisma" / "schema.prisma"
migrations_path = ROOT / "prisma" / "migrations"
datasource_url = os.environ.get("DATABASE_URL", "")
