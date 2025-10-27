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


### Env variables for H200 SXM
- VLLM_MEMORY_UTIL=0.5  # adjust memory utilization as needed (about 48GB needed for VLLM with 16384 context length)
- VLLM_DEVICE=0
- IMAGE_DEVICE=0
- PERSISTENT_VOLUME_DIR=/workspace  # mount persistent volume here
- DOWNLOAD_MODELS=1
- PORT=8008
- PORT_HEALTH=8009

```bash
docker run --gpus all -d -p 8008:8008 \
    --platform linux/amd64 \
    -v /path/to/persistent/volume:/workspace \
    -e PORT=8008 \
    -e PORT_HEALTH=8009 \
    -e PERSISTENT_VOLUME_DIR=/workspace \
    -e DOWNLOAD_MODELS=1 \
    -e VLLM_MEMORY_UTIL=0.5 \
    -e VLLM_DEVICE=0 \
    -e IMAGE_DEVICE=0
    riverfog7/genedit-backend:latest
```

- single request throughput: 51 tok/s
