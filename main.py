from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import zipfile
from typing import List
from starlette.requests import Request

app = FastAPI()

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up templates
templates = Jinja2Templates(directory="templates")

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploaded_images", StaticFiles(directory="uploaded_images"), name="uploaded_images")

# Directory to save uploaded images
UPLOAD_DIR = "uploaded_images"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    files = os.listdir(UPLOAD_DIR)
    images = [file for file in files if file.lower().endswith(('png', 'jpg', 'jpeg', 'gif'))]
    return templates.TemplateResponse("index.html", {"request": request, "images": images})

@app.post("/upload/")
async def upload_image(files: List[UploadFile] = File(...)):
    for file in files:
        if not (file.filename.lower().endswith(('png', 'jpg', 'jpeg', 'gif', 'zip'))):
            raise HTTPException(status_code=400, detail="Invalid file type. Only images and ZIP files are allowed.")
        if file.filename.lower().endswith('.zip'):
            zip_path = f"{UPLOAD_DIR}/{file.filename}"
            with open(zip_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(UPLOAD_DIR)
            os.remove(zip_path)
        else:
            file_location = f"{UPLOAD_DIR}/{file.filename}"
            with open(file_location, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
    return templates.TemplateResponse("upload_complete.html", {"request": {}})

@app.post("/delete_all/")
async def delete_all_images():
    for filename in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error: {e}")
    return {"detail": "All images deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
