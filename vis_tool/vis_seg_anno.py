import random

from PIL import Image, ImageDraw


def parse_txt(_txt_path):
    """
    解析seg txt文件
    txt文件格式: cls, p1_x, p1_y, p2_x, p2_y, ...
    :param _txt_path:
    :return: [cls, (p1_x, p1_y), (p2_x, p2_y), ...]
    """
    _anno = []
    with open(_txt_path, 'r') as f:
        _lines = f.readlines()
        for _line in _lines:
            seg_instance = []
            _content = _line.strip().split(' ')
            cls = _content[0]
            seg_instance.append(cls)
            for i in range(len(_content[1:]) // 2):
                seg_instance.append((int(_content[1 + 2 * i]), int(_content[2 + 2 * i])))
            _anno.append(seg_instance)
    return _anno


def draw_seg_anno(_img_path, _annos):
    """
    绘制seg标注结果
    :param _img_path: 图片路径
    :param _annos: 标注结果，格式: [[cls, (p1_x, p1_y), (p2_x, p2_y), ...], [cls, (p1_x, p1_y), (p2_x, p2_y), ...], ...]
    :return: 绘制好的图片
    """
    _img = Image.open(_img_path)
    _draw = ImageDraw.Draw(_img)
    for _anno in _annos:
        color = [random.randint(0, 255) for _ in range(3)]
        color = tuple(color)
        _cls = _anno[0]
        _points = _anno[1:]
        for _p in _points:
            _draw.ellipse((_p[0] - 2, _p[1] - 2, _p[0] + 2, _p[1] + 2), fill=color, outline=color)
    return _img


if __name__ == '__main__':
    img_path = rf"/path/to/image"
    txt_path = rf"/path/to/anno"

    anno = parse_txt(txt_path)
    img = draw_seg_anno(img_path, anno)
    img.show()

