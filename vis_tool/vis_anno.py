from PIL import Image, ImageDraw, ImageFont
import random
import platform

system_version = platform.platform()
if 'Linux' in system_version:
    font_file = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
elif 'macOS' in system_version:
    font_file = "/System/Library/Fonts/Monaco.ttf"
elif 'Windows':
    font_file = 'C:/Windows/Fonts/msyhbd.ttc'
else:
    raise NotImplemented

font = ImageFont.truetype(font_file, 22)


def get_font_render_size(text):
    canvas = Image.new('RGB', (600, 100))
    draw = ImageDraw.Draw(canvas)
    draw.text((0, 0), text, font=font, fill=(255, 255, 255))
    bbox = canvas.getbbox()
    # 宽高
    return bbox[2] - bbox[0] + 4, bbox[3] - bbox[1] + 6


def draw_img(draw, label, tp_x, tp_y, br_x, br_y):
    print(label, tp_x, tp_y, br_x, br_y)
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

    img_path = rf"/data/sdb1/dataset/dust_action/yolo_cleaner/images/94ba07c2-7baf-4f43-966d-c201a3508132_999.jpg"
    ann_path = rf"/data/sdb1/dataset/dust_action/yolo_cleaner/labels/94ba07c2-7baf-4f43-966d-c201a3508132_999.txt"

    image = Image.open(img_path)
    W, H = image.size
    print(W, H)

    ann = []
    with open(ann_path, 'r', encoding='UTF-8') as f:
        lines = f.readlines()
        for idx, line in enumerate(lines):
            print(idx + 1, line)
            ann.append(line.strip().split(' '))
    draw = ImageDraw.Draw(image)

    # func = vis_cls_xywh
    func = vis_cls_cxcywh
    # func = vis_cls_x1y1x2y2
    print(func.__name__)
    func(ann, draw, H, W)
    image.save('./tmp.jpg')
