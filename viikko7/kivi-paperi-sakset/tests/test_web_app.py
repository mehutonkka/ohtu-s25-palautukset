import sys
from pathlib import Path

# Ensure src is on path when running pytest from project root
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.append(str(SRC))

from web_app import WIN_SCORE, app  # noqa: E402


def _fresh_client():
    app.config.update(TESTING=True, SECRET_KEY="test-key")
    return app.test_client()


def test_start_initializes_session():
    client = _fresh_client()
    resp = client.post("/start", data={"mode": "b"})
    assert resp.status_code == 302

    with client.session_transaction() as sess:
        game = sess.get("game")
        assert game is not None
        assert game["mode"] == "b"
        assert game["status"] == "ongoing"
        assert game["scores"] == {"eka": 0, "toka": 0, "tasapelit": 0}


def test_play_ai_round_records_score_and_history():
    client = _fresh_client()
    client.post("/start", data={"mode": "b"})

    resp = client.post("/play", data={"first_move": "k"})
    assert resp.status_code == 302

    with client.session_transaction() as sess:
        game = sess.get("game")
        assert game is not None
        assert game["status"] in ("ongoing", "ended")
        assert game["scores"] == {"eka": 0, "toka": 1, "tasapelit": 0}
        assert len(game.get("history", [])) == 1
        round_entry = game["history"][0]
        assert round_entry["first_move"].endswith("(k)")
        assert round_entry["second_move"].endswith("(p)")  # Tekoaly aloittaa paperilla


def test_invalid_move_ends_game_without_history():
    client = _fresh_client()
    client.post("/start", data={"mode": "a"})

    # ensin ok eka siirto
    client.post("/play", data={"first_move": "k"})
    # sitten virheellinen toka siirto
    resp = client.post("/play", data={"second_move": "x"})
    assert resp.status_code == 302

    with client.session_transaction() as sess:
        game = sess.get("game")
        assert game is not None
        assert game["status"] == "ended"
        assert "Virheellinen" in (game.get("message") or "")
        assert game.get("history", []) == []


def test_game_ends_when_player_reaches_five_points():
    client = _fresh_client()
    client.post("/start", data={"mode": "b"})

    # Pelaaja 1 valitsee aina kiven; perustekoaly kiertää p/s/k ja kerää viisi voittoa 13 kierroksessa
    for _ in range(13):
        client.post("/play", data={"first_move": "k"})

    with client.session_transaction() as sess:
        game = sess.get("game")
        assert game is not None
        assert game["status"] == "ended"
        assert game["scores"]["toka"] >= WIN_SCORE
        assert f"saavutti {WIN_SCORE} pistettä" in (game.get("message") or "")
