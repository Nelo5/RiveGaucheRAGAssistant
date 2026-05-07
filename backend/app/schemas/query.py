from pydantic import BaseModel, Field, field_validator

class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000, description="Вопрос пользователя")

    @field_validator("question")
    def strip_whitespace(cls, v: str) -> str:
        return v.replace("\x00", "").strip()

class QueryResponse(BaseModel):
    answer: str = Field(..., description="Ответ на заданный вопрос")