"""
report.py
=========
Builds a formal equilibrium-calculation report as a PDF.

Typography: Times New Roman everywhere.
  * Looks for a real Times New Roman TTF on the machine, then for Liberation Serif
            (metric-compatible with Times New Roman), then DejaVu Serif, and finally falls back
            to the built-in PDF Times-Roman face (characters that face lacks are transliterated).

The module knows nothing about Streamlit. It receives a plain dictionary ("payload"):

    {
      "title": str, "author": str, "date": str,
      "calc_label": str, "reaction": str,
      "settings": [(label, value), ...],
      "solutions": [
          {"tag": str, "headline": str | None,
           "summary": [(label, value), ...],
           "tables": [{"title": str, "header": [...], "rows": [[...], ...], "note": str | None}],
           "warnings": [str], "working": [str]},
      ],
      "notes": [str],
    }
"""

from __future__ import annotations

import io
import os
from xml.sax.saxutils import escape

FOOTER_TEXT = "Chemical Reaction Equilibrium Simulator"

# ------------------------------------------------------------------
# Font discovery (PDF)
# ------------------------------------------------------------------

_WIN = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")


def _family(folder, regular, bold, italic, bold_italic, label):
    return (label, [os.path.join(folder, f) for f in (regular, bold, italic, bold_italic)])


_FONT_FAMILIES = [
    _family(_WIN, "times.ttf", "timesbd.ttf", "timesi.ttf", "timesbi.ttf", "Times New Roman"),
    _family("/Library/Fonts", "Times New Roman.ttf", "Times New Roman Bold.ttf",
            "Times New Roman Italic.ttf", "Times New Roman Bold Italic.ttf", "Times New Roman"),
    _family("/System/Library/Fonts/Supplemental", "Times New Roman.ttf", "Times New Roman Bold.ttf",
            "Times New Roman Italic.ttf", "Times New Roman Bold Italic.ttf", "Times New Roman"),
    _family("/usr/share/fonts/truetype/msttcorefonts", "Times_New_Roman.ttf", "Times_New_Roman_Bold.ttf",
            "Times_New_Roman_Italic.ttf", "Times_New_Roman_Bold_Italic.ttf", "Times New Roman"),
    _family("/usr/share/fonts/truetype/liberation", "LiberationSerif-Regular.ttf", "LiberationSerif-Bold.ttf",
            "LiberationSerif-Italic.ttf", "LiberationSerif-BoldItalic.ttf", "Liberation Serif (Times-compatible)"),
    _family("/usr/share/fonts/truetype/liberation2", "LiberationSerif-Regular.ttf", "LiberationSerif-Bold.ttf",
            "LiberationSerif-Italic.ttf", "LiberationSerif-BoldItalic.ttf", "Liberation Serif (Times-compatible)"),
    _family("/usr/share/fonts/truetype/dejavu", "DejaVuSerif.ttf", "DejaVuSerif-Bold.ttf",
            "DejaVuSerif-Italic.ttf", "DejaVuSerif-BoldItalic.ttf", "DejaVu Serif"),
]

_FONT_STATE = {}


def _setup_pdf_fonts():
    """Register a serif family once. Returns a dict describing the choice."""
    if _FONT_STATE:
        return _FONT_STATE
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.fonts import addMapping

    for label, paths in _FONT_FAMILIES:
        if all(os.path.isfile(p) for p in paths):
            try:
                names = ("RptSerif", "RptSerif-Bold", "RptSerif-Italic", "RptSerif-BoldItalic")
                fonts = [TTFont(n, p) for n, p in zip(names, paths)]
                for f in fonts:
                    pdfmetrics.registerFont(f)
                pdfmetrics.registerFontFamily(names[0], normal=names[0], bold=names[1],
                                              italic=names[2], boldItalic=names[3])
                cmap = fonts[0].face.charToGlyph
                _FONT_STATE.update(regular=names[0], bold=names[1], italic=names[2], bold_italic=names[3],
                                   label=label, ttf=True, supports=lambda ch, cm=cmap: ord(ch) in cm)
                return _FONT_STATE
            except Exception:
                continue

    _FONT_STATE.update(regular="Times-Roman", bold="Times-Bold", italic="Times-Italic",
                       bold_italic="Times-BoldItalic", label="Times (built-in PDF font)", ttf=False,
                       supports=lambda ch: ord(ch) < 256)
    return _FONT_STATE


def pdf_font_label():
    """Name of the serif face the PDF will use (for display in the app)."""
    try:
        return _setup_pdf_fonts()["label"]
    except Exception:
        return "Times"


# ------------------------------------------------------------------
# Text sanitising for PDF (only touches characters the font cannot draw)
# ------------------------------------------------------------------

_GREEK = dict(zip("αβγδεζηθικλμνξοπρστυφχψω", "abgdezhqiklmnxoprstufcyw"))
_GREEK.update(zip("ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ", "ABGDEZHQIKLMNXOPRSTUFCYW"))
_SUB = dict(zip("₀₁₂₃₄₅₆₇₈₉ᵢⱼₙₐₑₒₓ₊₋", "0123456789ijnaeox+-"))
_SUP = dict(zip("⁰¹²³⁴⁵⁶⁷⁸⁹ⁱⁿᴱ⁺⁻°", "0123456789inE+-°"))
_ASCII = {"−": "-", "–": "-", "—": "-", "→": "->", "⇌": "<->", "↔": "<->", "≈": "~", "≤": "<=", "≥": ">=",
          "≠": "!=", "∞": "inf", "′": "'", "’": "'", "‘": "'", "“": '"', "”": '"', "…": "...", "∑": "Sum",
          "∏": "Prod", "·": "·", "×": "×", "°": "°", "✓": "yes"}
_COMBINING = {"\u0302", "\u0303", "\u0304", "\u0307"}


def _pdf_text(text, supports):
    out = []
    for ch in str(text):
        if ch in _COMBINING:
            continue
        if ch == "&":
            out.append("&amp;")
        elif ch == "<":
            out.append("&lt;")
        elif ch == ">":
            out.append("&gt;")
        elif ch in "\n\r\t" or supports(ch):
            out.append(" " if ch in "\r\t" else ("<br/>" if ch == "\n" else ch))
        elif ch in ("Δ", "∆"):
            out.append("Delta ")      # reportlab's built-in Symbol font has no usable capital delta
        elif ch in _GREEK:
            out.append(f"<greek>{_GREEK[ch]}</greek>")
        elif ch in _SUB:
            out.append(f"<sub>{_SUB[ch]}</sub>")
        elif ch in _SUP:
            out.append(f"<super>{_SUP[ch]}</super>")
        elif ch in _ASCII:
            out.append(escape(_ASCII[ch]))
        else:
            out.append("?")
    return "".join(out)


# ------------------------------------------------------------------
# PDF
# ------------------------------------------------------------------

def build_pdf(payload):
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (HRFlowable, KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table,
                                    TableStyle)

    fs = _setup_pdf_fonts()
    sup = fs["supports"]
    T = lambda s: _pdf_text(s, sup)  # noqa: E731

    ink = colors.HexColor("#17324d")
    grey = colors.HexColor("#5b6b7b")
    band = colors.HexColor("#eaf0f6")
    rule = colors.HexColor("#b9c7d6")

    base = ParagraphStyle("base", fontName=fs["regular"], fontSize=11, leading=15, alignment=TA_JUSTIFY)
    s_title = ParagraphStyle("title", parent=base, fontName=fs["bold"], fontSize=21, leading=26,
                             alignment=TA_CENTER, textColor=ink, spaceAfter=4)
    s_meta = ParagraphStyle("meta", parent=base, alignment=TA_CENTER, fontName=fs["italic"], fontSize=10.5,
                            textColor=grey, leading=14)
    s_h1 = ParagraphStyle("h1", parent=base, fontName=fs["bold"], fontSize=14, leading=18, textColor=ink,
                          spaceBefore=14, spaceAfter=5, alignment=0)
    s_h2 = ParagraphStyle("h2", parent=base, fontName=fs["bold"], fontSize=11.5, leading=15, textColor=ink,
                          spaceBefore=9, spaceAfter=3, alignment=0)
    s_eq = ParagraphStyle("eq", parent=base, fontName=fs["italic"], fontSize=12.5, leading=17,
                          alignment=TA_CENTER, spaceBefore=4, spaceAfter=4)
    s_head = ParagraphStyle("head", parent=base, fontName=fs["bold"], fontSize=11.5, leading=15,
                            textColor=ink, alignment=0, backColor=band, borderPadding=(5, 6, 5, 6),
                            spaceBefore=6, spaceAfter=8)
    s_note = ParagraphStyle("note", parent=base, fontName=fs["italic"], fontSize=9, leading=12, textColor=grey,
                            alignment=0, spaceBefore=2)
    s_warn = ParagraphStyle("warn", parent=base, fontSize=10, leading=13, textColor=colors.HexColor("#8a4b08"),
                            alignment=0, leftIndent=8)
    s_work = ParagraphStyle("work", parent=base, fontSize=10.5, leading=14, alignment=0, leftIndent=10)
    cell = ParagraphStyle("cell", parent=base, fontSize=9, leading=11, alignment=0)
    cell_b = ParagraphStyle("cellb", parent=cell, fontName=fs["bold"])
    cell_h = ParagraphStyle("cellh", parent=cell, fontName=fs["bold"], fontSize=8.2, leading=10, textColor=colors.white)

    width = A4[0] - 4.4 * cm

    def make_table(header, rows, first_weight=1.0):
        ncol = len(header)
        weights = [first_weight] + [1.0] * (ncol - 1)
        col_w = [width * w / sum(weights) for w in weights]
        data = [[Paragraph(T(h), cell_h) for h in header]]
        for r in rows:
            data.append([Paragraph(T(v), cell_b if j == 0 else cell) for j, v in enumerate(r)])
        t = Table(data, colWidths=col_w, repeatRows=1)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), ink),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, band]),
            ("GRID", (0, 0), (-1, -1), 0.4, rule),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 3.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
            ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ]))
        return t

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(rule)
        canvas.setLineWidth(0.5)
        canvas.line(2.2 * cm, 1.6 * cm, A4[0] - 2.2 * cm, 1.6 * cm)
        canvas.setFont(fs["italic"], 8.5)
        canvas.setFillColor(grey)
        canvas.drawString(2.2 * cm, 1.1 * cm, _pdf_plain(payload.get("title", ""), sup)[:80])
        canvas.drawRightString(A4[0] - 2.2 * cm, 1.1 * cm, f"Page {doc.page}")
        canvas.restoreState()

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=2.2 * cm, rightMargin=2.2 * cm, topMargin=2.0 * cm,
                            bottomMargin=2.2 * cm, title=payload.get("title", "Equilibrium report"),
                            author=payload.get("author", "") or FOOTER_TEXT)
    story = [Paragraph(T(payload.get("title", "Chemical Equilibrium Report")), s_title)]
    meta = [m for m in (payload.get("author"), payload.get("date")) if m]
    if meta:
        story.append(Paragraph(T("  |  ".join(meta)), s_meta))
    story += [Spacer(1, 6), HRFlowable(width="100%", thickness=1.1, color=ink, spaceAfter=4)]

    story.append(Paragraph("1. Problem statement", s_h1))
    story.append(Paragraph(T(f"Calculation requested: {payload['calc_label']}."), base))
    story.append(Paragraph(T(payload["reaction"]), s_eq))

    story.append(Paragraph("2. Input data and models", s_h1))
    story.append(make_table(["Item", "Value"], [[k, v] for k, v in payload["settings"]], first_weight=0.55))

    story.append(Paragraph("3. Results", s_h1))
    for sol in payload["solutions"]:
        block = [Paragraph(T(sol["tag"]), s_h2)]
        if sol.get("headline"):
            block.append(Paragraph(T(sol["headline"]), s_head))
        if sol.get("summary"):
            block.append(make_table([k for k, _ in sol["summary"]], [[v for _, v in sol["summary"]]]))
        story.append(KeepTogether(block))
        for tb in sol.get("tables", []):
            story.append(Spacer(1, 7))
            story.append(Paragraph(T(tb["title"]), s_h2))
            story.append(make_table(tb["header"], tb["rows"], first_weight=1.3))
            if tb.get("note"):
                story.append(Paragraph(T(tb["note"]), s_note))
        for w in sol.get("warnings", []):
            story.append(Spacer(1, 4))
            story.append(Paragraph(T("Note: " + w), s_warn))
        if sol.get("working"):
            story.append(Paragraph(T(f"Working - {sol['tag'].lower()}"), s_h2))
            for line in sol["working"]:
                story.append(Paragraph(T(line), s_work))

    if payload.get("notes"):
        story.append(Paragraph("4. Notes", s_h1))
        for n in payload["notes"]:
            story.append(Paragraph(T(n), s_note))

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return buf.getvalue()


def _pdf_plain(text, supports):
    """Plain (non-markup) text for canvas.drawString: strip anything the font cannot draw."""
    return "".join(ch for ch in str(text) if supports(ch) and ch not in _COMBINING)
