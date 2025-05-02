from datasets import load_dataset
import os
import json
from tqdm import tqdm


# Load the dataset in a tabular format with image URLs and metadata
dataset = load_dataset("tanganke/stanford_cars")

# Access the training set directly
train_set = dataset["train"]

# Define the directory to save images and JSON files
output_dir = "static/cars"
os.makedirs(output_dir, exist_ok=True)

# List of known car makes
car_makes = [
    "AM General", "Acura", "Spyker", "Lincoln", "HUMMER", "smart", "Ram", "GMC", "MINI Cooper", "BUICK", "Buick",
    "FIAT", "Plymouth", "Scion xD", "Eagle", "Geo", "Isuzu",
    "Abarth", "Alfa Romeo", "Aston Martin", "Audi", "Bentley", "BMW", "Bugatti",
    "Cadillac", "Chevrolet", "Chrysler", "Citroën", "Dacia", "Daewoo", "Daihatsu",
    "Dodge", "Donkervoort", "DS", "Ferrari", "Fiat", "Fisker", "Ford", "Honda",
    "Hummer", "Hyundai", "Infiniti", "Iveco", "Jaguar", "Jeep", "Kia", "KTM",
    "Lada", "Lamborghini", "Lancia", "Land Rover", "Landwind", "Lexus", "Lotus",
    "Maserati", "Maybach", "Mazda", "McLaren", "Mercedes-Benz", "MG", "Mini",
    "Mitsubishi", "Morgan", "Nissan", "Opel", "Peugeot", "Porsche", "Renault",
    "Rolls-Royce", "Rover", "Saab", "Seat", "Skoda", "Smart", "SsangYong",
    "Subaru", "Suzuki", "Tesla", "Toyota", "Volkswagen", "Volvo"
]


for i in tqdm(range(len(train_set))):
    class_index = train_set[i]["label"]
    class_name = train_set.features["label"].int2str(class_index)
    make = next((make for make in car_makes if class_name.startswith(make)), None)
    if not make:
        raise ValueError(f"Missing make for {class_name}")

for i in tqdm(range(1000)):
    image_data = train_set[i]["image"]
    class_index = train_set[i]["label"]

    class_name = train_set.features["label"].int2str(class_index)

    make = next((make for make in car_makes if class_name.startswith(make)), None)
    if make:
        model = class_name[len(make):].strip()
    else:
        raise ValueError(f"Missing make for {class_name}")

    image_path = os.path.join(output_dir, f"{i}.png")
    image_data.save(image_path, "PNG")

    json_path = os.path.join(output_dir, f"{i}.json")
    with open(json_path, "w") as json_file:
        json.dump({"make": make, "model": model}, json_file)

    print(f"Saved {image_path} and {json_path} with make: {make}, model: {model}")