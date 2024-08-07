import sys
sys.path.append('../')
from typing import List
from fastapi.responses import JSONResponse
from fastapi import APIRouter, HTTPException, UploadFile, File
from loaders.main import save_files_to_directory, process_files
from loaders.PDFToTXT_Without_FilePath import process_and_save_files

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
    

@router.post("/uploadfiles-without-filepath/")
async def create_upload_files(files: List[UploadFile] = File(...)):
    saved_files = await process_and_save_files(files)
    return {"message": f"Successfully uploaded {len(saved_files)} files"}