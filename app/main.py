from fastapi import FastAPI
from .routers.segmentation import router as segmentation_router

app = FastAPI()
app.include_router(segmentation_router, prefix="/segment", tags=["segmentation"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}
