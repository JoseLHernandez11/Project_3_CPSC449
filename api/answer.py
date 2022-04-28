import collections
import contextlib
import sqlite3
import typing
from datetime import datetime

from fastapi import FastAPI, Depends, Response, HTTPException, status
from pydantic import BaseModel, BaseSettings

DEBUG = False

class Settings(BaseSettings):
    answers_database: str
    logging_config: str
    epoch: str
    max_words: int

    class Config:
        env_file = ".env"

class Word(BaseModel):
    word: str

def get_db():
    with contextlib.closing(sqlite3.connect(settings.answers_database)) as db:
        db.row_factory = sqlite3.Row
        yield db

# Grabs the index for the word of the day
def dayIndex():
    epoch = datetime.strptime(settings.epoch, "%Y-%m-%d")
    diff_days = (datetime.now() - epoch).days
    return diff_days % settings.max_words

settings = Settings()
app = FastAPI()

@app.put("/check/", status_code=status.HTTP_200_OK)
def check(word_obj: Word, response: Response, db: sqlite3.Connection = Depends(get_db)):

    word = word_obj.word.lower()

    if (len(word) != 5):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"msg": "Error: Incorrect word length"}

    try:
        cur = db.execute("SELECT word FROM Queued_Answer")
        db.commit()
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"msg": "Error: Failed to reach database. " + str(e)}
    
    rows = cur.fetchall()

    if(len(rows) == 0):
        day = dayIndex() 

        try:
            cur = db.execute("SELECT word FROM Answers WHERE id = ?", (day,))
            db.commit()
            rows = cur.fetchall()
        except Exception as e:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {"msg": "Error: Failed to reach database. " + str(e)}

    todaysWord = rows[0][0]
    
    # Create frequency map of each letter in the word 
    freq_map = {}
    for c in todaysWord:
        freq_map[c] = freq_map.get(c, 0) + 1

    results = [0] * len(word)

    # Find all perfect matches
    for i,c in enumerate(word):
        if c in freq_map and freq_map[c] > 0:
            if word[i] == todaysWord[i]:
                results[i] = 2
                freq_map[c] -= 1

    # Find all word matches that arent positioned correctly
    for i,c in enumerate(word):
        if c in freq_map and freq_map[c] > 0 and results[i] == 0:
            results[i] = 1
            freq_map[c] -= 1
    
    correct = True
    for letter in results:
        if letter != 2:
            correct = False
            break

    if (DEBUG):
        return {"correct": correct, "results": results, "word_of_the_day": todaysWord}
    else:
        return {"correct": correct, "results": results}

@app.post("/next-answer/", status_code=status.HTTP_201_CREATED)
def set_next_answer(
    word_obj: Word, response: Response, db: sqlite3.Connection = Depends(get_db)
):
    word = word_obj.word.lower() 
   
    if (len(word) != 5):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"msg": "Error: Incorrect word length"}

    try:
        cur = db.execute("DELETE FROM Queued_Answer")
        cur = db.execute("INSERT INTO Queued_Answer (word) VALUES (?)", (word,))
        db.commit()
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"msg": "Error: Failed to reach database. " + type(e).__name__ + " | " + str(e)}

    return {"msg": "Successfully set the new answer."}

@app.delete("/next-answer/", status_code=status.HTTP_201_CREATED)
def delete_next_answer(
    response: Response, db: sqlite3.Connection = Depends(get_db)
):
    try:
        cur = db.execute("DELETE FROM Queued_Answer")
        db.commit()
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"msg": "Error: Failed to reach database. " + type(e).__name__ + " | " + str(e)}

    return {"msg": "Successfully removed the custom answer. The new answer is the word of the day."}

@app.post("/answers/", status_code=status.HTTP_201_CREATED)
def create_answer(
    word_obj: Word, response: Response, db: sqlite3.Connection = Depends(get_db)
):
    word = word_obj.word.lower() 
   
    if (len(word) != 5):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"msg": "Error: Incorrect word length"}

    try:
        cur = db.execute("INSERT INTO Answers (id, word) VALUES (NULL, ?)", (word,))
        db.commit()
    except sqlite3.IntegrityError as e:
        response.status_code = status.HTTP_409_CONFLICT
        return {"msg": "Duplicate Entry."}
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"msg": "Error: Failed to reach database. " + type(e).__name__ + " | " + str(e)}

    return {"msg": "Successfully added to the answer list."}

@app.delete("/answers/", status_code=status.HTTP_200_OK)
def delete_answer(
    word_obj: Word, response: Response, db: sqlite3.Connection = Depends(get_db)
):
    word = word_obj.word.lower() 
   
    if (len(word) != 5):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"msg": "Error: Incorrect word length"}

    try:
        cur = db.execute("DELETE FROM Answers WHERE word = ?", (word,))
        db.commit()
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"msg": "Error: Failed to reach database. " + type(e).__name__ + " | " + str(e)}

    return {"msg": "Successfully removed from the word list."}
