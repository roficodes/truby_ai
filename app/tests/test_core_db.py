from sqlmodel import SQLModel
from sqlmodel import Session
import tempfile
import os

import app.core.db as core_db


def test_init_db_and_get_session(tmp_path, monkeypatch):
    # point DB path to a temp file
    db_file = tmp_path / "test.db"
    monkeypatch.setenv("SQL_DB_PATH", str(db_file))

    # re-import module to pick up env change
    import importlib
    importlib.reload(core_db)

    # initialize DB
    core_db.init_db()

    # get a session and ensure it yields a Session instance
    gen = core_db.get_session()
    sess = next(gen)
    assert isinstance(sess, Session)
    sess.close()
