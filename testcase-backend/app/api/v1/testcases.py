from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db import get_db
from app import models
from app.schemas import TestCaseOut, TestCaseUpdate

router = APIRouter()

@router.get("/testcases", response_model=list[TestCaseOut])
def list_testcases(
    q: str | None = Query(None, description="Search name/description"),
    suite_id: int | None = Query(None),
    db: Session = Depends(get_db),
):
    stmt = select(models.TestCase).order_by(models.TestCase.id)
    if suite_id:
        stmt = stmt.where(models.TestCase.suite_id == suite_id)
    if q:
        like = f"%{q.lower()}%"
        stmt = stmt.where(
            (models.TestCase.name.ilike(like)) |
            (models.TestCase.description.ilike(like))
        )
    return db.execute(stmt).scalars().all()

@router.patch("/testcases/{case_id}", response_model=TestCaseOut)
def update_testcase(case_id: int, payload: TestCaseUpdate, db: Session = Depends(get_db)):
    tc = db.get(models.TestCase, case_id)
    if not tc:
        raise HTTPException(404, "Test case not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(tc, field, value)
    db.commit()
    db.refresh(tc)
    return tc

@router.delete("/testcases/{case_id}", status_code=204)
def delete_testcase(case_id: int, db: Session = Depends(get_db)):
    tc = db.get(models.TestCase, case_id)
    if not tc:
        raise HTTPException(404, "Test case not found")
    db.delete(tc)
    db.commit()
    return
