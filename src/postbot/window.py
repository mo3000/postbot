from PyQt5.QtWidgets import (QWidget, QMessageBox, QPushButton, QBoxLayout, QHBoxLayout, QApplication,
                             QLabel, QLineEdit, QGridLayout, QStackedWidget, QTabBar, QTextBrowser,
                             )
import sys


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


class Main(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("fake news")
        layout = QHBoxLayout()
        layout.setSpacing(20)
        layout.addWidget(FolderBar())
        right_part = QBoxLayout(QBoxLayout.TopToBottom)
        editor = Editor()
        screen = Screen()
        right_part.addWidget(editor)
        right_part.addWidget(screen)
        right_part.setSpacing(10)
        self.right_part = right_part
        layout.addItem(right_part)
        self.setLayout(layout)
        self.output = screen
        self.editor = editor
        editor.btn_send.clicked.connect(lambda: self.fetch_response())

    def fetch_response(self):
        self.output.browser.setText("输出啦")


class FolderBar(QWidget):

    def __init__(self):
        super().__init__()
        self.setMinimumSize(300, 400)
        self.label = QLabel("folder", self)


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


class Screen(QWidget):

    def __init__(self):
        super().__init__()
        self.setMinimumSize(400, 400)
        self.browser = QTextBrowser(self)
        self.browser.setWindowTitle("result:")
        self.browser.resize(600, 400)

