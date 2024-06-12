from uuid import uuid4
from pathlib import Path
import argparse
from collections import defaultdict


class RenameTool:

    def __init__(self, data_root: str):
        self.data_root = data_root
        self.data_path = Path(self.data_root)

    def pair(self):
        res = defaultdict(list)
        dir_queue = [self.data_path]
        while dir_queue:
            current_path = dir_queue.pop()
            for anything in current_path.glob('*'):
                if anything.is_dir():
                    dir_queue.append(anything)
                    continue
                res[anything.stem].append(anything)
        return res       

    def rename(self):
        pair = self.pair()
        for stem, files in pair.items():
            gen_uuid = uuid4()
            for file in files:
                new_name = file.parent.joinpath(rf'{gen_uuid}{file.suffix}')
                file.rename(new_name)
        

def args_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_root", "-s", type=str, required=True, help="包含需要修改文件名称的文件夹，🧭：\033[31m原文件不保留\033[0m")
    opt = parser.parse_args()
    return opt


if __name__ == '__main__':
    opt = args_parser()
    tool = RenameTool(data_root=opt.data_root)
    tool.rename()
