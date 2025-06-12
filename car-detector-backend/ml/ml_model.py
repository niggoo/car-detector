import torch
import torchvision
from torch import nn


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
model.load_state_dict(torch.load("ml/car_ID_b1.pt", weights_only=True, map_location=torch.device('cpu')))
model.eval()