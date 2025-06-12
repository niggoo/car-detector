# README.m

## Project structure

There are 3 main folders in this project
* `car-detector-backend` houses the backend software implementation - A fastAPI python backend implementation
* `car-detector-frontend` houses the frontend implementation, it's a regular Angular app
* `machine-learning` contains all the code we used for training the model and to extract the similarity latent vectors for similarity comparison

## Setup
In order to run the project locally, follow these instructions closely:

Expected pre-requisistes:
* `conda` This project expects you have conda setup locally. For information on how to setup `conda` we refer to their setup guide https://www.anaconda.com/docs/getting-started/miniconda/install
* `NodeJS@22.14` We expect you have nodejs installed locally. https://nodejs.org/en/download

### Model and data download
```bash
wget https://files.auroria.io/car-detector/cars.zip
unzip cars.zip -d car-detector-backend/static/
rm cars.zip

wget https://files.auroria.io/car-detector/car_ID_b1.pt -P car-detector-backend/ml/
wget https://files.auroria.io/car-detector/fingerprint_database.pkl -P car-detector-backend/ml/
```

This will download the `cars.zip`, unzips the archive and moves them into the correct place to be accessible for the backend.  
Then it downloads the model `car_ID_b1.pt` into the correct path.  
Then it downloads the latent vector database matching the images of the cars `fingerprint_database.pkl`

### Backend services

```bash
cd car-detector-backend
conda env create -f environment.yml --name "car-detector"
conda activate car-detector
fastapi dev app.py
```

This will create the environment for the car-detector, activate it and boot up the fastapi backend server on `localhost:8000`

### Frontend services

```bash
cd car-detector-frontend
npm i
ng serve   
```

This will boot up a dev server that serves the angular app on `localhost:4200`

## How to use
Open up a browser and navigate to `http://localhost:4200`. Upload new images, have the model serve up similar images. Register, Login, Logout.  
Browse the catalogue of existing cars, and find similar cars to those.  
When logged in, the uploaded images are stored and can be reviewed again in the Profile section (`http://localhost:4200/profile`), one can click on them and re-check the previous similarity result.
