from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.category import Category
from app.models.record import Record
from app.models.user import User
from app.schemas.stats import CategoryStatsResponse, MonthlyStatsResponse


router = APIRouter(prefix="/stats", tags=["统计"])


@router.get("/monthly", response_model=MonthlyStatsResponse)
def monthly_stats(
    year: int = Query(..., ge=1),
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        start = date(year, month, 1)
    except ValueError as exc:
        raise HTTPException(
            # 使用当前 Starlette 推荐的 HTTP 422 状态码名称。
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="年份或月份无效",
        ) from exc

    if month == 12:
        end = date(year + 1, 1, 1)
    else:
        end = date(year, month + 1, 1)

    income_total, expense_total = (
        db.query(
            func.coalesce(
                func.sum(case((Record.type == "income", Record.amount), else_=0)),
                0,
            ),
            func.coalesce(
                func.sum(case((Record.type == "expense", Record.amount), else_=0)),
                0,
            ),
        )
        .filter(
            Record.user_id == current_user.id,
            Record.occurred_at >= start,
            Record.occurred_at < end,
        )
        .one()
    )
    income = float(income_total)
    expense = float(expense_total)
    return {
        "year": year,
        "month": month,
        "income": round(income, 2),
        "expense": round(expense, 2),
        "balance": round(income - expense, 2),
    }


@router.get("/by-category", response_model=list[CategoryStatsResponse])
def stats_by_category(
    start: date,
    end: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if start > end:
        raise HTTPException(
            # 日期范围无效属于无法处理的请求内容。
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="start不能晚于end",
        )

    rows = (
        db.query(
            Category.id.label("category_id"),
            Category.name.label("category_name"),
            Category.type.label("category_type"),
            func.sum(Record.amount).label("amount"),
        )
        .join(Record, Record.category_id == Category.id)
        .filter(
            Record.user_id == current_user.id,
            Record.occurred_at >= start,
            Record.occurred_at <= end,
        )
        .group_by(Category.id, Category.name, Category.type)
        .order_by(func.sum(Record.amount).desc())
        .all()
    )

    total_amount = sum((float(row.amount) for row in rows), 0.0)
    return [
        {
            "category_id": row.category_id,
            "category_name": row.category_name,
            "category_type": row.category_type,
            "amount": round(float(row.amount), 2),
            "percentage": round(float(row.amount) / total_amount * 100, 2) if total_amount else 0.0,
        }
        for row in rows
    ]