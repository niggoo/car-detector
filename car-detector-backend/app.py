from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from PIL import Image
from fastapi.middleware.cors import CORSMiddleware

import io
import hashlib
import random
import string
import os
import json

app = FastAPI()

origins = ["*"]

# Add CORS middleware to the application
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of allowed origins, or ["*"] to allow all
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Mock database
fake_db = {
    "users": []
}


def generate_random_hash() -> str:
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    hash_object = hashlib.sha256(random_string.encode())
    return hash_object.hexdigest()


class User(BaseModel):
    username: str
    password: str


@app.post("/signup/")
async def signup(user: User):
    for existing_user in fake_db["users"]:
        if existing_user["username"] == user.username:
            raise HTTPException(status_code=400, detail="Username already registered")

    user_id = generate_random_hash()
    fake_db["users"].append({"user_id": user_id, "username": user.username, "password": user.password})

    return JSONResponse(content={"message": "User registered successfully", "user_id": user_id})


@app.post("/login/")
async def login(user: User):
    for existing_user in fake_db["users"]:
        if existing_user["username"] == user.username and existing_user["password"] == user.password:
            return JSONResponse(content={"message": "Login successful", "user_id": existing_user["user_id"]})

    raise HTTPException(status_code=400, detail="Invalid credentials")


@app.post("/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    temp_folder = "static/temp"

    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        file_path = os.path.join(temp_folder, file.filename)
        image.save(file_path)

        # TODO: Replace with AI Logic!!!
        return JSONResponse(content={
            "url": file_path,
            "model": "Dodge Charger",
            "make": "Dodge",
            "alternatives": [
                {
                    "url": "static/cars/00029.jpg",
                    "model": "Spyker",
                    "make": "Spyker C8"
                },
                {
                    "url": "static/cars/00036.jpg",
                    "model": "Ferrari 458 Italia",
                    "make": "Ferrari"
                },
                {
                    "url": "static/cars/00044.jpg",
                    "model": "BMW Z4",
                    "make": "BMW"
                },
                {
                    "url": "static/cars/00046.jpg",
                    "model": "Audi TT RS",
                    "make": "Audi"
                },
                {
                    "url": "static/cars/00070.jpg",
                    "model": "BMW 3 Series",
                    "make": "BMW"
                },
            ]
        })
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)


@app.get("/cars/")
async def get_cars(page: int = Query(1, gt=0), page_size: int = Query(10, gt=0)):
    cars_folder = "static/cars"  # Assuming the folder name is 'cars'
    cars_list = []

    # Check if the folder exists
    if not os.path.exists(cars_folder):
        return JSONResponse(content={"error": "Cars folder not found"}, status_code=404)

    # Get a sorted list of JSON files in the folder
    json_files = sorted(
        (filename for filename in os.listdir(cars_folder) if filename.endswith(".json"))
    )

    # Calculate the start and end indices for pagination
    start_index = (page - 1) * page_size
    end_index = start_index + page_size

    # Apply pagination to the sorted list of JSON files
    paginated_files = json_files[start_index:end_index]

    # Iterate over the paginated list of JSON files
    for filename in paginated_files:
        file_path = os.path.join(cars_folder, filename)
        with open(file_path, "r") as file:
            car_data = json.load(file)

            image_url = f"{cars_folder}/{os.path.splitext(filename)[0]}.png"
            cars_list.append({
                "url": image_url,
                "model": car_data.get("model"),
                "make": car_data.get("make")
            })

    # Return the paginated list of cars
    return JSONResponse(content={
        "page": page,
        "page_size": page_size,
        "total_items": len(json_files),
        "cars": cars_list
    })

# Mount the static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")
