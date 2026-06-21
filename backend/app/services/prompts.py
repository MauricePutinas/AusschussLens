"""Prompt-Bausteine fuer die KI-gestuetzte 8D-Generierung."""

SYSTEM_8D = (
    "Du bist ein erfahrener Qualitaetsingenieur (QM) in einem produzierenden "
    "Mittelstandsbetrieb und erstellst professionelle 8D-Reports nach Automotive-"
    "Standard (IATF 16949 / VDA). Du arbeitest praezise, sachlich und auf Deutsch. "
    "Du nutzt die 5-Why-Methode fuer die Ursachenanalyse und unterscheidest sauber "
    "zwischen Sofort- (D3), Abstell- (D5) und Vorbeugemassnahmen (D7). "
    "Antworte AUSSCHLIESSLICH mit einem gueltigen JSON-Objekt, ohne Markdown, ohne "
    "Codeblock, ohne erklaerenden Text davor oder danach."
)

_SCHEMA_HINT = """Erzeuge ein JSON-Objekt mit exakt diesen Schluesseln:
{
  "titel": "kurzer Titel des Reports",
  "d1_team": ["Rolle 1", "Rolle 2", "..."],
  "d2_problem": "praezise Problembeschreibung mit Teil, Maschine, Menge, Kosten",
  "d3_sofort": ["Sofortmassnahme 1", "..."],
  "d4_ursache": "Grundursache in 1-3 Saetzen",
  "d4_five_whys": [
     {"frage": "Warum ...?", "antwort": "Weil ..."},
     ... genau 5 Eintraege, die logisch zur Grundursache fuehren ...
  ],
  "d5_abstell": ["Abstellmassnahme 1", "..."],
  "d6_wirksamkeit": "wie die Wirksamkeit geprueft wird",
  "d7_praevention": ["Vorbeugemassnahme 1 (FMEA/Pruefplan/Standard)", "..."],
  "d8_wuerdigung": "kurze Wuerdigung des Teams und Lessons Learned"
}"""


def build_user_prompt(event: dict) -> str:
    cost = event.get("total_cost") or 0
    return (
        "Erstelle einen vollstaendigen 8D-Report fuer folgenden Ausschuss-Vorfall:\n"
        f"- Sach-Nr.: {event.get('part_no')}\n"
        f"- Teil: {event.get('part_name') or '-'}\n"
        f"- Maschine/Anlage: {event.get('machine_name') or '-'} ({event.get('machine_code') or '-'})\n"
        f"- Fehler/Ursachen-Kategorie: {event.get('cause_name') or '-'} "
        f"[{event.get('cause_category') or '-'}]\n"
        f"- Menge Ausschuss: {event.get('quantity')}\n"
        f"- Geschaetzter Ausschusswert: {cost:.2f} EUR\n"
        f"- Beobachtung vor Ort: {event.get('note') or '-'}\n\n"
        + ("Falls ein Foto des Ausschussteils beiliegt, beziehe sichtbare Auffaelligkeiten "
           "in die Problembeschreibung (D2) ein.\n\n" if event.get("photo_path") else "")
        + _SCHEMA_HINT
    )
