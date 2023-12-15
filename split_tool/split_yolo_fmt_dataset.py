from pathlib import Path
from sklearn.model_selection import train_test_split

dataset_dir = rf"E:\Desktop\1000\instalce_seg"
dataset_path = Path(dataset_dir)

image_path = dataset_path.joinpath("images")
images = [f.name for f in image_path.glob("*")]

train_dataset, test_dataset = train_test_split(images, test_size=0.2, random_state=42)

with open(dataset_path.joinpath("train.txt"), mode='w', encoding='utf8') as f:
    for line in train_dataset:
        f.write(f"{line}\n")

with open(dataset_path.joinpath("test.txt"), mode='w', encoding='utf8') as f:
    for line in test_dataset:
        f.write(f"{line}\n")
