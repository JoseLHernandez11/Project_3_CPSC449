-- $ sqlite3 valid_words.db < valid_words.sql

PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;
DROP TABLE IF EXISTS ValidWords;
CREATE TABLE ValidWords (
    word CHAR(5) PRIMARY KEY
);
COMMIT;
