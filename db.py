import sqlite3

from settings import TABLES


class DB:
    def __init__(self):
        self.conn = sqlite3.connect("crawler.sqlite3")
        self.cur = self.conn.cursor()

        # create necessary tables
        for table in TABLES:
            try:
                self.create_table(table[0], table[1])
            except sqlite3.OperationalError:
                pass

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
        query = "INSERT INTO %s VALUES %s" % (table, str(values))
        self.cur.execute(query)
        self.conn.commit()

    def add_values(self, table: str, values: list):
        qlen = ""
        for i, v in enumerate(values[0]):
            qlen += "?"
            if not i == len(values[0]) - 1:
                qlen += ", "
        query = "INSERT INTO %s VALUES (%s)" % (table, qlen)
        self.cur.executemany(query, values)
        self.conn.commit()



if __name__ == "__main__":
    db = DB()
