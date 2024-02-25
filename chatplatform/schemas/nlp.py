from pydantic import BaseModel


class QueryRequest(BaseModel):
    query: str
    user_request: str
