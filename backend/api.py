from pathlib import Path
import sys
import shutil
import uuid

BACKEND_ROOT = Path(__file__).resolve().parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from config.settings import INPUT_DIR, ensure_runtime_directories
from schemas.review import DecisionRequest
from services.analysis_service import AnalysisService
from services.review_service import ReviewService
from utils.logger import logger

app = FastAPI(title="MISRA AI Agent", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

analysis_service = AnalysisService()
review_service = ReviewService()
ensure_runtime_directories()


@app.get("/")
def home():
    return {
        "application": "MISRA AI Agent",
        "status": "running",
        "workflow": "interactive_review",
    }


@app.post("/upload")
async def upload_code(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".c"):
        raise HTTPException(status_code=400, detail="Only .c source files are supported.")

    session_id = str(uuid.uuid4())
    file_path = INPUT_DIR / f"{session_id}.c"

    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        analysis_service.start_analysis(session_id=session_id, file_path=str(file_path))
        return review_service.status(session_id)
    except Exception as exc:
        logger.exception("Upload request failed for %s", file.filename)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/review/{session_id}")
def get_review_status(session_id: str):
    return _service_call(lambda: review_service.status(session_id))


@app.get("/review/{session_id}/explain")
def explain_current_rule(session_id: str):
    return _service_call(lambda: review_service.explain_current(session_id))


@app.post("/decision")
async def submit_decision(payload: DecisionRequest):
    return _service_call(
        lambda: review_service.submit(
            session_id=payload.session_id,
            action=payload.action,
            edited_code=payload.edited_code,
            comment=payload.comment,
        )
    )


@app.post("/finalize/{session_id}")
def finalize_review(session_id: str):
    return _service_call(lambda: review_service.finalize(session_id))


@app.get("/result/{session_id}")
def generate_result(session_id: str):
    return _service_call(lambda: review_service.generate(session_id))


def _service_call(callback):
    try:
        return callback()
    except KeyError as exc:
        logger.warning("Review session lookup failed: %s", exc)
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        logger.warning("Review workflow error: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
