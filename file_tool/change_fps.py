import cv2
from pathlib import Path
from tqdm import tqdm
from tqdm.contrib import tzip
import numpy as np


class ChangeFps:

    def __init__(self, _src_file: str, _dst_file: str, _dst_fps: int = 60):
        self.src_file = _src_file
        self.dst_file = _dst_file

        self.src_file_path = Path(self.src_file)
        self.dst_file_path = Path(self.dst_file)

        self.dst_fps = _dst_fps
        self.video_file_frames = []

    def get_video_info(self):
        video = cv2.VideoCapture(self.src_file_path.absolute().as_posix())
        self.video_h = video.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.video_w = video.get(cv2.CAP_PROP_FRAME_WIDTH)
        video_frames = []
        while video.isOpened():
            ret, frame = video.read()
            if ret:
                video_frames.append(frame)
            else:
                break
        assert len(video_frames) == video.get(cv2.CAP_PROP_FRAME_COUNT), \
            f"Get {self.src_file_path.absolute()} frames doesn't match with its property!"
        self.video_file_frames = np.array(video_frames)

    def write_video(self):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        width, height = int(self.video_w), int(self.video_h)
        video_writer = cv2.VideoWriter(self.dst_file_path.absolute().as_posix(), fourcc, self.dst_fps, (width, height))
        for frame in tqdm(self.video_file_frames):
            video_writer.write(frame)
        video_writer.release()

    def run(self):
        self.get_video_info()
        self.write_video()


if __name__ == '__main__':
    src_file = rf'/path/to/video.mp4'
    dst_file = rf'/path/to/save.mp4'
    dst_fps = 20

    align_tool = ChangeFps(src_file, dst_file, dst_fps)
    align_tool.run()
