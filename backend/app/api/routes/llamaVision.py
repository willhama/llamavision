import os
from fastapi import APIRouter, Response, File, UploadFile, HTTPException, Depends
from docling.document_converter import DocumentConverter
from app.api.deps import CurrentUser, SessionDep
from app.utils import dynamic_class_creator
from app.models import Document
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List
import instructor

source = "https://arxiv.org/pdf/2408.09869"  # document per local path or URL

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter()


@router.post("/vision/upload-and-extract")
async def upload_and_extract(
    session: SessionDep,
    current_user: CurrentUser,
    file: UploadFile = File(...)) -> Response:
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
            "documentData": json_content
        }

        item = Document.model_validate(item_in,
                                       update={"owner_id": current_user.id})
        session.add(item)
        session.commit()
        session.refresh(item)

        return Response(content=result.document.model_dump_json(),
                        media_type="application/json")

    except Exception as e:
        print("ERROR:", e)
        session.rollback()
        raise HTTPException(status_code=500,
                            detail=f"Operation failed: {str(e)}")


@router.post("/vision/structure")
async def structure(session: SessionDep, document_id: str) -> Response:
    # Extract data from the uploaded file
    columns = ["title", "content", "name", "symptom", "diagnosis", "treatment"]

    response_class = dynamic_class_creator(columns)

    # enables `response_model` in create call
    client = instructor.from_openai(
        OpenAI(
            base_url="http://ollama:11434/v1",
            api_key="ollama",  # required, but unused
        ),
        mode=instructor.Mode.JSON,
    )

    document = session.get(Document, document_id)

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    text = document.documentText
    title = document.title

    resp = client.chat.completions.create(
        model="llama3",
        messages=[{
            "role":
            "user",
            "content":
            "This is the document title: " + title +
            "this is the document text: " + text,
        }, {
            "role": "system",
            "content": text,
        }],
        response_model=response_class,
    )
    print(resp.model_dump_json(indent=2))
    return Response(content=resp.model_dump_json(),
                    media_type="application/json")
