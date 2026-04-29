from pydantic import BaseModel, Field, field_validator

class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000, description="Вопрос пользователя")

    @field_validator("question")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip()

class QueryResponse(BaseModel):
    answer: str = Field(..., description="Ответ на заданный вопрос")