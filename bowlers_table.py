import sqlite3
from bowler import Bowler
from bowlers_subset_table import BowlersSubsetTable
from enums import Commitment, Transport
from sql_table import SqlTable

class BowlersTable(BowlersSubsetTable):

    def __init__(self, cur):

        CREATE_BOWLER = """
        CREATE TABLE Bowlers (
            bowlerID INTEGER PRIMARY KEY AUTOINCREMENT,
            firstName TEXT NOT NULL,
            lastName TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            discord TEXT NOT NULL UNIQUE,
            commitment TEXT CHECK (commitment IN ('rostered', 'sub')),
            transport TEXT CHECK (transport IN ('bus', 'self')),
            team INTEGER NULL
        );
        """

        super().__init__(cur, "Bowlers", CREATE_BOWLER)


    def addBowler(self, fname: str, lname: str, email: str, discord: str, commitment: Commitment, team: int | None = None, transport: Transport = Transport.BUS) -> Bowler:

        if commitment == Commitment.ROSTERED and team is None:
            print("Rostered bowler must have a team")
            return "Error: Rostered bowler must have a team"
        
        if commitment == Commitment.SUB and team is not None:
            print("Substitute bowler cannot have a team")
            return "Error: Substitute bowler cannot have a team"

        try:
            self.cur.execute(
                f"INSERT INTO {self.tableName} (firstName, lastName, email, discord, commitment, transport, team) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (fname, lname, email, discord, commitment.value, transport.value, team if team is not None else "NULL")
            )
        except:
            print("Failed to insert", fname, lname)
            return None

        bowlerID = self.cur.lastrowid 
        return Bowler(self.cur, bowlerID)

    

    def get(self, condition: str | None = None) -> list[Bowler]:

        select = "SELECT bowlerID FROM BOWLERS"

        if condition is not None:
            select += "WHERE " + condition

        self.cur.execute(select)
        bowlerIDs = self.cur.fetchall()

        bowlers = []

        for bowlerID in bowlerIDs:
            bowlers.append(Bowler(self.cur, bowlerID[0]))

        return bowlers
    
    def getRosterTeams(self) -> dict[int, list[Bowler]]:

        teams = {}
        for bowler in self.get(condition = "commitment = 'rostered'"):

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