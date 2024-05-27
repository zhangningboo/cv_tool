from pathlib import Path
import uuid
import argparse
import shutil


class FilenameFmt:

    def __init__(self, dataset_dir: str, file_prefix: str= None):
        self.dataset_dir = dataset_dir
        self.dataset_path = Path(self.dataset_dir)
        self.save_path = self.dataset_path.joinpath('formatted')
        print(self.save_path)

    def purge_uuid_fmt(self, keep_original: bool=False):
        if self.save_path.exists():
            shutil.rmtree(self.save_path.absolute().as_posix())

        src_dir_len = len(self.dataset_path.absolute().as_posix())
        folder_queue = [self.dataset_path]
        while folder_queue:
            folder: Path = folder_queue.pop()
            for anything in folder.glob('*'):
                if anything.is_dir():  # 是文件夹，就下次迭代时处理
                    folder_queue.append(anything)
                    continue
                dst_path_suffix = anything.parent.absolute().as_posix()[src_dir_len:]
                dst_path = Path(rf'{self.save_path.absolute().as_posix()}{dst_path_suffix}')
                dst_filename = f'{uuid.uuid4()}{anything.suffix}'
                if keep_original:
                    dst_filename = f'{anything.stem}_{dst_filename}'
                if not dst_path.exists():
                    dst_path.mkdir(parents=True)
                dst_file = dst_path.joinpath(dst_filename)
                print(anything, dst_file)


def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset_dir', '-d', type=str, default="", required=True, help="需要转换的数据及路径")
    opt = parser.parse_args()
    return opt


if __name__ == '__main__':
    opt = parse_opt()
    tool = FilenameFmt(dataset_dir=opt.dataset_dir)
    tool.purge_uuid_fmt(keep_original=True)
