from fastapi.responses import JSONResponse
from fastapi import APIRouter, HTTPException
from CRUD.insert_records import upsert_data

router = APIRouter(
    prefix="/crud",
    tags=["database"],
    responses={
        404: {"description": "Not found"},
        400: {"description": "Bad request"},
        500: {"description": "Internal server error"}
    }
)  



@router.post("/insert-documents")
async def InsertDocuments():
    try:
        await upsert_data()
        return JSONResponse(status_code=200, content = "Document upserted successfully.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
