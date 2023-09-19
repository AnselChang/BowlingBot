from dates_table import DatesTable
from enums import Attendance, Commitment, Date, Transport

# a struct to cache bowler info
class CacheBowlerProfile:

    def __init__(self, bowlerID: int, firstName: str, lastName: str, email: str, discord: str, commitment: Commitment, transport: Transport, team: int | None):
        self.bowlerID = bowlerID
        self.firstName = firstName
        self.lastName = lastName
        self.email = email
        self.discord = discord
        self.commitment = commitment
        self.transport = transport
        self.team = team

class CacheBowlerSession:

    def __init__(self, bowlerID: int, profile: CacheBowlerProfile, date: str, currentTransport: Transport, attendance: Attendance):
        self.bowlerID = bowlerID
        self.profile = profile
        self.date = date
        self.attendance = attendance



class Bowler:

    def __init__(self, cur, bowlerID: int):
        self.cur = cur
        self.bowlerID = bowlerID

    def getID(self) -> int:
        return self.bowlerID
    
    def getFullName(self) -> tuple[str]:
        self.cur.execute("SELECT firstName, lastName FROM Bowlers WHERE bowlerID = ?", (self.bowlerID,))
        first, last = self.cur.fetchone()
        return first + " " + last
    
    def getEmail(self) -> str:
        self.cur.execute("SELECT email FROM Bowlers WHERE bowlerID = ?", (self.bowlerID,))
        return self.cur.fetchone()[0]
    
    def getDiscord(self) -> str:
        self.cur.execute("SELECT discord FROM Bowlers WHERE bowlerID = ?", (self.bowlerID,))
        return self.cur.fetchone()[0]
    
    def getCommitment(self) -> Commitment:
        self.cur.execute("SELECT commitment FROM Bowlers WHERE bowlerID = ?", (self.bowlerID,))
        return Commitment(self.cur.fetchone()[0])
    
    def getTeam(self) -> int | None:
        if self.getCommitment() == Commitment.SUB:
            print("Substitute has no team")
            return None
        self.cur.execute("SELECT team FROM Bowlers WHERE bowlerID = ?", (self.bowlerID,))
        return self.cur.fetchone()[0]

    def getTransport(self) -> Transport:
        self.cur.execute("SELECT transport FROM Bowlers WHERE bowlerID = ?", (self.bowlerID,))
        return Transport(self.cur.fetchone()[0])
    
    def setFullName(self, firstName: str, lastName: str):
        self.cur.execute("UPDATE Bowlers SET firstName = ?, lastName = ? WHERE bowlerID = ?", (firstName, lastName, self.bowlerID))

    def setEmail(self, email: str):
        self.cur.execute("UPDATE Bowlers SET email = ? WHERE bowlerID = ?", (email, self.bowlerID))

    def setDiscord(self, discord: str):
        self.cur.execute("UPDATE Bowlers SET discord = ? WHERE bowlerID = ?", (discord, self.bowlerID))

    def setCommitment(self, commitment: Commitment):
        self.cur.execute("UPDATE Bowlers SET commitment = ? WHERE bowlerID = ?", (commitment.value, self.bowlerID))

    def setTeam(self, team: int):
        if self.getCommitment() == Commitment.SUB:
            print("Cannot set team for substitute")
            return
        self.cur.execute("UPDATE Bowlers SET team = ? WHERE bowlerID = ?", (team, self.bowlerID))

    def setTransport(self, transport: str):
        self.cur.execute("UPDATE Bowlers SET transport = ? WHERE bowlerID = ?", (transport, self.bowlerID))

    """
    THESE FUNCTIONS ARE FOR THE SESSION BOWLER. THEY USE THE SESSION BOWLER TABLE
    AND ACTIVE DATE FROM THE DATES TABLE
    """

    def _getActiveDate(self) -> str:
        return DatesTable(self.cur).getActiveDate().value
    
    def isInSession(self) -> bool:
        
        # get the active date
        date = self._getActiveDate()

        # check if the bowler is in the session
        self.cur.execute(
            "SELECT EXISTS(SELECT 1 FROM SessionBowlers WHERE bowlerID = ? AND date = ?)",
            (self.bowlerID, date)
        )

        return self.cur.fetchone()[0] == 1
    
    def getAttendance(self) -> Attendance:

        if not self.isInSession():
            return Attendance.INVALID

        date = self._getActiveDate()

        self.cur.execute(
            "SELECT attendance FROM SessionBowlers WHERE bowlerID = ? AND date = ?",
            (self.bowlerID, date)
        )

        return Attendance(self.cur.fetchone()[0])
    
    def setAttendance(self, attendance: Attendance):

        if not self.isInSession():
            print("Bowler not in session")
            return

        date = self._getActiveDate()

        self.cur.execute(
            "UPDATE SessionBowlers SET attendance = ? WHERE bowlerID = ? AND date = ?",
            (attendance.value, self.bowlerID, date)
        )

    """
    Functions to cache bowler info
    """

    def cacheProfile(self) -> CacheBowlerProfile:

        firstName, lastName = self.getFullName()
        email = self.getEmail()
        discord = self.getDiscord()
        commitment = self.getCommitment()
        transport = self.getTransport()

        return CacheBowlerProfile(self.bowlerID, firstName, lastName, email, discord, commitment, transport)
    
    def cacheSession(self) -> CacheBowlerSession:

        profile = self.cacheProfile()
        date = self._getActiveDate()
        attendance = self.getAttendance()

        return CacheBowlerSession(self.bowlerID, profile, date, attendance)
    
    def log(self):

        print("Bowler ID:", self.bowlerID)
        print("Full Name:", self.getFullName())
        print("Email:", self.getEmail())
        print("Discord:", self.getDiscord())
        print("Commitment:", self.getCommitment())
        print("Transport:", self.getTransport())
        print("Active Date:", self._getActiveDate())
        print("Attendance:", self.getAttendance())
        print()
