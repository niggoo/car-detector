from torch.utils.data import DataLoader, Dataset
import scipy.io as sio
import pandas as pd
from torchvision import transforms
from PIL import Image
import numpy as np

import torch
import torchvision
from torch import nn
from tqdm import tqdm
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
## ---------Model-----------
## -------------------------

#Classifier for Car Identification
class CarIdentifier(nn.Module):
    
    def __init__(self, features: nn.Module, num_classes: int = 196):
        super(CarIdentifier, self).__init__()
        self.features = features
        self.global_avg_pool = nn.AdaptiveAvgPool2d(1)
        self.classifier = nn.Linear(1280,num_classes)
        
    def forward(self, x):
        x = self.features(x)
        x = self.global_avg_pool(x)
        x = torch.flatten(x,1)
        x = self.classifier(x)
        
        return x

#Initialize Efiicient Net b1
def enb3_init_(network: CarIdentifier):

    enb1= torchvision.models.efficientnet_b1(weights = "IMAGENET1K_V1")
    network.features = enb1.features
    
    for m in network.classifier.modules():
        if isinstance(m, nn.Linear):
            torch.nn.init.xavier_uniform_(m.weight)
            if m.bias is not None:
                torch.nn.init.constant_(m.bias, 0)
                
#Load Pretrained Eficcient Net B1 and fine tune last layers
def get_enb1(num_classes: int = 196, device: str = "cpu"):
    enb1 = torchvision.models.efficientnet_b1()
    net = CarIdentifier(enb1.features, num_classes=num_classes)
    enb3_init_(net)
    for par in net.features.parameters():
        par.requires_grad = False
    for par in net.features[6].parameters():
        par.requires_grad = True
    for par in net.features[7].parameters():
        par.requires_grad = True
    for par in net.features[8].parameters():
        par.requires_grad = True
    net = net.to(device)
    return net

## -------------------------
## --------Training---------
## -------------------------

@torch.no_grad()
def evaluate(network: nn.Module, dataloader: DataLoader, loss: nn.Module) -> list:
    network.eval()
    errors = []
    acc_list = []
    for _, data in enumerate(tqdm(dataloader)):
        x , y = data
        pred = network(x.to("cuda"))
        eval = loss(pred,y.long().to("cuda"))
        errors.append(eval.item())

        pred_class = torch.argmax(pred, dim=1)
        eq = torch.eq(pred_class, y.to("cuda"))
        acc = torch.sum(eq).item() / len(eq) * 100
        acc_list.append(acc)
        
    avg_acc = sum(acc_list) / len(acc_list)
    avg_loss = sum(errors) / len(errors)
    return avg_loss, avg_acc
    

@torch.enable_grad()
def update(network: nn.Module, dataloader: DataLoader, loss: nn.Module, 
           opt: torch.optim) -> list:
    network.train()
    errors = []
    acc_list = []
    for _, data in enumerate(tqdm(dataloader)):
        x , y = data
        opt.zero_grad()
        pred = network(x.to("cuda"))
        eval = loss(pred, y.long().to("cuda"))
        errors.append(eval.item())
        eval.backward()
        opt.step()
        
        pred_class = torch.argmax(pred, dim=1)
        eq = torch.eq(pred_class, y.to("cuda"))
        acc = torch.sum(eq).item() / len(eq) * 100
        acc_list.append(acc)
        
    avg_acc = sum(acc_list) / len(acc_list)
    avg_loss = sum(errors) / len(errors)
    return avg_loss, avg_acc

## -------------------------
## ------Run Training-------
## -------------------------

model = get_enb1(device='cuda' if torch.cuda.is_available() else 'cpu')

criterion = nn.CrossEntropyLoss()
optimiser = torch.optim.Adam(model.parameters(), lr=0.0015) 

print(f"Evaluating train...")
train_loss = evaluate(model, train_dataloader, criterion)
print(f"Evaluating valid...")
valid_loss = evaluate(model, test_dataloader, criterion)
print(f"Reference - Training Loss: {train_loss}, Valid Loss: {valid_loss}")
for i in range(26):
    train_loss, train_acc = update(model, train_dataloader, criterion, optimiser)
    
    print(f"Epoch {i}, Training Loss: {train_loss} Train Acc: {train_acc:.2f}")
    if i % 5 == 0:
        valid_loss, val_acc = evaluate(model, test_dataloader, criterion)
        print(f"Epoch {i}, Training Loss: {train_loss} Train Acc: {train_acc:.2f}, Valid Loss: {valid_loss} Val Acc: {val_acc:.2f}")
        torch.save(model.state_dict(), "carID_v1_enb1.pt")

@torch.no_grad()
def accuracy(network, dataloader):
    network.eval()
    acc_count = 0 
    for _, data in enumerate(tqdm(dataloader)):
        image , label = data
        image = image.to("cuda")
        label = label.to("cuda")
        pred = network(image)
        pred_class = torch.argmax(pred, dim=1)
        acc_count += (label == pred_class).sum().item()
                
    acc = 100* (acc_count / len(dataloader.dataset))
    return f"Model accuracy: {acc:.2f} %"

accuracy(model, test_dataloader)
