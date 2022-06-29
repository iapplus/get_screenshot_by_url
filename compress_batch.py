import cv2

src =cv2.imread("./images/bktour.cz.png", 1)
cv2.imwrite("./saveImg.jpg", src, [cv2.IMWRITE_PNG_COMPRESSION, 3])