---
name: pdf
description: Comprehensive PDF manipulation toolkit for extracting text and tables, creating new PDFs, merging/splitting documents, and handling forms. When Claude needs to fill in a PDF form or programmatically process, generate, or analyze PDF documents at scale.
license: Proprietary. LICENSE.txt has complete terms
---

# PDF Processing Guide

## Overview

This guide covers essential PDF processing operations using Python libraries and command-line tools. For advanced features, JavaScript libraries, and detailed examples, see reference.md. If you need to fill out a PDF form, read forms.md and follow its instructions.

## CRITICAL: PDF Document Formatting Best Practices

### Prevent Text Overlap and Formatting Issues

When creating PDFs with reportlab or other libraries, **ALWAYS** follow these rules:

#### Table Formatting (MOST CRITICAL)
1. **Calculate column widths properly** - Never use fixed widths that are too small
   ```python
   # ❌ WRONG - Fixed narrow widths cause text overlap
   col_widths = [100, 100, 100]  
   
   # ✅ CORRECT - Calculate based on content or use proportional widths
   from reportlab.lib.units import inch
   col_widths = [2*inch, 1.5*inch, 1*inch, 1.5*inch]  # Adequate space
   
   # ✅ BETTER - Calculate based on page width
   from reportlab.lib.pagesizes import letter
   page_width = letter[0] - 100  # Subtract margins
   col_widths = [page_width * 0.3, page_width * 0.25, page_width * 0.2, page_width * 0.25]
   ```

2. **Use auto-sizing tables when possible**
   ```python
   from reportlab.platypus import Table, TableStyle
   
   # Let reportlab calculate optimal widths
   t = Table(data)  # No colWidths specified - auto-sized
   
   # Or specify minimum widths with '*' for flexible columns
   t = Table(data, colWidths=[2*inch, '*', '*', 1.5*inch])
   ```

3. **Wrap text in cells** - Prevent overflow
   ```python
   from reportlab.platypus import Paragraph
   from reportlab.lib.styles import getSampleStyleSheet
   
   styles = getSampleStyleSheet()
   
   # Wrap long text in Paragraph objects
   data = [
       [Paragraph("Long header text that wraps", styles['Normal']),
        Paragraph("Another long text", styles['Normal'])]
   ]
   ```

4. **Test with actual content lengths** - Use real data to size columns
   ```python
   # Calculate max width needed for each column
   max_widths = []
   for col_idx in range(len(data[0])):
       max_len = max(len(str(row[col_idx])) for row in data)
       max_widths.append(max_len * 6 + 10)  # 6 pts per char + padding
   ```

5. **Set proper table styles** to prevent overlap
   ```python
   table_style = TableStyle([
       ('FONTSIZE', (0, 0), (-1, -1), 9),  # Reduce font if needed
       ('WORDWRAP', (0, 0), (-1, -1)),     # Enable word wrap
       ('VALIGN', (0, 0), (-1, -1), 'TOP'), # Top alignment
       ('PADDING', (0, 0), (-1, -1), 6),    # Adequate padding
       ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
   ])
   ```

#### Page Layout
1. **Use adequate margins** - Never less than 0.5 inches
   ```python
   from reportlab.lib.units import inch
   doc = SimpleDocTemplate(
       filename,
       pagesize=letter,
       topMargin=0.75*inch,
       bottomMargin=0.75*inch,
       leftMargin=0.75*inch,
       rightMargin=0.75*inch
   )
   ```

2. **Break long tables** across pages properly
   ```python
   t = Table(data, repeatRows=1)  # Repeat header on each page
   t.hAlign = 'LEFT'
   ```

3. **Check available width** before creating tables
   ```python
   from reportlab.lib.pagesizes import letter
   page_width, page_height = letter
   available_width = page_width - (2 * 0.75 * inch)  # Subtract margins
   ```

#### Font and Text
1. **Choose readable font sizes** - Minimum 9pt for body text
2. **Use proper line spacing** - At least 1.2x font size
3. **Test text wrapping** - Ensure no text is cut off

#### Common Pitfalls to AVOID
- ❌ Fixed column widths without testing content length
- ❌ Tables wider than page width
- ❌ Font sizes too large for table cells
- ❌ No padding in table cells
- ❌ Missing word wrap settings
- ❌ Hardcoded positions without margin calculations



## Quick Start

```python
from pypdf import PdfReader, PdfWriter

# Read a PDF
reader = PdfReader("document.pdf")
print(f"Pages: {len(reader.pages)}")

# Extract text
text = ""
for page in reader.pages:
    text += page.extract_text()
```

## Python Libraries

### pypdf - Basic Operations

#### Merge PDFs
```python
from pypdf import PdfWriter, PdfReader

writer = PdfWriter()
for pdf_file in ["doc1.pdf", "doc2.pdf", "doc3.pdf"]:
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        writer.add_page(page)

with open("merged.pdf", "wb") as output:
    writer.write(output)
```

#### Split PDF
```python
reader = PdfReader("input.pdf")
for i, page in enumerate(reader.pages):
    writer = PdfWriter()
    writer.add_page(page)
    with open(f"page_{i+1}.pdf", "wb") as output:
        writer.write(output)
```

#### Extract Metadata
```python
reader = PdfReader("document.pdf")
meta = reader.metadata
print(f"Title: {meta.title}")
print(f"Author: {meta.author}")
print(f"Subject: {meta.subject}")
print(f"Creator: {meta.creator}")
```

#### Rotate Pages
```python
reader = PdfReader("input.pdf")
writer = PdfWriter()

page = reader.pages[0]
page.rotate(90)  # Rotate 90 degrees clockwise
writer.add_page(page)

with open("rotated.pdf", "wb") as output:
    writer.write(output)
```

### pdfplumber - Text and Table Extraction

#### Extract Text with Layout
```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        print(text)
```

#### Extract Tables
```python
with pdfplumber.open("document.pdf") as pdf:
    for i, page in enumerate(pdf.pages):
        tables = page.extract_tables()
        for j, table in enumerate(tables):
            print(f"Table {j+1} on page {i+1}:")
            for row in table:
                print(row)
```

#### Advanced Table Extraction
```python
import pandas as pd

with pdfplumber.open("document.pdf") as pdf:
    all_tables = []
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            if table:  # Check if table is not empty
                df = pd.DataFrame(table[1:], columns=table[0])
                all_tables.append(df)

# Combine all tables
if all_tables:
    combined_df = pd.concat(all_tables, ignore_index=True)
    combined_df.to_excel("extracted_tables.xlsx", index=False)
```

### reportlab - Create PDFs

#### Basic PDF Creation
```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

c = canvas.Canvas("hello.pdf", pagesize=letter)
width, height = letter

# Add text
c.drawString(100, height - 100, "Hello World!")
c.drawString(100, height - 120, "This is a PDF created with reportlab")

# Add a line
c.line(100, height - 140, 400, height - 140)

# Save
c.save()
```

#### Create PDF with Multiple Pages
```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

doc = SimpleDocTemplate("report.pdf", pagesize=letter)
styles = getSampleStyleSheet()
story = []

# Add content
title = Paragraph("Report Title", styles['Title'])
story.append(title)
story.append(Spacer(1, 12))

body = Paragraph("This is the body of the report. " * 20, styles['Normal'])
story.append(body)
story.append(PageBreak())

# Page 2
story.append(Paragraph("Page 2", styles['Heading1']))
story.append(Paragraph("Content for page 2", styles['Normal']))

# Build PDF
doc.build(story)
```

## Command-Line Tools

### pdftotext (poppler-utils)
```bash
# Extract text
pdftotext input.pdf output.txt

# Extract text preserving layout
pdftotext -layout input.pdf output.txt

# Extract specific pages
pdftotext -f 1 -l 5 input.pdf output.txt  # Pages 1-5
```

### qpdf
```bash
# Merge PDFs
qpdf --empty --pages file1.pdf file2.pdf -- merged.pdf

# Split pages
qpdf input.pdf --pages . 1-5 -- pages1-5.pdf
qpdf input.pdf --pages . 6-10 -- pages6-10.pdf

# Rotate pages
qpdf input.pdf output.pdf --rotate=+90:1  # Rotate page 1 by 90 degrees

# Remove password
qpdf --password=mypassword --decrypt encrypted.pdf decrypted.pdf
```

### pdftk (if available)
```bash
# Merge
pdftk file1.pdf file2.pdf cat output merged.pdf

# Split
pdftk input.pdf burst

# Rotate
pdftk input.pdf rotate 1east output rotated.pdf
```

## Common Tasks

### Extract Text from Scanned PDFs
```python
# Requires: pip install pytesseract pdf2image
import pytesseract
from pdf2image import convert_from_path

# Convert PDF to images
images = convert_from_path('scanned.pdf')

# OCR each page
text = ""
for i, image in enumerate(images):
    text += f"Page {i+1}:\n"
    text += pytesseract.image_to_string(image)
    text += "\n\n"

print(text)
```

### Add Watermark
```python
from pypdf import PdfReader, PdfWriter

# Create watermark (or load existing)
watermark = PdfReader("watermark.pdf").pages[0]

# Apply to all pages
reader = PdfReader("document.pdf")
writer = PdfWriter()

for page in reader.pages:
    page.merge_page(watermark)
    writer.add_page(page)

with open("watermarked.pdf", "wb") as output:
    writer.write(output)
```

### Extract Images
```bash
# Using pdfimages (poppler-utils)
pdfimages -j input.pdf output_prefix

# This extracts all images as output_prefix-000.jpg, output_prefix-001.jpg, etc.
```

### Password Protection
```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
writer = PdfWriter()

for page in reader.pages:
    writer.add_page(page)

# Add password
writer.encrypt("userpassword", "ownerpassword")

with open("encrypted.pdf", "wb") as output:
    writer.write(output)
```

## Quick Reference

| Task | Best Tool | Command/Code |
|------|-----------|--------------|
| Merge PDFs | pypdf | `writer.add_page(page)` |
| Split PDFs | pypdf | One page per file |
| Extract text | pdfplumber | `page.extract_text()` |
| Extract tables | pdfplumber | `page.extract_tables()` |
| Create PDFs | reportlab | Canvas or Platypus |
| Command line merge | qpdf | `qpdf --empty --pages ...` |
| OCR scanned PDFs | pytesseract | Convert to image first |
| Fill PDF forms | pdf-lib or pypdf (see forms.md) | See forms.md |

## Next Steps

- For advanced pypdfium2 usage, see reference.md
- For JavaScript libraries (pdf-lib), see reference.md
- If you need to fill out a PDF form, follow the instructions in forms.md
- For troubleshooting guides, see reference.md
