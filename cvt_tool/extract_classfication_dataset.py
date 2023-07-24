from pathlib import Path
import os
from tqdm import tqdm
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from multiprocessing import cpu_count

pool_threads_num = cpu_count() // 2

all_cls_names = ['apple', 'person', ]
extract_cls = ['person', ]

curious_num = [0] * len(all_cls_names)
bbox_num = 1000

curious_cls_id = {}

for c_cls in extract_cls:
    assert c_cls in all_cls_names
    curious_cls_id[str(all_cls_names.index(c_cls))] = c_cls

yolo_root = rf"/yolo/root/path"
extract_root = rf"/save/path"

yolo_root_path = Path(yolo_root)
yolo_image_path = yolo_root_path.joinpath("images")
yolo_label_path = yolo_root_path.joinpath("labels")

extract_root_path = Path(extract_root)
extract_image_path = extract_root_path.joinpath("images")
extract_label_path = extract_root_path.joinpath("labels")

shutil.rmtree(extract_image_path, ignore_errors=True)
shutil.rmtree(extract_label_path, ignore_errors=True)

extract_image_path.mkdir(parents=True, exist_ok=True)
extract_label_path.mkdir(parents=True, exist_ok=True)

lock = Lock()
file_annotation_instance_count = {}


def get_annotation_content(label_file: str):
    label_file_path = yolo_label_path.joinpath(label_file)
    with open(label_file_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            cls, *_ = line.strip().split(' ')
            with lock:
                if label_file in file_annotation_instance_count.keys() \
                        and cls in file_annotation_instance_count[label_file].keys():
                    file_annotation_instance_count[label_file][cls] += 1
                else:
                    if label_file not in file_annotation_instance_count:
                        file_annotation_instance_count[label_file] = {}
                    file_annotation_instance_count[label_file][cls] = 1


label_files = os.listdir(yolo_label_path)
with ThreadPoolExecutor(max_workers=pool_threads_num) as pool:
    with tqdm(total=len(label_files), desc="Getting all annotation record...") as progress:
        tasks = [pool.submit(get_annotation_content, label_file) for label_file in label_files]
        for _ in as_completed(tasks):
            progress.update()

# print(file_annotation_instance_count)

picked_files = set()

# 总体尽量少的图片，且满足每类标注实例个数在规定的数量上
for cls in tqdm(curious_cls_id.keys(), desc="Extracting Files by Rules..."):
    cls_files = filter(lambda k: cls in file_annotation_instance_count[k].keys(),
                       file_annotation_instance_count.keys())
    cls_files = list(cls_files)
    cls_file_dict = [{x: file_annotation_instance_count[x]} for x in cls_files]
    if len(cls_file_dict):
        cls_file_dict.sort(key=lambda x: x[list(x.keys())[0]][cls])
        # cls_file_dict = cls_file_dict[::-1]

        for file_annotation in cls_file_dict:
            cls_instance_num = curious_num[int(cls)]
            file_name = list(file_annotation.keys())[0]
            if max(file_annotation[file_name].values()) > 3:
                continue
            if cls_instance_num > bbox_num or file_name in picked_files:
                break
            for f_cls in file_annotation[file_name].keys():
                if curious_num[int(f_cls)] < bbox_num:
                    break
            for f_cls in file_annotation[file_name].keys():
                curious_num[int(f_cls)] += file_annotation[file_name][f_cls]
            picked_files.add(file_name)


def move_file(label_file_name: str):
    image_name = label_file_name.replace('.txt', '.jpg')
    dst_img = extract_image_path.joinpath(image_name)
    src_img = yolo_image_path.joinpath(image_name)
    shutil.copy(src_img, dst_img)

    dst_label = extract_label_path.joinpath(label_file_name)
    src_label = yolo_label_path.joinpath(label_file_name)
    shutil.copy(src_label, dst_label)


with ThreadPoolExecutor(max_workers=pool_threads_num) as pool:
    with tqdm(total=len(picked_files), desc="Saving Extracted Files...") as progress:
        tasks = [pool.submit(move_file, picked_file) for picked_file in picked_files]
        for _ in as_completed(tasks):
            progress.update()

print(curious_num)

for cls in all_cls_names:
    print(f'{cls} 标注实例数: {curious_num[all_cls_names.index(cls)]}')
