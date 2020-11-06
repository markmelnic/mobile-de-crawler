import time, sqlite3
from queue import Queue
from threading import Thread


from utils import table_name, tuplify
from settings import CRAWLER_TABLES, DB_NAME


class DB:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        self.cur = self.conn.cursor()
        self.running = True

        # start the query execution queue
        self.Q = Queue()
        self.q_thread = Thread(target=self.qexec, args=())
        self.q_thread.start()

        # create necessary tables
        for table in CRAWLER_TABLES:
            self.create_table(table_name(table[0]), table[1])

        while not self.Q.empty():
            time.sleep(1)

    def qexec(self):
        while True:
            if not self.Q.empty():
                item = self.Q.get()
                # item - query
                # if tuple
                #   item[0] - query
                #   item[1] - values
                if type(item) == list:
                    self.cur.executemany(item[0], item[1])
                    # print(item[0])
                else:
                    self.cur.execute(item)
                    # print(item)
                self.conn.commit()
            elif self.Q.empty() and not self.running:
                break
            else:
                time.sleep(1)

    def create_table(self, table_name: str, fields: list):
        field_data = ""
        for f in fields:
            field_data += f[0] + " " + f[1]
            if not f == fields[-1]:
                field_data += ", "
        query = "CREATE TABLE IF NOT EXISTS %s (%s)" % (table_name, field_data)
        self.Q.put(query)

    def add_value(self, table: str, values: tuple):
        query = "INSERT INTO %s VALUES %s" % (
            table,
            tuple(
                values,
            ),
        )
        self.Q.put(query)

    def add_values(self, table: str, values: list):
        if len(values) == 0:
            return
        values = tuplify(values)
        qlen = ""
        for i, v in enumerate(values[0]):
            qlen += "?"
            if not i == len(values[0]) - 1:
                qlen += ", "
        query = "INSERT INTO %s VALUES (%s)" % (table_name(table), qlen)
        self.Q.put([query, values])

    def rewrite_table_values(self, table: str, values: list):
        if len(values) == 0:
            return
        del_query = "delete from %s" % table
        self.Q.put(del_query)
        values = tuplify(values)
        qlen = ""
        for i, v in enumerate(values[0]):
            qlen += "?"
            if not i == len(values[0]) - 1:
                qlen += ", "
        query = "INSERT INTO %s VALUES (%s)" % (table, qlen)
        self.Q.put([query, values])

    def read_table(self, table: str):
        query = "select * from %s" % table
        self.cur.execute(query)
        contents = self.cur.fetchall()
        data = []
        for cont in contents:
            if len(cont) == 1:
                data.append(cont[0])
            else:
                data.append([item for item in cont])
        return data

    def close_conn(self):
        self.running = False
        self.q_thread.join()
        self.conn.close()
