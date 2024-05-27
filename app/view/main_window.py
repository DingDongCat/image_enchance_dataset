# coding: utf-8
from PyQt5.QtCore import QUrl, QSize
from PyQt5.QtGui import QIcon, QDesktopServices, QColor
from PyQt5.QtWidgets import QApplication

from qfluentwidgets import (NavigationAvatarWidget, NavigationItemPosition, MessageBox, FluentWindow,
                            SplashScreen)
from qfluentwidgets import FluentIcon as FIF

from .gallery_interface import GalleryInterface
from .home_interface import HomeInterface

from .scroll_interface import ScrollInterface
from .setting_interface import SettingInterface
from .text_interface import TextInterface
from .view_interface import ViewInterface
from ..common.config import ZH_SUPPORT_URL, EN_SUPPORT_URL, cfg
from ..common.icon import Icon
from ..common.signal_bus import signalBus
from ..common.translator import Translator
from ..common import resource
from app.utils.common import SignalCenter


class MainWindow(FluentWindow):

    def __init__(self):
        super().__init__()
        self.initWindow()

        # create sub interface
        self.homeInterface = HomeInterface(self)
        # self.iconInterface = IconInterface(self)
        # self.basicInputInterface = BasicInputInterface(self)
        # self.dateTimeInterface = DateTimeInterface(self)
        # self.dialogInterface = DialogInterface(self)
        # self.layoutInterface = LayoutInterface(self)
        # self.menuInterface = MenuInterface(self)
        # self.materialInterface = MaterialInterface(self)
        # self.navigationViewInterface = NavigationViewInterface(self)
        self.scrollInterface = ScrollInterface(self)
        # self.statusInfoInterface = StatusInfoInterface(self)
        self.settingInterface = SettingInterface(self)
        self.textInterface = TextInterface(self)
        self.viewInterface = ViewInterface(self)

        # enable acrylic effect
        self.navigationInterface.setAcrylicEnabled(True)
        self.setCustomBackgroundColor(QColor(240, 244, 249), QColor(32, 32, 32))
        # self.setCustomBackgroundColor(QColor(24, 24, 24), QColor(32, 32, 32))

        self.connectSignalToSlot()

        # SignalCenter
        self.signalCenter = SignalCenter()
        self.signal_connect()

        # add items to navigation interface
        self.initNavigation()
        self.splashScreen.finish()

    def connectSignalToSlot(self):
        signalBus.micaEnableChanged.connect(self.setMicaEffectEnabled)
        signalBus.switchToSampleCard.connect(self.switchToSample)
        signalBus.supportSignal.connect(self.onSupport)

    def initNavigation(self):
        # add navigation items
        t = Translator()
        self.addSubInterface(self.homeInterface, FIF.HOME, self.tr('Home'))
        # self.addSubInterface(self.iconInterface, Icon.EMOJI_TAB_SYMBOLS, t.icons)
        self.navigationInterface.addSeparator()

        pos = NavigationItemPosition.SCROLL
        # self.addSubInterface(self.basicInputInterface, FIF.CHECKBOX, t.basicInput, pos)
        # self.addSubInterface(self.dateTimeInterface, FIF.DATE_TIME, t.dateTime, pos)
        # self.addSubInterface(self.dialogInterface, FIF.MESSAGE, t.dialogs, pos)
        # self.addSubInterface(self.layoutInterface, FIF.LAYOUT, t.layout, pos)
        # self.addSubInterface(self.materialInterface, FIF.PALETTE, t.material, pos)
        # self.addSubInterface(self.menuInterface, Icon.MENU, t.menus, pos)
        # self.addSubInterface(self.navigationViewInterface, FIF.MENU, t.navigation, pos)
        self.addSubInterface(self.scrollInterface, FIF.SCROLL, "单图片查看与测试", pos)
        # self.addSubInterface(self.statusInfoInterface, FIF.CHAT, t.statusInfo, pos)
        self.addSubInterface(self.textInterface, Icon.TEXT, "多图片测试配置", pos)
        self.addSubInterface(self.viewInterface, Icon.GRID, "结果统计", pos)

        # add custom widget to bottom
        # self.navigationInterface.addItem(
        #     routeKey='price',
        #     icon=Icon.PRICE,
        #     text=t.price,
        #     onClick=self.onSupport,
        #     selectable=False,
        #     tooltip=t.price,
        #     position=NavigationItemPosition.BOTTOM
        # )
        self.addSubInterface(
            self.settingInterface, FIF.SETTING, self.tr('Settings'), NavigationItemPosition.BOTTOM)

    def initWindow(self):
        self.resize(960, 780)
        self.setMinimumWidth(760)
        # self.setBackgroundColor(QColor("red"))
        self.setWindowIcon(QIcon(':/gallery/images/logo.png'))
        self.setWindowTitle('复杂光照数据集自动化测评系统')

        self.setMicaEffectEnabled(cfg.get(cfg.micaEnabled))

        # create splash screen
        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(106, 106))
        self.splashScreen.raise_()

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)
        self.show()
        QApplication.processEvents()

    def onSupport(self):
        language = cfg.get(cfg.language).value
        if language.name() == "zh_CN":
            QDesktopServices.openUrl(QUrl(ZH_SUPPORT_URL))
        else:
            QDesktopServices.openUrl(QUrl(EN_SUPPORT_URL))

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if hasattr(self, 'splashScreen'):
            self.splashScreen.resize(self.size())

    def switchToSample(self, routeKey, index):
        """ switch to sample """
        interfaces = self.findChildren(GalleryInterface)
        for w in interfaces:
            if w.objectName() == routeKey:
                self.stackedWidget.setCurrentWidget(w, False)
                w.scrollToCard(index)

    def signal_connect(self):
        self.scrollInterface.start_test_signal.connect(self.signalCenter.start_test)
        self.textInterface.start_multi_image_test_signal.connect(self.signalCenter.start_multi_image_test)
        self.signalCenter.pixmap_signal.connect(self.scrollInterface.setImage)
        self.signalCenter.test_finished_signal.connect(self.textInterface.test_finished)
        self.signalCenter.update_list_view_signal.connect(self.viewInterface.update_list_view)
