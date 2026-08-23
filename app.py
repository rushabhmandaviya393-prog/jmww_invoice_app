import streamlit as st
import pandas as pd
from datetime import date, timedelta
import io
import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm

st.set_page_config(page_title="Jay Mataji Welding Works - Invoicing", layout="wide")

COMPANY_GSTIN = "24BWUPM5424M1ZW"
COMPANY_PAN = "BWUPM5424M"
COMPANY_ADDRESS = "Plot No. 6, Oorja 10 Industrial Park, Near De-well Tools, Pardi - Padavala Road, Pardi, Rajkot, Gujarat-360024."
COMPANY_NAME = "JAY MATAJI WELDING WORKS"
BANK_DETAILS = "INDIAN OVERSEAS BANK (IOB)\nA/C No. : 181802000000600\nIFSC CODE : IOBA0001818\nBRANCH : P.D. MALAVIYA COLLEGE, RAJKOT."

DB_FILE = "invoice_records.csv"

def num_to_words(num):
    units = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten",
             "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
    
    n = int(round(num))
    if n == 0:
        return "Zero Rupees Only"
    
    def convert_below_thousand(val):
        res = ""
        if val >= 100:
            res += units[val // 100] + " Hundred "
            val %= 100
        if val >= 20:
            res += tens[val // 10] + " "
            val %= 10
        if val > 0:
            res += units[val] + " "
        return res

    result = ""
    crore = n // 10000000
    n %= 10000000
    lakh = n // 100000
    n %= 100000
    thousand = n // 1000
    n %= 1000
    rem = n

    if crore > 0:
        result += convert_below_thousand(crore) + "Crore "
    if lakh > 0:
        result += convert_below_thousand(lakh) + "Lakh "
    if thousand > 0:
        result += convert_below_thousand(thousand) + "Thousand "
    if rem > 0:
        result += convert_below_thousand(rem)
        
    paise = int(round((num - int(num)) * 100))
    paise_str = f" and {convert_below_thousand(paise).strip()} Paise" if paise > 0 else ""
    return result.strip() + " Rupees" + paise_str + " Only"

def load_records():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["IN NO", "NAME", "AMOUNT", "BILL DATE", "DUE DATE", "PAID", "TIME"])

def save_record(record):
    df = load_records()
    df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
    df.to_csv(DB_FILE, index=False)

def generate_pdf_invoice(d):
    buffer = io.BytesIO()
    # A4: 595.27 x 841.89 points. Usable width with 15pt margins = ~565pt
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4, 
        leftMargin=15, 
        rightMargin=15, 
        topMargin=15, 
        bottomMargin=15
    )
    story = []
    styles = getSampleStyleSheet()
    
    # Custom Compact Typography
    p_norm = ParagraphStyle('PNorm', parent=styles['Normal'], fontSize=7.5, leading=9.5)
    p_bold = ParagraphStyle('PBold', parent=styles['Normal'], fontSize=7.5, leading=9.5, fontName='Helvetica-Bold')
    p_center_bold = ParagraphStyle('PCBold', parent=p_bold, alignment=1)
    p_right = ParagraphStyle('PRight', parent=p_norm, alignment=2)
    p_right_bold = ParagraphStyle('PRBold', parent=p_bold, alignment=2)
    
    # 1. Header Image (Scaled to full page width, preserving aspect ratio)
    if os.path.exists("header.png"):
        story.append(RLImage("header.png", width=565, height=95))
    else:
        story.append(Paragraph(f"<b>{COMPANY_NAME}</b>", ParagraphStyle('HeadF', parent=p_center_bold, fontSize=12)))
        story.append(Spacer(1, 4))

    # 2. Tax Invoice Title Bar
    title_data = [
        [Paragraph("<b>DEBIT</b>", p_norm), 
         Paragraph("<b>TAX INVOICE</b>", ParagraphStyle('TIBig', parent=p_center_bold, fontSize=10)), 
         Paragraph("<b>ORIGINAL</b>", p_right_bold)]
    ]
    t_title = Table(title_data, colWidths=[100, 365, 100])
    t_title.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(t_title)

    # 3. Party & Meta Grid
    party_details = f"""<b>To,</b> {d['cust_name']}<br/>
    {d['cust_address']}<br/><br/>
    <b>State:</b> {d['state_name']} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>Code:</b> {d['state_code']}<br/>
    <b>Mo. No.:</b> {d['cust_mobile']} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>Term:</b> {d['term_days']} Days<br/>
    <b>Party's GSTIN No:</b> {d['cust_gstin']}<br/>
    <b>Party's PAN No:</b> {d['cust_pan']}
    """
    
    inv_meta = f"""<b>INVOICE NO:</b> {d['inv_no']} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>Date:</b> {d['bill_date']}<br/><br/>
    <b>TRANSPORT :</b> {d['transport']}<br/>
    <b>LR. NO. :</b> {d['lr_no']}<br/>
    <b>LR. DATE :</b> {d['lr_date']}<br/>
    <b>VEHICLE NO. :</b> {d['vehicle_no']}<br/>
    <b>CASES :</b> {d['cases']}<br/>
    <b>AGAINST FORM:</b>
    """

    t_meta = Table([
        [Paragraph(party_details, p_norm), Paragraph(inv_meta, p_norm)]
    ], colWidths=[315, 250])
    t_meta.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_meta)

    # 4. Item Table
    item_rows = [[
        Paragraph("<b>Sr.</b>", p_center_bold),
        Paragraph("<b>Item Description</b>", p_center_bold),
        Paragraph("<b>HSN Code</b>", p_center_bold),
        Paragraph("<b>Quantity</b>", p_center_bold),
        Paragraph("<b>Rate</b>", p_center_bold),
        Paragraph("<b>GST%</b>", p_center_bold),
        Paragraph("<b>Amount</b>", p_center_bold)
    ]]

    tot_qty = 0.0
    for idx, itm in enumerate(d['items']):
        tot_qty += float(itm['qty'])
        item_rows.append([
            Paragraph(str(idx + 1), p_center_bold),
            Paragraph(str(itm['desc']), p_norm),
            Paragraph(str(itm['hsn']), p_center_bold),
            Paragraph(f"{itm['qty']:,.2f}", p_right),
            Paragraph(f"{itm['rate']:,.2f}", p_right),
            Paragraph(f"{itm['gst_pct']:.0f}%", p_center_bold),
            Paragraph(f"{itm['amount']:,.2f}", p_right)
        ])

    # Pad empty rows to maintain full page height
    needed_pad = max(0, 10 - len(d['items']))
    for _ in range(needed_pad):
        item_rows.append([Paragraph("", p_norm), Paragraph("", p_norm), Paragraph("", p_norm), 
                          Paragraph("", p_norm), Paragraph("", p_norm), Paragraph("", p_norm), Paragraph("", p_norm)])

    # Total row right under items
    item_rows.append([
        Paragraph("", p_norm),
        Paragraph("", p_norm),
        Paragraph("", p_norm),
        Paragraph(f"<b>{tot_qty:,.2f}</b>", p_right_bold),
        Paragraph("<b>Total Amnt.</b>", p_center_bold),
        Paragraph("", p_norm),
        Paragraph(f"<b>{d['sub_total']:,.2f}</b>", p_right_bold)
    ])

    t_items = Table(item_rows, colWidths=[25, 235, 60, 50, 65, 40, 90])
    t_items.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 3),
        ('RIGHTPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_items)

    # 5. Bank Details & Calculations Summary Table
    b_text = f"<b>Bank Details:</b><br/>" + BANK_DETAILS.replace("\n", "<br/>")
    calc_text = f"""Trans. Charges &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; {d['trans_charges']:,.2f}<br/>
    <b>Sub Total</b> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>{d['sub_total']:,.2f}</b><br/>
    CGST &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; {d['cgst_amt']:,.2f}<br/>
    SGST &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; {d['sgst_amt']:,.2f}
    """
    
    t_mid = Table([
        [Paragraph(b_text, p_norm), Paragraph(calc_text, p_norm)]
    ], colWidths=[335, 230])
    t_mid.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_mid)

    # 6. GST Summary Grid
    half_gst = (d['items'][0]['gst_pct'] / 2.0) if len(d['items']) > 0 else 9.0
    gst_grid = [
        [Paragraph("<b>GST Summary</b>", p_norm), Paragraph("<b>Taxable Amnt</b>", p_center_bold), Paragraph("<b>CGST</b>", p_center_bold), Paragraph("<b>CGST Amnt</b>", p_center_bold), Paragraph("<b>SGST</b>", p_center_bold), Paragraph("<b>SGST Amnt</b>", p_center_bold), Paragraph("<b>Total GST</b>", p_center_bold)],
        [Paragraph("GST", p_norm), Paragraph(f"{d['taxable_amt']:,.2f}", p_right), Paragraph(f"{half_gst:.1f}%", p_center_bold), Paragraph(f"{d['cgst_amt']:,.2f}", p_right), Paragraph(f"{half_gst:.1f}%", p_center_bold), Paragraph(f"{d['sgst_amt']:,.2f}", p_right), Paragraph(f"{d['total_gst']:,.2f}", p_right)],
        [Paragraph("<b>Total :</b>", p_bold), Paragraph(f"<b>{d['taxable_amt']:,.2f}</b>", p_right_bold), Paragraph("", p_norm), Paragraph(f"<b>{d['cgst_amt']:,.2f}</b>", p_right_bold), Paragraph("", p_norm), Paragraph(f"<b>{d['sgst_amt']:,.2f}</b>", p_right_bold), Paragraph(f"<b>{d['total_gst']:,.2f}</b>", p_right_bold)]
    ]
    t_gst = Table(gst_grid, colWidths=[70, 95, 45, 85, 45, 85, 140])
    t_gst.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 3),
        ('RIGHTPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_gst)

    # 7. Grand Total Banner
    t_gt = Table([
        [Paragraph("<b>Grand Total</b>", ParagraphStyle('GT1', parent=p_bold, fontSize=8.5)),
         Paragraph(f"<b>₹{d['grand_total']:,.2f}</b>", ParagraphStyle('GT2', parent=p_right_bold, fontSize=8.5))]
    ], colWidths=[282, 283])
    t_gt.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_gt)

    # 8. Words & Footer Signature
    f_left = f"""<b>Amnt In Words:</b> {d['amt_in_words']}<br/><br/>
    <b>Company's GSTIN No.:</b> {COMPANY_GSTIN}<br/>
    <b>Company's PAN No. :</b> {COMPANY_PAN}<br/>
    <b>Company's Address :</b> {COMPANY_ADDRESS}
    """
    
    f_right = f"""<br/><b>For, {COMPANY_NAME}</b><br/><br/><br/><br/>
    Authorised Signatory
    """

    t_foot = Table([
        [Paragraph(f_left, p_norm), Paragraph(f_right, ParagraphStyle('FSing', parent=p_norm, alignment=2))]
    ], colWidths=[365, 200])
    t_foot.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_foot)

    doc.build(story)
    buffer.seek(0)
    return buffer

# --- STREAMLIT UI ---
menu = st.sidebar.radio("Navigation", ["Create New Invoice", "Invoice Records & History"])

if os.path.exists("header.png"):
    st.image("header.png", use_container_width=True)

if menu == "Create New Invoice":
    st.subheader("📄 Generate GST Invoice")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        inv_no = st.number_input("Invoice No.", min_value=1, step=1, value=1)
        bill_date = st.date_input("Invoice Date", value=date.today())
        term_days = st.number_input("Payment Term (Days)", min_value=0, value=2)
        due_date = bill_date + timedelta(days=int(term_days))

    with col2:
        cust_name = st.text_input("Customer Name", value="Rushabh Mandaviya")
        cust_address = st.text_area("Address", value="satyam hills g1304")
        cust_mobile = st.text_input("Mobile No.", value="8264605156")

    with col3:
        cust_gstin = st.text_input("Party GSTIN", value="")
        cust_pan = st.text_input("Party PAN", value="")
        state_name = st.text_input("State", value="Gujarat")
        state_code = st.text_input("Code", value="24")

    st.markdown("### 🚚 Transport")
    t1, t2, t3, t4, t5 = st.columns(5)
    with t1: transport = st.text_input("Transport", value="")
    with t2: lr_no = st.text_input("LR. No.", value="")
    with t3: lr_date = st.date_input("LR. Date", value=date.today())
    with t4: vehicle_no = st.text_input("Vehicle No.", value="")
    with t5: cases = st.text_input("Cases", value="")

    st.markdown("### 📦 Items")
    num_items = st.number_input("Number of Items", min_value=1, max_value=15, value=2)
    
    items = []
    for i in range(num_items):
        ic1, ic2, ic3, ic4, ic5 = st.columns([3, 1.5, 1.2, 1.5, 1.2])
        with ic1: desc = st.text_input(f"Item #{i+1} Description", key=f"desc_{i}")
        with ic2: hsn = st.text_input(f"HSN Code", key=f"hsn_{i}")
        with ic3: qty = st.number_input(f"Qty", min_value=0.0, step=1.0, value=1.0, key=f"qty_{i}")
        with ic4: rate = st.number_input(f"Rate (₹)", min_value=0.0, step=10.0, value=0.0, key=f"rate_{i}")
        with ic5: gst_pct = st.selectbox(f"GST %", [0.0, 5.0, 12.0, 18.0, 28.0], index=3, key=f"gst_{i}")
        
        item_amt = qty * rate
        items.append({"desc": desc, "hsn": hsn, "qty": qty, "rate": rate, "gst_pct": gst_pct, "amount": item_amt})

    taxable_amt = sum(item["amount"] for item in items)
    trans_charges = st.number_input("Transport Charges (₹)", min_value=0.0, value=0.0)
    sub_total = taxable_amt + trans_charges

    is_intrastate = (str(state_code).strip() == "24")
    cgst_amt = sum((item["amount"] * (item["gst_pct"] / 200.0)) for item in items) if is_intrastate else 0.0
    sgst_amt = cgst_amt
    igst_amt = sum((item["amount"] * (item["gst_pct"] / 100.0)) for item in items) if not is_intrastate else 0.0
    
    total_gst = (cgst_amt + sgst_amt) if is_intrastate else igst_amt
    grand_total = round(sub_total + total_gst, 2)
    amt_in_words = num_to_words(grand_total)

    inv_payload = {
        "inv_no": inv_no,
        "bill_date": bill_date.strftime("%d-%m-%Y"),
        "due_date": due_date.strftime("%d-%m-%Y"),
        "term_days": term_days,
        "cust_name": cust_name,
        "cust_address": cust_address,
        "cust_mobile": cust_mobile,
        "cust_gstin": cust_gstin,
        "cust_pan": cust_pan,
        "state_name": state_name,
        "state_code": state_code,
        "transport": transport,
        "lr_no": lr_no,
        "lr_date": lr_date.strftime("%d-%m-%Y"),
        "vehicle_no": vehicle_no,
        "cases": cases,
        "items": items,
        "taxable_amt": taxable_amt,
        "sub_total": sub_total,
        "trans_charges": trans_charges,
        "is_intrastate": is_intrastate,
        "cgst_amt": cgst_amt,
        "sgst_amt": sgst_amt,
        "igst_amt": igst_amt,
        "total_gst": total_gst,
        "grand_total": grand_total,
        "amt_in_words": amt_in_words
    }

    st.markdown("---")
    b1, b2 = st.columns(2)
    with b1:
        if st.button("💾 Save Invoice", type="primary", use_container_width=True):
            record = {
                "IN NO": inv_no,
                "NAME": cust_name,
                "AMOUNT": f"₹{grand_total:,.2f}",
                "BILL DATE": bill_date.strftime("%d-%m-%Y"),
                "DUE DATE": due_date.strftime("%d-%m-%Y"),
                "PAID": "NO",
                "TIME": pd.Timestamp.now().strftime("%d-%m-%Y %H:%M")
            }
            save_record(record)
            st.success(f"Invoice #{inv_no} saved successfully!")

    with b2:
        pdf_bytes = generate_pdf_invoice(inv_payload)
        st.download_button(
            label="📥 Download Invoice PDF",
            data=pdf_bytes,
            file_name=f"{inv_no}_{cust_name.strip()}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

elif menu == "Invoice Records & History":
    st.subheader("📑 Invoice History Ledger")
    records_df = load_records()
    if not records_df.empty:
        st.dataframe(records_df, use_container_width=True)
        csv_data = records_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Master Record CSV", data=csv_data, file_name="Master_Invoice_Records.csv", mime="text/csv")
    else:
        st.info("No records found.")
