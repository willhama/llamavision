import os
from fastapi import APIRouter, Response, File, UploadFile, HTTPException, Depends
from docling.document_converter import DocumentConverter
from app.api.deps import CurrentUser, SessionDep
from app.models import Document, DocumentMetadata, DocumentBulkRepsonse
from openai import OpenAI
import instructor
from sqlmodel import select

source = "https://arxiv.org/pdf/2408.09869"  # document per local path or URL

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter()


@router.get("/documents", response_model=None)
async def get_documents(session: SessionDep, current_user: CurrentUser) -> any:
    statement = (select(Document).where(Document.owner_id == current_user.id))
    items = session.exec(statement).all()
    return {"items": items}


@router.get("/documents/{document_id}", response_model=Document)
async def get_document(session: SessionDep, current_user: CurrentUser,
                       document_id: str) -> dict:
    document = session.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


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
        markdown_content = result.document.export_to_markdown()
        json_content = result.document.model_dump()

        # Write the extracted data to the database
        item_in = {
            "title": file.filename,
            "description": None,
            "url": file_path,
            "documentText": markdown_content,
            "documentData": {}
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

    class MeetingInfo(BaseModel):
        users: List[User]
        date: str
        location: str
        budget: int
        deadline: str

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
        response_model=MeetingInfo,
    )
    print(resp.model_dump_json(indent=2))
    return Response(content=resp.model_dump_json(),
                    media_type="application/json")
