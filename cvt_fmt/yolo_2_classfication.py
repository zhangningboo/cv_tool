from pathlib import Path
from typing import List
from sklearn.model_selection import train_test_split
from tqdm import tqdm
import numpy as np
import cv2
import uuid


"""
yolo 格式：cls cx cy w h，归一化
"""

np.random.seed(42)

# cls_names = ['苹果', '茄子', '胡萝卜', '人脸', '手', '芹菜', '牛奶瓶装', '牛奶盒装', '人体', '酸奶盒装', '抽屉']
cls_names = ['apple', 'eggplant', 'carrot', 'face', 'hand', 'celery', 'bottle-milk', 'box-milk', 'body', 'yogurt', 'drawer']
cls_name_to_id = {}


class ClsCvtTool:
    
    def __init__(self, yolo_path: Path, cls_path: Path=None, train_size=0.85):
        assert yolo_path.is_dir(), f'The dir is not exists: {yolo_path}'
        self.yolo_path = Path(yolo_path)
        self.yolo_images_path = self.yolo_path.joinpath('images')
        self.yolo_labels_path = self.yolo_path.joinpath('labels')
        self.cls_path = cls_path
        if self.cls_path is None:
            self.cls_path = yolo_path.joinpath('classfication')

        self.train_size = train_size
        self.train_path = None
        self.val_path = None

        self.images = []
        self.labels = []
        self.yolo_dataset = {}
    
    def walkthrough_yolo_dataset(self):
        image_files = [f for f in self.yolo_images_path.glob('*.jpg')]
        label_files = [f for f in self.yolo_labels_path.glob('*.txt')]
        label_files_dict = {}
        for label_file in tqdm(label_files, desc="Creating label files dict..."):
            label_file_name = label_file.name.removesuffix(label_file.suffix)
            label_files_dict[label_file_name] = label_file
        for image_file in tqdm(image_files, desc="Creating yolo dataset dict..."):
            image_file_name = image_file.name.removesuffix(image_file.suffix)
            if image_file_name not in label_files_dict.keys():
                print(f'\033[33mWarning: {image_file_name} maybe is background!\033[0m')
            else:
                self.yolo_dataset[image_file_name] = {
                    'image_path': image_file,
                    'label_path': label_files_dict[image_file_name],
                }
        if len(label_files) != len(self.yolo_dataset.keys()):
            print(f'\033[33mWarning: there are duplicate images in ori dataset\033[0m')
        train_files, val_files = train_test_split(list(self.yolo_dataset.keys()), train_size=self.train_size,
                                                  random_state=42)
        return train_files, val_files
    
    def save_cls_dataset(self):
        train_files, val_files = self.walkthrough_yolo_dataset()
        save_cls_train_path = self.cls_path.joinpath('train')
        save_cls_val_path = self.cls_path.joinpath('val')
        [save_cls_train_path.joinpath(cls_name).mkdir(exist_ok=True, parents=True) for cls_name in cls_names]
        [save_cls_val_path.joinpath(cls_name).mkdir(exist_ok=True, parents=True) for cls_name in cls_names]
        self.cls_name_to_id = {k: v for k, v in enumerate(cls_names)}
        self.process_image(train_files, save_cls_train_path)
        self.process_image(val_files, save_cls_val_path)
        
    def process_image(self, image_files: List, save_path: Path):
        for image in tqdm(image_files):
            image_file = self.yolo_images_path.joinpath(f'{image}.jpg')
            rgb = cv2.imdecode(np.fromfile(image_file.absolute().as_posix(), dtype=np.uint8), cv2.IMREAD_UNCHANGED)
            bboxes = []
            with open(self.yolo_labels_path.joinpath(f'{image}.txt'), mode='r') as f:
                bboxes = f.readlines()
            H, W, _ = rgb.shape
            for bbox in bboxes:
                if not bbox:
                    continue
                line = bbox.strip().split()
                bbox_cls_id, cx, cy, w, h = map(float, line)
                cx *= W
                cy *= H
                w *= W
                h *= H
                cx, cy, w, h = map(int, [cx, cy, w, h])
                tp_x = cx - w // 2
                tp_y = cy - h // 2
                bbox_img = rgb[tp_y:tp_y + h, tp_x:tp_x + w]
                uuid_name = uuid.uuid1()
                file_name = save_path.joinpath(cls_names[int(bbox_cls_id)]).joinpath(f'{image}_{uuid_name}.jpg')
                cv2.imencode('.jpg', bbox_img)[1].tofile(file_name.absolute().as_posix())

if __name__ == '__main__':
    yolo_path = Path(rf'/path/to/yolo')
    tool = ClsCvtTool(yolo_path=yolo_path)
    tool.save_cls_dataset()