import os

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
    rf'J:\train_dataset\2023_07_05_five_cls\five_cls\classification',
]

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

    for i in range(len(all_labels_num.keys())):
        print(f"{exists_labels[i]}:{all_labels_num[i]}")

    print(f'合并后标签数：{len(exists_labels)}')
    print(f'合并后标签：{exists_labels}')
