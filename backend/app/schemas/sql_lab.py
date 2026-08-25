from pydantic import BaseModel


class SqlRunRequest(BaseModel):
    sql: str


class SqlRunResult(BaseModel):
    columns: list[str]
    rows: list[list]
    truncated: bool
    row_count: int


class SqlRunError(BaseModel):
    error: str
