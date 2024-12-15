# _*_ coding: utf-8 _*_
# @Time    :   2024/12/02 11:02:17
# @FileName:   yolo_2_labelme.py
# @Author  :   zhangningboo
# @Email   :   zhangningbo21@mails.ucas.ac.cn

import uuid
import json
from pathlib import Path
from PIL import Image
import pandas as pd
import shutil


class Yolo2Labelme:
    
    def __init__(self, yolo_root: str, labelme_save_path: str, labelme_background_save_path: str=None):
        self.yolo_root_path = Path(yolo_root)
        self.yolo_image_path = self.yolo_root_path.joinpath('images')
        self.yolo_label_path = self.yolo_root_path.joinpath('labels')
        self.labelme_save_path = Path(labelme_save_path)
        if labelme_background_save_path:
            self.labelme_background_save_path = Path(labelme_background_save_path)
        else:
            self.labelme_background_save_path = self.labelme_save_path

    def labelme_template(self, image_name: str, image_height: int, image_width: int):
        return {
            "version": "5.5.0",
            "flags": {},
            "shapes": [],
            "imagePath": image_name,
            "imageData": None,
            "imageHeight": image_height,
            "imageWidth": image_width
        }
    
    def labelme_rectangle(self, label: str, points: list):
        assert len(points) == 2 and len(points[0]) == 2 and len(points[1]) == 2
        return {
            "label": label,
            "points": points,
            "group_id": None,
            "description": "",
            "shape_type": "rectangle",
            "flags": {},
            "mask": None
        }
        
    def collect_yolo_file(self):
        for image_file in self.yolo_image_path.glob('*'):
            label_file = self.yolo_label_path.joinpath(rf"{image_file.stem}.txt")
            if label_file.exists():
                yield [image_file, label_file]

    def convert(self, image_file: Path, label_file: Path):
        image = Image.open(image_file)
        image_width, image_hight = image.size
        # print(rf"{image_width = }, {image_hight = }, {label_file.exists()}")
        with open(label_file, mode='r', encoding="utf8") as f:
            content = f.readlines()
        if len(content) == 0:
            shutil.copy(image_file, self.labelme_background_save_path.joinpath(image_file.name))
            return
        labelme_content = self.labelme_template(image_file.name, image_hight, image_width)
        try:
            for line in content:
                line = line.strip().split(" ")
                if not line:
                    continue
                cls, *bbox = line
                cx, cy, w, h = map(float, bbox)
                x1 = int((cx - w / 2) * image_width)
                y1 = int((cy - h / 2) * image_hight)
                x2 = int((cx + w / 2) * image_width)
                y2 = int((cy + h / 2) * image_hight)
                print(cls)
                label = "fire" if cls == "0" else "smoke"
                annotation = self.labelme_rectangle(label=label, points=[[x1, y1], [x2, y2]])
                labelme_content['shapes'].append(annotation)
        except Exception as e:
            shutil.copy(image_file, self.labelme_background_save_path.joinpath(image_file.name))
            return
        json_str = json.dumps(labelme_content, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'))
        with open(self.labelme_save_path.joinpath(rf"{label_file.stem}.json"), mode='w', encoding="utf8") as f:
            f.writelines(json_str)
        shutil.copy(image_file, self.labelme_save_path.joinpath(image_file.name))
        return True


if __name__ == "__main__":
    root_path = Path("/data/sdb1/zhangningboo/fire_casia/trans_dataset")
    for anything in root_path.glob('*'):
        if anything.is_dir():
            tool = Yolo2Labelme(
                yolo_root=anything.absolute().as_posix(),
                labelme_save_path="/data/nvme1n1p1/zhangningboo/workspace/cv_tool/casia_labelme",
                labelme_background_save_path="/data/nvme1n1p1/zhangningboo/workspace/cv_tool/casia_labelme_background"
            )
            for [image_file, label_file] in tool.collect_yolo_file():
                # print(image_file)
                tool.convert(image_file, label_file)
