"""
src/agent/tools/appointments.py

Tools for booking a maintenance appointment at the (fictional) Toyota
dealership demo. Deterministic logic only (slot rules, SQLite reads/writes,
date parsing) — the LLM never computes availability or formats the
confirmation itself, it just calls these tools and relays their output.

Storage: a small local SQLite file (data/appointments.db, gitignored).
Availability rule is intentionally simple (no real calendar integration):
fixed hourly slots, Monday-Friday, 9h-12h and 14h-18h.
"""

import sqlite3
from datetime import datetime
from pathlib import Path

from langchain_core.tools import tool

DB_PATH = Path("data/appointments.db")

SLOT_HOURS = ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00", "17:00"]
DATE_FORMATS = ("%Y-%m-%d", "%d/%m/%Y")


def _get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            modele TEXT NOT NULL,
            kilometrage INTEGER NOT NULL,
            date TEXT NOT NULL,
            heure TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    return conn


def _parse_date(date: str) -> datetime | None:
    """Parse a date string in one of the accepted formats, or None if invalid."""
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(date.strip(), fmt)
        except ValueError:
            continue
    return None


def _booked_slots(conn: sqlite3.Connection, date: str) -> set[str]:
    rows = conn.execute(
        "SELECT heure FROM appointments WHERE date = ?", (date,)
    ).fetchall()
    return {row[0] for row in rows}


@tool
def check_availability(date: str) -> str:
    """
    List the available appointment slots for a given date at the dealership.

    Use this before booking, to show the customer which time slots are free
    on the date they want.

    Args:
        date (str): The requested date, formatted "YYYY-MM-DD" or "DD/MM/YYYY".

    Returns:
        str: A short sentence listing the free slots (e.g. "09:00, 10:00,
        14:00"), or a clear message if the date is invalid, in the past, or
        a weekend (the garage is closed Saturday/Sunday).
    """
    parsed = _parse_date(date)
    if parsed is None:
        return (
            f"Impossible de comprendre la date '{date}'. "
            "Merci de la donner au format JJ/MM/AAAA."
        )

    if parsed.date() < datetime.now().date():
        return f"Le {parsed.strftime('%d/%m/%Y')} est déjà passé. Merci de choisir une date future."

    if parsed.weekday() >= 5:  # Saturday=5, Sunday=6
        return f"Le garage est fermé le {parsed.strftime('%d/%m/%Y')} (week-end). Merci de choisir un jour en semaine."

    normalized = parsed.strftime("%Y-%m-%d")
    conn = _get_connection()
    try:
        taken = _booked_slots(conn, normalized)
    finally:
        conn.close()

    free = [h for h in SLOT_HOURS if h not in taken]
    if not free:
        return f"Il n'y a plus de créneau disponible le {parsed.strftime('%d/%m/%Y')}. Merci de choisir une autre date."

    return f"Créneaux disponibles le {parsed.strftime('%d/%m/%Y')} : {', '.join(free)}."


@tool
def book_appointment(
    modele: str, kilometrage: int, date: str, heure: str, confirme: bool = False
) -> str:
    """
    Book a maintenance appointment. Call check_availability first.

    IMPORTANT: this tool refuses to book unless confirme=True. The correct
    sequence is: collect model/mileage/date, call check_availability,
    propose a slot, RECAP everything out loud and ask the customer for an
    explicit yes/no, and only THEN call this tool again with confirme=True.
    A first call with confirme=False (the default) is expected and will
    return a recap to read back to the customer — that is not an error.

    Args:
        modele (str): The car model (e.g. "Yaris", "Corolla").
        kilometrage (int): Current mileage in kilometers.
        date (str): The appointment date, "YYYY-MM-DD" or "DD/MM/YYYY".
        heure (str): The chosen time slot, e.g. "09:00" (must be one of the
            slots returned by check_availability for that date).
        confirme (bool): Set to True only after the customer has explicitly
            said yes to the recap. Defaults to False.

    Returns:
        str: A pre-formatted confirmation sentence once actually booked
        (confirme=True), a recap to confirm with the customer
        (confirme=False), or a clear error message if the date/slot is
        invalid or no longer available.
    """
    parsed = _parse_date(date)
    if parsed is None:
        return (
            f"Impossible de comprendre la date '{date}'. "
            "Merci de la donner au format JJ/MM/AAAA."
        )
    if parsed.weekday() >= 5:
        return f"Le garage est fermé le {parsed.strftime('%d/%m/%Y')} (week-end)."

    heure = heure.strip()
    if heure not in SLOT_HOURS:
        return (
            f"'{heure}' n'est pas un créneau valide. "
            f"Créneaux possibles : {', '.join(SLOT_HOURS)}."
        )

    normalized = parsed.strftime("%Y-%m-%d")
    conn = _get_connection()
    try:
        # Checked both before and after the confirmation step, in case the
        # slot got taken by someone else while the customer was confirming.
        if heure in _booked_slots(conn, normalized):
            return f"Le créneau {heure} du {parsed.strftime('%d/%m/%Y')} vient d'être pris. Merci de choisir un autre créneau."

        if not confirme:
            return (
                f"Récapitulatif : {modele} ({kilometrage} km), "
                f"le {parsed.strftime('%d/%m/%Y')} à {heure}. "
                "Demande au client de confirmer, puis rappelle cet outil avec "
                "confirme=True s'il dit oui."
            )

        conn.execute(
            "INSERT INTO appointments (modele, kilometrage, date, heure, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (modele, kilometrage, normalized, heure, datetime.now().isoformat()),
        )
        conn.commit()
    finally:
        conn.close()

    return (
        f"Rendez-vous confirmé pour une {modele} ({kilometrage} km) "
        f"le {parsed.strftime('%d/%m/%Y')} à {heure}."
    )


TOOLS = [check_availability, book_appointment]
