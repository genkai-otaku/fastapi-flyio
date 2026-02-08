"""FastAPI エントリーポイント。"""

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.interfaces.memo_router import router as memo_router
from prisma import Prisma


@asynccontextmanager
async def lifespan(app: FastAPI):
    """起動時に Prisma に接続、終了時に切断する。"""
    db = Prisma()
    await db.connect()
    app.state.db = db
    try:
        yield
    finally:
        await db.disconnect()


app = FastAPI(lifespan=lifespan)

app.include_router(memo_router)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Hello from fastapi-flyio!"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
