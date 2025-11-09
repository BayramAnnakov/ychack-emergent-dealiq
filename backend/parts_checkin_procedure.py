"""
Automotive Parts Check-In Procedure Document Generator
Creates a professional PDF guide for dealership parts departments
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    ListFlowable, ListItem, KeepTogether
)
from reportlab.pdfgen import canvas
from datetime import datetime

def create_parts_checkin_procedure():
    """Generate comprehensive parts check-in procedure PDF"""

    output_file = "/app/backend/ab81b076-e5d8-473a-9bdb-7ea7c38f6ebc_output.pdf"

    # Create document
    doc = SimpleDocTemplate(
        output_file,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )

    # Styles
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=20,
        textColor=colors.HexColor('#1a365d'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#4a5568'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )

    heading1_style = ParagraphStyle(
        'CustomHeading1',
        parent=styles['Heading1'],
        fontSize=14,
        textColor=colors.HexColor('#1a365d'),
        spaceAfter=10,
        spaceBefore=16,
        fontName='Helvetica-Bold',
        borderWidth=0,
        borderColor=colors.HexColor('#1a365d'),
        borderPadding=0,
        leftIndent=0
    )

    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#2d3748'),
        spaceAfter=8,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#2d3748'),
        spaceAfter=6,
        alignment=TA_JUSTIFY,
        leading=14
    )

    warning_style = ParagraphStyle(
        'Warning',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#c53030'),
        spaceAfter=8,
        leftIndent=20,
        fontName='Helvetica-Bold',
        backColor=colors.HexColor('#fff5f5'),
        borderWidth=1,
        borderColor=colors.HexColor('#fc8181'),
        borderPadding=8
    )

    important_style = ParagraphStyle(
        'Important',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#2c5282'),
        spaceAfter=8,
        leftIndent=20,
        fontName='Helvetica-Bold',
        backColor=colors.HexColor('#ebf8ff'),
        borderWidth=1,
        borderColor=colors.HexColor('#4299e1'),
        borderPadding=8
    )

    # Build document content
    story = []

    # ===== TITLE PAGE =====
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("AUTOMOTIVE PARTS CHECK-IN", title_style))
    story.append(Paragraph("Standard Operating Procedure", subtitle_style))
    story.append(Spacer(1, 0.3*inch))

    # Info box
    info_data = [
        ['Document Type:', 'Standard Operating Procedure'],
        ['Audience:', 'Dealership Parts Department Staff'],
        ['Effective Date:', datetime.now().strftime('%B %Y')],
        ['Version:', '1.0']
    ]

    info_table = Table(info_data, colWidths=[2*inch, 3.5*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e2e8f0')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2d3748')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.5*inch))

    # Purpose
    story.append(Paragraph("PURPOSE", heading1_style))
    story.append(Paragraph(
        "This procedure establishes a standardized process for checking in stock and critical parts orders "
        "at automotive dealerships. The goal is to ensure order accuracy, maintain inventory integrity, "
        "reduce discrepancies, and facilitate timely communication with the manufacturer's parts distribution center.",
        body_style
    ))
    story.append(Spacer(1, 0.2*inch))

    # Scope
    story.append(Paragraph("SCOPE", heading1_style))
    story.append(Paragraph(
        "This procedure applies to all parts department personnel responsible for receiving, inspecting, "
        "and processing incoming parts deliveries from the manufacturer's distribution center.",
        body_style
    ))

    story.append(PageBreak())

    # ===== OVERVIEW SECTION =====
    story.append(Paragraph("ORDER TYPES: KEY DIFFERENCES", heading1_style))
    story.append(Spacer(1, 0.1*inch))

    # Table comparing order types
    order_types_data = [
        ['Characteristic', 'Stock Orders', 'Critical Orders'],
        ['Definition', 'Regularly scheduled replenishment orders for inventory maintained on parts shelves',
         'Urgent orders for specific customer repairs or immediate service needs'],
        ['Frequency', 'Daily or scheduled deliveries', 'As needed, often same-day or next-day'],
        ['Priority', 'Standard processing', 'HIGH PRIORITY - Process immediately upon arrival'],
        ['Documentation', 'Standard bill of lading', 'May include rush tags, customer work order numbers'],
        ['Shelf Location', 'Standard bin locations per parts catalog', 'Hold for specific technician or work order'],
        ['System Entry', 'Receive into inventory', 'Receive and immediately allocate to work order']
    ]

    order_table = Table(order_types_data, colWidths=[1.5*inch, 2.75*inch, 2.75*inch])
    order_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e0')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#e2e8f0')),
    ]))
    story.append(order_table)
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph(
        "<b>⚠ CRITICAL ORDER ALERT:</b> Critical orders must be identified immediately upon delivery "
        "and processed before stock orders to minimize vehicle downtime.",
        important_style
    ))

    story.append(PageBreak())

    # ===== STEP-BY-STEP PROCEDURE =====
    story.append(Paragraph("PARTS CHECK-IN PROCEDURE", heading1_style))
    story.append(Paragraph(
        "Follow these steps from delivery arrival through system confirmation:",
        body_style
    ))
    story.append(Spacer(1, 0.15*inch))

    # Step 1
    story.append(Paragraph("STEP 1: DELIVERY ARRIVAL & INITIAL VERIFICATION", heading2_style))

    step1_items = [
        "<b>1.1</b> Greet the delivery driver and note the arrival time in the parts receiving log.",
        "<b>1.2</b> Request the bill of lading (BOL) and any accompanying delivery documentation.",
        "<b>1.3</b> Verify driver identity and delivery company authorization (check ID badge if required by dealership policy).",
        "<b>1.4</b> <b>IDENTIFY ORDER TYPE:</b> Check for rush tags, red labels, or \"CRITICAL\" markings on boxes or documentation.",
        "<b>1.5</b> Count the total number of boxes/packages and compare to the quantity listed on the BOL.",
        "<b>1.6</b> Conduct a visual inspection for obvious external damage (crushed boxes, torn packaging, leaking fluids)."
    ]

    for item in step1_items:
        story.append(Paragraph(item, body_style))

    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(
        "<b>✓ CHECKPOINT:</b> If package count does not match BOL or significant damage is visible, "
        "note discrepancies on BOL and have driver sign acknowledgment BEFORE unloading.",
        important_style
    ))
    story.append(Spacer(1, 0.15*inch))

    # Step 2
    story.append(Paragraph("STEP 2: UNLOADING & STAGING", heading2_style))

    step2_items = [
        "<b>2.1</b> Unload all packages from the delivery vehicle to the designated receiving area.",
        "<b>2.2</b> <b>SEPARATE ORDER TYPES:</b> Place critical orders in a clearly marked \"CRITICAL/URGENT\" staging area, away from stock orders.",
        "<b>2.3</b> Organize stock order boxes by invoice number or order number for efficient processing.",
        "<b>2.4</b> Keep the bill of lading with the corresponding shipment at all times during the check-in process.",
        "<b>2.5</b> For temperature-sensitive parts (batteries, fluids, electronics in extreme weather), prioritize inspection and move to climate-controlled storage."
    ]

    for item in step2_items:
        story.append(Paragraph(item, body_style))

    story.append(Spacer(1, 0.15*inch))

    # Step 3
    story.append(Paragraph("STEP 3: DETAILED INSPECTION - CRITICAL ORDERS FIRST", heading2_style))

    story.append(Paragraph("<b>3A. CRITICAL ORDERS (Process immediately)</b>", body_style))

    step3a_items = [
        "<b>3A.1</b> Open each critical order package carefully using a box cutter (cut tape, not the box).",
        "<b>3A.2</b> Match each part to the critical order invoice and work order documentation.",
        "<b>3A.3</b> Verify part number, description, and quantity match the order.",
        "<b>3A.4</b> Inspect each part for damage: check for cracks, scratches, bent components, missing hardware.",
        "<b>3A.5</b> If part is correct and undamaged, immediately deliver to the requesting technician or service advisor.",
        "<b>3A.6</b> If discrepancy or damage found, see STEP 5 (Handling Issues) before notifying the service department."
    ]

    for item in step3a_items:
        story.append(Paragraph(item, body_style))

    story.append(Spacer(1, 0.1*inch))

    story.append(Paragraph("<b>3B. STOCK ORDERS (Process after critical orders complete)</b>", body_style))

    step3b_items = [
        "<b>3B.1</b> Open each stock order package systematically, working through invoices in numerical order.",
        "<b>3B.2</b> Match each part to the stock order invoice line by line.",
        "<b>3B.3</b> Verify part number, description, and quantity for every item.",
        "<b>3B.4</b> Inspect for visible damage or defects.",
        "<b>3B.5</b> Set aside parts with issues (see STEP 5) and continue checking remaining parts.",
        "<b>3B.6</b> Check for manufacturer's packing lists inside boxes - these may contain important notes."
    ]

    for item in step3b_items:
        story.append(Paragraph(item, body_style))

    story.append(Spacer(1, 0.15*inch))

    # Step 4
    story.append(Paragraph("STEP 4: SYSTEM ENTRY & CONFIRMATION", heading2_style))

    step4_items = [
        "<b>4.1</b> Log into the dealership parts management system (DMS).",
        "<b>4.2</b> Navigate to the 'Receive Parts' or 'Check-In' module.",
        "<b>4.3</b> Enter the invoice number or scan the barcode from the bill of lading.",
        "<b>4.4</b> <b>FOR CRITICAL ORDERS:</b> Confirm receipt and immediately issue parts to the specific work order. Verify technician or service advisor receives notification.",
        "<b>4.5</b> <b>FOR STOCK ORDERS:</b> Confirm receipt of each line item. System will update inventory quantities and bin locations.",
        "<b>4.6</b> Review the on-screen summary for accuracy before final confirmation.",
        "<b>4.7</b> Complete the receiving transaction in the system. Print receiving document if required by dealership policy.",
        "<b>4.8</b> Attach the receiving document to the bill of lading and file in the daily receiving folder."
    ]

    for item in step4_items:
        story.append(Paragraph(item, body_style))

    story.append(PageBreak())

    # Step 5 - Handling Issues
    story.append(Paragraph("STEP 5: HANDLING COMMON ISSUES", heading1_style))
    story.append(Paragraph(
        "When discrepancies occur, immediate documentation and communication are critical to resolution:",
        body_style
    ))
    story.append(Spacer(1, 0.15*inch))

    # Issue A: Damaged Parts
    story.append(Paragraph("<b>ISSUE A: DAMAGED PARTS</b>", heading2_style))

    damaged_steps = [
        "<b>A.1</b> DO NOT remove the part from the original packaging.",
        "<b>A.2</b> Take clear, well-lit photos showing:",
        "    • The damaged part from multiple angles",
        "    • The part label/part number visible in the photo",
        "    • The damaged packaging (exterior and interior)",
        "    • The shipping label and box markings",
        "<b>A.3</b> Place a highly visible RED \"DAMAGED\" tag on the package.",
        "<b>A.4</b> Move the damaged package to the designated damage holding area (separate from regular stock).",
        "<b>A.5</b> Note the damage on the bill of lading: write \"DAMAGED\" next to the line item and initial.",
        "<b>A.6</b> In the DMS system, do NOT receive the damaged part. Mark as \"damaged in transit\" or use your system's rejection code.",
        "<b>A.7</b> Contact the parts distribution center within 24 hours (call or use online portal):",
        "    • Provide invoice number, part number, and description of damage",
        "    • Submit photos via email or parts return portal",
        "    • Request return authorization (RA) number",
        "    • For critical orders, request emergency replacement with expedited shipping",
        "<b>A.8</b> Complete a Parts Damage Report form (if required by your dealership) and submit to parts manager.",
        "<b>A.9</b> <b>FOR CRITICAL ORDERS:</b> Immediately notify the service advisor and explore alternative solutions (loaner part, local parts runner, etc.)."
    ]

    for item in damaged_steps:
        story.append(Paragraph(item, body_style))

    story.append(Spacer(1, 0.15*inch))

    # Issue B: Missing Items
    story.append(Paragraph("<b>ISSUE B: MISSING ITEMS (Short Ship)</b>", heading2_style))

    missing_steps = [
        "<b>B.1</b> Verify the part is truly missing:",
        "    • Double-check all boxes in the shipment",
        "    • Check for separate packages that may have been staged elsewhere",
        "    • Look for packing notes indicating a separate shipment or backorder",
        "<b>B.2</b> If confirmed missing, note \"SHORT\" or \"MISSING\" on the BOL next to the affected line item.",
        "<b>B.3</b> In the DMS, receive only the parts physically present. Do NOT receive the missing part.",
        "<b>B.4</b> Check the system to see if the missing part shows as backordered or on a separate shipment.",
        "<b>B.5</b> Contact the distribution center same day to report the shortage:",
        "    • Provide invoice number and missing part number",
        "    • Verify if part was intentionally held (backorder) or is a shipping error",
        "    • Request expedited shipment if needed for customer commitments",
        "<b>B.6</b> <b>FOR CRITICAL ORDERS:</b> Immediately alert service advisor. Determine if the customer vehicle can wait or needs alternative arrangements.",
        "<b>B.7</b> Monitor the system daily until the missing part arrives."
    ]

    for item in missing_steps:
        story.append(Paragraph(item, body_style))

    story.append(Spacer(1, 0.15*inch))

    # Issue C: Discrepancies
    story.append(Paragraph("<b>ISSUE C: BILL OF LADING DISCREPANCIES</b>", heading2_style))

    discrepancy_steps = [
        "<b>C.1</b> <b>Wrong Part Number:</b> Part received does not match part number on invoice:",
        "    • Do NOT put the part on the shelf",
        "    • Photograph the part and its label",
        "    • Note discrepancy on BOL: \"INCORRECT PART - Ordered [correct #], Received [wrong #]\"",
        "    • Set aside with a YELLOW \"DISCREPANCY\" tag",
        "    • Contact distribution center for return authorization and correct part shipment",
        "    • In DMS, receive the part number that was physically received (not ordered) or reject based on dealership policy",
        "",
        "<b>C.2</b> <b>Quantity Discrepancy:</b> Received more or fewer parts than invoiced:",
        "    • Count carefully and verify multiple times",
        "    • Receive only the actual quantity in the DMS (system will show discrepancy)",
        "    • Note actual quantity on BOL and circle the discrepancy",
        "    • If over-shipped, contact distribution center - do NOT place extra parts in stock without authorization",
        "    • If under-shipped, follow \"Missing Items\" protocol (Issue B)",
        "",
        "<b>C.3</b> <b>Extra/Unexpected Parts:</b> Parts in shipment not listed on BOL:",
        "    • Set aside and tag as \"NOT ON INVOICE\"",
        "    • Check if part was on a previous order or backorder list",
        "    • Do NOT enter into inventory until verified with distribution center",
        "    • Contact distribution center to determine correct invoice or if mis-shipped"
    ]

    for item in discrepancy_steps:
        story.append(Paragraph(item, body_style))

    story.append(PageBreak())

    # Step 6
    story.append(Paragraph("STEP 6: SHELVING & ORGANIZATION", heading1_style))

    step6_items = [
        "<b>6.1</b> <b>CRITICAL ORDERS:</b> Should already be delivered to technician (Step 3A.5). Confirm with service advisor that part was received.",
        "<b>6.2</b> <b>STOCK ORDERS:</b> Place parts in their designated bin locations according to the parts catalog system:",
        "    • Verify the bin location matches the part number in the DMS",
        "    • Use FIFO (First In, First Out) principle - place new stock behind existing stock",
        "    • Ensure part labels face outward for easy identification",
        "    • For large or heavy parts, use appropriate material handling equipment",
        "<b>6.3</b> Update bin labels if stock levels require additional bins or location changes.",
        "<b>6.4</b> Set aside slow-moving or overstock items per parts manager guidelines.",
        "<b>6.5</b> Place any promotional items, sales literature, or technical bulletins in the designated communication area for parts manager review."
    ]

    for item in step6_items:
        story.append(Paragraph(item, body_style))

    story.append(Spacer(1, 0.15*inch))

    # Step 7
    story.append(Paragraph("STEP 7: DOCUMENTATION & COMMUNICATION", heading2_style))

    step7_items = [
        "<b>7.1</b> Complete the daily receiving log with:",
        "    • Invoice numbers processed",
        "    • Number of line items received",
        "    • Any issues or discrepancies noted",
        "    • Time completed",
        "<b>7.2</b> File the bill of lading and receiving documents in the appropriate daily folder.",
        "<b>7.3</b> <b>If any issues occurred:</b> Send summary email to parts manager including:",
        "    • Issue type (damage, shortage, discrepancy)",
        "    • Invoice and part numbers affected",
        "    • Whether critical order was impacted",
        "    • Actions taken and RA numbers obtained",
        "    • Status (pending, resolved, awaiting callback)",
        "<b>7.4</b> For critical orders, confirm with service advisor that the technician has the parts and work is proceeding.",
        "<b>7.5</b> Ensure all pending issues are documented in the \"Open Issues\" tracking log for follow-up."
    ]

    for item in step7_items:
        story.append(Paragraph(item, body_style))

    story.append(Spacer(1, 0.2*inch))

    # Best Practices
    story.append(Paragraph("BEST PRACTICES & TIPS", heading1_style))

    best_practices = [
        "<b>Prioritization:</b> Always process critical orders before stock orders. A delayed critical part can cost the dealership customer satisfaction and revenue.",
        "<b>Documentation:</b> When in doubt, document it. Photos and detailed notes resolve disputes with distribution centers faster.",
        "<b>Communication:</b> Proactive communication with service advisors about critical order status prevents surprises.",
        "<b>Accuracy Over Speed:</b> Taking an extra minute to verify part numbers prevents costly errors and re-deliveries.",
        "<b>System Integrity:</b> Never put parts on the shelf without receiving them in the system. This causes inventory inaccuracies and financial discrepancies.",
        "<b>Same-Day Resolution:</b> Contact the distribution center the same day issues are discovered. Delays reduce the likelihood of successful claims.",
        "<b>Organized Workspace:</b> Keep receiving areas clean and organized. Clearly separate damaged, discrepant, and good parts.",
        "<b>Team Coordination:</b> If multiple staff handle receiving, use status tags (\"CHECKED\", \"ENTERED\", \"SHELVED\") to avoid duplication."
    ]

    for item in best_practices:
        story.append(Paragraph(f"• {item}", body_style))

    story.append(Spacer(1, 0.2*inch))

    # Contact Information
    story.append(Paragraph("DISTRIBUTION CENTER CONTACT INFORMATION", heading1_style))

    story.append(Paragraph(
        "Keep the following contact information readily accessible in your receiving area:",
        body_style
    ))
    story.append(Spacer(1, 0.1*inch))

    contact_data = [
        ['Parts Distribution Center Main Line:', '_________________________________'],
        ['Returns/Damage Claims:', '_________________________________'],
        ['Expedite/Critical Orders:', '_________________________________'],
        ['After-Hours Emergency:', '_________________________________'],
        ['Online Parts Portal:', '_________________________________'],
        ['Parts Manager (Internal):', '_________________________________']
    ]

    contact_table = Table(contact_data, colWidths=[2.5*inch, 4*inch])
    contact_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e2e8f0')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2d3748')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(contact_table)

    story.append(Spacer(1, 0.3*inch))

    # Closing
    story.append(Paragraph(
        "<b>Remember:</b> Accurate parts check-in is the foundation of efficient service operations. "
        "Your attention to detail directly impacts customer satisfaction, technician productivity, "
        "and dealership profitability. Thank you for your commitment to excellence.",
        important_style
    ))

    story.append(Spacer(1, 0.2*inch))

    # Footer
    story.append(Paragraph(
        f"Document Generated: {datetime.now().strftime('%B %d, %Y')} | Version 1.0 | "
        "For questions or suggestions for improvement, contact your Parts Manager",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8,
                      textColor=colors.HexColor('#718096'), alignment=TA_CENTER)
    ))

    # Build PDF
    doc.build(story)
    print(f"✓ PDF created successfully: {output_file}")
    return output_file

if __name__ == "__main__":
    create_parts_checkin_procedure()
