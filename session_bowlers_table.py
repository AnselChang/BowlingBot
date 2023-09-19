from bowler import Bowler
from enums import Commitment, Transport
from sql_table import SqlTable

class SessionBowlersTable(SqlTable):

    def __init__(self, cur):

        CREATE_SESSION_BOWLER = """
        CREATE TABLE SessionBowlers (
            sessionBowlerID INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT REFERENCES Dates(date),
            bowlerID INTEGER REFERENCES Player(bowlerID),
            currentTransport TEXT CHECK (currentTransport IN ('bus', 'self')),
            attendance TEXT CHECK (Attendance IN ('await', 'yes', 'no'))
        );
        """

        super().__init__(cur, "SessionBowlers", CREATE_SESSION_BOWLER)

    def insertBowler(self, bowlerID: int, date: str) -> Bowler:

        # current transport is set to default transport
        # attendance is set to await

        currentTransport = Bowler(self.cur, bowlerID).getDefaultTransport()

        self.cur.execute(
            f"INSERT INTO {self.tableName} (date, bowlerID, currentTransport, attendance) VALUES (?, ?, ?, ?)",
            (date, bowlerID, currentTransport.value, "await")
        )

        sessionBowlerID = self.cur.lastrowid
        return Bowler(self.cur, sessionBowlerID)
    
    def removeBowler(self, bowlerID: int, date: str):
        self.cur.execute(f"DELETE FROM {self.tableName} WHERE bowlerID = ? AND date = ?", (bowlerID, date))