from PyQt5.QtWidgets import (QWidget, QMessageBox, QPushButton, QBoxLayout, QHBoxLayout, QApplication,
                             QLabel, QLineEdit, QGridLayout, QStackedWidget, QTabBar, QTextBrowser,
                             QTabWidget, QFormLayout, )
import sys
from typing import List, Dict
from collections import namedtuple
from .storage import TabStorage
from PyQt5.QtCore import Qt
from PyQt5.sip import cast
from json import dumps as json_encode, loads as json_decode


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
        self.setMinimumSize(300, 600)
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
        self.tabCloseRequested.connect(self.on_tab_close)

    def new_tab(self):
        tab_key = self.storage.new_tab()
        tab = TabPage(tab_key)
        self.insertTab(len(self.storage) - 1, tab, "unnamed")

    def on_tab_clicked(self, x: int):
        if x == len(self.storage):
            self.new_tab()
            self.setCurrentIndex(x - 1)

    def on_tab_close(self, x: int):
        if 0 < x < len(self.storage):
            self.removeTab(x)


class TabPage(QWidget):

    def __init__(self, tab_key: str):
        super().__init__()
        layout = QBoxLayout(QBoxLayout.TopToBottom)
        editor = Editor()
        layout.addWidget(editor)
        layout.setSpacing(10)
        self.setLayout(layout)
        self.editor = editor
        self.tab_key = tab_key

    def set_output(self, text: str):
        self.output.browser.setText(text)

    def get_request(self):
        pass


class RequestContentWidget(QWidget):

    class Row(QHBoxLayout):

        def __init__(self):
            super().__init__()
            btn_remove = QPushButton("-")
            key_input = QLineEdit()
            key_input.setMaximumWidth(120)
            value_input = QLineEdit()
            self.addWidget(btn_remove)
            self.btn_remove = btn_remove
            self.addWidget(key_input)
            self.addWidget(value_input)

    def __init__(self):
        super().__init__()
        self.request_layout = QFormLayout()
        self.request_layout.setVerticalSpacing(5)
        self.setLayout(self.request_layout)
        self.add_plus_row()
        for _ in range(0, 5):
            self.add_row()

    def add_row(self):
        """
        add one row: "-"  input  input
        :return: None
        """
        row = RequestContentWidget.Row()
        row.btn_remove.clicked.connect(lambda: self.on_btn_remove_click(row))
        self.request_layout.addRow(row)

    def add_plus_row(self):
        """add a row with a '+' button"""
        row = QHBoxLayout()
        btn_more = QPushButton("+")
        btn_more.clicked.connect(self.add_row)
        row.addWidget(btn_more)
        self.request_layout.addRow(row)

    def on_btn_remove_click(self, row):
        self.request_layout.removeRow(row)

    def get_contents(self):
        contents = {}
        for i in range(1, self.request_layout.rowCount()):
            row = self.request_layout.itemAt(i)
            k = row.layout().itemAt(1).widget().text().strip()
            if k != '':
                contents[k] = row.layout().itemAt(2).widget().text().strip()
        return contents


class RequestTab(QTabWidget):

    def __init__(self):
        super().__init__()
        self.header_tab = RequestContentWidget()
        self.body_tab = RequestContentWidget()
        self.addTab(self.header_tab, "header")
        self.addTab(self.body_tab, "body")

    def add_header_row(self):
        self.header_tab.add_row()


class Editor(QWidget):

    def __init__(self):
        super().__init__()
        editor_layout = QFormLayout()
        self.input_search = QLineEdit()
        self.input_search.setPlaceholderText("http://")
        self.input_search.setMinimumWidth(400)
        self.btn_send = QPushButton("send")
        self.btn_save = QPushButton("save")
        editor_layout.addRow(self.input_search)

        row = QHBoxLayout()
        self.btn_send.setMaximumWidth(60)
        self.btn_save.setMaximumWidth(60)
        row.addWidget(self.btn_send)
        row.addWidget(self.btn_save)
        editor_layout.addRow(row)

        self.request_tabbar = RequestTab()
        editor_layout.addRow(self.request_tabbar)
        self.btn_send.clicked.connect(lambda: self.response_screen.setText(json_encode(
            [self.request_tabbar.header_tab.get_contents(),
             self.request_tabbar.body_tab.get_contents()], indent=2)))

        self.response_screen = QTextBrowser()
        editor_layout.addRow(self.response_screen)

        self.editor_layout = editor_layout
        self.setLayout(editor_layout)

