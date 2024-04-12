import json
from pathlib import Path
from typing import List
import numpy as np
import glob
import PIL.Image
from labelme import utils
from tqdm import tqdm
from sklearn.model_selection import train_test_split
from shutil import copyfile
from argparse import ar


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(MyEncoder, self).default(obj)

class labelme2coco(object):
    def __init__(self, image_files=[], coco_path='./coco_2017', ignore_categories: List= []):
        self.image_files = image_files
        # coco
        self.coco_path = Path(coco_path)
        self.ignore_categories = ignore_categories
        self.train_path = None
        self.val_path = None
        self.test_path = None
        self.annotation_path = None
        self.train_json_file = None
        self.val_json_file = None
        self.test_json_file = None

        self.images = []
        self.categories = []
        self.annotations = []
        self.label = []
        self.annID = 1
        self.height = 0
        self.width = 0
        self.mkdir_coco()
        self.save_json()
    
    def mkdir_coco(self):
        self.coco_path.mkdir(exist_ok=True)
        self.train_path = self.coco_path.joinpath('train2017')
        self.val_path = self.coco_path.joinpath('val2017')
        self.test_path = self.coco_path.joinpath('test2017')
        self.annotation_path = self.coco_path.joinpath('annotations')
        self.train_json_file = self.annotation_path.joinpath('instances_train2017.json')
        self.val_json_file = self.annotation_path.joinpath('instances_val2017.json')
        self.test_json_file = self.annotation_path.joinpath('instances_test2017.json')

        self.train_path.mkdir(exist_ok=True)
        self.val_path.mkdir(exist_ok=True)
        self.test_path.mkdir(exist_ok=True)
        self.annotation_path.mkdir(exist_ok=True)
        self.train_json_file.touch(exist_ok=True)
        self.val_json_file.touch(exist_ok=True)
        self.test_json_file.touch(exist_ok=True)

    def reset(self):
        self.images = []
        self.categories = []
        self.annotations = []
        self.label = []
        self.annID = 1
        self.height = 0
        self.width = 0

    def data_transfer(self, image_files, coco_image_path: Path):
        for num, image_file in enumerate(tqdm(image_files)):
            copyfile(image_file, coco_image_path.joinpath(image_file.name))
            json_file = image_file.parent.joinpath(f'{image_file.name.removesuffix(image_file.suffix)}.json')
            if not json_file.is_file():
                self.images.append(self.image(num, image_file=image_file))
                continue
            with open(json_file, 'r') as fp:
                data = json.load(fp)  # Load JSON file
                self.images.append(self.image(num, data))
                for shapes in data['shapes']:
                    label = shapes['label']
                    if label in self.ignore_categories:
                        continue
                    if label not in self.label:
                        self.categories.append(self.categorie(label))
                        self.label.append(label)
                    points = shapes['points']
                    points.append([points[0][0], points[1][1]])
                    points.append([points[1][0], points[0][1]])
                    self.annotations.append(self.annotation(points, label, num))
                    self.annID += 1

    def image(self, num=None, data=None, image_file: Path=None):
        image = {}
        if data is not None:
            img = utils.img_b64_to_arr(data['imageData'])
            image['file_name'] = data['imagePath'].split('/')[-1]
            height, width = img.shape[:2]
        else:
            img = PIL.Image.open(image_file.absolute().as_posix())
            image['file_name'] = image_file.name
            width, height = img.size
        image['height'] = height
        image['width'] = width
        image['id'] = num + 1
        self.height = height
        self.width = width
        return image

    def categorie(self, label):
        categorie = {}
        categorie['supercategory'] = 'Cancer'
        categorie['id'] = len(self.label) + 1
        categorie['name'] = label
        return categorie

    def annotation(self, points, label, num):
        annotation = {}
        annotation['segmentation'] = [list(np.asarray(points).flatten())]
        annotation['iscrowd'] = 0
        annotation['image_id'] = num + 1
        annotation['bbox'] = list(map(float, self.getbbox(points)))
        annotation['area'] = annotation['bbox'][2] * annotation['bbox'][3]
        annotation['category_id'] = self.getcatid(label)
        annotation['id'] = self.annID
        return annotation

    def getcatid(self, label):
        for categorie in self.categories:
            if label == categorie['name']:
                return categorie['id']
        return 1

    def getbbox(self, points):
        polygons = points
        mask = self.polygons_to_mask([self.height, self.width], polygons)
        return self.mask2box(mask)

    def mask2box(self, mask):
        index = np.argwhere(mask == 1)
        rows = index[:, 0]
        clos = index[:, 1]
        left_top_r = np.min(rows)
        left_top_c = np.min(clos)
        right_bottom_r = np.max(rows)
        right_bottom_c = np.max(clos)
        return [left_top_c, left_top_r, right_bottom_c - left_top_c, right_bottom_r - left_top_r]

    def polygons_to_mask(self, img_shape, polygons):
        mask = np.zeros(img_shape, dtype=np.uint8)
        mask = PIL.Image.fromarray(mask)
        xy = list(map(tuple, polygons))
        PIL.ImageDraw.Draw(mask).polygon(xy=xy, outline=1, fill=1)
        mask = np.array(mask, dtype=bool)
        return mask

    def data2coco(self):
        data_coco = {}
        data_coco['images'] = self.images
        data_coco['categories'] = self.categories
        data_coco['annotations'] = self.annotations
        return data_coco

    def save_json(self):
        train_files, val_files = train_test_split(self.image_files, train_size=0.8, random_state=42)
        val_files, test_files = train_test_split(val_files, train_size=0.5, random_state=42)
        print(rf"训练集图片数量：{len(train_files)}, 验证集图片数量：{len(val_files)}, 测试集图片数量：{len(test_files)}")
        
        self.data_transfer(train_files, self.train_path)
        self.data_coco = self.data2coco()
        json.dump(self.data_coco, open(self.train_json_file, 'w'), indent=4, cls=MyEncoder)
        self.reset()

        self.data_transfer(val_files, self.val_path)
        self.data_coco = self.data2coco()
        json.dump(self.data_coco, open(self.val_json_file, 'w'), indent=4, cls=MyEncoder)
        self.reset()

        self.data_transfer(test_files, self.test_path)
        self.data_coco = self.data2coco()
        json.dump(self.data_coco, open(self.test_json_file, 'w'), indent=4, cls=MyEncoder)
        self.reset()



if __name__ == '__main__':
    labelme_dataset_dir = rf"/Users/zhangningboo/Documents/安科院/智能装备/数据集/消防器材"
    coco_save_dir = rf"/Users/zhangningboo/Documents/安科院/智能装备/数据集/coco"
    labelme_dataset_path = Path(labelme_dataset_dir)
    image_extensions = ['.jpg', '.JPG', '.png', '.PNG']
    image_files = [img for img in labelme_dataset_path.iterdir() if img.suffix in image_extensions and img.is_file()]
    ignore_categories = ['hard']
    labelme2coco(image_files, coco_path=coco_save_dir, ignore_categories=ignore_categories)
