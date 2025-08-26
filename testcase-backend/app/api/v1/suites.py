from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from app.db import get_db
from app import models
from app.schemas import (
    TestSuiteCreate, TestSuiteOut, TestSuiteUpdate, TestSuiteWithCases, TestCaseCreate, TestCaseOut
)

router = APIRouter()

@router.get("/suites", response_model=list[TestSuiteOut])
def list_suites(db: Session = Depends(get_db)):
    suites = db.execute(select(models.TestSuite).order_by(models.TestSuite.id)).scalars().all()
    return suites

@router.get("/suites/{suite_id}", response_model=TestSuiteWithCases)
def get_suite(suite_id: str, db: Session = Depends(get_db)):
    suite = db.get(models.TestSuite, int(suite_id))
    if not suite:
        raise HTTPException(404, "Suite not found")
    # ensure cases are loaded
    _ = suite.test_cases
    return suite

@router.post("/suites", response_model=TestSuiteOut, status_code=201)
def create_suite(payload: TestSuiteCreate, db: Session = Depends(get_db)):
    # unique by name
    existing = db.scalar(select(models.TestSuite).where(models.TestSuite.name == payload.name))
    if existing:
        raise HTTPException(409, "Suite with this name already exists")
    suite = models.TestSuite(name=payload.name, description=payload.description)
    db.add(suite)
    db.commit()
    db.refresh(suite)
    return suite

@router.patch("/suites/{suite_id}", response_model=TestSuiteOut)
def update_suite(suite_id: int, payload: TestSuiteUpdate, db: Session = Depends(get_db)):
    suite = db.get(models.TestSuite, suite_id)
    if not suite:
        raise HTTPException(404, "Suite not found")
    if payload.name is not None:
        suite.name = payload.name
    if payload.description is not None:
        suite.description = payload.description
    db.commit()
    db.refresh(suite)
    return suite

@router.delete("/suites/{suite_id}", status_code=204)
def delete_suite(suite_id: int, db: Session = Depends(get_db)):
    suite = db.get(models.TestSuite, suite_id)
    if not suite:
        raise HTTPException(404, "Suite not found")
    db.delete(suite)
    db.commit()
    return

# Create a test case inside a suite
@router.post("/suites/{suite_id}/testcases", response_model=TestCaseOut, status_code=201)
def add_case_to_suite(suite_id: int, payload: TestCaseCreate, db: Session = Depends(get_db)):
    suite = db.get(models.TestSuite, suite_id)
    if not suite:
        raise HTTPException(404, "Suite not found")
    tc = models.TestCase(
        suite_id=suite_id,
        name=payload.name,
        description=payload.description,
        status=payload.status,
        steps=payload.steps,
        expected_result=payload.expected_result,
    )
    db.add(tc)
    db.commit()
    db.refresh(tc)
    return tc

# Optional: suite counts helper (for your left panel if wanted)
@router.get("/suites-with-counts")
def suites_with_counts(db: Session = Depends(get_db)):
    stmt = (
        select(
            models.TestSuite.id,
            models.TestSuite.name,
            models.TestSuite.description,
            func.count(models.TestCase.id).label("case_count"),
        )
        .join(models.TestCase, models.TestCase.suite_id == models.TestSuite.id, isouter=True)
        .group_by(models.TestSuite.id)
        .order_by(models.TestSuite.id)
    )
    rows = db.execute(stmt).all()
    return [
        {"id": r.id, "name": r.name, "description": r.description, "case_count": r.case_count}
        for r in rows
    ]
