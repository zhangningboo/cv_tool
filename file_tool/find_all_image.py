from pathlib import Path
from typing import List


def find_all_images(parent_path: Path, image_extensions: List[str]):
    """
    在指定的父文件夹及其所有子文件夹下查找指定扩展名的图片文件。

    参数:
        parent_folder (str): 父文件夹的路径。
        image_extensions (list[str]): 图片文件扩展名列表（如 ['.jpg', '.png', '.gif']）。

    返回:
        generator: 包含所有匹配图片文件路径的生成器。
    """
    image_extensions = [i.lower() for i in image_extensions] + [i.upper() for i in image_extensions]
    # 构建包含所有子文件夹及文件的递归通配符模式
    glob_pattern = "*"
    glob_patterns = [f"{glob_pattern}{ext}" for ext in image_extensions]
    # 遍历所有通配符模式，合并生成所有匹配图片的路径
    image_files = []
    for pattern in glob_patterns:
        image_files.extend([img for img in parent_path.rglob(pattern)])
    return image_files


if __name__ == '__main__':
    parent_dir = "/path/to/your/data"
    image_extensions = ['.jpg', '.png', '.gif', '.bmp', '.tiff']  # 添加其他所需的图片扩展名
    parent_path = Path(parent_dir)
    for sub_folder in parent_path.glob('*'):
        if not sub_folder.is_dir():
            continue
        all_image_paths = find_all_images(sub_folder, image_extensions)
        print(sub_folder.name, len(all_image_paths))
