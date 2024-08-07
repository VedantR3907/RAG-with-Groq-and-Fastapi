from typing import List
import sys
sys.path.append('../')
from fastapi.responses import JSONResponse
from fastapi import APIRouter, HTTPException, UploadFile
from loaders.main import save_files_to_directory, process_files

router = APIRouter(
    prefix="/loader",
    tags=["Loader"],
    responses={
        404: {"description": "Not found"},
        400: {"description": "Bad request"},
        500: {"description": "Internal server error"}
    }
)  

@router.post('/loading-files')
async def LoadingFiles(files: List[UploadFile]):

    try:
        await save_files_to_directory(files)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving files: {e}")
    
    try:
        await process_files()
        return JSONResponse(content={"message": "Files processed successfully"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing files: {e}")