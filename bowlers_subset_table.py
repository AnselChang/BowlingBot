from typing import TYPE_CHECKING
from bowler import Bowler
from enums import Commitment

from sql_table import SqlTable

class BowlersSubsetTable(SqlTable):

    def __init__(self, con, cur, tableName: str, createCommand: str):

        super().__init__(con, cur, tableName, createCommand)

    def addBowler(self, bowler: Bowler):
        # attendance is set to await

        self.cur.execute(
            f"INSERT INTO {self.tableName} (bowlerID) VALUES (?)",
            (bowler.bowlerID,)
        )
        self.con.commit()
    
    def removeBowler(self, bowler: Bowler):
        self.cur.execute(f"DELETE FROM {self.tableName} WHERE bowlerID = ?", (bowler.bowlerID,))
        self.con.commit()
    
    # how many bowlers in list
    def count(self, condition = None) -> int:

        select = f"SELECT COUNT(*) FROM {self.tableName}"

        if condition is not None:
            select += " WHERE " + condition

        self.cur.execute(select)
        return self.cur.fetchone()[0]

    # whether the bowler is in the list
    def contains(self, bowler: Bowler) -> bool:
    
        # check if the bowler is in the session
        self.cur.execute(
            f"SELECT EXISTS(SELECT 1 FROM {self.tableName} WHERE bowlerID = ?)",
            (bowler.bowlerID)
        )

        return self.cur.fetchone()[0] == 1

    def get(self, condition: str | None = None) -> list[Bowler]:

        select = "SELECT bowlerID FROM BOWLERS"

        if condition is not None:
            select += " WHERE " + condition

        self.cur.execute(select)
        bowlerIDs = self.cur.fetchall()

        bowlers = []

        for bowlerID in bowlerIDs:
            bowlers.append(Bowler(self.con, self.cur, bowlerID[0]))

        return bowlers
    
        # get the bowler matching discord or none if not found
    def getBowlerByDiscord(self, discord: str) -> Bowler | None:

        results = self.get(condition=f"discord = '{discord}'")
        if len(results) == 0:
            return None
        
        bowlerID = results[0].bowlerID
        return Bowler(self.con, self.cur, bowlerID)
    
    def assignTeam(self, bowler: Bowler, team: int | None):
        self.cur.execute(f"UPDATE {self.tableName} SET team = ? WHERE bowlerID = ?", (team, bowler.bowlerID))
        self.con.commit()
    
    def log(self):
        print(f"{self.tableName}")
        for bowler in self.get():
            print(bowler.getFullName())