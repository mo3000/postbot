from PyQt5 import QtGui
from PyQt5.QtWidgets import (QWidget, QMessageBox, QPushButton, QBoxLayout, QHBoxLayout, QApplication,
                             QLabel, QLineEdit, QGridLayout, QStackedWidget, QTabBar, QTextBrowser,
                             QTabWidget, QFormLayout, QRadioButton, QButtonGroup, QTreeView, QMenu,
                             QFileIconProvider, QMainWindow, QInputDialog, )
import sys
from typing import List, Dict, Union
from .storage import TabStorage
from PyQt5.QtCore import QUrl, Qt, QEvent
from PyQt5.Qt import QStandardItemModel, QStandardItem, QPoint, QCursor, QIcon
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QHttpMultiPart, QHttpPart
from json import dumps as json_encode, loads as json_decode


def run():
    app = QApplication(sys.argv)
    main = Main()
    main.show()
    try:
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        pass


def alert(text: str):
    box = QMessageBox()
    box.setText(text)
    box.show()
    box.exec_()


class TreeNode(QStandardItem):

    def __init__(self, *args, **kwargs):
        if 'is_dir' in kwargs:
            self.__is_dir = kwargs['is_dir']
            del kwargs['is_dir']
        else:
            self.__is_dir = True
        super().__init__(*args, **kwargs)

    def is_dir(self):
        return self.__is_dir


class FolderTreeView(QTreeView):

    def __init__(self):
        super().__init__()
        self.setSelectionMode(QTreeView.SelectionMode.ExtendedSelection)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.setModel(QStandardItemModel())
        self.setHeaderHidden(True)
        self.setDragDropMode(self.InternalMove)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.folder_icon = QIcon(__file__ + '/../../resource/icons8-folder.svg')
        self.file_icon = QIcon(__file__ + '/../../resource/icons8-file.svg')

    def mouseDoubleClickEvent(self, e: QtGui.QMouseEvent) -> None:
        item = self.indexAt(e.pos())
        print(item)
        # if item is None or self.indexWidget(item).is_dir() is True:
        #     super().mouseDoubleClickEvent(e)

    def add_root_item(self, item):
        self.model().invisibleRootItem().appendRow(item)

    def dropEvent(self, e: QtGui.QDropEvent) -> None:
        selected_indexes = self.selectedIndexes()
        super().dropEvent(e)
        if e.isAccepted():
            self.expand(self.indexAt(e.pos()))

    def get_node_by_pos(self, pos: QPoint) -> TreeNode:
        return self.model().itemFromIndex(self.indexAt(pos))


class Main(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("fake news")
        layout = QHBoxLayout()
        layout.setSpacing(20)
        layout.addWidget(FolderBar())
        self.tab_store = TabStorage()
        self.tab_container = TabContainer(self.tab_store)
        self.tab_container.setCurrentIndex(0)
        layout.addWidget(self.tab_container)
        self.setLayout(layout)
        # self.icon_folder = QFileIconProvider().icon()

    def get_editor_content(self, key: str) -> Dict:
        pass


class FolderBar(QWidget):

    def __init__(self):
        super().__init__()
        self.setMinimumSize(300, 600)
        layout = QBoxLayout(QBoxLayout.TopToBottom)
        self.tree_view = FolderTreeView()
        layout.addWidget(self.tree_view)
        self.load_from_cache()
        self.setLayout(layout)
        self.tree_view.clicked.connect(self.__on_treenode_clicked)
        # selection mode: SingleSelection, ContiguousSelection, ExtendedSelection, MultiSelection, NoSelection
        self.tree_view.customContextMenuRequested.connect(self.show_context_menu)
        self.__clicked_item = None

    def add_item(self, parent: QStandardItem, name: str, **kwargs) -> TreeNode:
        node = TreeNode(name, **kwargs)
        if 'is_dir' in kwargs and kwargs['is_dir'] is False:
            node.setDropEnabled(False)
            node.setIcon(self.tree_view.file_icon)
        else:
            node.setIcon(self.tree_view.folder_icon)
        node.setText(name)
        parent.appendRow(node)
        return node

    def load_from_cache(self):
        """ load saved data (from database)"""
        p1 = TreeNode("America")
        self.add_item(p1, "1111111")
        self.add_item(p1, "2222222")
        self.add_item(p1, "3333333", is_dir=False)
        self.tree_view.add_root_item(p1)
        self.tree_view.expandAll()

    def show_context_menu(self, pos: QPoint):
        self.__clicked_item = self.tree_view.get_node_by_pos(pos)
        menu = QMenu(self)
        if self.__clicked_item is None or self.__clicked_item.is_dir():
            action = menu.addAction('add folder')
            action.triggered.connect(self.__context_action_add_folder)
        if self.__clicked_item is not None:
            action = menu.addAction('rename')
            action.triggered.connect(self.__context_action_rename)
            action = menu.addAction('delete')
            action.triggered.connect(self.__context_action_delete)
        menu.exec_(QCursor.pos())

    @staticmethod
    def new_folder_node(text: str) -> TreeNode:
        return TreeNode(text)

    def __on_treenode_clicked(self, node: TreeNode):
        pass

    def __context_action_delete(self):
        print('delete')

    def __context_action_add_folder(self):
        name, ok = QInputDialog.getText(self, '⌨️', 'please enter a name')
        if ok:
            if name == '':
                alert("name is empty! ")
                return
            node = self.new_folder_node(name)
            if self.__clicked_item is None:
                self.tree_view.add_root_item(node)
            elif self.__clicked_item.is_dir():
                self.__clicked_item.appendRow(node)
                self.tree_view.expand(self.__clicked_item.index())

    def __context_action_rename(self):
        print('rename')


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
        self.input_search.setText('http://localhost:8000/test/index')
        self.input_search.setMinimumWidth(400)
        self.btn_send = QPushButton("send")
        self.btn_cancel = QPushButton("cancel")
        self.btn_save = QPushButton("save")
        editor_layout.addRow(self.input_search)
        self.http = QNetworkAccessManager()
        self.http.setTransferTimeout(10000)

        row = QHBoxLayout()
        self.btn_send.setMaximumWidth(60)
        self.btn_cancel.setMaximumWidth(80)
        self.btn_save.setMaximumWidth(60)
        row.addWidget(self.btn_send)
        row.addWidget(self.btn_cancel)
        row.addWidget(self.btn_save)
        editor_layout.addRow(row)

        self.group_http_type = QButtonGroup()
        btn_get = QRadioButton("GET")
        btn_get.setChecked(True)
        btn_post = QRadioButton("POST")
        self.group_http_type.addButton(btn_get)
        self.group_http_type.addButton(btn_post)
        row = QHBoxLayout()
        row.addWidget(btn_get)
        row.addWidget(btn_post)
        editor_layout.addRow(row)

        self.request_tabbar = RequestTab()
        editor_layout.addRow(self.request_tabbar)
        self.btn_send.clicked.connect(self.__set_response_text)

        self.response_screen = QTextBrowser()
        editor_layout.addRow(self.response_screen)

        self.editor_layout = editor_layout
        self.setLayout(editor_layout)

    def __set_response_text(self):
        self.btn_send.setEnabled(False)
        request_content = {
            'header': self.request_tabbar.header_tab.get_contents(),
            'body': self.request_tabbar.body_tab.get_contents(),
            'type': self.group_http_type.checkedButton().text(),
            'url': self.input_search.text().strip(),
        }

        if request_content['url'] == '':
            alert('url is empty!')
            return

        req = QNetworkRequest(QUrl(request_content['url']))
        for k, v in request_content['header'].items():
            req.setRawHeader(k.encode('utf-8'), v.encode())

        if request_content['type'] == 'GET':
            resp = self.http.get(req)
        elif request_content['type'] == 'POST':
            req.setHeader(QNetworkRequest.ContentTypeHeader, 'application/x-www-form-urlencoded')
            body = []
            for k, v in request_content['body'].items():
                # part = QHttpPart()
                # part.setHeader(QNetworkRequest.ContentDispositionHeader, f'form-data; name="{k}"')
                # part.setBody(v.encode('utf-8'))
                body.append(f"{k}={v}")
            resp = self.http.post(req, '&'.join(body).encode())
        else:
            alert('req is not set, type: ' + request_content['type'])
            return

        self.btn_cancel.clicked.connect(lambda: self.__on_btn_cancel_clicked(resp))
        resp.finished.connect(lambda: self.__on_http_send_finished(resp))

    def __on_http_send_finished(self, resp):
        self.__disconnect_btn_cancel()
        self.btn_send.setEnabled(True)
        self.response_screen.setText(bytes(resp.readAll()).decode())

    def __on_btn_cancel_clicked(self, resp):
        if not resp.isFinished():
            resp.abort()
            self.btn_send.setEnabled(True)
        self.__disconnect_btn_cancel()

    def __disconnect_btn_cancel(self):
        mobj = self.btn_cancel.metaObject()
        if self.btn_cancel.isSignalConnected(mobj.method(mobj.indexOfMethod('clicked()'))):
            self.btn_cancel.clicked.disconnect()




