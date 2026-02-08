"""メモ API のルーター。ユースケースを呼び出し HTTP に変換する。"""
from fastapi import APIRouter, Depends, HTTPException, status

from app.deps import get_db
from app.domain.memo import Memo
from app.infrastructure.prisma_memo_repository import PrismaMemoRepository
from app.interfaces.memo_schema import (
    MemoCreateRequest,
    MemoResponse,
    MemoUpdateRequest,
)
from app.usecases.memo_use_cases import (
    CreateMemoUseCase,
    DeleteMemoUseCase,
    GetMemoUseCase,
    ListMemosUseCase,
    UpdateMemoUseCase,
)

router = APIRouter(prefix="/memos", tags=["memos"])


def _memo_to_response(memo: Memo) -> MemoResponse:
    return MemoResponse(
        id=memo.id,
        title=memo.title,
        content=memo.content,
        created_at=memo.created_at,
        updated_at=memo.updated_at,
    )


def _get_use_cases(db=Depends(get_db)) -> dict:
    """DI: リポジトリとユースケースを組み立てる。"""
    repo = PrismaMemoRepository(db)
    return {
        "create": CreateMemoUseCase(repo),
        "list": ListMemosUseCase(repo),
        "get": GetMemoUseCase(repo),
        "update": UpdateMemoUseCase(repo),
        "delete": DeleteMemoUseCase(repo),
    }


@router.post("", response_model=MemoResponse, status_code=status.HTTP_201_CREATED)
async def create_memo(
    body: MemoCreateRequest,
    use_cases: dict = Depends(_get_use_cases),
) -> MemoResponse:
    memo = await use_cases["create"].execute(
        title=body.title,
        content=body.content,
    )
    return _memo_to_response(memo)


@router.get("", response_model=list[MemoResponse])
async def list_memos(
    use_cases: dict = Depends(_get_use_cases),
) -> list[MemoResponse]:
    memos = await use_cases["list"].execute()
    return [_memo_to_response(m) for m in memos]


@router.get("/{memo_id}", response_model=MemoResponse)
async def get_memo(
    memo_id: str,
    use_cases: dict = Depends(_get_use_cases),
) -> MemoResponse:
    memo = await use_cases["get"].execute(memo_id)
    if memo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="メモが見つかりません",
        )
    return _memo_to_response(memo)


@router.patch("/{memo_id}", response_model=MemoResponse)
async def update_memo(
    memo_id: str,
    body: MemoUpdateRequest,
    use_cases: dict = Depends(_get_use_cases),
) -> MemoResponse:
    memo = await use_cases["update"].execute(
        memo_id,
        title=body.title,
        content=body.content,
    )
    if memo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="メモが見つかりません",
        )
    return _memo_to_response(memo)


@router.delete("/{memo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memo(
    memo_id: str,
    use_cases: dict = Depends(_get_use_cases),
) -> None:
    deleted = await use_cases["delete"].execute(memo_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="メモが見つかりません",
        )
