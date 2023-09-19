from bowlers_table import BowlersTable
from dates_table import DatesTable
from enums import Commitment
from session_bowlers_table import SessionBowlersTable
from sql_table import SqlTable

import sqlite3
con = sqlite3.connect("bowling.db")
cur = con.cursor()

bowlers = BowlersTable(cur)
dates = DatesTable(cur)
session = SessionBowlersTable(cur)

bowlers.deleteTable()
bowlers.createTable()
dates.deleteTable()
dates.createTable()
session.deleteTable()
session.createTable()

john = bowlers.insert("John", "Doe", "email@com", "jd#1234", Commitment.ROSTERED)
jane = bowlers.insert("Jane", "Doe", "email@com", "jd#1234", Commitment.SUB)

john.log()

session.addBowler(john)

john.log()

session.log()