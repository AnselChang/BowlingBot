import sqlite3
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
            defaultTransport TEXT CHECK (defaultTransport IN ('bus', 'self')),
            team INTEGER NULL
        );

        -- Trigger to prevent more than 3 members in a team
        CREATE TRIGGER prevent_more_than_three BEFORE INSERT ON Bowlers
        FOR EACH ROW
        WHEN NEW.commitment = 'rostered'
            AND (SELECT COUNT(*) FROM Bowlers WHERE commitment = 'rostered' AND team = NEW.team) >= 3
        BEGIN
            SELECT RAISE(FAIL, "A team can have a maximum of 3 rostered players");
        END;
        """

        super().__init__(cur, "Bowlers", CREATE_BOWLER)

    def isTeamFull(self, team: int) -> bool:
         # SQL query to count the number of members in a given team
        query = '''
        SELECT COUNT(bowlerID)
        FROM Bowlers
        WHERE commitment = 'rostered' AND team = ?;
        '''

        self.cur.execute(query, (team,))
        team_size = self.cur.fetchone()[0]

        return team_size >= 3

    def insert(self, fname: str, lname: str, email: str, discord: str, commitment: Commitment, team: int | None = None, defaultTransport: Transport = Transport.BUS) -> Bowler:

        if commitment == Commitment.ROSTERED and team is None:
            print("Rostered bowler must have a team")
            return "Error: Rostered bowler must have a team"
        
        if commitment == Commitment.ROSTERED and self.isTeamFull(team):
            print("Team is full")
            return "Error: Team is full"
        
        if commitment == Commitment.SUB and team is not None:
            print("Substitute bowler cannot have a team")
            return "Error: Substitute bowler cannot have a team"

        self.cur.execute(
            f"INSERT INTO {self.tableName} (firstName, lastName, email, discord, commitment, defaultTransport, team) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (fname, lname, email, discord, commitment.value, defaultTransport.value, team if team is not None else "NULL")
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
    
    def getRosterTeams(self):

        self.cur.execute("""
        SELECT team, GROUP_CONCAT(firstName || ' ' || lastName) AS BowlerIDs
        FROM Bowlers
        WHERE commitment = 'rostered' AND team IS NOT NULL
        GROUP BY team
        ORDER BY team;
        """)

        return self.cur.fetchall()

    
