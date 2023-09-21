import sqlite3
from bowler import Bowler
from bowlers_subset_table import BowlersSubsetTable
from enums import Commitment, Transport
from sql_table import SqlTable

class BowlersTable(BowlersSubsetTable):

    def __init__(self, con, cur):

        CREATE_BOWLER = """
        CREATE TABLE Bowlers (
            bowlerID INTEGER PRIMARY KEY AUTOINCREMENT,
            firstName TEXT NOT NULL,
            lastName TEXT NOT NULL,
            email TEXT DEFAULT '[Email not set]',
            discord TEXT NOT NULL UNIQUE,
            commitment TEXT CHECK (commitment IN ('rostered', 'sub')),
            transport TEXT CHECK (transport IN ('bus', 'self')),
            team INTEGER NULL
        );
        """

        super().__init__(con, cur, "Bowlers", CREATE_BOWLER)

    # team = 0 for subs. team number for rostered
    def addBowler(self, fname: str, lname: str, discord: str, team: int) -> Bowler:

        if team == 0:
            commitment = Commitment.SUB
            team = None
        else:
            commitment = Commitment.ROSTERED

        try:
            self.cur.execute(
                f"INSERT INTO {self.tableName} (firstName, lastName, email, discord, commitment, transport, team) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (fname, lname, "[Email not set]", discord, commitment.value, Transport.BUS.value, team)
            )
            self.con.commit()
        except:
            print("Failed to insert", fname, lname)
            return None

        bowlerID = self.cur.lastrowid 
        return Bowler(self.con, self.cur, bowlerID)
    
    def getRosterTeams(self) -> dict[int, list[Bowler]]:

        teams = {}
        for bowler in self.get(condition = "commitment = 'rostered'", order = "team ASC"):

            team = bowler.getTeam()
            if team not in teams:
                teams[team] = []
            teams[team].append(bowler)

        return teams

    def getSubs(self) -> list[Bowler]:
        
        return self.get(condition = "commitment = 'sub'")
    
    def countRostered(self) -> int:
        return self.count(condition = "commitment = 'rostered'")
    
    def countSubs(self) -> int:
        return self.count(condition = "commitment = 'sub'")