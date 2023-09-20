import csv

# write the roster to csv file
# each bowler is a record, sort by team
def csvRoster(cur) -> str:

    filename = "export/roster.csv"

    # get all bowlers
    cur.execute("SELECT * FROM Bowlers ORDER BY team")
    bowlers = cur.fetchall()

    # write to csv
    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Team", "First Name", "Last Name", "Email", "Discord", "Commitment", "Transport"])
        for bowler in bowlers:
            bowlerID, firstName, lastName, email, discord, commitment, transport, team = bowler
            writer.writerow([team, firstName, lastName, email, discord, commitment, transport])

    return filename

"""
CSV FORMAT:
Team, First name, last name, roster/sub, transport, attendance (left blank)
"""

def csvLineup(cur) -> str:

    filename = "export/lineup.csv"

    query = """

    SELECT 
        CASE WHEN B.team IS NULL THEN S.team ELSE B.team END AS team,
        B.firstName,
        B.lastName,
        B.discord,
        B.commitment,
        B.transport
    FROM Bowlers B
    LEFT JOIN SOIBowlers S ON B.bowlerID = S.bowlerID
    WHERE 
        NOT EXISTS (
            SELECT 1 FROM ROUBowlers R WHERE B.bowlerID = R.bowlerID
        )
    ORDER BY team ASC;

    """

    # get all bowlers
    cur.execute(query)
    bowlers = cur.fetchall()

    # write to csv
    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Team", "First Name", "Last Name", "Discord", "Commitment", "Transport", "Attendance"])
        for bowler in bowlers:
            team, fName, lName, discord, commitment, transport = bowler
            writer.writerow([team, fName, lName, discord, commitment, transport, ""])

    return filename