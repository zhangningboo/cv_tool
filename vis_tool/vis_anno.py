from PIL import Image, ImageDraw, ImageFont
import random

font = ImageFont.truetype('/usr/share/fonts/TTF/JetBrainsMonoNLNerdFontMono-LightItalic.ttf', 22)


def get_font_render_size(text):
    canvas = Image.new('RGB', (600, 100))
    draw = ImageDraw.Draw(canvas)
    draw.text((0, 0), text, font=font, fill=(255, 255, 255))
    bbox = canvas.getbbox()
    # 宽高
    size = (bbox[2] - bbox[0] + 4, bbox[3] - bbox[1] + 6)
    return size


def draw_img(draw, label, tp_x, tp_y, br_x, br_y):
    # print(label, " x1_y1_x2_y2:", tp_x, tp_y, br_x, br_y)
    w = br_x - tp_x
    h = br_y - tp_y
    print(label, " x1_y1_w_h:", ', '.join(map(str, [tp_x, tp_y, w, h])))
    tp_x, tp_y, br_x, br_y = map(int, [tp_x, tp_y, br_x, br_y])
    color = [random.randint(0, 255) for _ in range(3)]
    # box
    draw.rectangle(((tp_x, tp_y), (br_x, br_y)), width=3, outline=tuple(color))
    tw, th = get_font_render_size(label)
    rec_top = (tp_x, max(0, tp_y - th))
    rec_bot = (tp_x + tw, tp_y)
    draw.rectangle((rec_top, rec_bot), fill=tuple(color))
    draw.text(rec_top, text=label, font=font, fill=(255, 255, 255))


def vis_cls_x1y1x2y2(annos, draw, H, W):
    for cls, x1, y1, x2, y2 in annos:
        if float(x1) <= 1 and float(y1) <= 1 and float(x2) <= 1 and float(y2) <= 1:
            x1, y1, x2, y2 = map(float, [x1, y1, x2, y2])
            x1 *= W
            y1 *= H
            x2 *= W
            y2 *= H
        else:
            x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
        draw_img(draw, cls, x1, y1, x2, y2)


def vis_cls_xywh(annos, draw, H, W):
    for cls, x, y, w, h in annos:
        x, y, w, h = map(float, [x, y, w, h])
        if w <= 1 and h <= 1:
            x *= W
            y *= H
            w *= W
            h *= H
        tp_x = x
        tp_y = y
        br_x = x + w
        br_y = y + h
        print(cls, "x1_y1_w_h", x, y, w, h, "x1_y1_x2_y2:", tp_x, tp_y, br_x, br_y)
        draw_img(draw, cls, tp_x, tp_y, br_x, br_y)


def vis_cls_cxcywh(annos, draw, H, W):
    for cls, cx, cy, w, h in annos:
        cx, cy, w, h = map(float, [cx, cy, w, h])
        if w < 1 and h < 1:
            cx *= W
            cy *= H
            w *= W
            h *= H
        cx, cy, w, h = map(int, [cx, cy, w, h])
        tp_x = cx - w // 2
        tp_y = cy - h // 2
        br_x = cx + w // 2
        br_y = cy + h // 2
        draw_img(draw, cls, tp_x, tp_y, br_x, br_y)


if __name__ == '__main__':
    # ann_path = r"D:\ningd\Downloads\archive\coco128\labels\train2017\000000000034.txt"
    # img_path = r"D:\ningd\Downloads\archive\coco128\images\train2017\000000000034.jpg"

    # ann_path = r"D:\workspace\workspace-pycharm\dataset_util\src\dataset_trans_util\000000016228.txt"
    # img_path = r"D:\workspace\workspace-pycharm\dataset_util\src\dataset_trans_util\000000016228.jpg"

    # ann_path = r"N:\20230530冰箱数据1\2022_04_21_17_57_37_left_0200.txt"
    # ann_path = r"H:\workspace-pycharm\ultralytics\runs\detect\predict4\labels\2023_06_30_17_18_58_right.avi_14.txt"
    # img_path = r"J:\big_model_test\获取到的视频\2023_06_30_17_18_58_right.avi_imgs\2023_06_30_17_18_58_right.avi_14.jpg"

    img_path = rf"/home/ningboo/Downloads/val2017/000000397133.jpg"
    ann_path = rf"/data/workspace/workspace-pycharm/ai/cv_tool/vis_tool/000000397133.txt"

    image = Image.open(img_path)
    W, H = image.size

    ann = []
    with open(ann_path, 'r', encoding='UTF-8') as f:
        lines = f.readlines()
        for idx, line in enumerate(lines):
            ann.append(line.strip().split(' '))
    draw = ImageDraw.Draw(image)

    func = vis_cls_xywh
    # func = vis_cls_cxcywh
    # func = vis_cls_x1y1x2y2
    print(func.__name__)
    func(ann, draw, H, W)
    image.show(title=str(func.__name__))
