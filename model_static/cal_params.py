import torch
from torchsummary import summary


model = torch.(rf'/Users/zhangningboo/Downloads/yolov7.pt')

summary(model, (3, 640, 640))


