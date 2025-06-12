import numpy as np
import pandas as pd
import torch
from torch import nn


def get_fingerprint(image, model):
    avg_pool = nn.AdaptiveAvgPool2d(1)
    with torch.no_grad():
        latent_vector = model.features(image)
        latent_vector = avg_pool(latent_vector)
        latent_vector = torch.flatten(latent_vector, 1)

    return latent_vector.cpu().numpy()


def predict(input_image: torch.Tensor, model: nn.Module, fingerprint_database: pd.DataFrame, k: int = 3):
    similarities = []

    logits = model(input_image)
    pred = torch.argmax(logits, dim=1)

    input_latent = get_fingerprint(input_image, model)

    for index, row in fingerprint_database.iterrows():
        if row["class"] != int(pred):
            cosine_sim = np.dot(input_latent, row["Latent"]) / (
                np.linalg.norm(input_latent) * np.linalg.norm(row["Latent"])
            )
            similarities.append((cosine_sim.item(), str(row["file"]), int(row["class"]), index + 1))

    return sorted(similarities, key=lambda x: x[0], reverse=True)[:k], pred.item()
