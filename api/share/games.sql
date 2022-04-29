DROP TABLE IF EXISTS games;

CREATE TABLE games(
  user_id INTEGER NOT NULL,
  game_id INTEGER NOT NULL,
  game_finished DATE DEFAULT CURRENT_TIMESTAMP
  amount_of_guesses INTEGER,
  games_won BOOLEAN,
  PRIMARY KEY(user_id,game_id),
  FOREIGN KEY(user_id) REFERENCES users(user_id)
):
