"""
Flask-pohjainen web-käyttöliittymä Kivi-Paperi-Sakset -peliin.
Käyttää olemassa olevaa logiikkaa (Tuomari, Tekoälyt) ja säilyttää pelitilaa selaimen sessiossa.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Dict, Tuple

from flask import Flask, redirect, render_template_string, request, session, url_for

# Varmistetaan, että src-hakemiston moduulit löytyvät, vaikka sovellus ajetaan projektin juuresta
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.append(str(CURRENT_DIR))

from kivi_paperi_sakset import KiviPaperiSakset
from tekoaly import Tekoaly
from tekoaly_parannettu import TekoalyParannettu
from tuomari import Tuomari

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "kehitys-avaa-vaihdettavaksi")

MODES = {
    "a": "Ihminen vs ihminen",
    "b": "Tekoäly",
    "c": "Parannettu tekoäly",
}

VALID_MOVES = {
    "k": "Kivi",
    "p": "Paperi",
    "s": "Sakset",
}

WIN_SCORE = 3


def _is_valid_move(siirto: str) -> bool:
    if not siirto:
        return False
    return KiviPaperiSakset()._onko_ok_siirto(siirto)  # type: ignore[attr-defined]


def _empty_game(mode: str) -> Dict:
    return {
        "mode": mode,
        "scores": {"eka": 0, "toka": 0, "tasapelit": 0},
        "ai_state": {},
        "history": [],
        "status": "ongoing",
        "message": None,
    }


def _tuomari_from_scores(scores: Dict[str, int]) -> Tuomari:
    t = Tuomari()
    t.ekan_pisteet = scores.get("eka", 0)
    t.tokan_pisteet = scores.get("toka", 0)
    t.tasapelit = scores.get("tasapelit", 0)
    return t


def _scores_from_tuomari(tuomari: Tuomari) -> Dict[str, int]:
    return {
        "eka": tuomari.ekan_pisteet,
        "toka": tuomari.tokan_pisteet,
        "tasapelit": tuomari.tasapelit,
    }


def _apply_win_condition(game: Dict, tuomari: Tuomari) -> Dict:
    if tuomari.ekan_pisteet >= WIN_SCORE:
        game["status"] = "ended"
        game["message"] = f"Pelaaja 1 saavutti {WIN_SCORE} pistettä – peli päättyi."
    elif tuomari.tokan_pisteet >= WIN_SCORE:
        game["status"] = "ended"
        game["message"] = f"Vastustaja saavutti {WIN_SCORE} pistettä – peli päättyi."
    return game


def _ai_move(mode: str, first_move: str, ai_state: Dict) -> Tuple[str, Dict]:
    if mode == "b":
        ai = Tekoaly()
        ai._siirto = ai_state.get("siirto", 0)
        opponent_move = ai.anna_siirto()
        return opponent_move, {"siirto": ai._siirto}

    if mode == "c":
        memory = ai_state.get("muisti", [None] * 10)
        index = ai_state.get("indeksi", 0)
        ai = TekoalyParannettu(len(memory))
        ai._muisti = memory
        ai._vapaa_muisti_indeksi = index
        opponent_move = ai.anna_siirto()
        ai.aseta_siirto(first_move)
        return opponent_move, {
            "muisti": ai._muisti,
            "indeksi": ai._vapaa_muisti_indeksi,
        }

    # Ihminen vastaan ihminen -tilassa siirto tulee lomakkeelta
    return "", ai_state


def _round_outcome(tuomari: Tuomari, eka: str, toka: str) -> str:
    if tuomari._tasapeli(eka, toka):
        return "Tasapeli"
    if tuomari._eka_voittaa(eka, toka):
        return "Pelaaja 1 voitti"
    return "Vastustaja voitti"


def _default_message(mode: str) -> str:
    if mode == "a":
        return f"Peli käynnissä: Pelaaja 1 tekee siirron ensin, sitten Pelaaja 2. Ensimmäinen {WIN_SCORE} pisteeseen voittaa."
    return f"Peli käynnissä: Tee siirtosi, tekoäly reagoi. Ensimmäinen {WIN_SCORE} pisteeseen voittaa."


TEMPLATE = """<!doctype html>
<html lang=\"fi\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Kivi-Paperi-Sakset</title>
  <link rel=\"preconnect\" href=\"https://fonts.googleapis.com\" />
  <link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin />
  <link href=\"https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600&display=swap\" rel=\"stylesheet\" />
  <style>
    :root {
      --bg: linear-gradient(135deg, #0f172a 0%, #1f2937 40%, #0f172a 100%);
      --card: rgba(255, 255, 255, 0.06);
      --card-strong: rgba(255, 255, 255, 0.12);
      --text: #e5e7eb;
      --muted: #9ca3af;
      --accent: #f97316;
      --accent-2: #22d3ee;
      --shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.45);
      --radius: 18px;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: 'Space Grotesk', 'Inter', system-ui, -apple-system, sans-serif;
      color: var(--text);
      background-image: var(--bg);
      min-height: 100vh;
      padding: 32px 20px 48px;
      display: flex;
      justify-content: center;
    }
    main {
      width: min(1100px, 100%);
      display: grid;
      gap: 20px;
    }
    header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding: 18px 22px;
      background: var(--card-strong);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
    }
    header h1 { margin: 0; font-size: 24px; letter-spacing: -0.02em; }
    header p { margin: 4px 0 0; color: var(--muted); }
    .tag {
      padding: 6px 12px;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.12);
      font-weight: 600;
      letter-spacing: 0.03em;
      color: var(--accent-2);
    }
    section { background: var(--card); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: var(--radius); padding: 20px; box-shadow: var(--shadow); }
    h2 { margin: 0 0 12px; letter-spacing: -0.01em; }
    form { display: grid; gap: 12px; }
    .grid { display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); }
    .card { background: var(--card-strong); border: 1px solid rgba(255, 255, 255, 0.12); border-radius: var(--radius); padding: 16px; }
    label { font-weight: 600; }
    input[type="text"], select {
      width: 100%;
      padding: 12px 14px;
      border-radius: 12px;
      border: 1px solid rgba(255, 255, 255, 0.2);
      background: rgba(255, 255, 255, 0.04);
      color: var(--text);
      font-size: 16px;
    }
    input[type="text"]:focus, select:focus { outline: 2px solid var(--accent-2); border-color: transparent; }
    button {
      padding: 12px 16px;
      border-radius: 12px;
      border: none;
      cursor: pointer;
      font-weight: 700;
      letter-spacing: 0.01em;
      transition: transform 0.12s ease, box-shadow 0.12s ease, opacity 0.12s ease;
      color: #0b1120;
      background: linear-gradient(135deg, var(--accent) 0%, #fb923c 100%);
      box-shadow: 0 18px 28px -14px rgba(249, 115, 22, 0.65);
    }
    button.secondary { background: rgba(255, 255, 255, 0.1); color: var(--text); box-shadow: none; }
    button:active { transform: translateY(1px); }
    .status { display: flex; gap: 10px; align-items: center; font-weight: 600; color: var(--accent-2); }
    .choice-group { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px; margin: 10px 0 6px; }
    .choice-btn { width: 100%; border: 1px solid rgba(255, 255, 255, 0.18); border-radius: 14px; background: rgba(255, 255, 255, 0.06); padding: 14px 12px; color: var(--text); font-weight: 700; letter-spacing: 0.01em; display: grid; gap: 6px; justify-items: center; cursor: pointer; transition: all 0.14s ease; }
    .choice-btn .icon { width: 56px; height: 56px; border-radius: 16px; display: grid; place-items: center; font-size: 24px; font-weight: 800; color: #0b1120; }
    .choice-btn small { color: var(--muted); font-weight: 500; }
    .choice-btn:hover { transform: translateY(-1px); border-color: var(--accent-2); box-shadow: 0 12px 20px -14px rgba(34, 211, 238, 0.8); }
    .icon.rock { background: linear-gradient(135deg, #94a3b8, #cbd5e1); }
    .icon.paper { background: linear-gradient(135deg, #a5f3fc, #67e8f9); }
    .icon.scissors { background: linear-gradient(135deg, #fca5a5, #f97316); color: #0b1120; }
    .scores { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; }
    .score-box { padding: 14px; border-radius: 14px; background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.08); }
    .score-box strong { display: block; font-size: 14px; color: var(--muted); margin-bottom: 6px; }
    .score-box span { font-size: 26px; font-weight: 700; }
    .history { list-style: none; padding: 0; margin: 0; display: grid; gap: 8px; }
    .history li { padding: 12px 14px; border-radius: 12px; background: rgba(255, 255, 255, 0.06); border: 1px solid rgba(255, 255, 255, 0.1); display: flex; justify-content: space-between; gap: 12px; }
    .muted { color: var(--muted); }
    .badge { padding: 6px 10px; border-radius: 10px; background: rgba(34, 211, 238, 0.16); color: var(--accent-2); font-weight: 700; font-size: 13px; }
    .alert { margin-top: 8px; padding: 12px 14px; border-radius: 12px; background: rgba(239, 68, 68, 0.12); color: #fecdd3; border: 1px solid rgba(239, 68, 68, 0.4); }
  </style>
</head>
<body>
<main>
  <header>
    <div>
      <h1>Kivi-Paperi-Sakset</h1>
      <p>Valitse pelimuoto, tee siirto ja seuraa pistetilannetta kierros kerrallaan.</p>
    </div>
    <span class="tag">Web-versio</span>
  </header>

  <section>
    <div class="grid">
      <div class="card">
        <h2>Aloita peli</h2>
        <form method="post" action="{{ url_for('start') }}">
          <label for="mode">Pelimuoto</label>
          <select name="mode" id="mode" {% if game %}value="{{ game.mode }}"{% endif %}>
            {% for key, label in modes.items() %}
              <option value="{{ key }}" {% if game and game.mode == key %}selected{% endif %}>{{ label }}</option>
            {% endfor %}
          </select>
          <button type="submit">Käynnistä uusi peli</button>
        </form>
      </div>

      <div class="card">
        <h2>Tila</h2>
        {% if not game %}
          <p class="muted">Ei aktiivista peliä. Valitse pelimuoto ja aloita.</p>
        {% else %}
          <div class="status">
            <span class="badge">{{ modes[game.mode] }}</span>
            {% if game.status == 'ended' %}
              <span>Peli päättyi</span>
            {% else %}
              <span>Käynnissä</span>
            {% endif %}
          </div>
          {% if game.message %}
            <div class="alert">{{ game.message }}</div>
          {% endif %}
          <form method="post" action="{{ url_for('reset') }}">
            <button type="submit" class="secondary">Nollaa peli</button>
          </form>
        {% endif %}
      </div>
    </div>
  <section>
    <div class="card">
  <section>
    <div class="grid">
      <div class="card">
        <h2>Siirto</h2>
        {% if not game %}
          <p class="muted">Käynnistä peli ensin.</p>
        {% elif game.status == 'ended' %}
          <p class="muted">Peli on päättynyt. Aloita uusi peli jatkaaksesi.</p>
        {% else %}
          <form method="post" action="{{ url_for('play') }}">
            {% if game.mode != 'a' %}
              <label>Valitse siirto</label>
              <div class="choice-group">
                <button type="submit" name="first_move" value="k" class="choice-btn">
                  <span class="icon rock">🪨</span>
                  <span>Kivi</span>
                  <small>k</small>
                </button>
                <button type="submit" name="first_move" value="p" class="choice-btn">
                  <span class="icon paper">📄</span>
                  <span>Paperi</span>
                  <small>p</small>
                </button>
                <button type="submit" name="first_move" value="s" class="choice-btn">
                  <span class="icon scissors">✂️</span>
                  <span>Sakset</span>
                  <small>s</small>
                </button>
              </div>
            {% else %}
              {% set pending = game.get('pending_first_move') %}
              {% if not pending %}
                <label>Pelaaja 1: Valitse siirto</label>
                <div class="choice-group">
                  <button type="submit" name="first_move" value="k" class="choice-btn">
                    <span class="icon rock">🪨</span>
                    <span>Kivi</span>
                    <small>k</small>
                  </button>
                  <button type="submit" name="first_move" value="p" class="choice-btn">
                    <span class="icon paper">📄</span>
                    <span>Paperi</span>
                    <small>p</small>
                  </button>
                  <button type="submit" name="first_move" value="s" class="choice-btn">
                    <span class="icon scissors">✂️</span>
                    <span>Sakset</span>
                    <small>s</small>
                  </button>
                </div>
              {% else %}
                <label>Pelaaja 2: Valitse siirto</label>
                <div class="choice-group">
                  <button type="submit" name="second_move" value="k" class="choice-btn">
                    <span class="icon rock">🪨</span>
                    <span>Kivi</span>
                    <small>k</small>
                  </button>
                  <button type="submit" name="second_move" value="p" class="choice-btn">
                    <span class="icon paper">📄</span>
                    <span>Paperi</span>
                    <small>p</small>
                  </button>
                  <button type="submit" name="second_move" value="s" class="choice-btn">
                    <span class="icon scissors">✂️</span>
                    <span>Sakset</span>
                    <small>s</small>
                  </button>
                </div>
              {% endif %}
            {% endif %}
          </form>
          <p class="muted">Ensimmäisenä {{ win_score }} pistettä saanut voittaa. Virheellinen siirto (muu kuin k/p/s) päättää pelin.</p>
        {% endif %}
      </div>

      <div class="card">
        <h2>Pistetilanne</h2>
        {% if not game %}
          <p class="muted">Pisteet näkyvät pelin alettua.</p>
        {% else %}
          <div class="scores">
            <div class="score-box">
              <strong>Pelaaja 1</strong>
              <span>{{ game.scores.eka }}</span>
            </div>
            <div class="score-box">
              <strong>Vastustaja</strong>
              <span>{{ game.scores.toka }}</span>
            </div>
            <div class="score-box">
              <strong>Tasapelit</strong>
              <span>{{ game.scores.tasapelit }}</span>
            </div>
          </div>
        {% endif %}
      </div>
    </div>
  </section>

  <section>
    <div class="card">
      <h2>Viime kierrokset</h2>
      {% if not game or not game.history %}
        <p class="muted">Kierroksia ei ole vielä pelattu.</p>
      {% else %}
        <ul class="history">
          {% for round in game.history|reverse %}
            <li>
              <div>
                <div><strong>Pelaaja 1:</strong> {{ round.first_move }} · <strong>Vastustaja:</strong> {{ round.second_move }}</div>
                <div class="muted">{{ round.label }}</div>
              </div>
              <span class="badge">{{ round.outcome }}</span>
            </li>
          {% endfor %}
        </ul>
      {% endif %}
    </div>
  </section>
</main>
</body>
</html>
"""


@app.get("/")
def index():
    game = session.get("game")
    if game and not game.get("message"):
        game["message"] = _default_message(game.get("mode", "a"))
    return render_template_string(
        TEMPLATE, game=game, modes=MODES, valid_moves=VALID_MOVES, win_score=WIN_SCORE
    )


@app.post("/start")
def start():
    mode = request.form.get("mode", "a").strip().lower()
    if mode not in MODES:
        mode = "a"
    session["game"] = _empty_game(mode)
    session["game"]["message"] = _default_message(mode)
    return redirect(url_for("index"))


@app.post("/play")
def play():
    game = session.get("game")
    if not game or game.get("status") == "ended":
        return redirect(url_for("index"))

    mode = game.get("mode", "a")
    first_move = request.form.get("first_move", "").strip().lower()
    second_move_input = request.form.get("second_move", "").strip().lower()

    # Ihminen vs ihminen: kerätään siirrot vuorotellen, ei paljasteta ekaa siirtoa toiselle
    if mode == "a":
        pending = game.get("pending_first_move")

        if pending is None:
            if not _is_valid_move(first_move):
                game["status"] = "ended"
                game["message"] = (
                    "Virheellinen siirto lopetti pelin (vain k/p/s ovat sallittuja)."
                )
            else:
                game["pending_first_move"] = first_move
                game["message"] = (
                    "Ensimmäinen siirto vastaanotettu. Nyt Pelaaja 2 valitsee siirtonsa."
                )
            session["game"] = game
            return redirect(url_for("index"))

        # Toisen pelaajan vuoro
        second_move = second_move_input
        first_move = pending
        game.pop("pending_first_move", None)
        opponent_move = second_move
        ai_state = game.get("ai_state", {})

        if not (_is_valid_move(first_move) and _is_valid_move(second_move)):
            game["status"] = "ended"
            game["message"] = (
                "Virheellinen siirto lopetti pelin (vain k/p/s ovat sallittuja)."
            )
            session["game"] = game
            return redirect(url_for("index"))
    else:
        opponent_move, ai_state = _ai_move(mode, first_move, game.get("ai_state", {}))
        second_move = opponent_move

        if not (_is_valid_move(first_move) and _is_valid_move(second_move)):
            game["status"] = "ended"
            game["message"] = (
                "Virheellinen siirto lopetti pelin (vain k/p/s ovat sallittuja)."
            )
            session["game"] = game
            return redirect(url_for("index"))

    tuomari = _tuomari_from_scores(game.get("scores", {}))
    tuomari.kirjaa_siirto(first_move, second_move)

    outcome = _round_outcome(tuomari, first_move, second_move)
    tuomari_label = str(tuomari)

    history_entry = {
        "first_move": f"{VALID_MOVES.get(first_move, first_move)} ({first_move})",
        "second_move": f"{VALID_MOVES.get(second_move, second_move)} ({second_move})",
        "outcome": outcome,
        "label": tuomari_label,
    }

    game["scores"] = _scores_from_tuomari(tuomari)
    game["ai_state"] = ai_state if mode != "a" else game.get("ai_state", {})
    game.setdefault("history", []).append(history_entry)
    game["history"] = game["history"][-10:]
    game = _apply_win_condition(game, tuomari)
    if game.get("status") != "ended":
        game["message"] = _default_message(mode)
    session["game"] = game

    return redirect(url_for("index"))


@app.post("/reset")
def reset():
    session.pop("game", None)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
