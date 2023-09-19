from bowler import Bowler
from enums import Commitment, Transport
from sql_table import SqlTable

class BowlersTable(SqlTable):

    def __init__(self, cur):

        CREATE_BOWLER = """
        CREATE TABLE Bowlers (
            bowlerID INTEGER PRIMARY KEY AUTOINCREMENT,
            firstName TEXT NOT NULL,
            lastName TEXT NOT NULL,
            email TEXT NOT NULL,
            discord TEXT NOT NULL,
            commitment TEXT CHECK (commitment IN ('rostered', 'sub')),
            defaultTransport TEXT CHECK (defaultTransport IN ('bus', 'self'))
        );
        """

        super().__init__(cur, "Bowlers", CREATE_BOWLER)

    def insert(self, fname: str, lname: str, email: str, discord: str, commitment: Commitment, defaultTransport: Transport = Transport.BUS) -> Bowler:
        self.cur.execute(
            f"INSERT INTO {self.tableName} (firstName, lastName, email, discord, commitment, defaultTransport) VALUES (?, ?, ?, ?, ?, ?)",
            (fname, lname, email, discord, commitment.value, defaultTransport.value)
        )
        bowlerID = self.cur.lastrowid 
        return Bowler(self.cur, bowlerID)

    # get the bowler matching discord or none if not found
    def getBowlerByDiscord(self, discord: str) -> Bowler | None:
        self.cur.execute(f"SELECT bowlerID FROM {self.tableName} WHERE discord = ?", (discord,))
        row = self.cur.fetchone()
        if row is None:
            return None
        
        bowlerID = row[0]
        return Bowler(self.cur, bowlerID)

    
