from pathlib import Path
from collections import defaultdict

root_path = Path(rf'/Volumes/WD_BLACK/dataset/public_fire_smoke/Fire_Detection.v1i.yolov8/train/images')

suffix_type = defaultdict(int)

for anything in root_path.glob('*'):
    if not anything.is_file():
        continue
    suffix_type[anything.suffix] += 1

file_total_num = sum(suffix_type.values())
print(suffix_type)
print(f'文件总数: {file_total_num}')
