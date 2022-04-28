-- $ sqlite3 answers.db < answers.sql

PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;
DROP TABLE IF EXISTS Answers;
CREATE TABLE Answers (
    id INTEGER,
    word CHAR(5) UNIQUE,
    PRIMARY KEY(id)
);

DROP TABLE IF EXISTS Queued_Answer;
CREATE TABLE Queued_Answer (
    word CHAR(5),
    PRIMARY KEY(word)
);
COMMIT;
