from typing import List
from fastapi.responses import JSONResponse
from fastapi import APIRouter, HTTPException, Query
from CRUD.insert_records import upsert_data
from CRUD.delete_records import delete_records

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

@router.post("/delete-documents")
async def DeleteDocuments(
    file_names: List[str], 
    id: bool = Query(False, description="Keep special characters in filenames if True"),
    deleteall: bool = Query(False, description="Delete all records in the namespace if True")
):
    try:
        # Call the async delete_records function
        await delete_records(file_names, id=id, deleteall=deleteall)
        return JSONResponse(status_code=200, content="Records deleted successfully.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))