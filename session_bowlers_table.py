from typing import TYPE_CHECKING
from bowler import Bowler
from enums import Commitment

from sql_table import SqlTable
from dates_table import DatesTable

class SessionBowlersTable(SqlTable):

    def __init__(self, cur):

        CREATE_SESSION_BOWLER = """
        CREATE TABLE SessionBowlers (
            sessionBowlerID INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT REFERENCES Dates(date),
            bowlerID INTEGER REFERENCES Player(bowlerID),
            team INTEGER NULL,
            attendance TEXT CHECK (Attendance IN ('await', 'yes', 'no'))
        );
        """

        super().__init__(cur, "SessionBowlers", CREATE_SESSION_BOWLER)

    def addBowler(self, bowler: Bowler):
        # attendance is set to await

        self.cur.execute(
            f"INSERT INTO {self.tableName} (date, bowlerID, team, attendance) VALUES (?, ?, ?, ?)",
            (bowler._getActiveDate(), bowler.bowlerID, bowler.getTeam(), "await")
        )

        sessionBowlerID = self.cur.lastrowid
    
    def removeBowler(self, bowler: Bowler):
        date = bowler._getActiveDate()
        self.cur.execute(f"DELETE FROM {self.tableName} WHERE bowlerID = ? AND date = ?", (bowler.bowlerID, date))

    def getActiveDate(self) -> str:
        return DatesTable(self.cur).getActiveDate().value
    
    # whether the bowler is in the active bowling session
    def isBowlerInSession(self, bowler: Bowler) -> bool:
        
        # get the active date
        date = self.getActiveDate()

        # check if the bowler is in the session
        self.cur.execute(
            "SELECT EXISTS(SELECT 1 FROM SessionBowlers WHERE bowlerID = ? AND date = ?)",
            (bowler.bowlerID, date)
        )

        return self.cur.fetchone()[0] == 1

    # get all bowlers at active session
    def getAllSessionBowlers(self) -> list[Bowler]:

        self.cur.execute(f"SELECT bowlerID FROM {self.tableName} WHERE date = ?", (self.getActiveDate(),))
        bowlerIDs = self.cur.fetchall()

        bowlers = []

        for bowlerID in bowlerIDs:
            bowlers.append(Bowler(self.cur, bowlerID[0]))

        return bowlers
    
    def getSubsForTeam(self, team: int | None) -> list[Bowler]:

        if team is None:
            self.cur.execute(f"SELECT bowlerID FROM {self.tableName} WHERE date = ? AND team IS NULL", (self.getActiveDate(),))
        else:
            self.cur.execute(f"SELECT bowlerID FROM {self.tableName} WHERE date = ? AND team = ?", (self.getActiveDate(), team))
        bowlerIDs = self.cur.fetchall()

        print(team, bowlerIDs)

        bowlers = []

        for bowlerID in bowlerIDs:
            bowler = Bowler(self.cur, bowlerID[0])
            if bowler.getCommitment() == Commitment.SUB:
                bowlers.append(bowler)

        return bowlers
        
    def log(self):
        print("Session bowlers for ", self.getActiveDate())
        for bowler in self.getAllSessionBowlers():
            print(bowler.getFullName())