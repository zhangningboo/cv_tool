#include "opencv2/opencv.hpp"
#include "opencv2/aruco.hpp"
#include "opencv2/aruco/dictionary.hpp"
#include "yaml-cpp/yaml.h"


int main() {
    std::string camera_parameter = "/mnt/e/workspace-clion/cv_tool/ar_pose/aruco_det/camera.yaml";
    // Open the YAML file
    std::ifstream fin(camera_parameter);
    if (!fin.is_open()) {
        std::cerr << "Failed to open YAML file: " << camera_parameter << std::endl;
        return -1;
    }

    // Read camera parameters
    cv::Mat cameraMatrix, distortionCoeffs;

    // Parse the YAML file
    try {
        YAML::Node yamlNode = YAML::Load(fin);


        // Extract data from YAML nodes
        const YAML::Node &cameraMatrixNode = yamlNode["camera_matrix"];
        const YAML::Node &distortionCoeffsNode = yamlNode["distortion_coefficients"];

        // Check if the nodes exist and have the correct type
        if (cameraMatrixNode && cameraMatrixNode.IsMap()) {
            // Extract data from cameraMatrixNode
            // Assuming the node structure is [rows, cols, data]
            int rows = cameraMatrixNode["rows"].as<int>();
            int cols = cameraMatrixNode["cols"].as<int>();
            cv::Mat_<double> cameraMatrixData(rows, cols);
            for (int i = 0; i < rows; ++i) {
                for (int j = 0; j < cols; ++j) {
                    cameraMatrixData(i, j) = cameraMatrixNode["data"][i * cols + j].as<double>();
                }
            }
            // Assign the data to cameraMatrix
            cameraMatrix = cameraMatrixData;
        }

        if (distortionCoeffsNode && distortionCoeffsNode.IsMap()) {
            // Extract data from distortionCoeffsNode
            // Assuming the node structure is [rows, cols, data]
            int rows = distortionCoeffsNode["rows"].as<int>();
            int cols = distortionCoeffsNode["cols"].as<int>();
            cv::Mat_<double> distortionCoeffsData(rows, cols);
            for (int i = 0; i < rows; ++i) {
                for (int j = 0; j < cols; ++j) {
                    distortionCoeffsData(i, j) = distortionCoeffsNode["data"][i * cols + j].as<double>();
                }
            }
            // Assign the data to distortionCoeffs
            distortionCoeffs = distortionCoeffsData;
        }

        // Output camera parameters
        std::cout << "Camera Matrix:\n" << cameraMatrix << std::endl;
        std::cout << "Distortion Coefficients:\n" << distortionCoeffs << std::endl;
    } catch (const YAML::Exception &e) {
        std::cerr << "Error parsing YAML file: " << e.what() << std::endl;
        fin.close();  // Close the file
        return -1;
    }

    // Close the file
    fin.close();


    auto aruco_dict = cv::aruco::getPredefinedDictionary(cv::aruco::DICT_5X5_250);
    auto parameters = cv::aruco::DetectorParameters::create();
    cv::Mat image = cv::imread("/mnt/e/workspace-clion/cv_tool/ar_pose/aruco_det/DICT_5X5_250_14_test.png");

    // 检测ArUco标记
    std::vector<std::vector<cv::Point2f>> corners;
    std::vector<int> ids;
    cv::aruco::detectMarkers(image, aruco_dict, corners, ids, parameters);

    // 绘制检测结果
    cv::aruco::drawDetectedMarkers(image, corners, ids);

    if (!ids.empty()) {
        std::vector<cv::Vec3d> rvecs, tvecs;
        cv::aruco::estimatePoseSingleMarkers(corners, 0.05, cameraMatrix, distortionCoeffs, rvecs, tvecs);

        // Draw marker poses on the image
        for (size_t i = 0; i < ids.size(); ++i) {
            cv::aruco::drawAxis(image, cameraMatrix, distortionCoeffs, rvecs[i], tvecs[i], 0.1);
        }
    }

    // 显示结果
    cv::imshow("ArUco Detection", image);
    cv::waitKey(0);
    cv::destroyAllWindows();
    return 0;
}