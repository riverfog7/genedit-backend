from typing import List

from pydantic import BaseModel, Field


class DetectorInput(BaseModel):
    image: bytes
    text: List[str]
    threshold: float = 0.2


class DetectionResult(BaseModel):
    boxes: List[List[float]]
    scores: List[float]
    labels: List[str]


class DetectorOutput(BaseModel):
    detections: List[DetectionResult]


class DetectRequest(BaseModel):
    text: List[str] = Field(..., description="List of text prompts (e.g., ['a cat', 'a dog'])")
    threshold: float = Field(0.2, description="Detection confidence threshold", ge=0.0, le=1.0)
