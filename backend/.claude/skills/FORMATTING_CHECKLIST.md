# FORMATTING CHECKLIST - Read This First!

## Before Generating ANY Excel or PDF File

### Excel Files - Pre-Flight Checklist
- [ ] All column widths auto-adjusted for content
- [ ] Text wrapping enabled for long content
- [ ] All formulas tested for errors (#DIV/0!, #REF!, etc.)
- [ ] Division operations protected with IFERROR() or IF(divisor<>0)
- [ ] Number formats applied (currency, percentages, dates)
- [ ] Headers frozen (freeze panes)
- [ ] Consistent formula structure across rows
- [ ] No hardcoded values in formulas (use cell references)

### PDF Files - Pre-Flight Checklist
- [ ] Table column widths calculated based on content length
- [ ] Margins set to at least 0.75 inches on all sides
- [ ] Font size readable (minimum 9pt for body text)
- [ ] Tables don't exceed available page width
- [ ] Long text wrapped in Paragraph() objects
- [ ] Adequate cell padding (minimum 6pt)
- [ ] Headers repeat on multi-page tables
- [ ] Page breaks used appropriately

## Quick Formula Error Prevention

```python
# Excel - Protect against division by zero
= IFERROR(A1/B1, 0)  # Returns 0 if error
= IF(B1<>0, A1/B1, "-")  # Returns "-" if divisor is zero

# Excel - Protect against missing lookups
= IFERROR(VLOOKUP(A1, range, 2, FALSE), "Not Found")
```

## Quick Table Formatting

```python
# reportlab PDF - Proper table setup
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

page_width = letter[0] - (2 * 0.75 * inch)  # Account for margins
num_columns = 4
col_width = page_width / num_columns

# Or proportional
col_widths = [
    page_width * 0.30,  # 30% for column 1
    page_width * 0.25,  # 25% for column 2
    page_width * 0.20,  # 20% for column 3
    page_width * 0.25   # 25% for column 4
]

table = Table(data, colWidths=col_widths, repeatRows=1)
```

```python
# openpyxl Excel - Auto-adjust after data entry
for column in ws.columns:
    max_length = max(len(str(cell.value or "")) for cell in column)
    ws.column_dimensions[get_column_letter(column[0].column)].width = min(max_length + 2, 50)
```

---
**REMEMBER:** Always test your formatting with the LONGEST expected content, not average content!
