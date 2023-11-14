from psycopg import connect


class DataBase:
    magnet = None
    file_url = None
    member = None
    lang = None
    i = None

    def __init__(self):
        self.user = 'test_user'
        self.host = 'localhost'
        self.port = '5432'
        self.password = ''
        self.db = 'test_db'

    def auto_close(func):
        def wrapper(*args, **kwargs):
            self = args[0]
            try:
                self.conn = connect(dbname=self.db, user=self.user,
                                    password=self.password, host=self.host, port=self.port)
                self.cursor = self.conn.cursor()
                func(*args, **kwargs)
                self.conn.commit()
                self.cursor.close()
                self.conn.close()
            except Exception as e:
                print(e)

        return wrapper

    @auto_close
    def create_tables_users(self):
        table_name1 = 'torrent_users'
        self.cursor.execute(f'CREATE TABLE  {table_name1} ('
                            f'id SERIAL PRIMARY KEY,'
                            f'telegram_id INT,'
                            f'torrent_magnet CHAR (255),'
                            f'is_member INT,'
                            f'torrent_file CHAR (255),'
                            f'lang CHAR (2))')

    #  добавления пользователя
    @auto_close
    def get_user(self, telegram_id):
        self.i = bool(len(self.cursor.execute(f'SELECT telegram_id FROM torrent_user'
                                         f's WHERE telegram_id=%s', (telegram_id,)).fetchall()[0]))
        return self.i
    @auto_close
    def add_user_into_bd(self, telegram_id):

        self.cursor.execute(f'INSERT INTO torrent_users (telegram_id, lang) VALUES(%s, %s)', (telegram_id, 'en',))

    #  получения и изменения языка
    @auto_close
    def get_lang(self, telegram_id):
        self.lang = \
            self.cursor.execute(f'SELECT lang FROM torrent_users WHERE telegram_id=%s', (telegram_id,)).fetchall()[0]
        return self.lang

    @auto_close
    def set_lang(self, telegram_id, lang):
        self.cursor.execute(f'UPDATE torrent_users SET lang=%s  WHERE telegram_id=%s', (lang, telegram_id,))


    # получения и добавления магнита
    @auto_close
    def add_magnet(self, magnet_url, telegram_id):
        self.cursor.execute(f'UPDATE torrent_users SET torrent_magnet=%s WHERE telegram_id=%s',
                            (magnet_url, telegram_id,))

    @auto_close
    def get_magnet(self, telegram_id):
        self.magnet = \
            self.cursor.execute('SELECT torrent_magnet FROM torrent_users WHERE telegram_id=%s',
                                (telegram_id,)).fetchall()[0]
        return self.magnet


    #  получения и добавления файла
    @auto_close
    def get_file_url(self, telegram_id):
        self.file_url = \
            self.cursor.execute('SELECT torrent_file FROM torrent_users WHERE telegram_id=%s',
                                (telegram_id,)).fetchall()[0]
        return self.file_url

    @auto_close
    def add_file_url(self, file_url, telegram_id):
        self.cursor.execute(f'UPDATE torrent_users SET torrent_file=%s WHERE telegram_id=%s', (file_url, telegram_id,))

    #  получения и изменения является ли пользователь подписчиком
    @auto_close
    def update_is_member(self, token_id, num=0):
        self.cursor.execute(f'UPDATE torrent_users SET is_member=%s WHERE telegram_id=%s ', (num, token_id,))

    @auto_close
    def get_member(self, telegram_id):
        self.member = \
            self.cursor.execute(f'SELECT is_member FROM torrent_users WHERE telegram_id=%s', (telegram_id,)).fetchall()[0]
        return self.member


if __name__ == '__main__':
    a = DataBase()
    a.create_tables_users()
