from PyQt5.QtWidgets import (QWidget, QMessageBox, QPushButton, QBoxLayout, QHBoxLayout, QApplication,
                             QLabel, QLineEdit, QGridLayout, QStackedWidget, QTabBar, QTextBrowser,
                             QTabWidget, )
import sys
from typing import List, Dict
from collections import namedtuple
from .storage import TabStorage


def run():
    app = QApplication(sys.argv)
    main = Main()
    main.show()
    try:
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        pass


def alert(title: str, text: str):
    box = QMessageBox()
    box.setWindowTitle(title)
    box.setText(text)
    box.show()
    box.exec_()


KeyValue = namedtuple("KeyValue", ['k', 'v'])


class Main(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("fake news")
        layout = QHBoxLayout()
        layout.setSpacing(20)
        layout.addWidget(FolderBar())
        self.tab_store = TabStorage()
        self.tab_container = TabContainer(self.tab_store)
        layout.addWidget(self.tab_container)
        self.setLayout(layout)

    def fetch_response(self, key: str):
        """get content from param editor, send http request, write response to "screen\""""
        self.output.browser.setText("输出啦")
        request = self.get_editor_content(key)
        if request['type'] == 'get':
            pass
        elif request['type'] == 'post':
            pass
        # todo process request body

    def get_editor_content(self, key: str) -> Dict:
        pass


class FolderBar(QWidget):

    def __init__(self):
        super().__init__()
        self.setMinimumSize(300, 400)
        self.label = QLabel("folder", self)


class TabContainer(QTabWidget):

    def __init__(self, storage: TabStorage):
        super().__init__()
        self.storage = storage
        btn_add_tab = QWidget()
        self.addTab(btn_add_tab, "+")
        self.tabBarClicked.connect(self.on_tab_clicked)
        self.setTabsClosable(True)
        self.tabBar().setTabButton(0, QTabBar.LeftSide, None)
        if len(storage) == 0:
            self.new_tab()

    def new_tab(self):
        tab_key = self.storage.new_tab()
        tab = TabPage(tab_key)
        self.insertTab(len(self.storage) - 1, tab, "unnamed")

    def on_tab_clicked(self, x: int):
        print(x)
        if x == len(self.storage):
            self.new_tab()
            self.setCurrentIndex(x - 1)


class TabPage(QWidget):

    def __init__(self, tab_key: str):
        super().__init__()
        layout = QBoxLayout(QBoxLayout.TopToBottom)
        editor = Editor()
        screen = Screen()
        layout.addWidget(editor)
        layout.addWidget(screen)
        layout.setSpacing(10)
        self.setLayout(layout)
        self.output = screen
        self.editor = editor
        self.tab_key = tab_key

    def set_output(self, text: str):
        self.output.browser.setText(text)

    def get_request(self):
        pass


class Editor(QWidget):

    def __init__(self):
        super().__init__()
        self.setMinimumSize(400, 200)
        editor_layout = QGridLayout()
        self.input_search = QLineEdit()
        self.input_search.setPlaceholderText("http://")
        self.input_search.setMinimumWidth(400)
        self.btn_send = QPushButton("send")
        self.btn_save = QPushButton("save")
        editor_layout.addWidget(self.input_search, 1, 1)
        editor_layout.addWidget(self.btn_send, 1, 5)
        editor_layout.addWidget(self.btn_save, 1, 6)
        self.editor_layout = editor_layout
        self.setLayout(editor_layout)
        self.req_body_input = []
        self.req_header_input = []


class Screen(QWidget):

    def __init__(self):
        super().__init__()
        self.browser = QTextBrowser(self)
        self.browser.setWindowTitle("result:")
        self.browser.resize(600, 400)

