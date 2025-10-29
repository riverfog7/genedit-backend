import io
import json
import zipfile
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Response
from fastapi import HTTPException, Form
from pydantic import ValidationError

from ..internal.segmentation import Sam2Segmenter, SegmenterInput
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


def create_mask_zip(masks: list, scores: list, shape: tuple) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        for i, mask_bytes in enumerate(masks):
            zf.writestr(f'{i}.png', mask_bytes)

        metadata = {
            "scores": scores,
            "shape": list(shape)
        }
        zf.writestr('metadata.json', json.dumps(metadata))

    buf.seek(0)
    return buf.getvalue()


@router.post("/point")
def segment_with_points(
        image: UploadFile = File(..., description="Image file to segment"),
        data: str = Form(..., description="JSON string with points and labels"),
):
    if not segmenter:
        raise HTTPException(status_code=503, detail="Segmenter not initialized")

    try:
        data_dict = json.loads(data)
        request = PointSegmentRequest(**data_dict)

        image_bytes = image.file.read()

        input_data = SegmenterInput(
            image=image_bytes,
            points=request.points,
            labels=request.labels
        )

        result = segmenter.segment(input_data)

        zip_bytes = create_mask_zip(result.masks, result.scores, result.shape)

        return Response(
            content=zip_bytes,
            media_type="application/zip",
            headers={
                "Content-Disposition": "attachment; filename=masks.zip"
            }
        )

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON in 'data' field: {str(e)}")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=f"Validation error: {e.errors()}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Segmentation failed: {str(e)}")


@router.post("/box")
def segment_with_box(
        image: UploadFile = File(..., description="Image file to segment"),
        data: str = Form(..., description="JSON string with box coordinates"),
):
    if not segmenter:
        raise HTTPException(status_code=503, detail="Segmenter not initialized")

    try:
        data_dict = json.loads(data)
        request = BoxSegmentRequest(**data_dict)

        image_bytes = image.file.read()

        input_data = SegmenterInput(
            image=image_bytes,
            boxes=request.box
        )

        result = segmenter.segment(input_data)

        zip_bytes = create_mask_zip(result.masks, result.scores, result.shape)

        return Response(
            content=zip_bytes,
            media_type="application/zip",
            headers={
                "Content-Disposition": "attachment; filename=masks.zip"
            }
        )

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON in 'data' field: {str(e)}")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=f"Validation error: {e.errors()}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Segmentation failed: {str(e)}")


@router.post("/combined")
def segment_combined(
        image: UploadFile = File(..., description="Image file to segment"),
        data: str = Form(..., description="JSON string with points, labels, and/or box"),
):
    if not segmenter:
        raise HTTPException(status_code=503, detail="Segmenter not initialized")

    try:
        data_dict = json.loads(data)
        request = CombinedSegmentRequest(**data_dict)

        if not request.points and not request.box:
            raise HTTPException(
                status_code=400,
                detail="Must provide either points+labels or box"
            )

        if request.points and not request.labels:
            raise HTTPException(status_code=400, detail="Points require labels")

        image_bytes = image.file.read()

        input_data = SegmenterInput(
            image=image_bytes,
            points=request.points,
            labels=request.labels,
            boxes=request.box
        )

        result = segmenter.segment(input_data)

        zip_bytes = create_mask_zip(result.masks, result.scores, result.shape)

        return Response(
            content=zip_bytes,
            media_type="application/zip",
            headers={
                "Content-Disposition": "attachment; filename=masks.zip"
            }
        )

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON in 'data' field: {str(e)}")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=f"Validation error: {e.errors()}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Segmentation failed: {str(e)}")


@router.get("/health")
def health_check():
    return {
        "status": "healthy" if segmenter else "not initialized",
        "device": segmenter.device if segmenter else None,
        "model": segmenter.model_id if segmenter else None,
        "memory_footprint": segmenter.get_memory_footprint() if segmenter else None,
    }
