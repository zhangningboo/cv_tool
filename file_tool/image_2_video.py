import os
import cv2
from pathlib import Path
from tqdm import tqdm


class Image2Video:

    def __init__(self, src_image_folder: str, dst_video_file: str = None, sort_func=None, fps=60, image_suffix='.jpg'):
        assert isinstance(src_image_folder, (str,))
        self.src_image_path = Path(src_image_folder)
        self.fps = fps
        self.image_suffix = image_suffix

        if dst_video_file is None:
            self.dst_video_file = self.src_image_path.joinpath(f'combine_{self.fps}.mp4')
        else:
            assert isinstance(dst_video_file, (str,))
            self.dst_video_file = Path(dst_video_file)
        self.sort_func = sort_func


    def run(self):
        if not os.path.isdir(self.src_image_path):
            raise f'Image Folder is not exists: {self.src_image_path}'

        image_files = [f for f in self.src_image_path.glob(f'*{self.image_suffix}')]
        if self.sort_func is not None:
            image_files.sort(key=self.sort_func)
        first_frame = cv2.imread(image_files[0].absolute().as_posix())
        h, w, c = first_frame.shape
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        vid_writer = cv2.VideoWriter(self.dst_video_file.absolute().as_posix(), fourcc, self.fps, (w, h))

        cnt = 0
        for image_file in tqdm(image_files):
            frame = cv2.imread(image_file.absolute().as_posix())
            if cnt % (self.fps / 60) == 0:
                vid_writer.write(frame)
        vid_writer.release()


if __name__ == '__main__':
    src_image_folder = r"N:\hand_test2"
    sort_func = lambda file_name: int(file_name.name.split('_')[0])
    Image2Video(src_image_folder=src_image_folder, dst_video_file=r"N:\60fps_co_track.mp4", fps=60, sort_func=sort_func).run()
