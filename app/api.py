"""
API endpoints for the PPT Generator application.
"""
from fastapi import FastAPI, Request, Form, HTTPException, File, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List, Optional
import tempfile
import os
from pathlib import Path
import logging
import traceback
import shutil
import time
import asyncio
import base64

from app.services.screenshot_service import ScreenshotService
from app.services.pptx_service import PowerPointService
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="PPT Generator")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Initialize services
screenshot_service = ScreenshotService()
ppt_service = PowerPointService()

class UrlData(BaseModel):
    url: str
    croppedImage: Optional[str] = None

class GenerateRequest(BaseModel):
    urls: List[UrlData]

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Render the main page."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/preview")
async def preview_url(url: str):
    """Generate a preview image for a URL."""
    try:
        # Create a temporary file for the screenshot
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            await screenshot_service.take_screenshot(url, temp_file.name)
            return FileResponse(temp_file.name, media_type="image/png")
    except Exception as e:
        logger.error(f"Error generating preview: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate")
async def generate_presentation(urls: List[str] = Form(...), cropped_images: List[UploadFile] = File(None)):
    """Generate a PowerPoint presentation from URLs and optional cropped images."""
    if not urls:
        raise HTTPException(status_code=400, detail="No URLs provided")
    
    if len(urls) > 20:
        raise HTTPException(status_code=400, detail="Maximum 20 URLs allowed")
    
    # Create a temporary directory for screenshots and presentation
    temp_dir = tempfile.mkdtemp()
    screenshots = []
    pptx_path = None
    
    try:
        # Process each URL and its corresponding cropped image (if any)
        for i, url in enumerate(urls):
            if cropped_images and i < len(cropped_images) and cropped_images[i]:
                # Use the cropped image if provided
                screenshot_path = os.path.join(temp_dir, f"screenshot_{i}.png")
                with open(screenshot_path, "wb") as f:
                    content = await cropped_images[i].read()
                    f.write(content)
                screenshots.append(screenshot_path)
            else:
                # Take a new screenshot if no cropped image
                screenshot_path = os.path.join(temp_dir, f"screenshot_{i}.png")
                await screenshot_service.take_screenshot(url, screenshot_path)
                screenshots.append(screenshot_path)

        # Generate PowerPoint presentation
        pptx_path = os.path.join(temp_dir, "presentation.pptx")
        ppt_service.create_presentation(screenshots, pptx_path)

        # Create a copy in a persistent location
        persistent_dir = Path("temp/presentations")
        persistent_dir.mkdir(parents=True, exist_ok=True)
        persistent_path = persistent_dir / f"presentation_{int(time.time())}.pptx"
        shutil.copy2(pptx_path, persistent_path)

        # Return the persistent file instead of the temporary one
        return FileResponse(
            str(persistent_path),
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            filename="presentation.pptx"
        )

    except Exception as e:
        logger.error(f"Error generating presentation: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Failed to generate presentation")
    finally:
        # Clean up temporary files
        try:
            for screenshot in screenshots:
                if os.path.exists(screenshot):
                    os.remove(screenshot)
            if pptx_path and os.path.exists(pptx_path):
                os.remove(pptx_path)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)
        except Exception as e:
            logger.error(f"Error cleaning up temporary files: {str(e)}")
        
        # Clean up old presentations (keep only the last 10)
        try:
            if Path("temp/presentations").exists():
                presentations = sorted(Path("temp/presentations").glob("presentation_*.pptx"))
                if len(presentations) > 10:
                    for old_file in presentations[:-10]:
                        old_file.unlink()
                        logger.info(f"Cleaned up old presentation: {old_file}")
        except Exception as e:
            logger.error(f"Error cleaning up old presentations: {str(e)}") 