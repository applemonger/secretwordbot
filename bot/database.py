import duckdb
import os


class Database:
    PRECISION = 18
    SCALE = 6

    def __init__(self, path: str | None = None):
        self.db = duckdb.connect(path or os.getenv("DATABASE_PATH"))
        query = """
            CREATE TABLE IF NOT EXISTS SECRET_WORDS (
                guild_id BIGINT PRIMARY KEY,
                keeper BIGINT, 
                word VARCHAR,
            );
        """
        self.db.execute(query)
        query = """
            CREATE TABLE IF NOT EXISTS HINTS (
                guild_id BIGINT,
                hint_number INTEGER,
                hint VARCHAR
            )
        """
        self.db.execute(query)

    def get_secret(self, guild_id: int) -> str:
        query = """
            SELECT word
            FROM SECRET_WORDS
            WHERE guild_id = ?
        """
        result = self.db.execute(query, [guild_id]).fetchone()
        if result is None:
            return None
        else:
            word = None if result[0] is None else str(result[0])
            return word

    def secret_is_set(self, guild_id: int) -> bool:
        query = """
            SELECT word
            FROM SECRET_WORDS
            WHERE guild_id = ?
        """
        result = self.db.execute(query, [guild_id]).fetchone()
        if result is None:
            return False
        else:
            return result[0] is not None

    def get_keeper(self, guild_id: int) -> int:
        query = """
            SELECT keeper
            FROM SECRET_WORDS
            WHERE guild_id = ?
        """
        result = self.db.execute(query, [guild_id]).fetchone()
        if result is None:
            return None
        else:
            return int(result[0])

    def get_hints(self, guild_id: int) -> list[str]:
        query = "SELECT hint FROM HINTS WHERE guild_id = ? ORDER BY hint_number"
        result = self.db.execute(query, [guild_id]).fetchall()
        if len(result) == 0:
            return result
        else:
            return [x[0] for x in result]

    def add_hint(self, guild_id: int, hint: str) -> int:
        query = "SELECT COUNT(*) FROM HINTS WHERE guild_id = ?"
        hint_number = self.db.execute(query, [guild_id]).fetchone()[0] + 1
        query = "INSERT INTO HINTS VALUES (?, ?, ?)"
        self.db.execute(query, [guild_id, hint_number, hint])
        return hint_number

    def change_keeper(self, guild_id: int, member_id: int):
        query = """
            UPDATE SECRET_WORDS
            SET keeper = ?, word = NULL
            WHERE guild_id = ?
        """
        self.db.execute(query, [member_id, guild_id])

    def clear_hints(self, guild_id: int):
        query = "DELETE FROM HINTS WHERE guild_id = ?"
        self.db.execute(query, [guild_id])

    def set_word(self, guild_id: int, word: str):
        query = """
            UPDATE SECRET_WORDS
            SET word = ?
            WHERE guild_id = ?
        """
        self.db.execute(query, [word, guild_id])

    def is_keeper(self, guild_id: int, member_id: int) -> bool:
        query = """
            SELECT COUNT(*)
            FROM SECRET_WORDS
            WHERE guild_id = ? AND keeper = ?
        """
        result = self.db.execute(query, [guild_id, member_id]).fetchone()
        return int(result[0]) == 1

    def start_guild(self, guild_id: int, member_id: int, word: str):
        query = "INSERT INTO SECRET_WORDS VALUES (?, ?, ?);"
        self.db.execute(query, [guild_id, member_id, word])

    def guild_exists(self, guild_id: int) -> bool:
        query = "SELECT COUNT(*) FROM SECRET_WORDS WHERE guild_id = ?"
        result = self.db.execute(query, [guild_id]).fetchone()
        return int(result[0]) == 1

    def clear(self):
        self.db.execute("DROP TABLE SECRET_WORDS;")
        self.db.execute("DROP TABLE HINTS;")
