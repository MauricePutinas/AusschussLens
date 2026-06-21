"""Rendert einen 8D-Report als audit-taugliches PDF (pure-Python via xhtml2pdf)."""
import html
from datetime import datetime
from io import BytesIO

from xhtml2pdf import pisa


def _esc(value) -> str:
    return html.escape(str(value if value is not None else "-"))


def _ul(items) -> str:
    items = items or []
    lis = "".join(f"<li>{_esc(i)}</li>" for i in items)
    return f"<ul>{lis}</ul>" if lis else "<p>-</p>"


def _whys(items) -> str:
    rows = ""
    for idx, w in enumerate(items or [], start=1):
        if isinstance(w, dict):
            frage, antwort = w.get("frage", ""), w.get("antwort", "")
        else:
            frage, antwort = "Warum?", w
        rows += (f'<tr><td class="wn">{idx}</td>'
                 f'<td class="wq">{_esc(frage)}</td>'
                 f'<td class="wa">{_esc(antwort)}</td></tr>')
    return (f'<table class="whys"><tr><th>#</th><th>Frage</th><th>Antwort</th></tr>{rows}</table>'
            if rows else "<p>-</p>")


def _row(disc: str, title: str, body_html: str) -> str:
    return (f'<tr><td class="disc">{disc}</td>'
            f'<td class="dtitle">{_esc(title)}</td>'
            f'<td class="dbody">{body_html}</td></tr>')


def _build_html(event: dict, report: dict) -> str:
    d = report.get("data", {})
    created = report.get("created_at", "")[:16].replace("T", " ")
    cost = event.get("total_cost") or 0
    warn = d.get("_warnung")

    body = "".join([
        _row("D1", "Team", _ul(d.get("d1_team"))),
        _row("D2", "Problembeschreibung", f"<p>{_esc(d.get('d2_problem'))}</p>"),
        _row("D3", "Sofortmassnahmen", _ul(d.get("d3_sofort"))),
        _row("D4", "Ursachenanalyse (5-Why)",
             f"<p><b>{_esc(d.get('d4_ursache'))}</b></p>" + _whys(d.get("d4_five_whys"))),
        _row("D5", "Abstellmassnahmen", _ul(d.get("d5_abstell"))),
        _row("D6", "Wirksamkeitspruefung", f"<p>{_esc(d.get('d6_wirksamkeit'))}</p>"),
        _row("D7", "Vorbeugung / Lessons Learned", _ul(d.get("d7_praevention"))),
        _row("D8", "Wuerdigung des Teams", f"<p>{_esc(d.get('d8_wuerdigung'))}</p>"),
    ])

    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
    @page {{ size: A4; margin: 1.6cm; }}
    body {{ font-family: Helvetica, Arial, sans-serif; font-size: 9.5pt; color: #1a1a1a; }}
    .head {{ background: #0f172a; color: #fff; padding: 10px 14px; }}
    .head h1 {{ font-size: 15pt; margin: 0; }}
    .head .sub {{ font-size: 8.5pt; color: #93c5fd; margin-top: 2px; }}
    .meta {{ width: 100%; border-collapse: collapse; margin: 10px 0 4px; }}
    .meta td {{ border: 1px solid #cbd5e1; padding: 4px 7px; font-size: 8.5pt; }}
    .meta .k {{ background: #f1f5f9; font-weight: bold; width: 22%; }}
    table.eightd {{ width: 100%; border-collapse: collapse; margin-top: 6px; }}
    table.eightd td {{ border: 1px solid #cbd5e1; padding: 6px 8px; vertical-align: top; }}
    td.disc {{ background: #1d4ed8; color: #fff; font-weight: bold; width: 8%; text-align: center; }}
    td.dtitle {{ background: #eef2ff; font-weight: bold; width: 22%; }}
    ul {{ margin: 0; padding-left: 14px; }}
    table.whys {{ width: 100%; border-collapse: collapse; margin-top: 4px; }}
    table.whys th, table.whys td {{ border: 1px solid #dbeafe; padding: 3px 6px; font-size: 8.5pt; }}
    table.whys th {{ background: #dbeafe; }}
    .wn {{ width: 6%; text-align: center; }} .wq {{ width: 40%; }}
    .warn {{ background: #fef3c7; border: 1px solid #f59e0b; padding: 5px 8px; font-size: 8pt; margin-top: 6px; }}
    .foot {{ margin-top: 10px; font-size: 7.5pt; color: #64748b; }}
    </style></head><body>
    <div class="head">
      <h1>8D-Report &middot; {_esc(d.get('report_no'))}</h1>
      <div class="sub">{_esc(d.get('titel'))} &nbsp;|&nbsp; erstellt mit AusschussLens</div>
    </div>
    <table class="meta">
      <tr><td class="k">Sach-Nr.</td><td>{_esc(event.get('part_no'))}</td>
          <td class="k">Teil</td><td>{_esc(event.get('part_name'))}</td></tr>
      <tr><td class="k">Maschine</td><td>{_esc(event.get('machine_name'))} ({_esc(event.get('machine_code'))})</td>
          <td class="k">Fehler</td><td>{_esc(event.get('cause_name'))}</td></tr>
      <tr><td class="k">Menge</td><td>{_esc(event.get('quantity'))} Stk</td>
          <td class="k">Ausschusswert</td><td>{cost:.2f} EUR</td></tr>
      <tr><td class="k">Report-Datum</td><td>{_esc(created)}</td>
          <td class="k">Status</td><td>8D erstellt</td></tr>
    </table>
    {f'<div class="warn">{_esc(warn)}</div>' if warn else ''}
    <table class="eightd">{body}</table>
    <div class="foot">Automatisch generiert am {_esc(created)} &middot; AusschussLens v0.1 &middot;
      Provider: {_esc(report.get('provider'))}</div>
    </body></html>"""


def render_report_pdf(event: dict, report: dict) -> bytes:
    out = BytesIO()
    pisa.CreatePDF(src=_build_html(event, report), dest=out, encoding="utf-8")
    return out.getvalue()
