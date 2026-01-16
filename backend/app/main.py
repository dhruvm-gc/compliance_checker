from fastapi import FastAPI, UploadFile, File, Query
from pathlib import Path

from app.services.file_parser import parse_uploaded_file
from app.services.compliance_service import check_compliance
from app.vectordb.ingest_regulations_pdf import ingest_regulations_pdf
from app.vectordb.chroma_client import get_chroma

from app.middlewares import ExceptionMiddleware
from app.logger import get_logger


app = FastAPI(title="Compliance Checker")

DATA_DIR = Path(__file__).resolve().parent / "data"
UPLOAD_DIR = DATA_DIR / "uploads"

DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@app.on_event("startup")
def auto_ingest():
    db = get_chroma()
    count = db._collection.count()
    pdf = DATA_DIR / "regulations_master.pdf"

    if count == 0 and pdf.exists():
        print("[Startup] Auto ingest regulations_master.pdf")
        ingest_regulations_pdf(str(pdf), reset=False, max_chunks=300)
    else:
        print(f"[Startup] DB count: {count}. Skipping auto ingest.")

@app.get("/db/count")
def db_count():
    db = get_chroma()
    return {"count": db._collection.count()}

@app.post("/regulations/ingest")
async def regulations_ingest(
    file: UploadFile = File(...),
    reset: bool = Query(False),
    max_chunks: int = Query(300)
):
    save_path = DATA_DIR / file.filename
    save_path.write_bytes(await file.read())
    return ingest_regulations_pdf(str(save_path), reset=reset, max_chunks=max_chunks)

@app.post("/compliance/upload")
async def compliance_upload(
    file: UploadFile = File(...),
    top_k: int = Query(2)
):
    save_path = UPLOAD_DIR / file.filename
    save_path.write_bytes(await file.read())

    text = parse_uploaded_file(save_path)
    return check_compliance(text, top_k=top_k)
