from pydantic import BaseModel, ConfigDict
from typing import Optional, List

# ---------- TestCase ----------

class TestCaseBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: str = "In Queue"
    steps: Optional[str] = None
    expected_result: Optional[str] = None

class TestCaseCreate(TestCaseBase):
    pass

class TestCaseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    steps: Optional[str] = None
    expected_result: Optional[str] = None

class TestCaseOut(TestCaseBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    suite_id: int

# ---------- TestSuite ----------

class TestSuiteBase(BaseModel):
    name: str
    description: Optional[str] = None

class TestSuiteCreate(TestSuiteBase):
    pass

class TestSuiteUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class TestSuiteOut(TestSuiteBase):
    model_config = ConfigDict(from_attributes=True)
    id: int

class TestSuiteWithCases(TestSuiteOut):
    test_cases: List[TestCaseOut] = []
