import os
import json
from pathlib import Path
from glob import glob
import yaml
import numpy as np
import cv2
from nuscenes.nuscenes import NuScenes
from nuscenes.utils.data_classes import Box

import numpy as np

def rotation_matrix_to_quaternion(R: np.array):
    """
    Convert a 3x3 rotation matrix to a quaternion.

    Args:
        R (numpy.ndarray): A 3x3 rotation matrix.

    Returns:
        numpy.ndarray: A 4-dimensional quaternion [w, x, y, z].
    """
    trace = R.trace()
    if trace > 0:
        S = np.sqrt(trace + 1.0) * 2.0
        qw = 0.25 * S
        qx = (R[2, 1] - R[1, 2]) / S
        qy = (R[0, 2] - R[2, 0]) / S
        qz = (R[1, 0] - R[0, 1]) / S
    elif R[0, 0] > R[1, 1] and R[0, 0] > R[2, 2]:
        S = np.sqrt(1.0 + R[0, 0] - R[1, 1] - R[2, 2]) * 2.0
        qw = (R[2, 1] - R[1, 2]) / S
        qx = 0.25 * S
        qy = (R[0, 1] + R[1, 0]) / S
        qz = (R[0, 2] + R[2, 0]) / S
    elif R[1, 1] > R[2, 2]:
        S = np.sqrt(1.0 + R[1, 1] - R[0, 0] - R[2, 2]) * 2.0
        qw = (R[0, 2] - R[2, 0]) / S
        qx = (R[0, 1] + R[1, 0]) / S
        qy = 0.25 * S
        qz = (R[1, 2] + R[2, 1]) / S
    else:
        S = np.sqrt(1.0 + R[2, 2] - R[0, 0] - R[1, 1]) * 2.0
        qw = (R[1, 0] - R[0, 1]) / S
        qx = (R[0, 2] + R[2, 0]) / S
        qy = (R[1, 2] + R[2, 1]) / S
        qz = 0.25 * S

    return np.array([qw, qx, qy, qz])

class CameraIntrinsic:
    def __init__(self, width, height, focal_length, principal_point, distortion_coeffs):
        self.width = width
        self.height = height
        self.focal_length = focal_length
        self.principal_point = principal_point
        self.distortion_coeffs = distortion_coeffs

class CameraExtrinsic:
    def __init__(self, rotation, translation):
        self.rotation = rotation
        self.translation = translation

def readListInFileNode(filenode):
    assert(filenode.isSeq())
    res = []
    for i in range(filenode.size()):
        res.append(filenode.at(i).real())
    return res

# 定义类别映射函数、内外参转换函数等辅助函数...
def extract_and_convert_calibrations(calibration_dir: Path):
    camera_calibrations = []
    # 遍历yaml文件
    for yaml_file in calibration_dir.glob('*.yaml'):
        cv_data = cv2.FileStorage(yaml_file.absolute().as_posix(), cv2.FILE_STORAGE_READ)
        calib_data = {
                "CameraExtrinsicMat": cv_data.getNode("CameraExtrinsicMat").mat(),
                "CameraMat": cv_data.getNode("CameraMat").mat(),
                "DistCoeff": cv_data.getNode("DistCoeff").mat(),
                "ImageSize": readListInFileNode(cv_data.getNode("ImageSize")),
                "ReprojectionError": cv_data.getNode("ReprojectionError").real(),
                "DistModel": cv_data.getNode("DistModel").string()
        }
        # 提取内参
        # fx,  0,   cx
        # 0,   fy,  cy
        # 0,   0,   1
        intrinsic_dict = calib_data['CameraMat']
        focal_length = (intrinsic_dict[0][0], intrinsic_dict[1][1])  # fx, fy
        principal_point = (intrinsic_dict[0][2], intrinsic_dict[1][2])  # cx, cy
        distortion_coeffs = calib_data['DistModel']  # 假设为径向畸变系数列表
        width, height = calib_data['ImageSize']
        camera_intrinsics = CameraIntrinsic(
            width=width,  # 假设yaml文件中提供了图像宽度和高度
            height=height,
            focal_length=focal_length,
            principal_point=principal_point,
            distortion_coeffs=distortion_coeffs
        )
        
        # 提取外参
        extrinsic_dict = calib_data['CameraExtrinsicMat']
        rotation_matrix = extrinsic_dict[:, :3][:-1].reshape(3, 3)  # 假设R为3x3旋转矩阵列表
        rotation_matrix_to_quaternion(rotation_matrix)
        translation_vector = extrinsic_dict[:, -1][:-1]  # 假设T为平移向量列表

        camera_extrinsic = CameraExtrinsic(
            rotation=rotation_matrix,
            translation=translation_vector
        )

        # 组合内参和外参
        camera_calibration = {
            'camera_intrinsic': camera_intrinsics,
            'camera_extrinsic': camera_extrinsic,
            'camera_channel': os.path.splitext(os.path.basename(yaml_file))[0],  # 假设文件名即为相机通道标识
        }
        camera_calibrations.append(camera_calibration)
    return camera_calibrations

def convert_data(root_path: Path, output_path: Path):
    # 初始化nuScenes数据集对象
    nusc = NuScenes(version='v1.0-mini', dataroot=output_path.absolute().as_posix(), verbose=True)

    # 读取和处理calibration文件夹下的内外参数据
    camera_calibrations = extract_and_convert_calibrations(root_path.joinpath('calibration'))

    # 创建并填充cameras.json
    write_cameras_json(camera_calibrations, output_path.joinpath('cameras.json'))

    # 遍历image文件夹，重命名、移动图像，同时处理时间戳和关联标注
    for cam_folder in ['cam1', 'cam2', ...]:  # 替换为实际摄像头文件夹名
        img_files = glob(os.path.join(root_dir, 'image', cam_folder, '*.jpg'))
        for img_file in img_files:
            img_timestamp, img_channel = extract_timestamp_and_channel(img_file)
            # 重命名、移动图像
            new_img_path = ...
            os.rename(img_file, new_img_path)

            # 读取并转换关联的标注
            gt_json_file = find_associated_gt_json(img_file)  # 实现此函数以找到对应标注文件
            annotations = parse_gt_json(gt_json_file)
            nu_annotations = convert_annotations(annotations, img_timestamp)

            # 将转换后的标注写入samples.json
            nusc.add_sample_data(new_img_path, cam_channel=img_channel, annotations=nu_annotations)

    # 对pcd文件夹中的点云数据进行类似的处理，包括重命名、移动、关联标注等

    # 最后，保存nuscenes对象，生成必要的元信息文件
    nusc.export(os.path.join(output_dir, 'my_dataset'))

def main():
    root_dir = rf'/Users/zhangningboo/workspace/workspace-code/cv_tool/cvt_fmt/nuscenes/bev/mnt/data'
    output_dir = '/Users/zhangningboo/workspace/workspace-code/cv_tool/cvt_fmt/nuscenes/output'
    root_path = Path(root_dir)
    output_path = Path(output_dir)
    extract_and_convert_calibrations(root_path.joinpath('calibration'))
    # convert_data(root_path, output_path)

if __name__ == '__main__':
    main()