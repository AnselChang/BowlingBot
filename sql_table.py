import sql_command

class SqlTable:

    def __init__(self, cur, tableName: str, createCommand: str):
        self.cur = cur
        self.tableName = tableName
        self.createCommand = createCommand

    def exists(self) -> bool:
        self.cur.execute(sql_command.TABLE_EXISTS, (self.tableName,))
        return self.cur.fetchone()[0] == 1

    def createTable(self):

        if self.exists():
            print(f"Table {self.tableName} already exists")
            return

        self.cur.execute(self.createCommand)

    def deleteTable(self):

        if not self.exists():
            print(f"Table {self.tableName} does not exist")
            return

        self.cur.execute(f"DROP TABLE {self.tableName}")

    def getAll(self):
        self.cur.execute(f"SELECT * FROM {self.tableName}")
        return self.cur.fetchall()
    
    def getSchema(self):
        self.cur.execute(f"PRAGMA table_info({self.tableName})")
        return self.cur.fetchall()
    
    def log(self):
        for row in self.getAll():
            print(row)
        print()