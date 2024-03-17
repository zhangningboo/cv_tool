import cv2

squaresX, squaresY = 5, 9
squareLength, markerLength = 0.100, 0.080
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_100)
charuco_board = cv2.aruco.CharucoBoard((squaresX, squaresY), squareLength, markerLength, dictionary)
board_img = cv2.aruco.drawPlanarBoard(charuco_board, (1080, 1920), 10, 10)

cv2.imshow('board_img', board_img)
cv2.waitKey(0)
cv2.destroyAllWindows()
