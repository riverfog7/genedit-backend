import io
import json
import zipfile
from typing import List, Optional

from PIL import Image
from pydantic import BaseModel


class PointSegmentRequest(BaseModel):
    points: List[List[int]]
    labels: List[int]


class BoxSegmentRequest(BaseModel):
    box: List[int]


class CombinedSegmentRequest(BaseModel):
    points: Optional[List[List[int]]] = None
    labels: Optional[List[int]] = None
    box: Optional[List[int]] = None


class DetectRequest(BaseModel):
    text: List[str]
    threshold: float = 0.25


class DetectionResult(BaseModel):
    boxes: List[List[float]]
    scores: List[float]
    labels: List[str]


class DetectorOutput(BaseModel):
    detections: List[DetectionResult]


class SegmentationResult:
    def __init__(self, zip_bytes: bytes):
        self.zip_bytes = zip_bytes
        self._masks = None
        self._metadata = None

    def extract_masks(self) -> List[Image.Image]:
        if self._masks is None:
            self._masks = []
            with zipfile.ZipFile(io.BytesIO(self.zip_bytes)) as zf:
                for name in sorted(zf.namelist()):
                    if name.endswith('.png'):
                        self._masks.append(Image.open(io.BytesIO(zf.read(name))))
        return self._masks

    def get_metadata(self) -> dict:
        if self._metadata is None:
            with zipfile.ZipFile(io.BytesIO(self.zip_bytes)) as zf:
                self._metadata = json.loads(zf.read('metadata.json'))
        return self._metadata
