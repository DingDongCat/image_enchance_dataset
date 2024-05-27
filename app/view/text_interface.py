# coding:utf-8
import json
import os

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QSyntaxHighlighter
from PyQt5.QtWidgets import QCompleter, QGridLayout, QFileDialog, QMessageBox
from qfluentwidgets import (LineEdit, SpinBox, DoubleSpinBox, TimeEdit, DateTimeEdit, DateEdit,
                            TextEdit, SearchLineEdit, PasswordLineEdit, PushButton, IndeterminateProgressBar)

from .gallery_interface import GalleryInterface
from ..common.translator import Translator


# from app.utils.common import start_test

class TextInterface(GalleryInterface):
    """ Text interface """
    start_multi_image_test_signal = pyqtSignal(dict)

    def __init__(self, parent=None):
        t = Translator()
        super().__init__(
            title="多图片测试配置",
            subtitle="",
            parent=parent
        )
        self.setObjectName('textInterface')

        # text edit
        self.jsonEdit = TextEdit(self)
        self.jsonEdit.setMarkdown("hello world")
        self.jsonEdit.setFixedHeight(300)
        # self.addExampleCard(
        #     title=self.tr("A simple TextEdit"),
        #     widget=textEdit,
        #     sourcePath='https://github.com/zhiyiYo/PyQt-Fluent-Widgets/blob/master/examples/text/line_edit/demo.py',
        #     stretch=1
        # )

        self.editCard = self.getCard(title=None, widget=self.jsonEdit, stretch=1)
        # self.bar = IndeterminateProgressBar(self)
        # self.bar.setFixedWidth(200)
        # self.barCard = self.getCard(title=None, widget=self.bar, stretch=1)
        self.json_load_button = PushButton('导入json')
        self.json_load_button.clicked.connect(self.json_load)
        self.json_save_button = PushButton('导出json')
        self.json_save_button.clicked.connect(self.json_save)
        self.start_test_button = PushButton("开始测试")
        self.start_test_button.clicked.connect(self.start_test)
        self.generate_test_file_list_button = PushButton("生成测试文件路径")
        self.generate_test_file_list_button.clicked.connect(self.generate_test_file_list)
        self.select_gt_file_button = PushButton("选择gt文件")
        self.select_gt_file_button.clicked.connect(self.select_gt_file)
        self.select_pretrained_model_button = PushButton("选择预训练模型")
        self.select_pretrained_model_button.clicked.connect(self.select_pretrained_model)
        gridLayout = QGridLayout()
        gridLayout.addWidget(self.json_load_button, 0, 0)
        gridLayout.addWidget(self.json_save_button, 0, 1)
        gridLayout.addWidget(self.start_test_button, 1, 0)
        gridLayout.addWidget(self.generate_test_file_list_button, 2, 0)
        gridLayout.addWidget(self.select_gt_file_button, 2, 1)
        gridLayout.addWidget(self.select_pretrained_model_button, 3, 0)
        self.vBoxLayout.addLayout(gridLayout)
        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.setAlignment(Qt.AlignCenter)

    def json_load(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Open JSON File", "", "JSON Files (*.json);;All Files (*)",
                                                  options=options)
        if fileName:
            try:
                with open(fileName, 'r', encoding='utf-8') as file:
                    data = file.read()
                    self.jsonEdit.setPlainText(data)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not load file: {e}")

    def json_save(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Save JSON File", "", "JSON Files (*.json);;All Files (*)",
                                                  options=options)
        if fileName:
            try:
                json_data = self.jsonEdit.toPlainText()
                parsed = json.loads(json_data)  # Verify that the content is valid JSON
                with open(fileName, 'w', encoding='utf-8') as file:
                    json.dump(parsed, file, indent=4)
                QMessageBox.information(self, "Success", "The JSON has been saved!")
            except json.JSONDecodeError as e:
                QMessageBox.critical(self, "Error", f"Invalid JSON: {e}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save file: {e}")

    def start_test(self):
        print(self.objectName(), "start multi image test")
        try:
            json_data = self.jsonEdit.toPlainText()
            parsed = json.loads(json_data)
            print(parsed)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Unsupported json config: {e}")
        self.start_multi_image_test_signal.emit(parsed)

    def generate_test_file_list(self):
        folder_path = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if folder_path:
            file_names = ["/".join([folder_path, f]) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
            print(file_names)
            try:
                json_data = self.jsonEdit.toPlainText()
                parsed = json.loads(json_data)
            except Exception as e:
                parsed = {}

            parsed["test_file_list"] = file_names
            self.jsonEdit.setPlainText(json.dumps(parsed))

    def select_gt_file(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Open JSON File", "",
                                                  "Image Files (*.png *.jpg *.bmp *.CR2 *.ARW)",
                                                  options=options)
        if fileName:
            try:
                json_data = self.jsonEdit.toPlainText()
                parsed = json.loads(json_data)
            except Exception as e:
                parsed = {}
            parsed["gt_file"] = fileName
            self.jsonEdit.setPlainText(json.dumps(parsed))

    def select_pretrained_model(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Open pth File", "",
                                                  "pth Files (*.pth)",
                                                  options=options)
        if fileName:
            try:
                json_data = self.jsonEdit.toPlainText()
                parsed = json.loads(json_data)
            except Exception as e:
                parsed = {}
            parsed["pretrained_model"] = fileName
            self.jsonEdit.setPlainText(json.dumps(parsed))

    def test_finished(self, info):
        QMessageBox.information(self, "info", info)