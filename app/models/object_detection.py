from typing import List

from pydantic import BaseModel, Field


class DetectorInput(BaseModel):
    image: bytes
    text: str
    box_threshold: float = 0.4
    text_threshold: float = 0.3


class DetectionResult(BaseModel):
    boxes: List[List[float]]
    scores: List[float]
    labels: List[str]


class DetectorOutput(BaseModel):
    detections: List[DetectionResult]


class DetectRequest(BaseModel):
    text: str = Field(..., description="Text prompts separated by dots (e.g., 'a cat. a dog.')")
    box_threshold: float = Field(0.4, description="Box confidence threshold", ge=0.0, le=1.0)
    text_threshold: float = Field(0.3, description="Text confidence threshold", ge=0.0, le=1.0)
