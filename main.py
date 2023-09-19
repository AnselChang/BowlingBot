from bowlers_table import BowlersTable
from dates_table import DatesTable
from enums import Commitment
from sql_table import SqlTable

import sqlite3
con = sqlite3.connect("bowling.db")
cur = con.cursor()

bowlers = BowlersTable(cur)
dates = DatesTable(cur)

bowlers.deleteTable()
bowlers.createTable()
dates.deleteTable()
dates.createTable()

john = bowlers.insert("John", "Doe", "email@com", "jd#1234", Commitment.ROSTERED)
jane = bowlers.insert("Jane", "Doe", "email@com", "jd#1234", Commitment.SUB)

dates.log()
print()
dates.setActiveDate("October 25")
dates.log()