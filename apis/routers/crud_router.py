import asyncio
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi import APIRouter, HTTPException, BackgroundTasks
from CRUD import insert_records

router = APIRouter(
    prefix="/crud",
    tags=["database"],
    responses={
        404: {"description": "Not found"},
        400: {"description": "Bad request"},
        500: {"description": "Internal server error"}
    }
)  


class UpsertDataRequest(BaseModel):
    json_path: str
    index_name: str
    namespace: str

@router.post("/insert-documents", response_model=UpsertDataRequest)
async def InsertDocuments(docs: UpsertDataRequest, background_task: BackgroundTasks):
    try:
        # Add the task to background
        background_task.add_task(
            asyncio.run,
            insert_records(docs.json_path, docs.index_name, docs.namespace)
        )
        return JSONResponse(status_code=200, content = "Document upserted successfully. (it can take time to show it in pinecone database)")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
