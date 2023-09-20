BEGIN TRANSACTION;
CREATE TABLE Bowler (
    bowlerID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    email TEXT NOT NULL,
    discord TEXT NOT NULL,
    commitment TEXT CHECK (commitment IN ('rostered', 'sub')),
    defaultTransport TEXT CHECK (defaultTransport IN ('bus', 'self'))
);
CREATE TABLE Bowlers (
            bowlerID INTEGER PRIMARY KEY AUTOINCREMENT,
            firstName TEXT NOT NULL,
            lastName TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            discord TEXT NOT NULL UNIQUE,
            commitment TEXT CHECK (commitment IN ('rostered', 'sub')),
            transport TEXT CHECK (transport IN ('bus', 'self')),
            team INTEGER NULL
        );
INSERT INTO "Bowlers" VALUES(3,'Ansel','Chang','aychang@wpi.edu','450748389001265186','rostered','bus',1);
CREATE TABLE Dates (
            dateID INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE,
            status TEXT CHECK (status IN ('past', 'active', 'future'))
        );
INSERT INTO "Dates" VALUES(1,'September 20','active');
INSERT INTO "Dates" VALUES(2,'September 27','future');
INSERT INTO "Dates" VALUES(3,'October 4','future');
INSERT INTO "Dates" VALUES(4,'October 25','future');
INSERT INTO "Dates" VALUES(5,'November 1','future');
INSERT INTO "Dates" VALUES(6,'November 8','future');
INSERT INTO "Dates" VALUES(7,'November 15','future');
INSERT INTO "Dates" VALUES(8,'November 29','future');
INSERT INTO "Dates" VALUES(9,'December 6','future');
CREATE TABLE ROUBowlers (
            ROUBowlerID INTEGER PRIMARY KEY AUTOINCREMENT,
            bowlerID INTEGER REFERENCES Player(bowlerID) ON DELETE CASCADE
        );
CREATE TABLE SOIBowlers (
            SOIBowlerID INTEGER PRIMARY KEY AUTOINCREMENT,
            bowlerID INTEGER REFERENCES Player(bowlerID) ON DELETE CASCADE,
            team INTEGER NULL
        );
INSERT INTO "SOIBowlers" VALUES(1,2,NULL);
CREATE TABLE SessionBowler (
    sessionBowlerID INTEGER PRIMARY KEY AUTOINCREMENT,
    bowlerID INTEGER REFERENCES Player(bowlerID),
    currentTransport TEXT CHECK (currentTransport IN ('bus', 'self')),
    attendance TEXT CHECK (Attendance IN ('await', 'yes', 'no'))
);
CREATE TABLE SessionBowlers (
            sessionBowlerID INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT REFERENCES Dates(date),
            bowlerID INTEGER REFERENCES Player(bowlerID),
            team INTEGER NULL,
            attendance TEXT CHECK (Attendance IN ('await', 'yes', 'no'))
        );
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('Dates',9);
INSERT INTO "sqlite_sequence" VALUES('Bowlers',3);
INSERT INTO "sqlite_sequence" VALUES('ROUBowlers',1);
INSERT INTO "sqlite_sequence" VALUES('SOIBowlers',1);
COMMIT;
