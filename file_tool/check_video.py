import cv2


cap = cv2.VideoCapture(rf'/Users/zhangningboo/Downloads/20241008_20241008001908_20241008001927_001909.mp4')
print(cap.get(cv2.CAP_PROP_FRAME_COUNT))
cnt = 0
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    print(cnt, frame.shape)
    cnt += 1
