import os
import cv2
from pathlib import Path


class Video2Image:

    def __init__(self, src_video_file: str, dst_image_path=None):
        assert isinstance(src_video_file, (str,))
        self.src_video_file = Path(src_video_file)
        if dst_image_path is None:
            dst_path = self.src_video_file.parent.joinpath(f'{self.src_video_file.name}_frames')
            dst_path.mkdir(exist_ok=True)
            self.dst_image_path = dst_path

    def run(self):
        if not os.path.isfile(self.src_video_file):
            raise f'Video File is not exists: {self.src_video_file}'
        cap = cv2.VideoCapture(self.src_video_file.absolute().as_posix())
        cnt = 0
        prefix = os.path.basename(self.src_video_file) + '_'
        while True:
            ret, frame = cap.read()
            if ret:
                h, w, _ = frame.shape
                # frame = cv2.resize(frame, (w * 2, h * 2))
                # frame = cv2.resize(frame, (w, h))
                image = os.path.join(self.dst_image_path, prefix + str(cnt) + '.jpg')
                cv2.imencode(os.path.splitext(image)[1], frame)[1].tofile(image)
                cnt += 1
                print(image)
            else:
                break


if __name__ == '__main__':
    src_video_file = rf"E:\Videos\2022_09_05_18_02_54_left.mp4"
    Video2Image(src_video_file=src_video_file).run()
