import torch
import torchvision
from torch import nn
from torch.utils.data import DataLoader, Dataset
import scipy.io as sio
import pandas as pd
from torchvision import transforms
from PIL import Image
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
## -------------------------
## -------Load Model--------
## -------------------------

#Define model and load weights
class CarIdentifier(nn.Module):
    
    def __init__(self, num_classes: int = 196):
        super(CarIdentifier, self).__init__()

        self.global_avg_pool = nn.AdaptiveAvgPool2d(1)
        self.classifier = nn.Linear(1280,num_classes)
        
        enb3= torchvision.models.efficientnet_b1()
        self.features = enb3.features
        
    def forward(self, x):
        x = self.features(x)
        x = self.global_avg_pool(x)
        x = torch.flatten(x,1)
        x = self.classifier(x)
        
        return x
    
model = CarIdentifier()
model.load_state_dict(torch.load("car_ID_b1.pt", weights_only=True))
model.eval()

## -------------------------
## --------Dataset----------
## -------------------------

#load train labels and create dataframe
car_train = sio.loadmat("devkit/cars_train_annos.mat")
label_train = np.squeeze(car_train["annotations"])

train_labels_df = pd.DataFrame(columns=["class", "file"])
for i in range(len(label_train)):
    train_labels_df.loc[i, "class"] = label_train[i][4][0][0] 
    train_labels_df.loc[i,"file"]  = label_train[i][5][0]

#load test labels
car_test = sio.loadmat("devkit/cars_test_annos_withlabels.mat")
label_test = np.squeeze(car_test["annotations"])

test_labels_df = pd.DataFrame(columns=["class", "file"])
for i in range(len(label_test)):
    test_labels_df.loc[i, "class"] = label_test[i][4][0][0] 
    test_labels_df.loc[i,"file"]  = label_test[i][5][0]


#Set index to start from 0 to match python idexing
test_labels_df.set_index("file")
train_labels_df.set_index("file")

test_labels_df["class"] -= 1
train_labels_df["class"] -= 1

#create image dataset
class ImageDataset(Dataset):
    def __init__(self, image_path, labels_df, transform=None):
        self.image_path = image_path
        self.labels_df = labels_df
        self.transform = transform

    def __len__(self):
        return len(self.labels_df)

    def __getitem__(self, idx):
        image = Image.open(self.image_path + self.labels_df.loc[idx, "file"]).convert('RGB') 
        label = self.labels_df.loc[idx,'class'] 

        if self.transform:
            image = self.transform(image)

        return image, label

#transofrmations for train and test data
transform_train =  transforms.Compose([
        transforms.Resize((320,320)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(35),
        transforms.RandomAdjustSharpness(sharpness_factor=2, p=0.5),
        transforms.RandomGrayscale(p=0.5),
        transforms.RandomPerspective(distortion_scale=0.5, p=0.5),
        transforms.RandomPosterize(bits=2, p=0.5),
        transforms.ToTensor(),
        transforms.Normalize((0.485,0.456,0.406), (0.229,0.224,0.225))       
    ])

transform_test = transforms.Compose([
        transforms.Resize((320,320)),
        transforms.ToTensor(),
        transforms.Normalize((0.485,0.456,0.406), (0.229,0.224,0.225))       
    ])

#create dataloaders
test_images = ImageDataset("cars_test/", test_labels_df, transform_test)
train_images = ImageDataset("cars_train/", train_labels_df, transform_train)

train_dataloader = DataLoader(train_images, batch_size=64, shuffle=True)
test_dataloader = DataLoader(test_images, batch_size=64, shuffle=False)

## -------------------------
## ---Fingerprint Database--
## -------------------------

def get_fingerprint(image, model):
    avg_pool = nn.AdaptiveAvgPool2d(1)
    with torch.no_grad():
        latent_vector = model.features(image)
        latent_vector = avg_pool(latent_vector)
        latent_vector = torch.flatten(latent_vector,1)
    
    return latent_vector.cpu().numpy()

#latents = get_fingerprint(images, model)


fingerprint_images = ImageDataset("cars_train/", train_labels_df, transform_test)
fingerprint_dataloader = DataLoader(train_images, batch_size=64, shuffle=False)

def fingerprint_database(model : nn.Module, images: DataLoader, database : pd.DataFrame):
    database["Latent"] = ""
    model = model.to("cuda")
    for j, data in enumerate(tqdm(images)):
        x , _ = data
        
        latents = get_fingerprint(x.to("cuda"), model)
        
        for i in range(len(latents)):
            database.at[(j*64)+i, "Latent"] = latents[i]
    
    return database

fingerprint_data = fingerprint_database(model, fingerprint_dataloader, train_labels_df)

fingerprint_data.to_pickle("fingerprint_database.pkl")

## --------------------------
## ---Compute Similarities---
## --------------------------

#get cosine similarities
def cosine_similarity(input_image: torch.Tensor, model: nn.Module, fingerprint_database: pd.DataFrame, k: int = 3):
    similarities = []
    
    logits = model(input_image)
    pred = torch.argmax(logits, dim=1)

    input_latent = get_fingerprint(input_image, model)
    
    for index, row in fingerprint_database.iterrows():
        if row["class"] != int(pred):
            cosine_sim = np.dot(input_latent, row["Latent"]) / (
                np.linalg.norm(input_latent) * np.linalg.norm(row["Latent"])
            )
            similarities.append((cosine_sim, row["file"], row["class"]))
            
    return sorted(similarities, key=lambda x: x[0], reverse=True)[:k], pred
#logits = model(test_images[0][0].unsqueeze(dim=0).to("cuda"))

sims, pred = cosine_similarity(test_images[0][0].unsqueeze(dim=0).to("cuda"), model, fingerprint_data)

#display class name
classes = np.squeeze(sio.loadmat("devkit/cars_meta.mat")["class_names"])
def im_class(pred):
    car = classes[pred][0]
    return f"Car: {car}"

#display top results
def top_results(input_image: torch.Tensor, model: nn.Module, fingerprint_database: pd.DataFrame, k: int = 3):
    
    similars, pred_class = cosine_similarity(input_image.to("cuda").unsqueeze(dim=0), model, fingerprint_database, k)
    pred_class_name = im_class(pred_class.item())
    fig, axs = plt.subplots(1, k + 1, figsize=(20, 5))
    axs[0].imshow(input_image.permute(1,2,0))
    axs[0].axis("off")
    axs[0].set_title(f"Input Image\nPredicted: {pred_class_name}")
    
    for i, (similarity, im_path, im_cl) in enumerate(similarss):
        name = im_class(im_cl.item())
        proto_image = Image.open("cars_train/"+im_path).convert("RGB")
        axs[i + 1].imshow(proto_image)
        axs[i + 1].axis("off")
        axs[i + 1].set_title(f"Prototype {i + 1}\nClass: {name}\nSimilarity: {similarity}")

    plt.tight_layout()
    plt.show()


#input_im = test_images[1750][0]
#top_results(input_im, model, fingerprint_data, 3)
    
    

