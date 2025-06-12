import torch
from fastapi import FastAPI, File, UploadFile, HTTPException, Query, Header
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from PIL import Image
from fastapi.middleware.cors import CORSMiddleware
from ml.ml_model import model
from ml.ml_transforms import transform
from ml.classes import car_informations
from ml.similarity_matching import predict
from utils.user_utils import User, generate_random_hash
from utils.similarity_utils import get_car_information
from ml.fingerprint_db import fingerprint_database
import io
import hashlib
import random
import string
import os
import json
from passlib.hash import bcrypt


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


temp_folder = "static/temp"
cars_folder = "static/cars"

# Mock database
fake_db = {
    "users": []
}

@app.post("/signup/")
async def signup(user: User):
    for existing_user in fake_db["users"]:
        if existing_user["username"] == user.username:
            raise HTTPException(status_code=400, detail="Username already registered")

    user_id = generate_random_hash()
    hashed_password = hash_password(user.password)

    fake_db["users"].append({
        "user_id": user_id,
        "username": user.username,
        "password": hashed_password,  # Store hashed password
        "images": []
    })

    return JSONResponse(content={"user_id": user_id})

def hash_password(password: str) -> str:
    return bcrypt.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.verify(plain_password, hashed_password)

@app.post("/login/")
async def login(user: User):
    for existing_user in fake_db["users"]:
        if existing_user["username"] == user.username and verify_password(user.password, existing_user["password"]):
            return JSONResponse(content={"user_id": existing_user["user_id"]})

    raise HTTPException(status_code=400, detail="Invalid credentials")


def find_user(user_id):
    for existing_user in fake_db["users"]:
        if existing_user["user_id"] == user_id:
            return existing_user

    return None

def get_user_id_from_authorization(auth_string):
    if auth_string is not None:
        return auth_string.split(" ")[1]
    return None

@app.post("/upload-image/")
async def upload_image(file: UploadFile = File(...), authorization: str = Header(None)):
    print(fake_db)
    user = find_user(get_user_id_from_authorization(authorization))

    contents = await file.read()
    image = Image.open(io.BytesIO(contents))

    file_path = os.path.join(temp_folder, file.filename)
    image.save(file_path)

    if user is not None:
        user["images"].append(file_path)
    print(fake_db)

    predicted_car, alternatives = find_similar_cars(image)

    return JSONResponse(content={
        "url": file_path,
        "model": predicted_car["model"],
        "make": predicted_car["make"],
        "alternatives": alternatives
    })

@app.get("/find-similar/")
async def find_similar(car_id: int = Query(None), car_path: str = Query(None)):
    if car_id is None and car_path is None:
        raise HTTPException(status_code=400, detail="Either car_id or car_path must be provided")
    if car_id is not None and car_path is not None:
        raise HTTPException(status_code=400, detail="Only one of car_id or car_path should be provided")

    if car_id is not None:
        file_path = f"{cars_folder}/{car_id:05d}.jpg"
    else:
        filename = os.path.basename(car_path)
        if not filename:
            raise HTTPException(status_code=400, detail="Invalid car_path: no filename found")
        file_path = f"{temp_folder}/{filename}"

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image file not found")

    image = Image.open(file_path)
    predicted_car, alternatives = find_similar_cars(image)

    return JSONResponse(content={
        "url": file_path,
        "model": predicted_car["model"],
        "make": predicted_car["make"],
        "alternatives": alternatives
    })

def find_similar_cars(image):
    image_tensor = transform(image).unsqueeze(0)
    similarities, predicted_class = predict(image_tensor, model, fingerprint_database, 8)

    predicted_car = get_car_information(predicted_class, car_informations)

    alternatives = []

    for sim in similarities:
        car_info = get_car_information(sim[2], car_informations)
        alternatives.append({
            "id": sim[3],
            "url": f"{cars_folder}/{sim[1]}",
            "make": car_info["make"],
            "model": car_info["model"]
        })
    return predicted_car, alternatives


@app.get("/cars/")
async def get_cars(page: int = Query(1, gt=0), page_size: int = Query(8, gt=0)):
    cars_list = []

    # Calculate the start and end indices for pagination
    start_index = (page - 1) * page_size
    end_index = start_index + page_size

    # Iterate over the paginated slice of the fingerprint database
    for index, row in fingerprint_database.iloc[start_index:end_index].iterrows():
        car_info = get_car_information(row["class"], car_informations)

        # Construct the image URL
        image_url = f"{cars_folder}/{row['file']}"

        cars_list.append({
            "id": index + 1,
            "url": image_url,
            "model": car_info["model"],
            "make": car_info["make"]
        })

    # Return the paginated list of cars
    return JSONResponse(content={
        "page": page,
        "page_size": page_size,
        "total_items": len(fingerprint_database),
        "cars": cars_list
    })


@app.get("/profile/")
async def profile(authorization: str = Header(None)):
    print(fake_db)
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = find_user(get_user_id_from_authorization(authorization))

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    images = user.get("images", [])

    return JSONResponse(content={
        "username": user["username"],
        "images": images
    })
