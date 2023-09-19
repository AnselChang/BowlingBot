from enums import Date
from sql_table import SqlTable

class DatesTable(SqlTable):

    def __init__(self, cur):

        CREATE_DATES = """
        CREATE TABLE Dates (
            dateID INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE,
            status TEXT CHECK (status IN ('past', 'active', 'future'))
        );
        """

        super().__init__(cur, "Dates", CREATE_DATES)

    def createTable(self):

        if self.exists():
            print(f"Table {self.tableName} already exists")
            return
        
        super().createTable()

        activeDate = Date.SEPTEMBER20

        for date in Date:
            mode = "active" if date == activeDate else "future"
            self.cur.execute(
                f"INSERT INTO {self.tableName} (date, status) VALUES (?, ?)",
                (date.value, mode)
            )

    def getActiveDate(self) -> Date:
        self.cur.execute(f"SELECT date FROM {self.tableName} WHERE status = 'active'")
        return Date(self.cur.fetchone()[0])
    
    # make the date active, all the dates before it past, and all the dates after it future
    # use id for comparing date order
    def setActiveDate(self, date: Date):
        self.cur.execute(f"SELECT dateID FROM {self.tableName} WHERE date = ?", (date.value,))
        dateID = self.cur.fetchone()[0]
        self.cur.execute(f"UPDATE {self.tableName} SET status = 'past' WHERE dateID < ?", (dateID,))
        self.cur.execute(f"UPDATE {self.tableName} SET status = 'active' WHERE dateID = ?", (dateID,))
        self.cur.execute(f"UPDATE {self.tableName} SET status = 'future' WHERE dateID > ?", (dateID,))