from pathlib import Path
import json
import numpy as np
from PIL import Image
import shutil
from tqdm import tqdm
from sklearn.model_selection import train_test_split
from concurrent.futures import ThreadPoolExecutor, as_completed
from multiprocessing import cpu_count
from common_tool import Timer

"""
yolo 格式：cls cx cy w h，归一化
coco 格式：x1 y1 w h，未归一化
"""

np.random.seed(42)

cls_names = ['苹果', '茄子', '胡萝卜', '人脸', '手', '芹菜', '牛奶瓶装', '牛奶盒装', '人体', '酸奶盒装', '抽屉']
cls_name_to_id = {}


class Yolo2Coco:

    def __init__(self, yolo_path: str, coco_path: str, train_size=0.9):

        self.yolo_path = Path(yolo_path)
        self.yolo_images_path = self.yolo_path.joinpath('images')
        self.yolo_labels_path = self.yolo_path.joinpath('labels')

        self.coco_path = Path(coco_path)
        self.train_path = None
        self.val_path = None
        self.annotation_path = None
        self.train_json_file = None
        self.val_json_file = None

        self.images = []
        self.labels = []
        self.yolo_dataset = {}
        self.coco_train_dataset = {}
        self.coco_val_dataset = {}

        categories = [{'supercategory': 'none', 'id': cls_id, 'name': cls} for cls_id, cls in enumerate(cls_names)]

        self.coco_train_json = {
            'info': 'yolo 2 coco',
            'license': ['license'],
            'images': [],
            'annotations': [],
            'categories': categories
        }
        self.coco_val_json = {
            'info': 'yolo 2 coco',
            'license': ['license'],
            'images': [],
            'annotations': [],
            'categories': categories
        }

        self.image_id = 0
        self.annotation_id = 0

        self.train_size = train_size

    def mkdir_coco(self):
        self.coco_path.mkdir(exist_ok=True)
        self.train_path = self.coco_path.joinpath('train2017')
        self.val_path = self.coco_path.joinpath('val2017')
        self.annotation_path = self.coco_path.joinpath('annotations')
        self.train_json_file = self.annotation_path.joinpath('instances_train2017.json')
        self.val_json_file = self.annotation_path.joinpath('instances_val2017.json')

        self.train_path.mkdir(exist_ok=True)
        self.val_path.mkdir(exist_ok=True)
        self.annotation_path.mkdir(exist_ok=True)
        self.train_json_file.touch(exist_ok=True)
        self.val_json_file.touch(exist_ok=True)

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
        for k in train_files:
            self.coco_train_dataset[k] = self.yolo_dataset[k]
        for k in val_files:
            self.coco_val_dataset[k] = self.yolo_dataset[k]

    def gen_coco_data(self, data, save_path: Path, json_dict: dict):
        image_path = data['image_path']
        label_path = data['label_path']

        shutil.copy(image_path, save_path)
        image = Image.open(image_path).convert('RGB')
        img_w, img_h = image.size
        with open(label_path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                cls, cx, cy, w, h = line.strip().split(' ')
                cx, cy, w, h = map(float, [cx, cy, w, h])
                cls = int(cls)
                x = int((cx - w / 2) * img_w)
                y = int((cy - h / 2) * img_h)
                w = int(w * img_w)
                h = int(h * img_h)
                annotation = {}
                annotation['id'] = self.annotation_id
                self.annotation_id += 1
                annotation['image_id'] = self.image_id
                annotation['category_id'] = cls
                annotation['segmentation'] = []
                annotation['bbox'] = [x, y, w, h]
                annotation['iscrowd'] = 0
                annotation['area'] = 1.0
                json_dict['annotations'].append(annotation)

        image_info = {
            'file_name': image_path.name,
            'height': img_h,
            'width': img_w,
            'id': self.image_id,
        }
        json_dict['images'].append(image_info)
        self.image_id += 1

    def dump_json_file(self):
        json.dump(self.coco_train_json, open(self.train_json_file, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        json.dump(self.coco_val_json, open(self.val_json_file, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


if __name__ == '__main__':

    yolo_root = rf'/data/fridge/five_cls'
    coco_root = rf'/data/fridge/five_cls/coco_format'

    timer = Timer.Timer()

    yolo2coco = Yolo2Coco(yolo_root, coco_root)
    yolo2coco.mkdir_coco()
    yolo2coco.walkthrough_yolo_dataset()
    print(f'Gathering dataset time is {timer.stop()} s')

    tasks = []
    with ThreadPoolExecutor(max_workers=cpu_count() // 2) as pool:
        with tqdm(total=len(yolo2coco.coco_train_dataset.values()), desc="Training dataset converting...") as progress:
            for image in yolo2coco.coco_train_dataset.values():
                task = pool.submit(yolo2coco.gen_coco_data, image, yolo2coco.train_path, yolo2coco.coco_train_json)
                task.add_done_callback(lambda p: progress.update())
                tasks.append(task)
            for _ in as_completed(tasks):
                progress.update()
        print(f'Converting training dataset cost time is {timer.stop()} s')

        with tqdm(total=len(yolo2coco.coco_val_dataset.values()), desc="Validating dataset converting...") as progress:
            for image in yolo2coco.coco_val_dataset.values():
                task = pool.submit(yolo2coco.gen_coco_data, image, yolo2coco.val_path, yolo2coco.coco_val_json)
                task.add_done_callback(lambda p: progress.update())
                tasks.append(task)
            for _ in as_completed(tasks):
                progress.update()
        print(f'Converting validation dataset cost time is {timer.stop()} s')
    yolo2coco.dump_json_file()
    print(f'Dump JSON file cost time is {timer.stop()} s')
