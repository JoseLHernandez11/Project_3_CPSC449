import collections
import contextlib
from os import stat
from pstats import Stats
import sqlite3
import typing

from datetime import date, datetime
from fastapi import FastAPI, Depends, Response, HTTPException, status
from pydantic import BaseModel, BaseSettings

from api.answer import Settings

class player_db_Settings(BaseSettings):
    stat_db: str
    game_db: str
    user_db: str

    class Config:
        env_fle = ".env"


class User(BaseModel):
    user_id: int
    username: str

class Game(BaseModel):
    user_id: str
    game_id: str
    number_of_guesses: int
    win: bool

class Statistics(BaseModel):
    user_id: str
    game_id: str
    amount_of_guesses: str
    games_won: int

def get_db():
    with contextlib.closing(sqlite3.connect(settings.stats_db)) as db:
        db.row_factory = sqlite3.Row
        yield db

settings = Settings()
app = FastAPI()

@app.post("/endgame/",status_code=status.HTTP_200_OK)
def process_end(
    stats:Stats, response: Response, db: list() = Depends(get_db)
):
    today_date = date.today().strftime("%Y-%m-%d")
    user_id = stats.user_id

    try: 
        cur = db[stats].cursor()
        cur.execute(
        """
        INSERT INTO games VALUES(?,?,?,?,?)
        """
        ,(user_id, stats.game_id, today_date, stats.guesses, stats.won))
    except Exception as e:
        return {"msg":"Error: Unable to insert values to tables"}

@app.get("/player_stats/", status_code=status.HTTP_200_OK)
def fetch_stats(
    user: User, response: Response, db: list() = Depends(get_db)
):
    today = date.today().strftime("%Y-%m-%d")
    cur_id = user.user_id
    result = {}

    try: 
        #Check if the word has been found by a user for the day
        cur = db.execute("SELECT MAX(streak)FROM streaks WHERE user_id = ?", (cur_id))
        longest : cur.fetchall()[0][0]
        
        #Check for max streak of the day
        cur = db.execute("SELECT MAX(streak) FROM streaks where user_id = ? AND ending = ?", (cur_id, today))
        todayScore = cur.fetchall()[0][0]

        #Check for avg number of guesses
        cur = db.execute("SELECT AVG(number_of_guesses) FROM games WHERE user_id = ?", (cur_id))
        avgGuess = cur.fetchall()[0][0]

        #Check for total amnt of games
        cur = db.execute("SELECT COUNT(games) FROM games WHERE user_id = ?", (cur_id))
        gamesPlayed = cur.fetchall()[0][0]

        #Check for games won 
        cur = db.execute("SELECT [COUNT(won)] FROM wins WHERE user_id = ?", (cur_id))
        gamesWon = cur.fetchall()[0][0]

        result["CurrentStreak:"] = longest
        result["DailyStreak:"] = todayScore
        result ["AVG Guesses:"] = avgGuess
        result ["Games Played:"] = gamesPlayed
        result["Games Won:"] = gamesWon
        result["Win %:"] = round(gamesWon/gamesPlayed)
        return result

    except Exception as e:
        return {"msg": "Erorr: Unable to load {} data." + str(e)}



@app.get("/top_wins/", status_code=status.HTTP_200_OK)
def get_top_wins(
    response: Response, db:list() = Depends(get_db)
):
    result = {}
    leaderboard = []

    for i in user_ids:
        try:
            cur = db[stats].cursor()

        except Exception as e: 
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {"msg": "Error: Failed to identify player statistics table."+ str(e)}


@app.get("/maximum_streak/", status_code=status.HTTP_200_OK)
def get_longest_streak(
    response: Response, db: list() = Depends(get_db)
):
    result = {}

    try:
        cur = db.execute("SELECT user_id, streak FROM streaks ORDER BY steak DESC LIMIT 10",)
        top_table = cur.fetchall()
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"msg": "Error: Failed to reach the wins table." + str(e)}
    user_ids=[]

    for row in top_table:
        user_ids.append(row[0])
    player_names = []

    try:
        for i in user_ids:
            cur = db.execute("SELECT username FROM users WHERE user_id = ?", (i,))
            player_names.append(cur.fetchall()[0][0])
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"msg":"Error Failed to reach wins table." + str(e)}
    users = []
    for i in range(10):
        temp = {}
        temp["username"] = player_names[i]
        temp["user_id"] = user_ids[i]
        users.append(temp)
    result ["Players"] = users
    return result