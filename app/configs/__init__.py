import os
from pathlib import Path

import torch
from pydantic import BaseModel


class Config(BaseModel):
    device: str = "mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu"
    hf_home: Path = Path(os.getenv("PERSISTENT_VOLUME_DIR")) / "models"
    sam2_model_id: str = os.getenv("SAM2_MODEL_ID")
    gdino_model_id: str = os.getenv("GDINO_MODEL_ID")
    diffusion_model_id: str = os.getenv("DIFFUSION_MODEL_ID")
    diffusion_controlnet_model_id: str = os.getenv("DIFFUSION_CONTROLNET_MODEL_ID")
    diffusion_orig_model_id: str = os.getenv("DIFFUSION_ORIG_MODEL_ID")

config = Config()
