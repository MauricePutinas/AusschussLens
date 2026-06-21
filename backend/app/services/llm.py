"""LLM-Abstraktion: erzeugt strukturierte 8D-Daten.

Provider:
  - "mock"      -> deterministischer, fachlich sauberer 8D-Entwurf (ohne API-Key).
  - "anthropic" -> echte KI-Generierung mit Claude (Text + optional Foto-Analyse).
"""
import base64
import json
import re

from ..config import LLM_PROVIDER, ANTHROPIC_API_KEY, ANTHROPIC_MODEL
from .prompts import SYSTEM_8D, build_user_prompt

# Erwartete Schluessel eines vollstaendigen Reports
_KEYS = ["titel", "d1_team", "d2_problem", "d3_sofort", "d4_ursache",
         "d4_five_whys", "d5_abstell", "d6_wirksamkeit", "d7_praevention", "d8_wuerdigung"]


def generate_8d(event: dict, image_bytes: bytes | None = None) -> tuple[dict, str]:
    """Liefert (report_data, provider_tag)."""
    if LLM_PROVIDER == "anthropic" and ANTHROPIC_API_KEY:
        try:
            data = _anthropic_8d(event, image_bytes)
            return _normalize(data, event), f"anthropic:{ANTHROPIC_MODEL}"
        except Exception as exc:  # robust: nie die Demo crashen lassen
            data = _mock_8d(event)
            data["_warnung"] = f"KI nicht erreichbar, Mock-Entwurf verwendet ({exc})."
            return data, "mock-fallback"
    return _mock_8d(event), "mock"


# ---------------------------------------------------------------- Anthropic
def _anthropic_8d(event: dict, image_bytes: bytes | None) -> dict:
    from anthropic import Anthropic

    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    content: list = [{"type": "text", "text": build_user_prompt(event)}]
    if image_bytes:
        content.insert(0, {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": _media_type(event.get("photo_path")),
                "data": base64.standard_b64encode(image_bytes).decode(),
            },
        })
    msg = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=2500,
        system=SYSTEM_8D,
        messages=[{"role": "user", "content": content}],
    )
    text = "".join(getattr(b, "text", "") for b in msg.content if getattr(b, "type", "") == "text")
    return _parse_json(text)


def _parse_json(text: str) -> dict:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise ValueError("Keine gueltige JSON-Antwort vom Modell erhalten.")


def _normalize(data: dict, event: dict) -> dict:
    """Stellt sicher, dass alle Schluessel vorhanden und sauber typisiert sind."""
    base = _mock_8d(event)
    for k in _KEYS:
        if data.get(k):
            base[k] = data[k]
    # five_whys robust normalisieren
    whys = []
    for w in base.get("d4_five_whys", []):
        if isinstance(w, dict):
            whys.append({"frage": str(w.get("frage", "Warum?")),
                         "antwort": str(w.get("antwort", w.get("weil", "")))})
        else:
            whys.append({"frage": "Warum?", "antwort": str(w)})
    base["d4_five_whys"] = whys
    for list_key in ("d1_team", "d3_sofort", "d5_abstell", "d7_praevention"):
        if not isinstance(base.get(list_key), list):
            base[list_key] = [str(base.get(list_key, ""))]
    return base


def _media_type(name: str | None) -> str:
    n = (name or "").lower()
    if n.endswith(".png"):
        return "image/png"
    if n.endswith(".webp"):
        return "image/webp"
    if n.endswith(".gif"):
        return "image/gif"
    return "image/jpeg"


# ---------------------------------------------------------------- Mock
_WHY_CHAINS = {
    "Maschine": [
        ("Warum trat der Fehler auf?", "Das Werkzeug/Prozessmittel lag ausserhalb seines spezifizierten Zustands."),
        ("Warum lag es ausserhalb der Spezifikation?", "Standzeit bzw. Verschleissgrenze wurde ueberschritten, bevor ein Wechsel erfolgte."),
        ("Warum wurde die Grenze ueberschritten?", "Es gab keine verbindliche, zaehlerbasierte Wechsel-/Wartungsvorgabe."),
        ("Warum fehlte die Vorgabe?", "Der Werkzeug-/Wartungsplan war nicht datenbasiert hinterlegt und nicht ueberwacht."),
        ("Warum war er nicht ueberwacht?", "Es fehlt eine systematische Erfassung von Stueckzahl/Zustand pro Werkzeug (Grundursache)."),
    ],
    "Material": [
        ("Warum trat der Fehler auf?", "Das eingesetzte Material bzw. die Charge entsprach nicht der Spezifikation."),
        ("Warum wurde fehlerhaftes Material verarbeitet?", "Der Materialfehler wurde im Wareneingang nicht erkannt."),
        ("Warum wurde er nicht erkannt?", "Die Wareneingangspruefung deckt dieses Merkmal nicht ab."),
        ("Warum deckt sie es nicht ab?", "Der Pruefumfang basiert nicht auf einer Risikobewertung der Merkmale."),
        ("Warum fehlt diese Bewertung?", "Es fehlt eine merkmalsbasierte WE-Pruefstrategie mit dem Lieferanten (Grundursache)."),
    ],
    "Mensch": [
        ("Warum trat der Fehler auf?", "Der Prozess wurde nicht gemaess Vorgabe ausgefuehrt."),
        ("Warum wich die Ausfuehrung ab?", "Die korrekte Vorgehensweise war im Moment nicht eindeutig verfuegbar."),
        ("Warum war sie nicht verfuegbar?", "Die Standardarbeitsanweisung war unvollstaendig oder nicht am Arbeitsplatz."),
        ("Warum war die Einweisung nicht abgesichert?", "Qualifizierung und Freigabe waren nicht systematisch geregelt."),
        ("Warum konnte der Fehler ueberhaupt passieren?", "Es fehlt eine fehlersichere Vorrichtung/Freigabe (Poka-Yoke), die den Fehler unmoeglich macht (Grundursache)."),
    ],
    "Methode": [
        ("Warum trat der Fehler auf?", "Die angewandte Methode bzw. Parametrierung war nicht prozesssicher."),
        ("Warum war sie nicht prozesssicher?", "Prozessparameter lagen ausserhalb des sicheren Fensters."),
        ("Warum lagen sie ausserhalb?", "Das sichere Prozessfenster war nicht definiert/dokumentiert."),
        ("Warum war es nicht definiert?", "Kritische Parameter wurden nicht geregelt oder ueberwacht."),
        ("Warum fehlte die Ueberwachung?", "Kritische Merkmale werden nicht statistisch ueberwacht (SPC fehlt) (Grundursache)."),
    ],
    "Messung": [
        ("Warum trat der Fehler auf?", "Die Messung/Pruefung lieferte ein falsches Ergebnis (Schlupf)."),
        ("Warum war die Messung falsch?", "Das Pruefmittel/der Sensor war nicht faehig oder dejustiert."),
        ("Warum war es dejustiert?", "Es fehlte eine regelmaessige Pruefmittelfaehigkeit/Kalibrierung."),
        ("Warum fehlte die Kalibrierung?", "Kalibrier- und MSA-Intervalle waren nicht festgelegt."),
        ("Warum waren sie nicht festgelegt?", "Es fehlt ein abgesichertes Pruefmittelmanagement (Grundursache)."),
    ],
}
_WHY_CHAINS["Mitwelt"] = _WHY_CHAINS["Methode"]

_CORRECTIVE = {
    "Maschine": ["Zaehlerbasierten Werkzeug-/Wartungsplan einfuehren und im System hinterlegen.",
                 "Standzeitueberwachung pro Werkzeug aktivieren, Wechsel vor Erreichen der Grenze.",
                 "Werkzeug/Anlage instand setzen und Erstmusterfreigabe nach Eingriff."],
    "Material": ["Merkmalsbasierte Wareneingangspruefung fuer kritische Merkmale einfuehren.",
                 "Reklamation/8D beim Lieferanten anstossen, Charge sperren.",
                 "Spezifikation und Pruefvereinbarung mit Lieferant aktualisieren."],
    "Mensch": ["Standardarbeitsanweisung ueberarbeiten und am Arbeitsplatz visualisieren.",
               "Poka-Yoke / Vorrichtung ergaenzen, die Falschteil/Fehlbedienung verhindert.",
               "Qualifizierung und Freigabe der Mitarbeiter dokumentiert sicherstellen."],
    "Methode": ["Sicheres Prozessfenster definieren und in der Anweisung dokumentieren.",
                "SPC fuer kritische Parameter/Merkmale einfuehren.",
                "Prozess-FMEA aktualisieren und Massnahmen ableiten."],
    "Messung": ["Pruefmittel kalibrieren und Pruefmittelfaehigkeit (MSA) nachweisen.",
                "Kalibrier- und Pruefintervalle verbindlich festlegen.",
                "Pruefanweisung und Lehren/Sensoren absichern."],
}
_CORRECTIVE["Mitwelt"] = _CORRECTIVE["Methode"]

_PREVENTION = {
    "Maschine": ["Werkzeug-Standzeitmanagement als Standard ueber alle vergleichbaren Anlagen ausrollen.",
                 "Wartungsplan und FMEA aktualisieren, Wirksamkeit im Audit nachhalten."],
    "Material": ["WE-Pruefstrategie auf vergleichbare Teile/Lieferanten uebertragen.",
                 "Lieferantenbewertung und Spezifikationen anpassen, Lessons Learned dokumentieren."],
    "Mensch": ["Poka-Yoke-Prinzip auf aehnliche Arbeitsplaetze uebertragen.",
               "Schulungsstandard und Freigabeprozess firmenweit verankern."],
    "Methode": ["SPC/Prozessfenster-Standard auf vergleichbare Prozesse ausrollen.",
                "Control-Plan und FMEA als Lessons Learned aktualisieren."],
    "Messung": ["Pruefmittelmanagement systematisch fuer alle kritischen Merkmale etablieren.",
                "Kalibrier-/MSA-Standard in das QM-System aufnehmen."],
}
_PREVENTION["Mitwelt"] = _PREVENTION["Methode"]


def _mock_8d(event: dict) -> dict:
    part = event.get("part_name") or event.get("part_no") or "Teil"
    cause = event.get("cause_name") or "Fehler"
    category = event.get("cause_category") or "Maschine"
    machine = event.get("machine_name") or "der Anlage"
    qty = event.get("quantity") or 0
    cost = event.get("total_cost") or 0
    note = (event.get("note") or "").strip()

    whys = [{"frage": q, "antwort": a} for q, a in _WHY_CHAINS.get(category, _WHY_CHAINS["Maschine"])]
    root = whys[-1]["antwort"]

    return {
        "titel": f"8D-Report: {cause} an {part}",
        "d1_team": [
            "Q-Ingenieur (Teamleitung 8D)",
            f"Schichtmeister {machine}",
            "Einrichter / Werker",
            "Instandhaltung",
            "Einkauf / Lieferantenbetreuung",
        ],
        "d2_problem": (
            f"An {machine} wurden {qty} Teile '{part}' (Sach-Nr. {event.get('part_no')}) "
            f"als Ausschuss aufgrund '{cause}' erfasst. Geschaetzter Ausschusswert: {cost:.2f} EUR."
            + (f" Beobachtung vor Ort: {note}." if note else "")
        ),
        "d3_sofort": [
            f"Betroffene Charge an {machine} gesperrt und mit Q-Sperre gekennzeichnet.",
            "100%-Sortierung der seit der letzten i.O.-Pruefung gefertigten Teile.",
            "NIO-Teile dokumentiert verschrottet bzw. zur Nacharbeit freigegeben.",
            "Folgeprozess und ggf. Kunde ueber moeglichen Durchschlupf informiert.",
        ],
        "d4_ursache": f"Grundursache: {root}",
        "d4_five_whys": whys,
        "d5_abstell": _CORRECTIVE.get(category, _CORRECTIVE["Maschine"]),
        "d6_wirksamkeit": (
            "Wirksamkeit ueber die naechsten 3 Fertigungslose bzw. 2 Wochen verfolgt: "
            "Die Ausschussquote fuer diese Ursache muss auf 0 sinken. Pruefnachweis im 8D-Anhang."
        ),
        "d7_praevention": _PREVENTION.get(category, _PREVENTION["Maschine"]),
        "d8_wuerdigung": (
            "Das Team hat den Fehler schnell eingegrenzt und nachhaltig abgestellt. "
            "Die Erkenntnisse werden in FMEA, Pruefplan und Standardarbeitsanweisung uebernommen."
        ),
    }
