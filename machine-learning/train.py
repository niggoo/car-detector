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

#Classifier for Car Identification
class CarIdentifier(nn.Module):
    
    def __init__(self, features: nn.Module, num_classes: int = 196):
        super(CarIdentifier, self).__init__()
        self.features = features
        self.global_avg_pool = nn.AdaptiveAvgPool2d(1)
        self.classifier = nn.Sequential(
            nn.Linear(512,1024),
            nn.ReLU(inplace=True),
            nn.Linear(1024,num_classes),
        )
        
    def forward(self, x):
        x = self.features(x)
        x = self.global_avg_pool(x)
        x = torch.flatten(x,1)
        x = self.classifier(x)
        
        return x

#Initialize VGG19
def vgg_init_(network: CarIdentifier):
    from torchvision.models import vgg
    vgg19 = torchvision.models.vgg19(weights = "VGG19_Weights.IMAGENET1K_V1")
    network.features = vgg19.features
    
    for m in network.classifier.modules():
        if isinstance(m, nn.Linear):
            torch.nn.init.xavier_uniform_(m.weight)
            if m.bias is not None:
                torch.nn.init.constant_(m.bias, 0)
                
#Load Pretrained VGG19
def get_vgg(num_classes: int = 196, device: str = "cpu"):
    vgg19 = torchvision.models.vgg19()
    net = CarIdentifier(vgg19.features, num_classes=num_classes)
    vgg_init_(net)
    for par in net.features.parameters():
        par.requires_grad = False
    net = net.to(device)
    return net

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
#test_labels_df = pd.DataFrame(columns=["class", "file"])
#test_labels_df.loc[:,"class"] = pd.read_csv("devkit/train_perfect_preds.txt")

#for i in range(len(test_labels_df)-1):
#    test_labels_df.loc[i, "file"] = str(i+1).zfill(5) + ".jpg"

test_labels_df = pd.DataFrame(columns=["class", "file"])
for i in range(len(label_test)):
    test_labels_df.loc[i, "class"] = label_test[i][4][0][0] 
    test_labels_df.loc[i,"file"]  = label_test[i][5][0]

test_labels_df.set_index("file")
train_labels_df.set_index("file")

#Set index to start from 0
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

#pre-processing
transform =  transforms.Compose([
        transforms.Resize((224,224)),
        transforms.ToTensor(),       
    ])

test_images = ImageDataset("cars_test/", test_labels_df, transform)
train_images = ImageDataset("cars_train/", train_labels_df, transform)

#display class name
classes = np.squeeze(sio.loadmat("devkit/cars_meta.mat")["class_names"])
def im_class(pred):
    car = classes[pred][0]
    return f"Car: {car}"

train_dataloader = DataLoader(train_images, batch_size=128, shuffle=True)
test_dataloader = DataLoader(test_images, batch_size=128, shuffle=False)


@torch.no_grad()
def evaluate(network: nn.Module, data, metric) -> list:
    network.eval()
    errors = []
    acc_list = []
    for i, data in enumerate(tqdm(data)):
        x , y = data
        pred = network(x.to("cuda"))
        eval = metric(pred,y.long().to("cuda"))
        errors.append(eval.item())

        pred_class = torch.argmax(pred, dim=1)
        eq = torch.eq(pred_class, y.to("cuda"))
        acc = torch.sum(eq).item() / len(eq) * 100
        acc_list.append(acc)
        
    avg_acc = sum(acc_list) / len(acc_list)
    avg_loss = sum(errors) / len(errors)
    return avg_loss, avg_acc
    

@torch.enable_grad()
def update(network: nn.Module, data, loss: nn.Module, 
           opt) -> list:
    network.train()
    errors = []
    acc_list = []
    for i, data in enumerate(tqdm(data)):
        x , y = data
        opt.zero_grad()
        pred = network.forward(x.to("cuda"))
        err = loss.forward(pred, y.long().to("cuda"))
        errors.append(err.item())
        err.backward()
        opt.step()
        
        pred_class = torch.argmax(pred, dim=1)
        eq = torch.eq(pred_class, y.to("cuda"))
        acc = torch.sum(eq).item() / len(eq) * 100
        acc_list.append(acc)
        
    avg_acc = sum(acc_list) / len(acc_list)
    avg_loss = sum(errors) / len(errors)
    return avg_loss, avg_acc


#Training loop
model = get_vgg(device='cuda' if torch.cuda.is_available() else 'cpu')

criterion = nn.CrossEntropyLoss()
optimiser = torch.optim.SGD(model.classifier.parameters(), lr=0.01) 
model.load_state_dict(torch.load("carID_new.pt", weights_only=True))
model.eval()


print(f"Evaluating train...")
train_loss = evaluate(model, train_dataloader, criterion)
print(f"Evaluating valid...")
valid_loss = evaluate(model, test_dataloader, criterion)
print(f"Reference - Training Loss: {train_loss}, Valid Loss: {valid_loss}")
for i in range(76):
    train_loss, train_acc = update(model, train_dataloader, criterion, optimiser)
    
    print(f"Epoch {i}, Training Loss: {train_loss} Train Acc: {train_acc}")
    if i % 5 == 0:
        valid_loss, val_acc = evaluate(model, test_dataloader, criterion)
        print(f"Epoch {i}, Training Loss: {train_loss} Train Acc: {train_acc}, Valid Loss: {valid_loss} Val Acc: {val_acc}")
        torch.save(model.state_dict(), "carID_new.pt")
        
torch.save(model.state_dict(), "carID_new.pt")

torch.save(model.state_dict(), "carID_v1.pt")

image, label = next(iter(train_dataloader))
preds = model(image.to("cuda"))
p_class = torch.argmax(preds, dim=1)
eq = torch.eq(label.to("cuda"), p_class)
acc = torch.sum(eq)                    
err = nn.CrossEntropyLoss()
output = err(preds, label.to("cuda"))
label.type()
train_labels_df.unique()
len(eq)

@torch.no_grad()
def accuracy(network, data):
    network.eval()
    acc_list = []
    for i, data in enumerate(tqdm(data)):
        x , y = data
        pred = network(x.to("cuda"))
        pred_class = torch.argmax(pred, dim=1)
        eq = torch.eq(pred_class, y.to("cuda"))
        acc = torch.sum(eq).item() / len(eq) * 100

        acc_list.append(acc)
        
    avg_acc = sum(acc_list) / len(acc_list)
    return avg_acc    

accuracy(model, test_dataloader)

