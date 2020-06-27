from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from uuid import uuid1


class Db:

    def __init__(self):
        db = QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName("./postbot.db")
        db.open()
        self.db = db
        self.__init_db()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()

    def __init_db(self):
        """create table"""
        query = self.db.exec("select * from sqlite_master where type='table' and tbl_name='tabs'")
        if not query.first():
            self.db.exec("""
            create table tabs(
              `id` char(36) primary key,
              name varchar(60) default '',
              request_type varchar(5) default 'get',
              url varchar(600)
            )
            """)
            self.db.exec("""
            create table opened_tabs(
              tabid char(36) not null,
              `index` integer not null
            )
            """)
            self.db.exec("""
            create table tab_header(
                `id` integer primary key autoincrement ,
                tabsid varchar(36) ,
                key varchar(60) not null ,
                value varchar(300) default ''
            )
            """)
            self.db.exec("create index tab_header_index on tab_header(tabsid)")
            self.db.exec("""
            create table tab_body(
                `id` integer primary key autoincrement ,
                tabsid varchar(36) not null,
                is_file integer default 0,
                key varchar(60) not null ,
                value text default ''
            )
            """)
            self.db.exec("create index tab_body_index on tab_body(tabsid)")
        # # todo delete
        # self.save_tab_header('wawadai-yoho-nima', [
        #     {'k': 'Content-Type', 'v': 'text/html'},
        #     {'k': 'Content-Length', 'v': '128'},
        #     {'k': 'wawadai', 'v': 'yamaidai'},
        # ])

    def __enter__(self):
        return self.db

    def __save_tab(self, key, tab_type, content):
        query = self.db.exec(f"select `id`, `key` from tab_{tab_type} where tabsid=:key")
        query.bindValue(':key', key)
        in_database = []
        while query.next():
            in_database.append(query.value('key'))
        content_map = {
            item['k']: {'v': item['v']} for item in content}
        database_keys = set(in_database)
        gui_keys = set([item['k'] for item in content])
        for k in gui_keys - database_keys:
            query = QSqlQuery()
            query.prepare(f'insert into tab_{tab_type}(tabsid, `key`, `value`) values(:key, :k, :v)')
            query.bindValue(':key', key)
            query.bindValue(':k', k)
            query.bindValue(':v', content_map[k]['v'])
            query.exec()
        for k in database_keys - gui_keys:
            query = QSqlQuery()
            query.prepare(f'delete from tab_{tab_type} where tabsid=:key and `key`=:k')
            query.bindValue(':key', key)
            query.bindValue(':k', k)
            query.exec()
        for k in gui_keys & database_keys:
            query = QSqlQuery()
            query.prepare(f'update tab_{tab_type} set value=:v where tabsid=:key and `key`=:k')
            query.bindValue(':k', k)
            query.bindValue(':key', key)
            query.bindValue(':v', content_map[k]['v'])
            query.exec()

    def save_tab_header(self, key, headers):
        self.__save_tab(key, 'header', headers)

    def save_tab_body(self, key, bodys):
        self.__save_tab(key, 'body', bodys)

    def save_tab_content(self, key, content):
        query = QSqlQuery()
        query.prepare(f'select * from tabs where id=:id')
        query.bindValue(':id', key)
        if query.first():
            query = QSqlQuery()
            query.prepare(f'update tabs set name=:name, request_type=:type, url=:url where id=:key')
            query.bindValue(':url', content['url'])
            query.bindValue(':type', content['request_type'])
            query.bindValue(':name', content['name'])
            query.bindValue(':key', key)
            query.exec()
        else:
            query = QSqlQuery()
            query.prepare(f'insert into tabs (`id`, name, request_type, url) values(:key, :name, :type, :url)')
            query.bindValue(':key', key)
            query.bindValue(':name', content['name'])
            query.bindValue(':type', content['request_type'])
            query.bindValue(':url', content['url'])
            query.exec()
        self.save_tab_header(key, content['header'])
        self.save_tab_body(key, content['body'])

    def load_opened_tab(self):
        tabs = []
        query = self.db.exec("select * from opened_tabs order by `index`")
        while query.next():
            tabs.append(query.value('tabid'))
        if len(tabs) == 0:
            return tabs
        query = self.db.exec('select * from tabs where `id` in ({})'.format(','.join(["'" + s + "'" for s in tabs])))
        tabs = []
        while query.next:
            tabs.append({
                'name': query.value('name'),
                'request_type': query.value('request_type'),
                'id': query.value('id'),
                'url': query.value('url'),
            })
        for tab in tabs:
            headers = []
            bodys = []
            query = self.db.exec(f"select * from tab_header where tabsid='{tab['id']}'")
            while query.next():
                headers.append({
                    'id': query.value('id'),
                    'key': query.value('key'),
                    'value': query.value('value'),
                })
            query = self.db.exec(f"select * from tab_body where tabsid='{tab['id']}'")
            while query.next():
                bodys.append({
                    'id': query.value('id'),
                    'key': query.value('key'),
                    'value': query.value('value'),
                })
            tab['body'] = bodys
            tab['header'] = headers
        return tabs

    def load_tab(self, key):
        query = QSqlQuery()
        query.prepare("select * from tabs where `id`=:key")
        query.bindValue(':key', key)
        query.exec()
        if query.first():
            tab = {
                'id': query.value('id'),
                'name': query.value('name'),
                'request_type': query.value('request_type'),
            }
        else:
            raise RuntimeError('sql error: ' + query.lastError().text())
        headers = []
        bodys = []
        query = self.db.exec(f"select * from tab_header where tabsid='{tab['id']}'")
        while query.next():
            headers.append({
                'id': query.value('id'),
                'key': query.value('key'),
                'value': query.value('value'),
            })
        query = self.db.exec(f"select * from tab_body where tabsid='{tab['id']}'")
        while query.next():
            bodys.append({
                'id': query.value('id'),
                'key': query.value('key'),
                'value': query.value('value'),
            })
        tab['body'] = bodys
        tab['header'] = headers
        return tab


class TabStorage:
    """tab data helper"""
    def __init__(self):
        self.data = set()
        self.load()

    def load(self) -> None:
        """load data from db(perhaps)"""
        pass

    def new_tab(self) -> str:
        uuid = uuid1()
        self.data.add(uuid)
        return str(uuid)

    def add(self, key):
        self.data.add(key)

    def remove(self, key: str):
        self.data.remove(key)

    def __len__(self):
        return len(self.data)

