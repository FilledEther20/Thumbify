import torch.nn as nn
from transformers import BertModel
from torchvision import models as vision_models
import torch


class TextEncoder(nn.Module):
    def __init__(self):
        super().__init__()
        self.bert=BertModel.from_pretrained('bert-base-uncased')
        
        for param in self.bert.parameters():
            param.requires_grad=False
            
        self.projection=nn.Linear(768,128)
    
    def forward(self,input_ids,attention_mask):
        # Extract BERT embeddings
        outputs=self.bert(input_ids=input_ids,attention_mask=attention_mask)
        
        pooler_output=outputs.pooler_output
        
        return self.projection(pooler_output)
    
    
    
class VideoEncoder(nn.Module):
    def __init__(self):
        super().__init__()
        self.backbone=vision_models.video.r3d_18(pretrained=True)
        
        for param in self.backbone.parameters():
            param.requires_grad=False
        
        num_fts=self.backbone.fc.in_features
        self.backbone.fc=nn.Sequential(
            nn.Linear(num_fts,128),
            nn.ReLU(),
            nn.Dropout(0.2)
        )
        
    def forward(self,x):
        x=x.transpose(1,2)
        return self.backbone(x)
    
    
class AudioEncoder(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv_layers=nn.Sequential(
            #Lower level features
            nn.Conv1d(64,64,kernel_size=3),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.MaxPool1d(2),
            
            #Higher level features
            nn.Conv1d(64,128,kernel_size=3),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.AdaptiveAvgPool1d(1)
        )
        
        for params in self.conv_layers.parameters():
            params.requires_grad=False
        
        self.projection=nn.Sequential(
            nn.Linear(128,128),
            nn.ReLU(),
            nn.Dropout(0.2)
        )
        
    def forward(self,x):
        x=x.squeeze(1)
        
if __name__=="__main__":
    batch_size=2
    x=torch.randn(batch_size,1,64,300)
    print(f"1. Input shape:{x.shape}")
    
    x_squeezed=x.squeeze(3)
    print(f"2. Squeezed Shape:{x_squeezed.shape}")