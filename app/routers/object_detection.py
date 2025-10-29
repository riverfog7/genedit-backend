import json
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from pydantic import ValidationError

from ..internal.object_detection import GDinoDetector, DetectorInput, DetectorOutput
from ..models.object_detection import DetectRequest

detector: Optional[GDinoDetector] = None


@asynccontextmanager
async def lifespan(fastapi_router: APIRouter):
    global detector
    detector = GDinoDetector()
    yield
    detector.stop()
    detector = None


router = APIRouter(prefix="", tags=["object_detection"], lifespan=lifespan)


@router.post("", response_model=DetectorOutput)
def detect_objects(
        image: UploadFile = File(..., description="Image file to detect objects"),
        data: str = Form(..., description="JSON string with text prompts and thresholds"),
):
    if not detector:
        raise HTTPException(status_code=503, detail="Detector not initialized")

    try:
        data_dict = json.loads(data)
        request = DetectRequest(**data_dict)

        image_bytes = image.file.read()

        input_data = DetectorInput(
            image=image_bytes,
            text=request.text,
            threshold=request.threshold,
        )

        result = detector.detect(input_data)
        return result

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON in 'data' field: {str(e)}")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=f"Validation error: {e.errors()}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")


@router.get("/health")
def health_check():
    return {
        "status": "healthy" if detector else "not initialized",
        "device": detector.device if detector else None,
        "model": detector.model_id if detector else None,
        "memory_footprint": detector.get_memory_footprint() if detector else None,
    }
