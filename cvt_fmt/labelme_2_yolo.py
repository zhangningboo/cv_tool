"""
@Description :   
@Author      :   zhangningboo
@Email       :   zhangningbo21@mails.ucas.ac.cn
@Time        :   2024/12/16 05:00:35
"""
from pathlib import Path
import math
import json
import shutil
from tqdm import tqdm
import yaml


class Labelme2Yolo:
    
    def __init__(self, labelme_path: Path, yolo_path: Path, class_id: dict):
        self.labelme_path = labelme_path
        self.yolo_path = yolo_path
        self.yolo_label_path = self.yolo_path.joinpath('labels')
        self.yolo_label_path.mkdir(exist_ok=True)
        self.yolo_image_path = self.yolo_path.joinpath('images')
        self.yolo_image_path.mkdir(exist_ok=True)
        self.class_id = class_id
        
    def files_sum(self) -> int:
        return sum(1 for _ in self.labelme_path.glob('*.json'))
    
    def run(self):
        with tqdm(total=self.files_sum()) as pbar:
            for json_file in self.labelme_path.glob('*.json'):
                with open(json_file, mode='r', encoding="utf8") as f:
                    json_content = json.load(f)
                height, width = map(int, map(json_content.get, ['imageHeight', 'imageWidth']))
                txt_content = []
                for bbox in json_content['shapes']:
                    label = bbox['label']
                    points = bbox['points']
                    x_points = list(map(math.floor, [points[0][0], points[1][0]]))
                    y_points = list(map(math.floor, [points[0][1], points[1][1]]))
                    x1, x2 = min(x_points), max(x_points)
                    y1, y2 = min(y_points), max(y_points)
                    w = max(1, x2 - x1)
                    h = max(1, y2 - y1)
                    cx = x1 + w // 2
                    cy = y1 + h // 2
                    cx, cy, w, h = cx / width, cy / height, w / width, h / height
                    line = f"{self.class_id[label]} {cx} {cy} {w} {h}\n"
                    txt_content.append(line)
                if txt_content:
                    txt_content[-1] = txt_content[-1].strip()
                    txt_file = self.yolo_label_path.joinpath(rf"{json_file.stem}.txt")
                    with open(txt_file, mode='w', encoding='utf8') as f:
                        f.writelines(txt_content)
                image_file = json_file.parent.joinpath(rf"{json_file.stem}.jpg")
                shutil.copyfile(image_file, self.yolo_path.joinpath('images').joinpath(image_file.name))
                pbar.update()

if __name__ == "__main__":
    labelme_root = r"/data/sdb1/dataset/dust_action/labelme_cleaner"
    yolo_root = r"/data/sdb1/dataset/dust_action/yolo_cleaner"
    class_id = {
        'cleaner': 0,
        'people': 1,
    }
    tool = Labelme2Yolo(
        labelme_path=Path(labelme_root),
        yolo_path=Path(yolo_root),
        class_id=class_id
    )
    
    tool.run()