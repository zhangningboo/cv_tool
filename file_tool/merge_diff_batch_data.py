from pathlib import Path
import argparse
import shutil


class MergeTool:
    
    def __init__(self, data_root: str, save_dir: str) -> None:
        self.data_root = data_root
        self.data_root_path = Path(self.data_root)
        
        self.save_dir = save_dir
        self.save_path = Path(self.save_dir)
    
    def find_all_files_by_suffix(self, file_suffixes=['.json', ]):
        dir_queue = [self.data_root_path]
        files = []
        file_names = set()
        while dir_queue:
            current_path = dir_queue.pop()
            for anything in current_path.glob('*'):
                if anything.is_dir():
                    dir_queue.append(anything)
                    continue
                if anything.suffix in file_suffixes:
                    files.append(anything)
                    file_names.add(anything.name)
        assert len(file_names) == len(files), '存在重名的文件，请注意！'
        return files
    
    def merge_file(self):
        labels = self.find_all_files_by_suffix(file_suffixes=['.json', ])
        images = self.find_all_files_by_suffix(file_suffixes=['.jpg', '.png', ])
        print(labels[:10], images[:10])
    

def args_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_root", "-d", type=str, default='/home/zhangningboo/Downloads/dust', help="不同批次数据的根路径")
    parser.add_argument("--save_dir", "-s", type=str, default='/home/zhangningboo/Downloads/dust_train', help="保存路径")
    opt = parser.parse_args()
    return opt


if __name__ == '__main__':
    opt = args_parser()
    
    tool = MergeTool(
        data_root=opt.data_root,
        save_dir=opt.save_dir,
    )
    
    tool.merge_file()