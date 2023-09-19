from bowler import Bowler
from bowlers_subset_table import BowlersSubsetTable

# sub opt in
class SOITable(BowlersSubsetTable):

    def __init__(self, cur):

        SOIBowlers = """
        CREATE TABLE SOIBowlers (
            SOIBowlerID INTEGER PRIMARY KEY AUTOINCREMENT,
            bowlerID INTEGER REFERENCES Player(bowlerID) ON DELETE CASCADE,
            team INTEGER NULL
        );
        """

        super().__init__(cur, "SOIBowlers", SOIBowlers)