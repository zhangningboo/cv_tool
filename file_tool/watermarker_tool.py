import os
from pathlib import Path
import cv2
import numpy as np
from watermarker.marker import add_mark
# import matplotlib.pyplot as plt


class Watermarker:
    
    def __init__(self, image_file: str, watermark_text: str):
        self.image_file = image_file
        self.watermark_text = watermark_text
        self.image_path = Path(image_file)
    
    def opencv_fmt(self):
        # 读取原始图片
        image = cv2.imdecode(np.fromfile(self.image_path.absolute().as_posix(), dtype=np.uint8),-1)

        # 设置字体、字号和颜色
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1
        font_color = (0, 0, 255)  # BGR颜色，这里是红色
        font_thickness = 2

        # 获取文本的大小
        text_size, _ = cv2.getTextSize(watermark_text, font, font_scale, font_thickness)
        text_width, text_height = text_size

        # 选择要放置水印的位置（这里是右下角）
        x_offset = image.shape[1] - text_width - 10
        y_offset = image.shape[0] - 10

        # 设置文本的透明度（0-1之间，0表示完全透明，1表示完全不透明）
        alpha = 0.3

        # 在原始图片上添加文本水印
        watermarked_image = image.copy()
        cv2.putText(watermarked_image, watermark_text, (x_offset, y_offset), font, font_scale, font_color, font_thickness, cv2.LINE_AA)
        cv2.addWeighted(watermarked_image, alpha, image, 1 - alpha, 0, image)

        # 保存添加水印后的图片
        cv2.imencode('.jpg', image)[1].tofile(self.save_file.absolute().as_posix())  # 

    def fmt(self, save_file_path: Path=None, opacity=0.2, angle=45, space=30):
        if save_file_path is None:
            save_file_path = self.save_file.absolute().as_posix()
        add_mark(file=self.image_path.absolute().as_posix(), 
                 out=save_file_path.absolute().as_posix(), 
                 mark=self.watermark_text, 
                 opacity=opacity, angle=angle, space=space)


if __name__ == '__main__':
    watermark_text = rf"仅用于xxx认证"
    # 获取当前脚本的绝对路径
    script_path = os.path.abspath(__file__)
    # 获取当前脚本所在目录
    script_dir = os.path.dirname(script_path)
    save_file_path = Path(script_dir)
    
    marker = Watermarker(image_file=rf"path/to/image", watermark_text=watermark_text)
    marker.fmt(save_file_path=save_file_path)
    
    marker = Watermarker(image_file=rf"path/to/image", watermark_text=watermark_text)
    marker.fmt(save_file_path=save_file_path)
