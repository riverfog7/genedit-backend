## Models
### Open vocabulary object detection
openmmlab-community/mm_grounding_dino_large_all

### Object segmentation
facebook/sam2.1-hiera-large

### SLM
unsloth/gemma-3n-E2B-it

### Image Inpainting (Adapter weights only)
InstantX/Qwen-Image-ControlNet-Inpainting

### Image Generation
Qwen/Qwen-Image

## Container Environment Vars
### Required
- PORT: Port for the web server
- PERSISTENT_VOLUME_DIR: Directory for persistent storage

### Optional
- DOWNLOAD_MODELS: If set to 1 and there is no model in the persistent volume, download models to the persistent volume (Defaults to 0)
