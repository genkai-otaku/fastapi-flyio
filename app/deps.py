"""FastAPI の依存性（DB 取得など）。"""
from fastapi import Request


def get_db(request: Request):
    """リクエストから Prisma クライアントを取得する。"""
    return request.app.state.db
