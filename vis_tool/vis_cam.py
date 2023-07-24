import cv2
import platform


class Camera:
    def __init__(self, _cam_dev: [str, int], _frame_size_w_h: tuple = (640, 480), _fps=60):
        self.cam_dev = _cam_dev
        self.fps = _fps
        self.frame_w, self.frame_h = _frame_size_w_h
        self.cam_app = self.get_hardware_type()
        self.dev_str = None
        if self.cam_app == cv2.CAP_GSTREAMER:
            self.dev_link_info = f"v4l2src device={self.cam_dev} ! image/jpeg, width={self.frame_w}, height={self.frame_h}, framerate={self.fps}/1 ! jpegdec ! videoconvert ! video/x-raw, format=BGR ! appsink"
            print(self.dev_link_info)
        else:
            self.dev_link_info = self.cam_dev

    @staticmethod
    def get_hardware_type():
        if 'Linux' in platform.platform():
            return cv2.CAP_GSTREAMER
        else:
            return cv2.CAP_DSHOW

    def run(self):
        cam_stream = cv2.VideoCapture(self.cam_dev)
        cv2.namedWindow(self.cam_dev)
        cv2.moveWindow(self.cam_dev, 0, 0)

        while cam_stream.isOpened():
            ret, frame = cam_stream.read()
            if not ret:
                continue
            cv2.imshow(self.cam_dev, frame)
            keyboard_input = cv2.waitKey(1)
            if keyboard_input == ord('q'):
                cv2.destroyAllWindows()
                break


if __name__ == "__main__":
    cam_dev = rf"/dev/video0"
    cam = Camera(cam_dev)
    cam.run()

