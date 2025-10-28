import json
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Response, HTTPException, Form
from pydantic import ValidationError

from ..internal.generation import QwenImageGenerator
from ..models.generation import GenerateInput, InpaintInput, GenerateRequest, InpaintRequest

generator: Optional[QwenImageGenerator] = None


@asynccontextmanager
async def lifespan(fastapi_router: APIRouter):
    global generator
    generator = QwenImageGenerator()
    yield
    generator.stop()
    generator = None


router = APIRouter(prefix="", tags=["image_generation"], lifespan=lifespan)


@router.post("/generate")
def generate_image(
    data: str = Form(..., description="JSON string with generation parameters"),
):
    if not generator:
        raise HTTPException(status_code=503, detail="Generator not initialized")

    try:
        data_dict = json.loads(data)
        request = GenerateRequest(**data_dict)

        input_data = GenerateInput(
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            width=request.width,
            height=request.height,
            num_inference_steps=request.num_inference_steps,
            true_cfg_scale=request.true_cfg_scale,
            seed=request.seed
        )

        result = generator.generate(input_data)

        return Response(
            content=result.image,
            media_type="image/png",
            headers={
                "Content-Disposition": "inline; filename=generated.png"
            }
        )

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON in 'data' field: {str(e)}")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=f"Validation error: {e.errors()}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@router.post("/inpaint")
def inpaint_image(
    control_image: UploadFile = File(..., description="Input image to inpaint"),
    control_mask: UploadFile = File(..., description="Mask image (white=inpaint, black=keep)"),
    data: str = Form(..., description="JSON string with inpainting parameters"),
):
    if not generator:
        raise HTTPException(status_code=503, detail="Generator not initialized")

    try:
        data_dict = json.loads(data)
        request = InpaintRequest(**data_dict)

        control_image_bytes = control_image.file.read()
        control_mask_bytes = control_mask.file.read()

        input_data = InpaintInput(
            prompt=request.prompt,
            control_image=control_image_bytes,
            control_mask=control_mask_bytes,
            negative_prompt=request.negative_prompt,
            num_inference_steps=request.num_inference_steps,
            true_cfg_scale=request.true_cfg_scale,
            controlnet_conditioning_scale=request.controlnet_conditioning_scale,
            seed=request.seed
        )

        result = generator.inpaint(input_data)

        return Response(
            content=result.image,
            media_type="image/png",
            headers={
                "Content-Disposition": "inline; filename=inpainted.png"
            }
        )

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON in 'data' field: {str(e)}")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=f"Validation error: {e.errors()}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inpainting failed: {str(e)}")


@router.get("/health")
def health_check():
    return {
        "status": "healthy" if generator else "not initialized",
        "device": generator.device if generator else None,
        "dtype": str(generator.torch_dtype) if generator else None
    }
