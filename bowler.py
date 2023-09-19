from dates_table import DatesTable
from enums import Attendance, Commitment, Transport
from session_bowlers_table import SessionBowlersTable


class Bowler:

    def __init__(self, cur, bowlerID: int):
        self.cur = cur
        self.bowlerID = bowlerID

    def getID(self) -> int:
        return self.bowlerID
    
    def getFullName(self) -> tuple[str]:
        self.cur.execute("SELECT firstName, lastName FROM Bowlers WHERE bowlerID = ?", (self.bowlerID,))
        return self.cur.fetchone()
    
    def getEmail(self) -> str:
        self.cur.execute("SELECT email FROM Bowlers WHERE bowlerID = ?", (self.bowlerID,))
        return self.cur.fetchone()[0]
    
    def getDiscord(self) -> str:
        self.cur.execute("SELECT discord FROM Bowlers WHERE bowlerID = ?", (self.bowlerID,))
        return self.cur.fetchone()[0]
    
    def getCommitment(self) -> Commitment:
        self.cur.execute("SELECT commitment FROM Bowlers WHERE bowlerID = ?", (self.bowlerID,))
        return Commitment(self.cur.fetchone()[0])
    
    def getDefaultTransport(self) -> Transport:
        self.cur.execute("SELECT defaultTransport FROM Bowlers WHERE bowlerID = ?", (self.bowlerID,))
        return Transport(self.cur.fetchone()[0])
    
    def setFullName(self, firstName: str, lastName: str):
        self.cur.execute("UPDATE Bowlers SET firstName = ?, lastName = ? WHERE bowlerID = ?", (firstName, lastName, self.bowlerID))

    def setEmail(self, email: str):
        self.cur.execute("UPDATE Bowlers SET email = ? WHERE bowlerID = ?", (email, self.bowlerID))

    def setDiscord(self, discord: str):
        self.cur.execute("UPDATE Bowlers SET discord = ? WHERE bowlerID = ?", (discord, self.bowlerID))

    def setCommitment(self, commitment: Commitment):
        self.cur.execute("UPDATE Bowlers SET commitment = ? WHERE bowlerID = ?", (commitment.value, self.bowlerID))

    def setDefaultTransport(self, defaultTransport: str):
        self.cur.execute("UPDATE Bowlers SET defaultTransport = ? WHERE bowlerID = ?", (defaultTransport, self.bowlerID))

    """
    THESE FUNCTIONS ARE FOR THE SESSION BOWLER. THEY USE THE SESSION BOWLER TABLE
    AND ACTIVE DATE FROM THE DATES TABLE
    """

    def _getActiveDate(self) -> str:
        return DatesTable(self.cur).getActiveDate()
    
    # whether the bowler is in the active bowling session
    def isBowlerInSession(self) -> bool:
        
        # get the active date
        date = self._getActiveDate()

        # check if the bowler is in the session
        self.cur.execute(
            "SELECT EXISTS(SELECT 1 FROM SessionBowlers WHERE bowlerID = ? AND date = ?)",
            (self.bowlerID, date)
        )

        return self.cur.fetchone()[0] == 1
    
    # add the bowler to the active session
    def addBowlerToSession(self):

        if self.isBowlerInSession():
            print("Bowler already in session")
            return
        
        sessionBowlersTable = SessionBowlersTable(self.cur)
        sessionBowlersTable.insertBowler(self.bowlerID, self._getActiveDate())

    # remove the bowler from the active session
    def removeBowlerFromSession(self):

        if not self.isBowlerInSession():
            print("Bowler already not in session")
            return
        
        sessionBowlersTable = SessionBowlersTable(self.cur)
        sessionBowlersTable.removeBowler(self.bowlerID, self._getActiveDate())

    
    def getAttendance(self) -> Attendance:

        date = self._getActiveDate()

        self.cur.execute(
            "SELECT attendance FROM SessionBowlers WHERE bowlerID = ? AND date = ?",
            (self.bowlerID, date)
        )

        return Attendance(self.cur.fetchone()[0])
    
    def getCurrentTransport(self) -> Transport:
            
            date = self._getActiveDate()
    
            self.cur.execute(
                "SELECT currentTransport FROM SessionBowlers WHERE bowlerID = ? AND date = ?",
                (self.bowlerID, date)
            )
    
            return Transport(self.cur.fetchone()[0])
    
    def setAttendance(self, attendance: Attendance):

        date = self._getActiveDate()

        self.cur.execute(
            "UPDATE SessionBowlers SET attendance = ? WHERE bowlerID = ? AND date = ?",
            (attendance.value, self.bowlerID, date)
        )

    def setCurrentTransport(self, currentTransport: Transport):

        date = self._getActiveDate()

        self.cur.execute(
            "UPDATE SessionBowlers SET currentTransport = ? WHERE bowlerID = ? AND date = ?",
            (currentTransport.value, self.bowlerID, date)
        )