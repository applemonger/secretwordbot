import pytest
from bot.database import Database


@pytest.fixture()
def db():
    db = Database("db/test.db")
    yield db
    db.clear()


class TestDatabase:
    def test_get_secret(self, db: Database):
        assert db.get_secret(0) is None
        db.start_guild(0, 0, "word")
        assert db.get_secret(0) == "word"

    def test_secret_is_set(self, db: Database):
        assert not db.secret_is_set(0)
        db.start_guild(0, 0, "word")
        assert db.secret_is_set(0)
        assert not db.secret_is_set(1)

    def test_get_keeper(self, db: Database):
        assert db.get_keeper(0) is None
        db.start_guild(0, 0, "word")
        assert db.get_keeper(0) == 0
        db.change_keeper(0, 1)
        assert db.get_keeper(0) == 1

    def test_get_hints(self, db: Database):
        assert db.get_hints(0) == []
        db.add_hint(0, "hint")
        assert db.get_hints(0) == ["hint"]
        db.add_hint(0, "hint2")
        assert db.get_hints(0) == ["hint", "hint2"]

    def test_add_hint(self, db: Database):
        assert db.get_hints(0) == []
        db.add_hint(0, "hint")
        assert db.get_hints(0) == ["hint"]
        db.add_hint(0, "hint2")
        assert db.get_hints(0) == ["hint", "hint2"]

    def test_change_keeper(self, db: Database):
        db.start_guild(0, 0, "word")
        assert db.get_keeper(0) == 0
        assert db.get_secret(0) == "word"
        db.change_keeper(0, 1)
        assert db.get_keeper(0) == 1
        assert db.get_secret(0) is None

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
        assert secret is None
        db.start_guild(0, 0, "word")
        secret = db.get_secret(0)
        assert secret == "word"
        db.set_word(0, "sword")
        secret = db.get_secret(0)
        assert secret == "sword"

    def test_is_keeper(self, db: Database):
        db.start_guild(0, 0, "word")
        assert db.is_keeper(0, 0)
        assert not db.is_keeper(0, 1)
        assert not db.is_keeper(1, 0)
        assert not db.is_keeper(1, 1)

    def test_start_guild(self, db: Database):
        assert not db.guild_exists(0)
        db.start_guild(0, 0, "word")
        assert db.guild_exists(0)

    def test_guild_exists(self, db: Database):
        assert not db.guild_exists(0)
        db.start_guild(0, 0, "word")
        assert db.guild_exists(0)
