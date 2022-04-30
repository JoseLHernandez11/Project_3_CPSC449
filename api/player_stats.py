import collections
import contextlib
from os import stat
from pstats import Stats
import sqlite3
import typing

from collections import OrderedDict
from datetime import date, datetime
from fastapi import FastAPI, Depends, Response, HTTPException, status
from pydantic import BaseModel, BaseSettings

class Settings(BaseSettings):
    stats_database: str

    class Config:
        env_fle = ".env"


class User(BaseModel):
    user_id: int
    username: str

class Game(BaseModel):
    user_id: str
    game_id: str
    finished: str
    guesses: int
    win: bool

def get_db():
    with contextlib.closing(sqlite3.connect(settings.stats_database)) as db:
        db.row_factory = sqlite3.Row
        yield db

settings = Settings()
app = FastAPI()

#sqlite3.register_converter('GUID',lambda b: uuid.UUID(bytes_le=b))
#sqlite3.register_adapter(uuid.UUID, lambda u: u.bytes_le)

@app.post("/finish/",status_code=status.HTTP_200_OK)
def process_end(
    stats:Stats, response: Response, db: list() = Depends(get_db)
):
    today_date = date.today().strftime("%Y-%m-%d")
    username = stats.username

    try: 
        cur = db[3].cursor()
        cur.execute("SELECT user_id FROM users WHERE user_id = ?", (username,))
        u_id = cur.fetcha11()[0][0]
        db[3].commit()

    except Exception as e:
        return {"msg": "Error: Failed to identify user id" + str(e)}
    
    row = cur.fetchall()
    if len(row) != 0:
        return {"Today's game is over"}

    try: 
        cur = db[stats].cursor()
        cur.execute(
        """
        INSERT INTO games VALUES(?,?,?,?,?)
        """
        ,(stats.game_id, today_date, stats.guesses, stats.won))
    except Exception as e:
        return {"msg":"Error: Unable to insert values to tables"}

@app.get("/stats/", status_code=status.HTTP_200_OK)
def fetch_stats(
    user: User, response: Response, db: list() = Depends(get_db)
):
    today = date.today().strftime("%Y-%m-%d")
    cur_name = user.username
    cur_id = user.user_id

    if not cur_id:
        try:
            cur = db[3].cursor()
            cur.execute("SELECT user_id FROM users WHERE username = ?", (cur_name,))
            cur_id = cur.fetchall()[0][0]
        except Exception as e:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {"msg": "Error: Failed to identify player_id " + str(e)}

@app.get("/top_wins/", status_code=status.HTTP_200_OK)
def get_top_wins(
    response: Response, db: sqlite3.Connection = Depends(get_db)
):
    leaderboard = []

    cur = db.execute("""SELECT * FROM wins ORDER BY "COUNT(won)" DEC LIMIT 10""")
    for res in cur.fetchall():
        leaderboard.append(res)
    
    return leaderboard

@app.get("/longest_streak/", status_code=status.HTTP_200_OK)
def get_longest_streak(
    response: Response, db: list() = Depends(get_db)
):
    longest_streak = []

    cur = db.execute("""SELECT streak FROM streaks ORDER BY streak DESC LIMIT 10""")
    for res in cur.fetchall():
        longest_streak.append(res)

    return longest_streak