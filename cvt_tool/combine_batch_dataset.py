from collections import defaultdict
from pathlib import Path
from enum import Enum


class Keys(Enum):
    images = 'images'
    labels = 'labels'


class Process:

    def __init__(self, root_dir: str):
        self.filter_things = defaultdict(dict)
        self.root_path = Path(root_dir)

    def walkthrough_path(self, suffix=None):
        if suffix is None:
            suffix = ['.jpg', '.png']
        suffix = [*suffix, *[item.upper() for item in suffix]]
        path_queue = [self.root_path]
        while path_queue:
            path_item = path_queue.pop()
            for anything in path_item.glob('*'):
                if anything.is_dir():
                    path_queue.append(anything)
                elif anything.suffix in suffix:
                    label = anything.parent.joinpath(Keys.labels.value).joinpath(f'{anything.stem}.txt')
                    self.filter_things[anything.stem] = {
                        Keys.labels.value: label,
                        Keys.images.value: anything
                    }


if __name__ == '__main__':
    tool = Process(rf'/Users/zhangningboo/workspace/workspace-code/cv_tool')
    tool.walkthrough_path(suffix=['.py'])
    print(f'{len(tool.filter_things.keys()) = }')
