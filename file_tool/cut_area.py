from pathlib import Path
import cv2
import numpy as np
    
image_dir = rf"E:\Documents\中期报告"
image_path = Path(image_dir)
image_files = [f for f in image_path.glob("*")]
image_files = sorted(image_files, key=lambda path: int(path.name.removesuffix(path.suffix).split('_')[-1]))

for image_file in image_files:
    img = cv2.imdecode(np.fromfile(image_file.absolute().as_posix(), dtype=np.uint8), -1)
    x, y, w, h = 0, 0, 480, 640
    img = img[y: y + h, x:x + w]
    cv2.imshow('test', img)
    cv2.waitKey(0)

cv2.destroyAllWindows()
