import os
import matplotlib
import matplotlib.pyplot as plt

matplotlib.rc('font', family='FangSong', weight='bold')

all_labels = set([])
all_labels_num = {}

exists_labels = []


def static_labels(file_name: str):
    with open(file_name, 'r') as f:
        contents = f.readlines()
        for line in contents:
            line = line.strip()
            line = line.split(' ')
            all_labels.add(line[0])
            if line[0] in all_labels_num:
                all_labels_num[line[0]] = all_labels_num[line[0]] + 1
            else:
                all_labels_num[line[0]] = 1


def get_file_absolute_path(root_path: str):
    root_dir = os.walk(root_path)
    for path, dir_list, file_list in root_dir:
        for file_name in file_list:
            if file_name.endswith('.txt'):
                static_labels(os.path.join(path, file_name))


dir_list = [
    rf'/yolo/format/data/path',
]

cls_names = ['person',]

if __name__ == '__main__':
    exists = {}
    for d in dir_list:
        get_file_absolute_path(d + '/labels')
    print(f'所有标签：{len(all_labels)}')
    print(f'所有标签：{all_labels}')
    print(f'所有标签数量：{all_labels_num}')

    for item in all_labels:
        if item not in exists_labels:
            exists_labels.append(item)

    print(f'合并后标签数：{len(exists_labels)}')
    print(f'合并后标签：{exists_labels}')

    exists_labels.sort(key=lambda x: int(x))
    instance_num = []
    label_tag = []
    for k in exists_labels:
        instance_num.append(all_labels_num[k])
        label_tag.append(cls_names[int(k)])
    plt.figure(figsize=(8, 6))

    for b, i in zip(instance_num, range(len(label_tag))):  # zip 函数
        plt.text(i, b + 10, str(instance_num[i]), ha='center', fontsize=14)  # plt.text 函数

    plt.xticks(range(len(label_tag)), label_tag, rotation=45)
    plt.bar(range(len(exists_labels)), instance_num, width=0.6, )
    plt.show()

    print(f'排序后标签数：{instance_num}')
    print(f'排序后标签：{exists_labels}')
