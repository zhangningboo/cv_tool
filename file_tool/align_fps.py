import cv2
from pathlib import Path
from tqdm import tqdm
from tqdm.contrib import tzip
import numpy as np


class AlignFps:

    def __init__(self, _dst_file: str, _video_files: list):
        self.dst_file = _dst_file
        self.video_files = _video_files
        self.video_file_paths = []
        self.video_file_fps = []
        self.video_file_frames = []
        self.video_aligned_frames = []
        self.video_h = []
        self.video_w = []
        self.max_fps = -1

    def check_files(self):
        self.video_file_paths = []
        for video_file in tqdm(self.video_files, desc='Checking video files...'):
            video_file_path = Path(video_file)
            assert video_file_path.exists(), f"File {video_file_path.absolute()} doesn't exists!"
            self.video_file_paths.append(video_file_path)

    def get_video_info(self):

        for video_path in tqdm(self.video_file_paths, desc='Checking video file frames...'):
            video_frames = []
            video = cv2.VideoCapture(video_path.absolute().as_posix())
            self.video_file_fps.append(video.get(cv2.CAP_PROP_FPS))
            self.video_h.append(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.video_w.append(video.get(cv2.CAP_PROP_FRAME_WIDTH))

            while video.isOpened():
                ret, frame = video.read()
                if ret:
                    video_frames.append(frame)
                else:
                    break
            assert len(video_frames) == video.get(cv2.CAP_PROP_FRAME_COUNT), \
                f"Get {video_path.absolute()} frames doesn't match with its property!"
            self.video_file_frames.append(np.array(video_frames))

    def fill_video_frame(self):
        self.max_fps = max(self.video_file_fps)
        for video_file, video_fps, video_frames in tzip(self.video_file_paths, self.video_file_fps,
                                                        self.video_file_frames, desc='Filling video frames...'):
            inter_frames = self.max_fps / video_fps
            assert inter_frames > 0, f"Video file {video_file.absolute()} fps property maybe is wrong!: {video_fps}"
            if inter_frames % 1 == 0:
                self.video_aligned_frames.append(video_frames.repeat(inter_frames, axis=0))
            else:
                # TODO
                raise "Haven't implement"
        self.video_aligned_frames = np.array(self.video_aligned_frames)

    def combine_videos(self):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        width = len(self.video_w) * self.video_w[0]
        height = self.video_h[0]
        width, height = int(width), int(height)
        video_writer = cv2.VideoWriter(self.dst_file, fourcc, self.max_fps, (width, height))
        for frame_num in tqdm(range(len(self.video_aligned_frames[0]))):
            frames = self.video_aligned_frames[:, frame_num]
            add_fps_txt = []
            for frame, fps in zip(frames, self.video_file_fps):
                frame = cv2.putText(frame, f'{fps} FPS', (10, 10), cv2.FONT_HERSHEY_PLAIN, 1.0, (0, 0, 255), 2)
                add_fps_txt.append(frame)
            frame = cv2.hconcat(add_fps_txt)
            video_writer.write(frame)
        video_writer.release()

    def run(self):
        self.check_files()
        self.get_video_info()
        self.fill_video_frame()
        self.combine_videos()


if __name__ == '__main__':
    video_files = [
        rf'/home/ningboo/Downloads/10fps_co_track.mp4',
        rf'/home/ningboo/Downloads/20fps_co_track.mp4',
        # rf'/home/ningboo/Downloads/30fps_co_track.mp4',
    ]

    dst_file = rf'./align.mp4'
    align_tool = AlignFps(dst_file, video_files)
    align_tool.run()
