import os
from fastapi import APIRouter, Response, File, UploadFile, HTTPException, Depends
from docling.document_converter import DocumentConverter
from app.api.deps import CurrentUser, SessionDep
from app.models import Document

source = "https://arxiv.org/pdf/2408.09869"  # document per local path or URL

router = APIRouter()


UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter()

@router.post("/vision/upload-and-extract")
async def upload_and_extract(
    session: SessionDep,
    current_user: CurrentUser,
    file: UploadFile = File(...)
) -> Response:
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    try:
        # Save the uploaded file to the filesystem
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        # Extract data from the uploaded file
        converter = DocumentConverter()
        result = converter.convert(file_path)
        # print("DOCUMENT DOUCMENT", result.document.model_dump())
        markdown_content = result.document.export_to_markdown()
        json_content = result.document.model_dump()

        # Write the extracted data to the database
        item_in = {  
        "title": file.filename,
        "description": None,
        "url": file_path,
        "documentText": markdown_content,
        "documentData": json_content}
        print("ITEM IN", item_in)

        item = Document.model_validate(item_in, update={"owner_id": current_user.id})
        session.add(item)
        session.commit()
        session.refresh(item)

        return Response(content=result.document.model_dump_json(), media_type="application/json")

    except Exception as e:
        print("ERROR:",e)
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Operation failed: {str(e)}")
