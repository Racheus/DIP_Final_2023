import sys
import cv2
import numpy as np
import tensorflow as tf
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QWidget, QHBoxLayout

# Load the pre-trained model
model = tf.keras.models.load_model('model9543.h5')

class GestureRecognitionApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Gesture Recognition-DIP2023 Final Work")
        self.setGeometry(100, 100, 1200, 600)

        self.videoLabel = QLabel(self)
        self.resultTextEdit = QTextEdit(self)
        self.usageTextEdit = QTextEdit(self)  # 新添加的文本框
        self.exitButton = QPushButton("Exit", self)

        layout = QHBoxLayout()
        layout.addWidget(self.videoLabel)

        rightLayout = QVBoxLayout()
        rightLayout.addWidget(self.usageTextEdit)  # 新文本框的位置
        rightLayout.addWidget(self.exitButton)
        rightLayout.addWidget(self.resultTextEdit)

        layout.addLayout(rightLayout)

        widget = QWidget(self)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # 设置文本框内容
        self.usageTextEdit.setFixedHeight(200) 
        self.resultTextEdit.setFixedHeight(300)
        self.usageTextEdit.setPlainText("使用说明：请尽量在白色背景（如墙壁）下使用此识别程序。\nThank you for your using! \n Author : Racheus Zhao\n Class : AU3304-01")


        self.capture = cv2.VideoCapture(0)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.showFrame)
        self.timer.start(30)

        self.exitButton.clicked.connect(self.exit)

    def apply_skin_detection(self, image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        lower_skin = np.array([0, 12, 20], dtype=np.uint8)
        upper_skin = np.array([25, 255, 255], dtype=np.uint8)

        skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)

        kernel = np.ones((2, 2), np.uint8)
        skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_OPEN, kernel)
        contours, _ = cv2.findContours(skin_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(image, contours, -1, (0, 255, 0), 2)
        return image

    def apply_canny_edge_detection(self, image):
        edges = cv2.Canny(image, 120, 200)
        return edges

    def showFrame(self):
        ret, frame = self.capture.read()
        if ret:
            frame = cv2.flip(frame, 1)  # 非镜像显示
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape

            # 肤色检测
            skin_detection_result = self.apply_skin_detection(rgb_image)

            # 边缘检测
            edges = self.apply_canny_edge_detection(skin_detection_result)

            # 调整图像大小为模型需要的输入大小
            image = cv2.resize(edges, (300, 300))
            image = image / 255.0  # 将像素值归一化到 [0, 1] 范围内
            image = np.expand_dims(image, axis=0)

            # 使用模型进行手势识别
            output = model.predict(image)
            predicted = np.argmax(output, axis=1)

            gesture_label = ["Paper", "Scissors", "Rock"]
            result = gesture_label[predicted[0]]

            # 在实时画面上绘制识别结果
            cv2.putText(rgb_image, result, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

            # 在文本框中显示识别结果
            self.resultTextEdit.setText(result)

            # 显示处理后的图像
            q_image = QImage(rgb_image.data, w, h, QImage.Format_RGB888)
            self.videoLabel.setPixmap(QPixmap.fromImage(q_image))

    def exit(self):
        self.capture.release()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GestureRecognitionApp()
    window.show()
    sys.exit(app.exec_())
