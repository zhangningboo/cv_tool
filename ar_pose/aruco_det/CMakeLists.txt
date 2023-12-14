cmake_minimum_required(VERSION 3.22)
project(aruco_det)

find_package(OpenCV REQUIRED)
find_package(yaml-cpp REQUIRED)

message(${OpenCV_INCLUDE_DIRS})
message(${OpenCV_LIBS})

include_directories(${OpenCV_INCLUDE_DIRS} ${YAML_CPP_INCLUDE_DIR})

add_executable(${PROJECT_NAME} src/main.cpp)

target_link_directories(${PROJECT_NAME} PRIVATE ${OpenCV_INCLUDE_DIRS} ${YAML_CPP_INCLUDE_DIR})
target_link_libraries(${PROJECT_NAME} PRIVATE ${OpenCV_LIBS} yaml-cpp)