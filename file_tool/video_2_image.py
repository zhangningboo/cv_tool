import os
import cv2
from pathlib import Path
import random


class Video2Image:

    def __init__(self, src_video_file: str, dst_image_path=None, extract_frame=False, resize_half=False):
        assert isinstance(src_video_file, (str,))
        self.src_video_file = Path(src_video_file)
        self.extract_frame = extract_frame
        self.resize_half = resize_half
        if dst_image_path is None:
            self.dst_image_path = self.src_video_file.parent.joinpath(f'{self.src_video_file.name}_frames')
        else:
            self.dst_image_path = Path(dst_image_path)
        self.dst_image_path.mkdir(exist_ok=True)

    def run(self, cnt = 0):
        assert f'Video File is not exists: {self.src_video_file}'
        cap = cv2.VideoCapture(self.src_video_file.absolute().as_posix())
        cap.set(cv2.CAP_PROP_POS_FRAMES, cnt)
        total_num = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if self.extract_frame:
            interval_frame_cnt = 100 if total_num >= 1000 else 20
            frame_index = [random.randint(0, interval_frame_cnt // 2) + i for i in list(range(total_num))[::interval_frame_cnt]]
            print(frame_index)
            if frame_index[-1] >= total_num:
                frame_index[-1] = total_num - 1
        else:
            frame_index = range(total_num)

        prefix = os.path.basename(self.src_video_file) + '_'

        for idx in frame_index:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if not ret:
                break
            if self.resize_half:
                h, w, _ = frame.shape
                frame = cv2.resize(frame, (w // 2, h // 2))
            image_path = os.path.join(self.dst_image_path, prefix + str(idx) + '.jpg')
            cv2.imencode(os.path.splitext(image_path)[1], frame)[1].tofile(image_path)
            print(image_path)


if __name__ == '__main__':
    src_video_file = rf"/Volumes/WD_BLACK/dataset/public_fire_smoke/20240925_Visfire/Smoke_Manavgat_Raw.avi"
    dst_image_path = rf"/Volumes/WD_BLACK/dataset/public_fire_smoke/20240925_Visfire/Smoke_Manavgat_Raw"
    Video2Image(src_video_file=src_video_file, dst_image_path=dst_image_path, extract_frame=True).run(cnt=0)
