from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class TaskType(str, Enum):
    GENERATE = "generate"
    INPAINT = "inpaint"


class GenerateInput(BaseModel):
    prompt: str
    negative_prompt: str = ""
    width: int = 1664
    height: int = 928
    num_inference_steps: int = 50
    true_cfg_scale: float = 4.0
    seed: Optional[int] = None


class InpaintInput(BaseModel):
    prompt: str
    control_image: bytes
    control_mask: bytes
    negative_prompt: str = ""
    num_inference_steps: int = 30
    true_cfg_scale: float = 4.0
    controlnet_conditioning_scale: float = 1.0
    seed: Optional[int] = None


class GeneratorOutput(BaseModel):
    image: bytes


class GenerateRequest(BaseModel):
    prompt: str = Field(..., description="Text prompt for image generation")
    negative_prompt: str = Field("", description="Negative prompt")
    width: int = Field(1664, description="Image width", ge=512, le=2048)
    height: int = Field(928, description="Image height", ge=512, le=2048)
    num_inference_steps: int = Field(50, description="Number of denoising steps", ge=1, le=100)
    true_cfg_scale: float = Field(4.0, description="Classifier-free guidance scale", ge=1.0, le=20.0)
    seed: Optional[int] = Field(None, description="Random seed for reproducibility")


class InpaintRequest(BaseModel):
    prompt: str = Field(..., description="Text prompt for inpainting")
    negative_prompt: str = Field("", description="Negative prompt")
    num_inference_steps: int = Field(30, description="Number of denoising steps", ge=1, le=100)
    true_cfg_scale: float = Field(4.0, description="Classifier-free guidance scale", ge=1.0, le=20.0)
    controlnet_conditioning_scale: float = Field(1.0, description="ControlNet conditioning scale", ge=0.0, le=2.0)
    seed: Optional[int] = Field(None, description="Random seed for reproducibility")
