from bowler import Bowler
from bowlers_subset_table import BowlersSubsetTable

# roster opt out
class ROUTable(BowlersSubsetTable):

    def __init__(self, cur):

        ROUBowlers = """
        CREATE TABLE ROUBowlers (
            ROUBowlerID INTEGER PRIMARY KEY AUTOINCREMENT,
            bowlerID INTEGER REFERENCES Player(bowlerID) ON DELETE CASCADE
        );
        """

        super().__init__(cur, "ROUBowlers", ROUBowlers)