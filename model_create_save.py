# -*- coding: utf-8 -*-
"""Untitled0.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1HgLhbDddBFJayxu7GUP98LDwVI68RKD3
"""

!pip install -q  pytorch_lightning
!pip install optuna
import cv2 
import torch,torchvision
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 
import seaborn as sns
import pytorch_lightning as pl
from torchvision import transforms
import torch.nn as nn
import torch.nn.functional as F
from pytorch_lightning.metrics.functional import accuracy
from torchvision.datasets import CIFAR10
from google.colab import files
from pytorch_lightning.callbacks import EarlyStopping
import optuna

uploaded=files.upload()

img=cv2.imread('image2.jpg')
img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
plt.imshow(img)
plt.show()

uploaded=files.upload()

def show_img():
  fig,axes=plt.subplots(1,2,figsize=(14,4))
  ax=axes.ravel()

  img=cv2.imread('image1.jpg')
  img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
  img2=cv2.imread('image2.jpg')
  img2=cv2.cvtColor(img2,cv2.COLOR_BGR2RGB)
  ax[0].imshow(img)
  ax[1].imshow(img2)
  plt.show()

show_img()

def get_data():
  transform=transforms.Compose([
                              transforms.ToTensor(),
                              # transforms.Resize((224,224)),
                              transforms.Normalize(mean=[0.485,0.456,0.496],std=[0.229,0.224,0.225]),
                              transforms.RandomVerticalFlip(),
                              transforms.RandomHorizontalFlip(),

  ])

  data=CIFAR10(root='data',download=True,train=True,transform=transform)
  test=CIFAR10(root='data',download=True,train=False,transform=transform)

  n_train=int(len(data)*0.8)
  n_val=len(data)-n_train

  train,val=torch.utils.data.random_split(data,[n_train,n_val])
  return train,val,test

def get_images(train):
  fig,axes=plt.subplots(5,5,figsize=(10,10))
  ax=axes.ravel()

  for i in range(25):

    img01=np.array(train[i][0])
    img=np.transpose(img01,(1,2,0))
    ax[i].imshow(img)
    ax[i].set_title(i,color='white')
  plt.show()

train,val,test=get_data()

def get_loader(train,val,test):
  batch_size=128

  train_loader=torch.utils.data.DataLoader(train,batch_size,shuffle=True,drop_last=True)
  val_loader=torch.utils.data.DataLoader(val,batch_size)
  test_loader=torch.utils.data.DataLoader(test,batch_size)

  return train_loader,val_loader,test_loader

train_loader,val_loader,test_loader=get_loader(train,val,test)

get_images(train)

pl.seed_everything(0)
class Net(pl.LightningModule):
  def __init__(self):
    super(Net,self).__init__()
    self.conv1=nn.Conv2d(3,64,3,padding=1)
    self.conv2=nn.Conv2d(64,128,3,padding=1)
    self.conv3=nn.Conv2d(128,216,3,padding=1)
    self.conv4=nn.Conv2d(216,512,3,padding=1)

    self.fc1=nn.Linear(512*2*2,10)

    self.bt1=nn.BatchNorm2d(64)
    self.bt2=nn.BatchNorm2d(128)
    self.bt3=nn.BatchNorm2d(216)
    self.bt4=nn.BatchNorm2d(512)

    self.dropout=nn.Dropout2d(p=0.5)

    # self.resnet=resnet18(pretrained=True)
    # self.fc=nn.Linear(1000,10)

    # for param in self.resnet.parameters():
    #   param.requires_grad=False

  def forward(self,x):
    x=self.conv1(x)
    x=self.bt1(x)
    x=F.relu(x)
    x=F.max_pool2d(x,2,2)

    x=self.conv2(x)
    x=self.bt2(x)
    x=F.relu(x)
    x=F.max_pool2d(x,2,2)

    x=self.conv3(x)
    x=self.bt3(x)
    x=F.relu(x)
    x=F.max_pool2d(x,2,2)

    x=self.conv4(x)
    x=self.bt4(x)
    x=F.relu(x)
    x=F.max_pool2d(x,2,2)

    x=x.view(-1,512*2*2)
    x=self.dropout(x)
    x=self.fc1(x)
    x=F.relu(x)
    # x=self.resnet(x)
    # x=F.relu(x)
    # x=self.fc(x)
    return x

  def training_step(self,batch,batch_idx):
    x,t=batch
    y=self.forward(x)
    loss=F.cross_entropy(y,t)
    return loss

  def validation_step(self,batch,batch_idx):
    x,t=batch
    y=self.forward(x)
    loss=F.cross_entropy(y,t)
    acc=accuracy(y,t)
    self.log('val_acc',acc,on_epoch=True)
    self.log('val_loss',loss,on_epoch=True)
    return loss

  def test_step(self,batch,batch_idx):
    x,t=batch
    y=self.forward(x)
    loss=F.cross_entropy(y,t)
    acc=accuracy(y,t)
    self.log('test_acc',acc,on_epoch=True)
    self.log('test_loss',loss,on_epoch=True)

    return loss

  def configure_optimizers(self):
    optimizer=torch.optim.SGD(self.parameters(),lr=0.01,weight_decay=0.001)
    return optimizer
#optunaによる早期終了
def objective(trial):
    lr=trial.suggest_loguniform('lr',1e-5,1e-1)
    pl.seed_everything(0)
    net=Net(lr=lr)
    trainer=pl.Trainer(max_epochs=30,gpus=1,callbacks=[EalyStopping(monitor='val_acc')]
    trainer.fit(net,trainer_loader,val_loader)
    return trainer.callback_metrics['val_acc']

sampler=optuna.samplers.TPESampler(seed=0)
study=optuna.create_study(sampler=sampler)
study.optimize(objective,n_train=10)
                       
trainer.test(test_dataloaders=test_loader)

trainer.callback_metrics

# Commented out IPython magic to ensure Python compatibility.
%load_ext tensorboard
%tensorboard --logdir lightning_logs/

# first result 
# {'test_acc': tensor(0.5896, device='cuda:0'),
#  'test_loss': tensor(1.1961, device='cuda:0'),
#  'val_acc': tensor(0.5859, device='cuda:0'),
#  'val_loss': tensor(1.1908, device='cuda:0')}
# second result as dropout Lasso
# {'test_acc': tensor(0.6923, device='cuda:0'),
#  'test_loss': tensor(0.8865, device='cuda:0'),
#  'val_acc': tensor(0.7044, device='cuda:0'),
#  'val_loss': tensor(0.8544, device='cuda:0')}
# third result as transforms
# {'test_acc': tensor(0.6926, device='cuda:0'),
#  'test_loss': tensor(0.8582, device='cuda:0'),
#  'val_acc': tensor(0.6954, device='cuda:0'),
#  'val_loss': tensor(0.8550, device='cuda:0')}

img=train[100][0]
ToPIL=transforms.ToPILImage()
img=ToPIL(img)
img

def show(img,img1):
  fig,axes=plt.subplots(1,2,figsize=(10,10))
  ax=axes.ravel()

  ax[0].imshow(img)
  ax[0].set_title('before')
  ax[1].set_title('after')

  ax[1].imshow(img1)
  plt.show()

transform=transforms.RandomHorizontalFlip(p=1)
out=transform(img)
out.save('out.jpg')
show(img,out)

transform=transforms.RandomVerticalFlip(p=1)
out2=transform(img)
show(img,out2)

def save_load_result(model_name,net):
  if model_name:
    torch.save(net.state_dict(),model_name)
    net=Net()
    net.load_state_dict(torch.load('third_model.pt'))
    a=train[0][0].reshape(1,3,32,32)
    y=net.forward(a)
    return torch.argmax(y) == train[0][1]

save_load_result('hello.pt',net)



