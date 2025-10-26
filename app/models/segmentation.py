from typing import List, Optional
from typing import Tuple

from pydantic import BaseModel, Field


class SegmenterInput(BaseModel):
    image: bytes
    points: Optional[List[List[int]]] = None
    labels: Optional[List[int]] = None
    boxes: Optional[List[int]] = None


class SegmenterOutput(BaseModel):
    masks: List[bytes]
    scores: List[float]
    shape: Tuple


class PointSegmentRequest(BaseModel):
    """Request schema for point-based segmentation."""
    points: List[List[int]] = Field(
        ...,
        description="List of point coordinates [[x, y], [x2, y2]]",
        examples=[[[500, 375], [600, 400]]]
    )
    labels: List[int] = Field(
        ...,
        description="Labels for each point (1=positive click, 0=negative click)",
        examples=[[1, 1]]
    )


class BoxSegmentRequest(BaseModel):
    """Request schema for box-based segmentation."""
    box: List[int] = Field(
        ...,
        description="Bounding box coordinates [x_min, y_min, x_max, y_max]",
        examples=[[100, 100, 500, 500]],
        min_length=4,
        max_length=4
    )


class CombinedSegmentRequest(BaseModel):
    """Request schema for combined point and box segmentation."""
    points: Optional[List[List[int]]] = Field(
        None,
        description="List of point coordinates",
        examples=[[[500, 375]]]
    )
    labels: Optional[List[int]] = Field(
        None,
        description="Labels for each point",
        examples=[[1]]
    )
    box: Optional[List[int]] = Field(
        None,
        description="Bounding box coordinates [x_min, y_min, x_max, y_max]",
        examples=[[100, 100, 500, 500]],
        min_length=4,
        max_length=4
    )
