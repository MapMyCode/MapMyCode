from pydantic import BaseModel
from typing import List, Dict

from pydantic import BaseModel
from typing import List


class DependencyInfo(BaseModel):
    dependency_name: str
    role: str


class ImportantSymbol(BaseModel):
    name: str
    type: str
    role: str


class FileSummary(BaseModel):
    file_name: str
    file_purpose: str
    flow_role: str
    dependencies: List[DependencyInfo]
    important_symbols: List[ImportantSymbol]