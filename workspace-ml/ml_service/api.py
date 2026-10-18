import io
import os
import threading
import warnings
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image, UnidentifiedImageError

from .inference.hf_disease_test import MODEL_ID, ModelLoadError, load_model, predict_image

MAX_IMAGE_BYTES = 10 * 1024 * 1024
MAX_IMAGE_PIXELS = 20_000_000
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
EXTENSION_FORMATS = {
    ".jpg": "JPEG",
    ".jpeg": "JPEG",
    ".png": "PNG",
    ".webp": "WEBP",
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_model_state(app.state)
    yield


def initialize_model_state(state) -> None:
    state.interpreter = None
    state.labels = None
    state.inference_lock = threading.Lock()
    state.model_error = None
    try:
        state.interpreter, state.labels = load_model()
    except ModelLoadError as exc:
        state.model_error = str(exc)


app = FastAPI(title="KisanSetu Crop Disease API", lifespan=lifespan)
router = APIRouter()

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "KISANSETU_CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,"
        "http://localhost:5174,http://127.0.0.1:5174",
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


def _display_name(class_name: str) -> str:
    crop, separator, disease = class_name.partition("___")
    if not separator:
        return class_name.replace("_", " ").strip()
    return f"{crop.replace('_', ' ').strip()} {disease.replace('_', ' ').strip()}"


def model_health(state):
    if state.interpreter is None or state.model_error:
        return JSONResponse(
            status_code=503,
            content={
                "ready": False,
                "model_ready": False,
                "detail": state.model_error or "Disease model is not loaded.",
            },
        )
    return {
        "ready": True,
        "model_ready": True,
        "model_used": f"{MODEL_ID}:tflite",
    }


@app.get("/health")
def standalone_health(request: Request):
    return model_health(request.app.state)


@router.get("/health/ml")
def health(request: Request):
    return model_health(request.app.state)


@router.post("/predict")
def predict(request: Request, file: UploadFile = File(...)):
    state = request.app.state
    if state.interpreter is None or state.model_error:
        raise HTTPException(
            status_code=503,
            detail=state.model_error or "Disease model is not loaded.",
        )

    filename = file.filename or ""
    extension = os.path.splitext(filename)[1].lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail="Unsupported image format. Upload a JPG, JPEG, PNG, or WebP image.",
        )

    payload = file.file.read(MAX_IMAGE_BYTES + 1)
    if not payload:
        raise HTTPException(status_code=400, detail="The uploaded image is empty.")
    if len(payload) > MAX_IMAGE_BYTES:
        raise HTTPException(
            status_code=413,
            detail="Image is too large. The maximum upload size is 10 MB.",
        )

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(payload)) as image:
                if image.format != EXTENSION_FORMATS[extension]:
                    raise HTTPException(
                        status_code=415,
                        detail="The image content does not match its file extension.",
                    )
                if image.width * image.height > MAX_IMAGE_PIXELS:
                    raise HTTPException(
                        status_code=413,
                        detail="Image dimensions are too large. Maximum is 20 megapixels.",
                    )
                image.verify()
            with Image.open(io.BytesIO(payload)) as image:
                leaf_image = image.convert("RGB")
    except HTTPException:
        raise
    except (
        UnidentifiedImageError,
        OSError,
        ValueError,
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
    ) as exc:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not a valid, readable image.",
        ) from exc

    try:
        with state.inference_lock:
            predictions = predict_image(leaf_image, state.interpreter, state.labels)
    except (RuntimeError, ValueError, OSError) as exc:
        raise HTTPException(status_code=500, detail=f"Disease model inference failed: {exc}") from exc

    top_predictions = [
        {
            "class_name": item["label"],
            "display_name": _display_name(item["label"]),
            "confidence": item["score"],
        }
        for item in predictions
    ]
    if not top_predictions:
        raise HTTPException(status_code=500, detail="Disease model returned no predictions.")

    return {
        "success": True,
        "prediction": top_predictions[0],
        "top_predictions": top_predictions,
        "model_used": f"{MODEL_ID}:tflite",
    }


app.include_router(router)