# coding:utf-8
import json
import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QListWidgetItem, QFrame, QTreeWidgetItem, QHBoxLayout,
                             QTreeWidgetItemIterator, QTableWidgetItem, QGridLayout, QFileDialog, QMessageBox)
from qfluentwidgets import TreeWidget, TableWidget, ListWidget, HorizontalFlipView, PushButton, ComboBox

from .gallery_interface import GalleryInterface
from ..common.translator import Translator
from ..common.style_sheet import StyleSheet


class ViewInterface(GalleryInterface):
    """ View interface """

    def __init__(self, parent=None):
        t = Translator()
        super().__init__(
            title="结果统计",
            subtitle="",
            parent=parent
        )
        self.setObjectName('viewInterface')

        # list view
        # self.addExampleCard(
        #     title=self.tr('A simple ListView'),
        #     widget=ListFrame(self),
        #     sourcePath='https://github.com/zhiyiYo/PyQt-Fluent-Widgets/blob/master/examples/view/list_view/demo.py'
        # )

        # table view
        # self.addExampleCard(
        #     title=self.tr('A simple TableView'),
        #     widget=TableFrame(self),
        #     sourcePath='https://github.com/zhiyiYo/PyQt-Fluent-Widgets/blob/master/examples/view/table_view/demo.py'
        # )

        self.table = TableFrame(self)
        self.card = self.getCard(title=None,
                                 widget=self.table)
        self.start_sort_button = PushButton('结果排序')
        self.start_sort_button.clicked.connect(self.sort)

        self.comboBox = ComboBox()
        self.comboBox.addItems(self.table.header_labels)
        self.comboBox.setCurrentIndex(0)
        self.comboBox.setMinimumWidth(210)

        self.load_by_json_button = PushButton("从json导入结果")
        self.load_by_json_button.clicked.connect(self.load_by_json)
        self.load_by_folder_button = PushButton("从文件夹导入结果")
        self.load_by_folder_button.clicked.connect(self.load_by_folder)
        self.save_by_json_button = PushButton("结果保存为json")
        self.save_by_json_button.clicked.connect(self.save_by_json)
        self.clear_results_button = PushButton("清除结果")
        self.clear_results_button.clicked.connect(self.clear_results)

        gridLayout = QGridLayout()
        gridLayout.addWidget(self.comboBox, 0, 0)
        gridLayout.addWidget(self.start_sort_button, 0, 1)
        gridLayout.addWidget(self.load_by_json_button, 1, 0)
        gridLayout.addWidget(self.load_by_folder_button, 1, 1)
        gridLayout.addWidget(self.save_by_json_button, 2, 0)
        gridLayout.addWidget(self.clear_results_button, 2, 1)
        self.vBoxLayout.addLayout(gridLayout)
        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.setAlignment(Qt.AlignCenter)

    def sort(self, key_index=2):
        key_index = self.table.header_labels.index(self.comboBox.currentText())
        self.table.infos = sorted(self.table.infos, key=lambda x: x[key_index])
        self.table.table_show()

    def load_by_json(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Open JSON File", "", "JSON Files (*.json);;All Files (*)",
                                                  options=options)
        if fileName:
            try:
                with open(fileName, 'r', encoding='utf-8') as file:
                    results = json.load(file)
                    self.table.infos = results["results"]
                    self.table.table_show()

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not load file: {e}")

    def load_by_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if folder_path:
            file_names = [f for f in os.listdir(folder_path) if
                          os.path.isfile(os.path.join(folder_path, f))]
            file_names = [".".join(file_name.split(".")[0:-1]) for file_name in file_names]
            print(file_names)
            infos = []
            for file_name in file_names:
                info = file_name.split("#")
                infos.append(info)
            self.table.infos = infos
            self.table.table_show()

    def save_by_json(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Save JSON File", "", "JSON Files (*.json);;All Files (*)",
                                                  options=options)
        if fileName:
            try:
                json_data = {"results": self.table.infos}
                with open(fileName, 'w', encoding='utf-8') as file:
                    json.dump(json_data, file, indent=4)
                QMessageBox.information(self, "Success", "The JSON has been saved!")
            except json.JSONDecodeError as e:
                QMessageBox.critical(self, "Error", f"Invalid JSON: {e}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save file: {e}")

    def update_list_view(self, list_result):
        self.table.infos = list_result
        self.table.table_show()

    def clear_results(self):
        self.table.infos = []
        self.table.table_show()

# class Frame(QFrame):
#
#     def __init__(self, parent=None):
#         super().__init__(parent=parent)
#         self.hBoxLayout = QHBoxLayout(self)
#         self.hBoxLayout.setContentsMargins(0, 8, 0, 0)
#
#         self.setObjectName('frame')
#         StyleSheet.VIEW_INTERFACE.apply(self)
#
#     def addWidget(self, widget):
#         self.hBoxLayout.addWidget(widget)


# class ListFrame(Frame):
#
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.listWidget = ListWidget(self)
#         self.addWidget(self.listWidget)
#
#         stands = [
#             self.tr("Star Platinum"), self.tr("Hierophant Green"),
#             self.tr("Made in Haven"), self.tr("King Crimson"),
#             self.tr("Silver Chariot"), self.tr("Crazy diamond"),
#             self.tr("Metallica"), self.tr("Another One Bites The Dust"),
#             self.tr("Heaven's Door"), self.tr("Killer Queen"),
#             self.tr("The Grateful Dead"), self.tr("Stone Free"),
#             self.tr("The World"), self.tr("Sticky Fingers"),
#             self.tr("Ozone Baby"), self.tr("Love Love Deluxe"),
#             self.tr("Hermit Purple"), self.tr("Gold Experience"),
#             self.tr("King Nothing"), self.tr("Paper Moon King"),
#             self.tr("Scary Monster"), self.tr("Mandom"),
#             self.tr("20th Century Boy"), self.tr("Tusk Act 4"),
#             self.tr("Ball Breaker"), self.tr("Sex Pistols"),
#             self.tr("D4C • Love Train"), self.tr("Born This Way"),
#             self.tr("SOFT & WET"), self.tr("Paisley Park"),
#             self.tr("Wonder of U"), self.tr("Walking Heart"),
#             self.tr("Cream Starter"), self.tr("November Rain"),
#             self.tr("Smooth Operators"), self.tr("The Matte Kudasai")
#         ]
#         for stand in stands:
#             self.listWidget.addItem(QListWidgetItem(stand))
#
#         self.setFixedSize(300, 380)


# class TreeFrame(Frame):
#
#     def __init__(self, parent=None, enableCheck=False):
#         super().__init__(parent)
#         self.tree = TreeWidget(self)
#         self.addWidget(self.tree)
#
#         item1 = QTreeWidgetItem([self.tr('JoJo 1 - Phantom Blood')])
#         item1.addChildren([
#             QTreeWidgetItem([self.tr('Jonathan Joestar')]),
#             QTreeWidgetItem([self.tr('Dio Brando')]),
#             QTreeWidgetItem([self.tr('Will A. Zeppeli')]),
#         ])
#         self.tree.addTopLevelItem(item1)
#
#         item2 = QTreeWidgetItem([self.tr('JoJo 3 - Stardust Crusaders')])
#         item21 = QTreeWidgetItem([self.tr('Jotaro Kujo')])
#         item21.addChildren([
#             QTreeWidgetItem(['空条承太郎']),
#             QTreeWidgetItem(['空条蕉太狼']),
#             QTreeWidgetItem(['阿强']),
#             QTreeWidgetItem(['卖鱼强']),
#             QTreeWidgetItem(['那个无敌的男人']),
#         ])
#         item2.addChild(item21)
#         self.tree.addTopLevelItem(item2)
#         self.tree.expandAll()
#         self.tree.setHeaderHidden(True)
#
#         self.setFixedSize(300, 380)
#
#         if enableCheck:
#             it = QTreeWidgetItemIterator(self.tree)
#             while (it.value()):
#                 it.value().setCheckState(0, Qt.Unchecked)
#                 it += 1


class TableFrame(TableWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.verticalHeader().hide()
        self.setBorderRadius(8)
        self.setBorderVisible(True)

        self.header_labels = [
            self.tr('模型名称'), self.tr('图片名称'), self.tr('推理时间'), self.tr('PSNR'), self.tr('SSIM')
        ]
        self.infos = [
        ]
        self.table_show()

        self.setFixedSize(16 * 30, 9 * 30)
        self.resizeColumnsToContents()

    def table_show(self):
        self.setColumnCount(len(self.header_labels))
        self.setRowCount(len(self.infos))
        self.setHorizontalHeaderLabels(self.header_labels)
        for i, info in enumerate(self.infos):
            for j in range(len(self.header_labels)):
                self.setItem(i, j, QTableWidgetItem(info[j]))

        self.resizeColumnsToContents()
        self.resizeRowsToContents()

