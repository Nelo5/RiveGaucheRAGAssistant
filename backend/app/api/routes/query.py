from fastapi import APIRouter
from app.schemas.query import QueryRequest, QueryResponse
from app.services.rag_service import rag_service

router = APIRouter(prefix='/query', tags=['Query'])

@router.post('', response_model=QueryResponse, responses={400: {"description": "Malformed JSON body"}})
def ask(req: QueryRequest) -> QueryResponse:
    answer = rag_service.ask(req.question)
    return QueryResponse(answer=answer)