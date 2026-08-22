from pathlib import Path

from docx import Document
from docx.table import Table as DocxTable
from docx.text.paragraph import Paragraph as DocxParagraph
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DOCX = HERE / "TrustLens_AI_Research_Report.docx"
PDF = HERE / "TrustLens_AI_Research_Report.pdf"
FIGURE = ROOT / "figures" / "final_test_summary.png"

NAVY = colors.HexColor("#17365D")
BLUE = colors.HexColor("#2E74B5")
GRAY = colors.HexColor("#5B6573")
PALE = colors.HexColor("#EAF1F8")
LIGHT = colors.HexColor("#F3F5F7")


def escape(text):
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def iter_blocks(parent):
    for child in parent.element.body.iterchildren():
        if child.tag.endswith("}p"):
            yield DocxParagraph(child, parent)
        elif child.tag.endswith("}tbl"):
            yield DocxTable(child, parent)


def has_page_break(paragraph):
    return bool(paragraph._p.xpath('.//w:br[@w:type="page"]'))


def has_drawing(paragraph):
    return bool(paragraph._p.xpath('.//w:drawing'))


styles = getSampleStyleSheet()
body = ParagraphStyle(
    "PaperBody", parent=styles["BodyText"], fontName="Helvetica", fontSize=9.6,
    leading=12.2, textColor=colors.HexColor("#20252B"), spaceAfter=7,
)
title = ParagraphStyle(
    "PaperTitle", parent=body, fontName="Helvetica-Bold", fontSize=24,
    leading=28, textColor=NAVY, alignment=TA_CENTER, spaceAfter=10,
)
subtitle = ParagraphStyle(
    "PaperSubtitle", parent=body, fontSize=11.5, leading=15, textColor=GRAY,
    alignment=TA_CENTER, spaceAfter=10,
)
kicker = ParagraphStyle(
    "Kicker", parent=body, fontName="Helvetica-Bold", fontSize=10,
    textColor=BLUE, alignment=TA_CENTER, spaceAfter=9,
)
h1 = ParagraphStyle(
    "H1", parent=body, fontName="Helvetica-Bold", fontSize=14.5,
    leading=17, textColor=BLUE, spaceBefore=11, spaceAfter=6, keepWithNext=True,
)
h2 = ParagraphStyle(
    "H2", parent=body, fontName="Helvetica-Bold", fontSize=11.5,
    leading=14, textColor=BLUE, spaceBefore=8, spaceAfter=4, keepWithNext=True,
)
h3 = ParagraphStyle(
    "H3", parent=body, fontName="Helvetica-Bold", fontSize=10.5,
    leading=13, textColor=NAVY, spaceBefore=6, spaceAfter=3, keepWithNext=True,
)
bullet = ParagraphStyle(
    "Bullet", parent=body, leftIndent=18, firstLineIndent=-9, bulletIndent=7,
    spaceAfter=4,
)
caption = ParagraphStyle(
    "Caption", parent=body, fontName="Helvetica-Oblique", fontSize=8.5,
    leading=10.5, textColor=GRAY, alignment=TA_CENTER, spaceAfter=8,
)
table_header = ParagraphStyle(
    "TableHeader", parent=body, fontName="Helvetica-Bold", fontSize=8.8,
    leading=10.5, textColor=colors.white, spaceAfter=0,
)


class ResearchDocTemplate(BaseDocTemplate):
    def __init__(self, filename):
        super().__init__(
            filename, pagesize=LETTER, leftMargin=0.82 * inch,
            rightMargin=0.82 * inch, topMargin=0.72 * inch,
            bottomMargin=0.68 * inch, title="TrustLens AI Research Report",
            author="Akshith Moharampudi",
        )
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="normal")
        self.addPageTemplates(PageTemplate(id="research", frames=frame, onPage=self.decorate))

    def decorate(self, canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica-Bold", 7.5)
        canvas.setFillColor(GRAY)
        canvas.drawString(self.leftMargin, LETTER[1] - 0.39 * inch, "TRUSTLENS AI  |  RESEARCH REPORT")
        canvas.setStrokeColor(colors.HexColor("#D7DEE7"))
        canvas.setLineWidth(0.5)
        canvas.line(self.leftMargin, LETTER[1] - 0.45 * inch, LETTER[0] - self.rightMargin, LETTER[1] - 0.45 * inch)
        canvas.setFont("Helvetica", 8)
        canvas.drawRightString(LETTER[0] - self.rightMargin, 0.38 * inch, f"Page {doc.page}")
        canvas.restoreState()


def convert_table(tbl, first_table=False):
    rows = [[escape(cell.text.strip()) for cell in row.cells] for row in tbl.rows]
    cols = len(rows[0]) if rows else 1
    data = []
    for row_index, row in enumerate(rows):
        row_style = table_header if row_index == 0 and not first_table and cols > 1 else body
        data.append([Paragraph(value or " ", row_style) for value in row])
    if cols == 1:
        widths = [6.5 * inch]
    elif first_table and cols == 2:
        widths = [1.4 * inch, 5.15 * inch]
    elif cols == 2:
        widths = [1.55 * inch, 4.95 * inch]
    elif cols == 3:
        widths = [1.55 * inch, 1.55 * inch, 3.4 * inch]
    elif cols == 4:
        widths = [1.7 * inch, 0.95 * inch, 2.45 * inch, 1.4 * inch]
    elif cols == 6:
        widths = [2.05 * inch, 0.83 * inch, 0.83 * inch, 0.73 * inch, 0.73 * inch, 1.08 * inch]
    else:
        widths = [6.5 * inch / cols] * cols
    out = Table(data, colWidths=widths, repeatRows=0 if first_table else 1, hAlign="CENTER")
    commands = [
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#B9C2CE")),
    ]
    if cols == 1:
        commands += [
            ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#20252B")),
            ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#9FB4CA")),
        ]
    elif first_table:
        commands += [
            ("BACKGROUND", (0, 0), (0, -1), PALE),
            ("TEXTCOLOR", (0, 0), (0, -1), NAVY),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ]
    else:
        commands += [
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ]
    out.setStyle(TableStyle(commands))
    return out


document = Document(DOCX)
story = []
table_count = 0
figure_pending_caption = False
for block in iter_blocks(document):
    if isinstance(block, DocxTable):
        table_count += 1
        story.extend([convert_table(block, first_table=table_count == 1), Spacer(1, 9)])
        continue

    text = block.text.strip()
    style_name = block.style.name if block.style else "Normal"
    if has_page_break(block):
        story.append(PageBreak())
        continue
    if has_drawing(block) and FIGURE.exists():
        img = Image(str(FIGURE), width=5.65 * inch, height=3.04 * inch)
        story.append(img)
        figure_pending_caption = True
        continue
    if not text:
        story.append(Spacer(1, 5))
        continue
    safe = escape(text).replace("\n", "<br/>")
    if text == "TRUSTLENS AI":
        story.append(Spacer(1, 55))
        story.append(Paragraph(safe, kicker))
    elif style_name == "Title":
        story.append(Paragraph(safe, title))
    elif style_name == "Subtitle":
        story.append(Paragraph(safe, subtitle))
    elif style_name == "Heading 1":
        story.append(Paragraph(safe, h1))
    elif style_name == "Heading 2":
        story.append(Paragraph(safe, h2))
    elif style_name == "Heading 3":
        story.append(Paragraph(safe, h3))
    elif style_name.startswith("List Bullet"):
        story.append(Paragraph(safe, bullet, bulletText="•"))
    elif style_name.startswith("List Number"):
        story.append(Paragraph(safe, bullet))
    elif figure_pending_caption and text.startswith("Figure 1."):
        story.append(Paragraph(safe, caption))
        figure_pending_caption = False
    elif text.startswith("Table 1."):
        story.append(Paragraph(safe, caption))
    else:
        story.append(Paragraph(safe, body))

ResearchDocTemplate(str(PDF)).build(story)
print(PDF)
