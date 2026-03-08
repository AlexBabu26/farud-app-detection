#!/usr/bin/env python3
"""
Convert schema.md to a clean PDF: one section per table with title = table name,
followed by the columns table and any notes (foreign keys, indexes, etc.).

Requires: pip install reportlab
Usage: python scripts/schema_to_pdf.py [schema.md] [--output schema.pdf]
"""

import argparse
import re
import sys
from pathlib import Path


def parse_schema_md(content: str) -> list[dict]:
    """Parse schema.md into a list of table sections."""
    sections = []
    # Split by table headers: ## Table: `name`
    pattern = r"## Table: `([^`]+)`\s*\n+(.*?)(?=\n---\n|\n## Table:|\n## Entity|\Z)"
    for m in re.finditer(pattern, content, re.DOTALL):
        table_name = m.group(1).strip()
        body = m.group(2).strip()
        # First paragraph = description (until first | or **)
        desc_match = re.match(r"^([^\n|*]+(?:\n(?!\||\*\*)[^\n|*]*)*)", body)
        description = desc_match.group(1).strip() if desc_match else ""
        # Markdown table: lines starting with |
        table_lines = []
        in_table = False
        notes = []  # list of (heading, bullet_lines)
        current_heading = None
        current_bullets = []
        for line in body.split("\n"):
            if line.strip().startswith("|") and "---" not in line:
                in_table = True
                # Split by | and keep empty cells so PK/FK columns align
                raw = [c.strip() for c in line.strip().split("|")]
                if raw and raw[0] == "" and raw[-1] == "":
                    raw = raw[1:-1]
                cells = raw
                if cells and (cells[0].lower() != "column" or len(table_lines) > 0):
                    table_lines.append(cells)
            elif in_table and line.strip().startswith("|") and "---" in line:
                continue  # skip separator row
            else:
                in_table = False
                if line.strip().startswith("**") and line.strip().endswith("**"):
                    if current_heading:
                        notes.append((current_heading, current_bullets))
                    current_heading = line.strip().strip("*")
                    current_bullets = []
                elif line.strip().startswith("- ") and current_heading:
                    current_bullets.append(line.strip()[2:].strip())
        if current_heading:
            notes.append((current_heading, current_bullets))
        # Normalize table: first row might be header
        if table_lines and table_lines[0][0].lower() == "column":
            # Skip original header
            rows = table_lines[1:]
        else:
            rows = table_lines

        # Transform to Field, Data Types, Constraints
        new_header = ["Field", "Data Types", "Constraints"]
        new_rows = []
        for r in rows:
            # Ensure we have enough columns (Markdown table might vary)
            while len(r) < 5:
                r.append("")
            
            field = r[0]
            dtype = r[1]
            pk = r[2]
            fk = r[3]
            desc = r[4]
            
            constraints = []
            if "✓" in pk or "PK" in pk:
                constraints.append("Primary Key")
            if "✓" in fk or "FK" in fk:
                constraints.append("Foreign Key")
            
            # Extract common constraints from description
            desc_lower = desc.lower()
            if "auto-increment" in desc_lower:
                constraints.append("Auto-increment")
            if "unique" in desc_lower:
                constraints.append("Unique")
            if "nullable" in desc_lower:
                constraints.append("Nullable")
            if "not null" in desc_lower:
                constraints.append("Not Null")

            new_rows.append([field, dtype, ", ".join(constraints)])

        sections.append({
            "table_name": table_name,
            "description": description,
            "header": new_header,
            "rows": new_rows,
            "notes": [],  # No footer notes requested
        })
    return sections


def build_pdf(sections: list[dict], output_path: str, schema_title: str = "Database Schema") -> None:
    """Generate PDF using reportlab."""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
        )
    except ImportError:
        print("Install reportlab: pip install reportlab  (or: uv pip install reportlab)")
        sys.exit(1)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        name="SchemaTitle",
        parent=styles["Heading1"],
        fontSize=18,
        spaceAfter=12,
    )
    table_title_style = ParagraphStyle(
        name="TableTitle",
        parent=styles["Heading2"],
        fontSize=14,
        spaceBefore=14,
        spaceAfter=6,
    )
    body_style = styles["Normal"]
    note_heading_style = ParagraphStyle(
        name="NoteHeading",
        parent=styles["Heading3"],
        fontSize=10,
        spaceBefore=8,
        spaceAfter=4,
    )
    story = []
    story.append(Paragraph(schema_title, title_style))
    story.append(Spacer(1, 0.2 * inch))

    for sec in sections:
        # Section title = table name
        story.append(Paragraph(sec["table_name"], table_title_style))
        if sec["description"]:
            story.append(Paragraph(sec["description"], body_style))
            story.append(Spacer(1, 0.1 * inch))
        # Columns table
        header = sec["header"]
        rows = sec["rows"]
        ncols = len(header)
        # Pad rows to same width as header
        rows = [list(r) + [""] * (ncols - len(r)) for r in rows]
        rows = [r[:ncols] for r in rows]
        if rows:
            data = [header] + rows
            col_widths = [doc.width / len(header)] * len(header)
            if len(header) == 3:
                col_widths[0] = doc.width * 0.30  # Field
                col_widths[1] = doc.width * 0.30  # Data Types
                col_widths[2] = doc.width * 0.40  # Constraints
            elif len(header) >= 5:
                col_widths[0] = doc.width * 0.18   # Column
                col_widths[1] = doc.width * 0.14   # Data Type
                col_widths[2] = doc.width * 0.06   # PK
                col_widths[3] = doc.width * 0.06   # FK
                col_widths[4] = doc.width - sum(col_widths[:4])  # Description
            t = Table(data, colWidths=col_widths[: len(header)])
            t.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.white),
                        ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("ALIGN", (2, 0), (3, -1), "CENTER"),  # PK, FK
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 10),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                        ("TOPPADDING", (0, 0), (-1, -1), 6),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ]
                )
            )
            story.append(t)
            story.append(Spacer(1, 0.15 * inch))
        # Notes (Foreign keys, Indexes, etc.)
        for heading, bullets in sec["notes"]:
            story.append(Paragraph(heading, note_heading_style))
            for b in bullets:
                story.append(Paragraph(f"• {b}", body_style))
            story.append(Spacer(1, 0.05 * inch))
        story.append(Spacer(1, 0.15 * inch))

    doc.build(story)
    print(f"Wrote {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Convert schema.md to PDF.")
    parser.add_argument("input", nargs="?", default="schema.md", help="Input schema.md path")
    parser.add_argument("--output", "-o", default="schema.pdf", help="Output PDF path")
    parser.add_argument("--title", "-t", default="Database Schema", help="PDF main title")
    args = parser.parse_args()
    input_path = Path(args.input)
    if not input_path.is_file():
        print(f"File not found: {input_path}")
        sys.exit(2)
    content = input_path.read_text(encoding="utf-8")
    sections = parse_schema_md(content)
    if not sections:
        print("No table sections found in schema.md")
        sys.exit(3)
    build_pdf(sections, args.output, schema_title=args.title)


if __name__ == "__main__":
    main()
