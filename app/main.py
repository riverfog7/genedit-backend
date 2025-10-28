import os

from fastapi import FastAPI

from .routers import segmentation_router, object_detection_router, generation_router

app = FastAPI(root_path=os.getenv("IMAGE_ROOT_PATH") or "")
app.include_router(segmentation_router, prefix="/segment", tags=["segmentation"])
app.include_router(object_detection_router, prefix="/detect", tags=["object_detection"])
app.include_router(generation_router, prefix="/generate", tags=["image_generation"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}
