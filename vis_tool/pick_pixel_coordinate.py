import cv2
import numpy as np

# 全局变量
refPt = []
cropping = False

def imread(filename, flags=cv2.IMREAD_COLOR, dtype=np.uint8):
    try:
        n = np.fromfile(filename, dtype)
        img = cv2.imdecode(n, flags)
        return img
    except Exception as e:
        print(e)
        return None

# 初始化全局变量
points = []
drawing = False

def draw_line(event, x, y, flags, param):
    global points, drawing, img
    
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        points.append((x, y))

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        if len(points) > 1:
            # 连接最后两个点
            cv2.line(img, points[-2], points[-1], (0, 0, 255), 2)
        
        # 显示每个点的坐标值
        for i in range(len(points)):
            cv2.putText(img, f"({points[i][0]}, {points[i][1]})", 
                        (points[i][0] + 10, points[i][1]), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        
        # 绘制每个点
        cv2.circle(img, (x, y), 5, (0, 0, 255), -1)

# 加载图像
img = imread(rf'/Users/zhangningboo/35_2024-09-29_14-52-58.jpg')
if img is None:
    print('Failed to load image file.')
    exit()

# 创建窗口并设置回调函数
cv2.namedWindow('image')
cv2.setMouseCallback('image', draw_line)

while True:
    # 显示图像
    cv2.imshow('image', img)
    
    # 按 'q' 键退出循环
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

# 清理窗口
cv2.destroyAllWindows()
