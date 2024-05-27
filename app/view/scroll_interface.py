# coding:utf-8
from PyQt5.QtCore import Qt, QEasingCurve, pyqtSignal
from PyQt5.QtGui import QPixmap, QColor, QImage
from PyQt5.QtWidgets import QWidget, QGridLayout, QHBoxLayout, QVBoxLayout, QFileDialog, QLineEdit
from qfluentwidgets import (SingleDirectionScrollArea, SmoothScrollArea, ToolTipFilter, PixmapLabel,
                            ScrollArea, ImageLabel, HorizontalPipsPager, PipsScrollButtonDisplayMode, VerticalPipsPager,
                            PushButton)

from .gallery_interface import GalleryInterface
from ..common.translator import Translator
import numpy as np
import cv2
import rawpy
from PIL import Image
from ..utils.common import *


# from app.utils.common. import

def get_qimage_from_raw(raw_file_path):
    with rawpy.imread(raw_file_path) as raw:
        img = pack_raw_bayer(raw)
        wb, ccm = read_wb_ccm(raw)
        ccm = np.array([[1.9712269, -0.6789218, -0.29230508],
                        [-0.29104823, 1.748401, -0.45735288],
                        [0.02051281, -0.5380369, 1.5175241]])
        # chw 2 hwc(bgr)
        img = raw2rgb_v2(img, wb, ccm).transpose(1, 2, 0)
    # hwc(bgr) 2 hwc(rbg)
    img = img[:, :, (2, 1, 0)] * 255
    print(img.shape)
    height, width, _ = img.shape
    img = img.astype(np.uint8)
    # print(img)
    img = img[:, :, ::-1]
    qimage = QImage(img.data.tobytes(), width, height, width * 3, QImage.Format_RGB888)

    return qimage


class ScrollInterface(GalleryInterface):
    """ Scroll interface """
    start_test_signal = pyqtSignal(str, str, str)

    def __init__(self, parent=None):
        t = Translator()
        super().__init__(
            title="单图片查看与测试",
            subtitle="",
            parent=parent
        )
        self.setObjectName('scrollInterface')

        self.test_file_path = "app/model/data/0009_U3_3200_10.CR2"
        self.test_model_path = "app/model/pretrained_model/500_G.pth"
        self.gt_file_path = ""
        # smooth scroll area
        w = SmoothScrollArea()
        self.label = ImageLabel(':/gallery/images/test/BIT_logo.png', self)
        # self.label.setBorderRadius(8, 8, 8, 8)
        # self.label.setScaledContents(True)
        # self.scale_factor = 1.0
        w.setWidget(self.label)
        w.setFixedSize(16 * 50, 9 * 50)

        card = self.getCard(self.tr(""), w)
        self.gt_file_line = QLineEdit("gt_file:")
        self.gt_file_line.setReadOnly(True)
        self.gt_file_line.setFixedHeight(30)
        self.pretrained_model_line = QLineEdit("pretrained_model:")
        self.pretrained_model_line.setReadOnly(True)
        self.pretrained_model_line.setFixedHeight(30)
        self.open_image_button = PushButton('打开图片')
        self.open_image_button.clicked.connect(self.open_image)
        self.start_test_button = PushButton('开始测试')
        self.start_test_button.clicked.connect(self.start_test)
        self.select_gt_file_button = PushButton('选择gt图片')
        self.select_gt_file_button.clicked.connect(self.select_gt_file)
        self.select_pretrained_model_button = PushButton("选择预训练模型")
        self.select_pretrained_model_button.clicked.connect(self.select_pretrained_model)

        gridLayout = QGridLayout()
        gridLayout.addWidget(self.open_image_button, 0, 0)
        gridLayout.addWidget(self.start_test_button, 0, 1)
        gridLayout.addWidget(self.select_gt_file_button, 1, 0)
        gridLayout.addWidget(self.gt_file_line, 1, 1)
        gridLayout.addWidget(self.select_pretrained_model_button, 2, 0)
        gridLayout.addWidget(self.pretrained_model_line, 2, 1)
        self.vBoxLayout.addLayout(gridLayout)
        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.setAlignment(Qt.AlignCenter)

    def open_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image File", "",
                                                   "Image Files (*.png *.jpg *.bmp *.CR2 *.ARW)")

        if file_path:
            self.test_file_path = file_path
            if self.test_file_path.split(".")[-1] in ["png", "jpg", "bmp", "PNG", "JPG", "BMP"]:
                pixmap = QPixmap(file_path)
                self.label.setPixmap(pixmap)
            else:
                qimage = get_qimage_from_raw(self.test_file_path)
                self.label.setImage(qimage)
                print("unsupported file type")

    def setImage(self, pixmap):
        self.label.setPixmap(pixmap)

    def start_test(self):
        print(self.objectName(), "start test")
        self.start_test_signal.emit(self.test_model_path, self.test_file_path, self.gt_file_path)

    def select_gt_file(self):
        options = QFileDialog.Options()
        self.gt_file_path, _ = QFileDialog.getOpenFileName(self, "Open JSON File", "",
                                                            "Image Files (*.png *.jpg *.bmp *.CR2 *.ARW)",
                                                            options=options)
        self.gt_file_line.setText("gt_file:" + self.gt_file_path)

    def select_pretrained_model(self):
        options = QFileDialog.Options()
        self.test_model_path, _ = QFileDialog.getOpenFileName(self, "Open pth File", "",
                                                              "pth Files (*.pth)",
                                                              options=options)
        self.pretrained_model_line.setText("pretrained_model:" + self.test_model_path)