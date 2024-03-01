from pathlib import Path
import cv2
from tqdm import tqdm


class Images2Video:

    def __init__(self, images_dir: str,
                 images_name_prefix: str = None,
                 images_sort_func=None,
                 video_dir: str = None,
                 fps: int = 60):
        self.images_path = Path(images_dir)
        self.images_name_prefix = images_name_prefix
        self.video_path = Path(video_dir) if video_dir is not None else None
        self.fps = fps
        self.images_sort_func = images_sort_func

        self.images = []

    def gather_images(self):
        regex = f'{self.images_name_prefix}*' if self.images_name_prefix is not None else '*'
        self.images = [f.absolute().as_posix() for f in self.images_path.glob(regex)]

        if self.images_sort_func is not None:
            self.images.sort(key=self.images_sort_func)
        assert len(self.images) > 1

    def cvt_2_video(self):
        first_frame_path = self.images[0]
        first_frame = cv2.imread(first_frame_path)
        h, w, _ = first_frame.shape

        if self.video_path is None:
            if self.images_name_prefix is None:
                video_name = self.images_path.name + '.mp4'
            else:
                video_name = self.images_name_prefix + '.mp4'
            self.video_path = self.images_path.joinpath(video_name)

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(self.video_path.absolute().as_posix(), fourcc, self.fps, (w, h))
        for image_path in tqdm(self.images):
            frame = cv2.imread(image_path)
            video_writer.write(frame)
        video_writer.release()

    def run(self):
        self.gather_images()
        self.cvt_2_video()


def images_sort_func(file_name):
    return int(file_name.split('_')[-1].replace('.jpg', ''))  # 排序： xxxx_xx_xx_timestamp_123.jpg


if __name__ == '__main__':
    image_dir = rf'E:\Videos\111'
    images_name_prefix = rf'2022_09_05_18_02_54_left'

    images2video = Images2Video(image_dir, images_name_prefix=images_name_prefix, images_sort_func=images_sort_func)
    images2video.run()
