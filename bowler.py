from enums import Commitment, Transport

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

    def setTransport(self, transport: Transport):
        self.cur.execute("UPDATE Bowlers SET transport = ? WHERE bowlerID = ?", (transport.value, self.bowlerID))

    def isInSession(self) -> bool:

        # check if the bowler is in the session.
        # whether opted out for rostered players or opted in for substitutes

        if self.getCommitment() == Commitment.ROSTERED:
            self.cur.execute(
                "SELECT EXISTS(SELECT 1 FROM ROUBowlers WHERE bowlerID = ?);",
                (self.bowlerID,)
            )
            return self.cur.fetchone()[0] == 0 # is not in ROU
        else:
            self.cur.execute(
                "SELECT EXISTS(SELECT 1 FROM SUBBowlers WHERE bowlerID = ?);",
                (self.bowlerID,)
            )
            return self.cur.fetchone()[0] == 1 # is not in SOI

    # takes snapshot of bowler info
    def cacheProfile(self) -> CacheBowlerProfile:

        firstName, lastName = self.getFullName()
        email = self.getEmail()
        discord = self.getDiscord()
        commitment = self.getCommitment()
        transport = self.getTransport()

        return CacheBowlerProfile(self.bowlerID, firstName, lastName, email, discord, commitment, transport)
    
    def log(self):

        print("Bowler ID:", self.bowlerID)
        print("Full Name:", self.getFullName())
        print("Email:", self.getEmail())
        print("Discord:", self.getDiscord())
        print("Commitment:", self.getCommitment())
        print("Transport:", self.getTransport())
        print()
