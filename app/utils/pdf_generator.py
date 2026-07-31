import io

import qrcode  # type: ignore[import-untyped]
from reportlab.lib import colors  # type: ignore[import-untyped]
from reportlab.lib.pagesizes import letter  # type: ignore[import-untyped]
from reportlab.lib.units import inch  # type: ignore[import-untyped]
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle  # type: ignore[import-untyped]

try:
    from reportlab.platypus import HRFlowable  # type: ignore[import-untyped]
except ImportError:
    from reportlab.platypus.flowables import HRFlowable  # type: ignore[import-untyped]
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet  # type: ignore[import-untyped]


def generate_ticket_pdf(
    pnr: str,
    passenger_name: str,
    email: str,
    phone: str,
    flight_number: str,
    airline_name: str,
    source_name: str,
    destination_name: str,
    departure_time: str,
    arrival_time: str,
    flight_date: str,
    seat_number: str,
    seat_class: str,
    gate_no: str,
    terminal_no: str,
    total_amount: float,
    payment_method: str,
    transaction_id: str,
    booking_status: str,
    baggage_allowance: str = "7kg Cabin + 15kg Check-in",
    trip_type: str = "One-Way",
    ticket_url: str = "",
) -> bytes:
    """Generate a high-resolution, professional PDF with Boarding Pass, Payment Receipt & QR Code."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    story = []
    styles = getSampleStyleSheet()

    # Custom styles
    primary_color = colors.HexColor("#0f172a")  # Deep Navy
    accent_color = colors.HexColor("#2563eb")   # Royal Blue
    light_bg = colors.HexColor("#f8fafc")       # Light Slate

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=primary_color,
    )
    header_right = ParagraphStyle(
        'HeaderRight',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        alignment=2,
        textColor=accent_color,
    )
    label_style = ParagraphStyle(
        'CellLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#64748b"),
    )
    val_style = ParagraphStyle(
        'CellValue',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=primary_color,
    )
    seat_val_style = ParagraphStyle(
        'SeatValue',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=accent_color,
    )

    # Generate QR Code image in memory — DIRECT HTTP URL for instant scanning access!
    qr_target_link = ticket_url or f"http://localhost:8000/api/bookings/{pnr}/pdf"
    qr_img = qrcode.make(qr_target_link)
    qr_buffer = io.BytesIO()
    qr_img.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    qr_image = Image(qr_buffer, width=1.1*inch, height=1.1*inch)

    qr_cell = [
        qr_image,
        Paragraph("<font size=7 color='#2563eb'><b>📲 SCAN TO VERIFY TICKET</b></font>", ParagraphStyle('QRCap', alignment=1, leading=8))
    ]

    header_right_info = Paragraph(
        f"PNR: <b>{pnr}</b><br/>"
        f"<font size=8 color='#64748b'>Gate: <b>{gate_no}</b> | Terminal: <b>{terminal_no}</b></font><br/>"
        f"<font size=8 color='#10b981'><b>● CONFIRMED & ISSUED</b></font>",
        header_right
    )

    # 1. Top Header Row with Top-Right QR Code Placement
    header_data = [
        [
            Paragraph(f"✈ <b>SkyBooker Airlines</b> ({trip_type.upper()})<br/><font size=8 color='#64748b'>OFFICIAL BOARDING PASS & TAX INVOICE</font>", title_style),
            header_right_info,
            qr_cell
        ]
    ]
    header_table = Table(header_data, colWidths=[270, 160, 110])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (2,0), (2,0), 'CENTER'),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=2, color=accent_color, spaceBefore=0, spaceAfter=12))

    # 2. Full-Width Boarding Pass Section
    story.append(Paragraph("<b>1. BOARDING PASS & PASSENGER INFORMATION</b>", ParagraphStyle('SecTitle', fontName='Helvetica-Bold', fontSize=11, textColor=accent_color)))
    story.append(Spacer(1, 8))

    pass_grid = [
        [
            Paragraph("PASSENGER NAME", label_style),
            Paragraph("FLIGHT NUMBER", label_style),
            Paragraph("AIRLINE", label_style),
            Paragraph("SEAT NUMBER", label_style),
        ],
        [
            Paragraph(passenger_name, val_style),
            Paragraph(flight_number, val_style),
            Paragraph(airline_name or "SkyBooker Express", val_style),
            Paragraph(f"<b>{seat_number}</b> ({seat_class.upper()})", seat_val_style),
        ],
        [
            Paragraph("FROM (ORIGIN)", label_style),
            Paragraph("TO (DESTINATION)", label_style),
            Paragraph("DEPARTURE DATE & TIME", label_style),
            Paragraph("GATE / TERMINAL / BAGGAGE", label_style),
        ],
        [
            Paragraph(source_name or "Origin", val_style),
            Paragraph(destination_name or "Destination", val_style),
            Paragraph(f"{flight_date or '2026-08-01'}<br/>Dep: {departure_time or '06:00'}", val_style),
            Paragraph(f"Gate <b>{gate_no}</b> / Term <b>{terminal_no}</b><br/>{baggage_allowance}", val_style),
        ]
    ]

    table_pass = Table(pass_grid, colWidths=[135, 135, 135, 135])
    table_pass.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), light_bg),
        ('PADDING', (0,0), (-1,-1), 8),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(table_pass)



    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceBefore=0, spaceAfter=15))

    # 3. Tax Invoice & Receipt Section
    story.append(Paragraph("<b>2. TAX INVOICE & PAYMENT RECEIPT</b>", ParagraphStyle('SecTitle2', fontName='Helvetica-Bold', fontSize=11, textColor=primary_color)))
    story.append(Spacer(1, 8))

    base_price = total_amount * 0.82
    gst_tax = total_amount * 0.18

    tax_grid = [
        [Paragraph("ITEM DESCRIPTION", label_style), Paragraph("TRANSACTION INFO", label_style), Paragraph("AMOUNT", label_style)],
        [
            Paragraph(f"Base Air Fare Ticket ({flight_number} — Seat {seat_number})", val_style),
            Paragraph(f"Method: <b>{payment_method}</b><br/>Txn ID: {transaction_id}", val_style),
            Paragraph(f"₹{base_price:,.2f}", val_style),
        ],
        [
            Paragraph("Airport Taxes & Aviation GST (18%)", val_style),
            Paragraph(f"Booking Status: <font color='#10b981'><b>{booking_status.upper()}</b></font>", val_style),
            Paragraph(f"₹{gst_tax:,.2f}", val_style),
        ],
        [
            Paragraph("<b>TOTAL AMOUNT PAID</b>", val_style),
            Paragraph("", val_style),
            Paragraph(f"<font color='#10b981' size=11><b>₹{total_amount:,.2f}</b></font>", val_style),
        ]
    ]

    receipt_table = Table(tax_grid, colWidths=[240, 180, 120])
    receipt_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#e2e8f0")),
        ('PADDING', (0,0), (-1,-1), 8),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,3), (-1,3), colors.HexColor("#f1f5f9")),
    ]))
    story.append(receipt_table)

    # 4. Footer Guidelines
    story.append(Spacer(1, 25))
    footer_text = Paragraph(
        "<font color='#64748b' size=8>Airport Guidelines: Please present this official PDF boarding pass alongside a valid photo ID (Passport / Aadhaar) at security screening. Web check-in closes 60 minutes prior to departure. Have a pleasant flight!</font>",
        ParagraphStyle('Footer', fontName='Helvetica-Oblique', alignment=1)
    )
    story.append(footer_text)

    doc.build(story)
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data
