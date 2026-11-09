from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.category import Category
from app.models.record import Record
from app.models.user import User
from app.schemas.record import RecordCreate, RecordPage, RecordResponse, RecordUpdate


router = APIRouter(prefix="/records", tags=["记录"])


def get_owned_record(record_id: int, db: Session, user_id: int) -> Record:
    # 查询同时包含资源 ID 和当前用户 ID，避免修改或删除不属于自己的记录。
    record = (
        db.query(Record)
        .filter(Record.id == record_id, Record.user_id == user_id)
        .first()
    )
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="记录不存在")
    return record


@router.get("", response_model=RecordPage)
def list_records(
    start: date | None = None,
    end: date | None = None,
    category_id: int | None = Query(None, gt=0),
    type: Literal["income", "expense"] | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if start is not None and end is not None and start > end:
        # 日期范围无效属于无法处理的请求内容。
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="start不能晚于end")

    query = db.query(Record).filter(Record.user_id == current_user.id)
    if start is not None:
        query = query.filter(Record.occurred_at >= start)
    if end is not None:
        query = query.filter(Record.occurred_at <= end)
    if category_id is not None:
        query = query.filter(Record.category_id == category_id)
    if type is not None:
        query = query.filter(Record.type == type)

    # 组合筛选后统计总数，再应用分页。
    total = query.count()
    items = (
        query.order_by(Record.occurred_at.desc(), Record.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {"total": total, "page": page, "page_size": page_size, "items": items}


@router.post("", response_model=RecordResponse, status_code=status.HTTP_201_CREATED)
def create_record(
    payload: RecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    category = (
        db.query(Category)
        .filter(Category.id == payload.category_id, Category.user_id == current_user.id)
        .first()
    )
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="分类不存在")

    record = Record(
        category_id=payload.category_id,
        amount=payload.amount,
        note=payload.note,
        type=payload.type,
        user_id=current_user.id,
        occurred_at=payload.occurred_at,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.patch("/{record_id}", response_model=RecordResponse)
def update_record(
    record_id: int,
    payload: RecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = get_owned_record(record_id, db, current_user.id)
    data = payload.model_dump(exclude_unset=True)
    if "category_id" in data:
        category = (
            db.query(Category)
            .filter(
                Category.id == data["category_id"],
                Category.user_id == current_user.id,
            )
            .first()
        )
        if category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="分类不存在")

    # PATCH 只更新请求中实际提供的字段。
    for field, value in data.items():
        setattr(record, field, value)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = get_owned_record(record_id, db, current_user.id)
    db.delete(record)
    db.commit()