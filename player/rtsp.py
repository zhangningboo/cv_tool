import cv2
import argparse

# --onefile --console
class OpenRTSP:

    def __init__(self, rtsp_url: str):
        self.rtsp_url = rtsp_url

    def view(self):
        cap = cv2.VideoCapture(self.rtsp_url)
        assert cap.isOpened()
        window = cv2.namedWindow('RTSP')
        q, Q = ord('q'), ord('Q')
        cnt = 0
        while True:
            ret, frame = cap.read()
            cnt += 1
            if ret:
                cv2.imshow(window, frame)
                k = cv2.waitKey(1)
                if k == Q or k == q:
                    cv2.destroyAllWindows()
                    break
            else:
                print(f'Failed read image, {cnt = }')


def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rtsp", type=str, default="", required=True, help="rtsp url like: rtsp://ip/path")
    opt = parser.parse_args()
    return opt


if __name__ == '__main__':
    arg = parse_opt()
    arg.rtsp = rf'ws://172.16.16.200:9080/?nodeType=GB28181&type=real_Platform&channel=51018201581314000811&'
    rtsp_client = OpenRTSP(arg.rtsp)
    rtsp_client.view()
