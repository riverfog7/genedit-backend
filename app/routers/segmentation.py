from contextlib import asynccontextmanager
from typing import Optional, Annotated

from fastapi import APIRouter, UploadFile, File
from fastapi import HTTPException, Form

from ..internal.segmentation import Sam2Segmenter, SegmenterInput, SegmenterOutput
from ..models.segmentation import PointSegmentRequest, BoxSegmentRequest, CombinedSegmentRequest

segmenter: Optional[Sam2Segmenter] = None

@asynccontextmanager
async def lifespan(fastapi_router: APIRouter):
    global segmenter
    segmenter = Sam2Segmenter()
    yield
    segmenter.stop()
    segmenter = None

router = APIRouter(prefix="", tags=["segmentation"], lifespan=lifespan)

@router.post("/point", response_model=SegmenterOutput)
def segment_with_points(
        image: UploadFile = File(..., description="Image file to segment"),
        request: Annotated[PointSegmentRequest, Form()] = None,
):
    """
    Segment objects using point clicks.

    Provide an image and a list of point coordinates with labels.
    - Label 1 = positive click (include this in mask)
    - Label 0 = negative click (exclude this from mask)
    """
    if not segmenter:
        raise HTTPException(status_code=503, detail="Segmenter not initialized")

    try:
        image_bytes = image.file.read()

        input_data = SegmenterInput(
            image=image_bytes,
            points=request.points,
            labels=request.labels
        )

        result = segmenter.segment(input_data)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Segmentation failed: {str(e)}")


@router.post("/box", response_model=SegmenterOutput)
def segment_with_box(
        image: UploadFile = File(..., description="Image file to segment"),
        request: Annotated[BoxSegmentRequest, Form()] = None,
):
    """
    Segment objects using a bounding box.

    Provide an image and bounding box coordinates [x_min, y_min, x_max, y_max].
    """
    if not segmenter:
        raise HTTPException(status_code=503, detail="Segmenter not initialized")

    try:
        image_bytes = image.file.read()

        input_data = SegmenterInput(
            image=image_bytes,
            boxes=request.box
        )

        result = segmenter.segment(input_data)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Segmentation failed: {str(e)}")

@router.post("/combined", response_model=SegmenterOutput)
def segment_combined(
        image: UploadFile = File(..., description="Image file to segment"),
        request: Annotated[CombinedSegmentRequest, Form()] = None,
):
    """
    Segment with combination of prompts (points and/or box).

    You can provide:
    - Just points + labels
    - Just box
    - Both points and box for refinement
    """
    if not segmenter:
        raise HTTPException(status_code=503, detail="Segmenter not initialized")

    if not request.points and not request.box:
        raise HTTPException(
            status_code=400,
            detail="Must provide either points+labels or box"
        )

    if request.points and not request.labels:
        raise HTTPException(status_code=400, detail="Points require labels")

    try:
        image_bytes = image.file.read()

        input_data = SegmenterInput(
            image=image_bytes,
            points=request.points,
            labels=request.labels,
            boxes=request.box
        )

        result = segmenter.segment(input_data)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Segmentation failed: {str(e)}")


@router.get("/health")
def health_check():
    """Check if the segmenter is ready."""
    return {
        "status": "healthy" if segmenter else "not initialized",
        "device": segmenter.device if segmenter else None,
        "model": segmenter.model_id if segmenter else None
    }
