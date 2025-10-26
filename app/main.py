import os

from fastapi import FastAPI

from .routers import segmentation_router, object_detection_router

app = FastAPI(root_path=os.getenv("IMAGE_ROOT_PATH") or "")
app.include_router(segmentation_router, prefix="/segment", tags=["segmentation"])
app.include_router(object_detection_router, prefix="/detect", tags=["object_detection"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}
