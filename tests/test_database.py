import pytest
from bot.database import Database


@pytest.fixture()
def db():
    db = Database("db/test.db")
    yield db
    db.clear()


class TestDatabase:
    def test_get_secret(self, db: Database):
        secret = db.get_secret(0)
        assert secret.word is None
        assert secret.author is None
        assert secret.guesser is None
        db.start_guild(0, 0, "word")
        secret = db.get_secret(0)
        assert secret.word == "word"
        assert secret.author == 0
        assert secret.guesser is None
        db.set_word(0, 1, "word2")
        secret = db.get_secret(0)
        assert secret.word == "word2"
        assert secret.author == 1
        assert secret.guesser is None

    def test_get_hints(self, db: Database):
        assert db.get_hints(0) == []
        db.start_guild(0, 0, "word")
        db.add_hint(0, "hint")
        assert db.get_hints(0) == ["hint"]

    def test_add_hint(self, db: Database):
        assert db.get_hints(0) == []
        db.add_hint(0, "hint")
        assert db.get_hints(0) == ["hint"]
        db.add_hint(0, "hint2")
        assert db.get_hints(0) == ["hint", "hint2"]

    def test_clear_hints(self, db: Database):
        assert db.get_hints(0) == []
        db.add_hint(0, "hint")
        assert db.get_hints(0) == ["hint"]
        db.add_hint(0, "hint2")
        assert db.get_hints(0) == ["hint", "hint2"]
        db.clear_hints(0)
        assert db.get_hints(0) == []

    def test_set_word(self, db: Database):
        secret = db.get_secret(0)
        assert secret.word is None
        db.start_guild(0, 0, "word")
        secret = db.get_secret(0)
        assert secret.word == "word"

    def test_is_author(self, db: Database):
        db.start_guild(0, 0, "word")
        assert db.is_author(0, 0)
        assert not db.is_author(0, 1)
        assert not db.is_author(1, 0)
        assert not db.is_author(1, 1)

    def test_set_guesser(self, db: Database):
        db.start_guild(0, 0, "word")
        secret = db.get_secret(0)
        assert secret.guesser is None
        db.set_guesser(0, 1)
        secret = db.get_secret(0)
        assert not secret.is_set()
        assert secret.guesser == 1

    def test_start_guild(self, db: Database):
        assert not db.guild_exists(0)
        db.start_guild(0, 0, "word")
        assert db.guild_exists(0)

    def test_guild_exists(self, db: Database):
        assert not db.guild_exists(0)
        db.start_guild(0, 0, "word")
        assert db.guild_exists(0)
