
from enums import Commitment, Transport


class BowlerInfo:
    def __init__(self, id, fullName: str, discord: str,
                 commitment: Commitment, transport: Transport,
                 team: int | None = None, rosteredOptOut: bool = False
                 ):
        self.id = id
        self.fullName = fullName
        self.discord = discord
        self.commitment = commitment
        self.transport = transport
        self.team = team
        self.rosteredOptOut = rosteredOptOut

class Lineup:

    def parse(self, data) -> BowlerInfo:
            
        id = data[0]
        fullName = data[1]
        discord = data[2]
        commitment = Commitment(data[3])
        transport = Transport(data[4])
        if len(data) >= 6:
            team = data[5]
            rosteredOptOut = data[6] == 'out'
        else:
            team = None
            rosteredOptOut = None

        return BowlerInfo(id, fullName, discord, commitment, transport, team, rosteredOptOut)

    def __init__(self, cur):

        # selects all rostered players plus opted-in subs ordered by team
        # omits subs in overflow lanes
        # contains info whether the rostered player is opted out 
        TEAMS = """
            SELECT 
                B.bowlerID,
                B.firstName || ' ' || B.lastName as fullName,
                B.discord,
                B.commitment,
                B.transport,
                S.team,
                CASE WHEN R.ROUBowlerID IS NOT NULL THEN 'out' ELSE 'in' END AS status
            FROM Bowlers B
            LEFT JOIN SOIBowlers S ON B.bowlerID = S.bowlerID
            LEFT JOIN ROUBowlers R ON B.bowlerID = R.bowlerID
            WHERE B.commitment = 'rostered' OR S.team IS NOT NULL
            ORDER BY S.team ASC;
        """

        cur.execute(TEAMS)
        self._teamBowlerInfo = [self.parse(data) for data in cur.fetchall()]

        # selects only opted-in subs in overflow lanes
        OVERFLOW = """
            SELECT 
                B.bowlerID,
                B.firstName || ' ' || B.lastName as fullName,
                B.discord,
                B.commitment,
                B.transport
            FROM Bowlers B
            JOIN SOIBowlers S ON B.bowlerID = S.bowlerID
            WHERE S.TEAM IS NULL;
        """
        cur.execute(OVERFLOW)
        self._overflowBowlerInfo = [self.parse(data) for data in cur.fetchall()]

    def getLineup(self) -> list[BowlerInfo]:
        return self._teamBowlerInfo
    
    def getOverflow(self) -> list[BowlerInfo]:
        return self._overflowBowlerInfo

