import sqlite3

from utils import table_name
from settings import CRAWLER_TABLES, _MDE_MAKES_DICT, DB_NAME, CAR_TABLE_DATA


class DB:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        self.cur = self.conn.cursor()

        # create necessary tables
        for table in CRAWLER_TABLES:
            try:
                self.create_table(table[0], table[1])
            except sqlite3.OperationalError:
                pass

        for item in _MDE_MAKES_DICT:
            name = item["n"]
            for model in item["models"]:
                mod = model["m"]
                try:
                    self.create_table(table_name([name, mod]), CAR_TABLE_DATA)
                except sqlite3.OperationalError:
                    pass

    # turn list into tuples
    def tuplify(self, data: list):
        return [(d,) for d in data]

    def create_table(self, table_name: str, fields: list):
        field_data = ""
        for f in fields:
            field_data += f[0] + " " + f[1]
            if not f == fields[-1]:
                field_data += ", "
        query = "CREATE TABLE %s (%s)" % (table_name, field_data)
        self.cur.execute(query)
        self.conn.commit()

    def add_value(self, table: str, values: tuple):
        query = "INSERT INTO %s VALUES %s" % (table, tuple(values,))
        print(query)
        self.cur.execute(query)
        self.conn.commit()

    def add_values(self, table: str, values: list):
        qlen = ""
        for i, v in enumerate(values[0]):
            qlen += "?"
            if not i == len(values[0]) - 1:
                qlen += ", "
        query = "INSERT INTO %s VALUES (%s)" % (table_name(table), qlen)
        self.cur.executemany(query, values)
        self.conn.commit()

    def rewrite_table_values(self, table: str, values: list):
        del_query = "delete from %s" % table
        self.cur.execute(del_query)
        qlen = ""
        for i, v in enumerate(values[0]):
            qlen += "?"
            if not i == len(values[0]) - 1:
                qlen += ", "
        query = "INSERT INTO %s VALUES (%s)" % (table, qlen)
        self.cur.executemany(query, values)
        self.conn.commit()

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
        self.conn.close()
