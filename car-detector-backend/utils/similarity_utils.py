

def get_car_information(predicted_class, car_informations):
    return next(
            (car for car in car_informations if car["class"] == predicted_class),
            {"make": "Unknown", "model": "Unknown"}
        )