import streamlit as st
import pandas as pd
from datetime import date, timedelta
import io
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors

st.set_page_config(page_title="JAY MATAJI WELDING WORKS", layout="wide")

COMPANY_GSTIN = "24BWUPM5424M1ZW"
COMPANY_PAN = "BWUPM5424M"
COMPANY_ADDRESS = "Plot No. 6, Oorja 10 Industrial Park, Near De-well Tools, Pardi - Padavala Road, Pardi, Rajkot, Gujarat-360024."
COMPANY_NAME = "JAY MATAJI WELDING WORKS"
BANK_DETAILS = [
    "INDIAN OVERSEAS BANK (IOB)",
    "A/C No. : 181802000000600",
    "IFSC CODE : IOBA0001818",
    "BRANCH : P.D. MALAVIYA COLLEGE, RAJKOT."
]
DB_FILE = "invoice_records.csv"

def num_to_words(num):
    units = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten",
             "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
    n = int(round(num))
    if n == 0:
        return "Zero Rupees Only"
    def conv(val):
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
    res = ""
    crore = n // 10000000
    n %= 10000000
    lakh = n // 100000
    n %= 100000
    thousand = n // 1000
    n %= 1000
    rem = n
    if crore > 0: res += conv(crore) + "Crore "
    if lakh > 0: res += conv(lakh) + "Lakh "
    if thousand > 0: res += conv(thousand) + "Thousand "
    if rem > 0: res += conv(rem)
    paise = int(round((num - int(num)) * 100))
    p_str = f" and {conv(paise).strip()} Paise" if paise > 0 else ""
    return res.strip() + " Rupees" + p_str + " Only"

def draw_exact_invoice(d):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4 # 595.27 x 841.89
    
    # Outer Margins
    left = 20
    right = width - 20 # 575.27 -> width = 555.27
    top = height - 20  # 821.89
    bottom = 25
    
    # 1. Outer Box Border
    c.setLineWidth(1.2)
    c.setStrokeColor(colors.black)
    c.rect(left, bottom, right - left, top - bottom)
    
    # 2. Header Image
    header_height = 85
    if os.path.exists("header.png"):
        c.drawImage("header.png", left + 1, top - header_height, width=(right - left - 2), height=header_height, preserveAspectRatio=False)
    
    # Divider under Header
    y = top - header_height
    c.line(left, y, right, y)
    
    # 3. Tax Invoice Title Strip
    strip_h = 16
    c.setFont("Helvetica-Bold", 8)
    c.drawString(left + 5, y - 11, "DEBIT")
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString((left + right) / 2.0, y - 12, "TAX INVOICE")
    c.setFont("Helvetica-Bold", 8)
    c.drawRightString(right - 5, y - 11, "ORIGINAL")
    
    y -= strip_h
    c.line(left, y, right, y)
    
    # 4. Party Details & Meta Info Section
    meta_h = 95
    mid_x = left + 315
    c.line(mid_x, y, mid_x, y - meta_h) # Vertical Split
    
    # Left Side: Party Details
    c.setFont("Helvetica-Bold", 8)
    c.drawString(left + 5, y - 12, f"To,  {d['cust_name']}")
    c.setFont("Helvetica", 8)
    c.drawString(left + 23, y - 24, f"{d['cust_address']}")
    
    c.setFont("Helvetica-Bold", 8)
    c.drawString(left + 5, y - 46, "State:")
    c.setFont("Helvetica", 8)
    c.drawString(left + 35, y - 46, f"{d['state_name']}")
    c.setFont("Helvetica-Bold", 8)
    c.drawString(left + 160, y - 46, "Code:")
    c.setFont("Helvetica", 8)
    c.drawString(left + 190, y - 46, f"{d['state_code']}")
    
    c.setFont("Helvetica-Bold", 8)
    c.drawString(left + 5, y - 60, "Mo. No.:")
    c.setFont("Helvetica", 8)
    c.drawString(left + 45, y - 60, f"{d['cust_mobile']}")
    c.setFont("Helvetica-Bold", 8)
    c.drawString(left + 160, y - 60, "Term:")
    c.setFont("Helvetica", 8)
    c.drawString(left + 190, y - 60, f"{d['term_days']} Days")
    
    c.setFont("Helvetica-Bold", 8)
    c.drawString(left + 5, y - 74, "Party's GSTIN No:")
    c.setFont("Helvetica", 8)
    c.drawString(left + 90, y - 74, f"{d['cust_gstin']}")
    
    c.setFont("Helvetica-Bold", 8)
    c.drawString(left + 5, y - 88, "Party's PAN No:")
    c.setFont("Helvetica", 8)
    c.drawString(left + 90, y - 88, f"{d['cust_pan']}")
    
    # Right Side: Invoice Meta
    c.setFont("Helvetica-Bold", 8)
    c.drawString(mid_x + 5, y - 12, "INVOICE NO:")
    c.setFont("Helvetica-Bold", 9)
    c.drawString(mid_x + 65, y - 12, f"{d['inv_no']}")
    c.setFont("Helvetica-Bold", 8)
    c.drawString(mid_x + 125, y - 12, "Date:")
    c.setFont("Helvetica", 8)
    c.drawString(mid_x + 155, y - 12, f"{d['bill_date']}")
    
    c.setFont("Helvetica-Bold", 8)
    c.drawString(mid_x + 5, y - 26, "TRANSPORT :")
    c.setFont("Helvetica", 8)
    c.drawString(mid_x + 75, y - 26, f"{d['transport']}")
    
    c.setFont("Helvetica-Bold", 8)
    c.drawString(mid_x + 5, y - 40, "LR. NO. :")
    c.setFont("Helvetica", 8)
    c.drawString(mid_x + 75, y - 40, f"{d['lr_no']}")
    
    c.setFont("Helvetica-Bold", 8)
    c.drawString(mid_x + 5, y - 54, "LR. DATE :")
    c.setFont("Helvetica", 8)
    c.drawString(mid_x + 75, y - 54, f"{d['lr_date']}")
    
    c.setFont("Helvetica-Bold", 8)
    c.drawString(mid_x + 5, y - 68, "VEHICLE NO. :")
    c.setFont("Helvetica", 8)
    c.drawString(mid_x + 75, y - 68, f"{d['vehicle_no']}")
    
    c.setFont("Helvetica-Bold", 8)
    c.drawString(mid_x + 5, y - 82, "CASES :")
    c.setFont("Helvetica", 8)
    c.drawString(mid_x + 75, y - 82, f"{d['cases']}")
    
    c.setFont("Helvetica-Bold", 8)
    c.drawString(mid_x + 5, y - 93, "AGAINST FORM:")
    
    y -= meta_h
    c.line(left, y, right, y)
    
    # 5. Item Table Setup
    col_x = [left, left + 25, left + 270, left + 335, left + 385, left + 450, left + 490, right]
    
    # Item Header
    c.setFont("Helvetica-Bold", 8)
    th_h = 16
    c.drawCentredString((col_x[0] + col_x[1])/2, y - 11, "Sr.")
    c.drawString(col_x[1] + 5, y - 11, "Iteam Description")
    c.drawCentredString((col_x[2] + col_x[3])/2, y - 11, "HSN Code")
    c.drawCentredString((col_x[3] + col_x[4])/2, y - 11, "Quantity")
    c.drawCentredString((col_x[4] + col_x[5])/2, y - 11, "Rate")
    c.drawCentredString((col_x[5] + col_x[6])/2, y - 11, "GST%")
    c.drawCentredString((col_x[6] + col_x[7])/2, y - 11, "Amount")
    
    y -= th_h
    c.line(left, y, right, y)
    
    # Items Content Rows
    table_top_y = y
    row_h = 18
    tot_qty = 0.0
    for idx, itm in enumerate(d['items']):
        tot_qty += float(itm['qty'])
        c.setFont("Helvetica", 8)
        c.drawCentredString((col_x[0] + col_x[1])/2, y - 12, str(idx + 1))
        c.drawString(col_x[1] + 5, y - 12, str(itm['desc']))
        c.drawCentredString((col_x[2] + col_x[3])/2, y - 12, str(itm['hsn']))
        c.drawRightString(col_x[4] - 4, y - 12, f"{itm['qty']:,.2f}")
        c.drawRightString(col_x[5] - 4, y - 12, f"{itm['rate']:,.2f}")
        c.drawCentredString((col_x[5] + col_x[6])/2, y - 12, f"{itm['gst_pct']:.0f}%")
        c.drawRightString(col_x[7] - 5, y - 12, f"{itm['amount']:,.2f}")
        y -= row_h
        c.line(left, y, right, y)
        
    # Minimum empty space filler for table
    min_table_y = top - header_height - strip_h - meta_h - th_h - 220
    if y > min_table_y:
        y = min_table_y
        c.line(left, y, right, y)
        
    # Draw Vertical Gridlines for Item Table
    for cx in col_x:
        c.line(cx, table_top_y + th_h, cx, y)
        
    # Total Quantity / Amount Row
    c.setFont("Helvetica-Bold", 8)
    c.drawRightString(col_x[4] - 4, y - 12, f"{tot_qty:,.2f}")
    c.drawString(col_x[4] + 8, y - 12, "Total Amnt.")
    c.drawRightString(col_x[7] - 5, y - 12, f"{d['sub_total']:,.2f}")
    c.line(col_x[3], y, col_x[3], y - 16)
    c.line(col_x[4], y, col_x[4], y - 16)
    c.line(col_x[6], y, col_x[6], y - 16)
    
    y -= 16
    c.line(left, y, right, y)
    
    # 6. Bank Details & Calculations Split
    mid_split = left + 345
    bank_h = 60
    c.line(mid_split, y, mid_split, y - bank_h)
    
    # Left Bank Details
    c.setFont("Helvetica-Bold", 8)
    c.drawString(left + 5, y - 12, "Bank Details:")
    c.setFont("Helvetica", 7.5)
    by = y - 24
    for bline in BANK_DETAILS:
        c.drawString(left + 5, by, bline)
        by -= 10
        
    # Right Charges & Taxes breakdown
    c.setFont("Helvetica", 8)
    c.drawString(mid_split + 5, y - 12, "Trans. Charges")
    c.drawRightString(right - 5, y - 12, f"{d['trans_charges']:,.2f}")
    
    c.setFont("Helvetica-Bold", 8)
    c.drawString(mid_split + 5, y - 25, "Sub Total")
    c.drawRightString(right - 5, y - 25, f"{d['sub_total']:,.2f}")
    
    c.setFont("Helvetica", 8)
    c.drawString(mid_split + 5, y - 38, "CGST")
    c.drawRightString(right - 5, y - 38, f"{d['cgst_amt']:,.2f}")
    
    c.drawString(mid_split + 5, y - 51, "SGST")
    c.drawRightString(right - 5, y - 51, f"{d['sgst_amt']:,.2f}")
    
    y -= bank_h
    c.line(left, y, right, y)
    
    # 7. GST Summary Full Width Table
    gst_cols = [left, left + 75, left + 165, left + 215, left + 300, left + 350, left + 435, right]
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(gst_cols[0] + 3, y - 10, "GST Summary")
    c.drawCentredString((gst_cols[1]+gst_cols[2])/2, y - 10, "Taxable Amnt")
    c.drawCentredString((gst_cols[2]+gst_cols[3])/2, y - 10, "CGST")
    c.drawCentredString((gst_cols[3]+gst_cols[4])/2, y - 10, "CGST Amnt")
    c.drawCentredString((gst_cols[4]+gst_cols[5])/2, y - 10, "SGST")
    c.drawCentredString((gst_cols[5]+gst_cols[6])/2, y - 10, "SGST Amnt")
    c.drawCentredString((gst_cols[6]+gst_cols[7])/2, y - 10, "Total GST")
    
    c.line(left, y - 13, right, y - 13)
    
    half_gst = (d['items'][0]['gst_pct'] / 2.0) if len(d['items']) > 0 else 9.0
    c.setFont("Helvetica", 7.5)
    c.drawString(gst_cols[0] + 3, y - 23, "GST")
    c.drawRightString(gst_cols[2] - 4, y - 23, f"{d['taxable_amt']:,.2f}")
    c.drawCentredString((gst_cols[2]+gst_cols[3])/2, y - 23, f"{half_gst:.1f}%")
    c.drawRightString(gst_cols[4] - 4, y - 23, f"{d['cgst_amt']:,.2f}")
    c.drawCentredString((gst_cols[4]+gst_cols[5])/2, y - 23, f"{half_gst:.1f}%")
    c.drawRightString(gst_cols[6] - 4, y - 23, f"{d['sgst_amt']:,.2f}")
    c.drawRightString(gst_cols[7] - 4, y - 23, f"{d['total_gst']:,.2f}")
    
    c.line(left, y - 26, right, y - 26)
    
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(gst_cols[0] + 3, y - 36, "Total :")
    c.drawRightString(gst_cols[2] - 4, y - 36, f"{d['taxable_amt']:,.2f}")
    c.drawRightString(gst_cols[4] - 4, y - 36, f"{d['cgst_amt']:,.2f}")
    c.drawRightString(gst_cols[6] - 4, y - 36, f"{d['sgst_amt']:,.2f}")
    c.drawRightString(gst_cols[7] - 4, y - 36, f"{d['total_gst']:,.2f}")
    
    for gcx in gst_cols:
        c.line(gcx, y, gcx, y - 40)
        
    y -= 40
    c.line(left, y, right, y)
    
    # 8. Grand Total Strip
    c.setFont("Helvetica-Bold", 9)
    c.drawString(left + 5, y - 12, "Grand Total")
    c.drawRightString(right - 5, y - 12, f"₹{d['grand_total']:,.2f}")
    
    y -= 16
    c.line(left, y, right, y)
    
    # 9. Amount in Words & Final Footer
    sign_split = left + 370
    c.line(sign_split, y, sign_split, bottom)
    
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(left + 5, y - 12, "Amnt In Words:")
    c.setFont("Helvetica-Oblique", 7.5)
    c.drawString(left + 72, y - 12, f"{d['amt_in_words']}")
    
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(left + 5, y - 28, "Company's GSTIN No.:")
    c.setFont("Helvetica", 7.5)
    c.drawString(left + 105, y - 28, COMPANY_GSTIN)
    
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(left + 5, y - 40, "Company's PAN No. :")
    c.setFont("Helvetica", 7.5)
    c.drawString(left + 105, y - 40, COMPANY_PAN)
    
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(left + 5, y - 52, "Company's Address :")
    c.setFont("Helvetica", 6.5)
    c.drawString(left + 95, y - 52, COMPANY_ADDRESS[:65])
    c.drawString(left + 5, y - 62, COMPANY_ADDRESS[65:])
    
    # Right Signatory
    c.setFont("Helvetica-Bold", 8)
    c.drawRightString(right - 8, y - 14, f"For, {COMPANY_NAME}")
    c.setFont("Helvetica", 8)
    c.drawRightString(right - 15, bottom + 8, "Authorised Signatory")
    
    c.save()
    buffer.seek(0)
    return buffer

# Streamlit App Logic
menu = st.sidebar.radio("Navigation", ["Create New Invoice", "Invoice Records & History"])

if menu == "Create New Invoice":
    st.subheader("Tax Invoice Entry")
    c1, c2, c3 = st.columns(3)
    with c1:
        inv_no = st.number_input("Invoice No.", min_value=1, step=1, value=1)
        bill_date = st.date_input("Invoice Date", value=date.today())
        term_days = st.number_input("Term (Days)", min_value=0, value=2)
    with c2:
        cust_name = st.text_input("Customer Name", value="Rushabh Mandaviya")
        cust_address = st.text_input("Address", value="satyam hills g1304")
        cust_mobile = st.text_input("Mobile No.", value="8264605156")
    with c3:
        cust_gstin = st.text_input("GSTIN", value="")
        cust_pan = st.text_input("PAN", value="")
        state_name = st.text_input("State", value="Gujarat")
        state_code = st.text_input("State Code", value="24")

    t1, t2, t3, t4, t5 = st.columns(5)
    with t1: transport = st.text_input("Transport", value="")
    with t2: lr_no = st.text_input("LR. No.", value="")
    with t3: lr_date = st.text_input("LR. Date", value="")
    with t4: vehicle_no = st.text_input("Vehicle No.", value="")
    with t5: cases = st.text_input("Cases", value="")

    num_items = st.number_input("Items Count", min_value=1, max_value=10, value=2)
    items = []
    for i in range(num_items):
        ic1, ic2, ic3, ic4, ic5 = st.columns([3, 1.5, 1, 1.5, 1])
        with ic1: desc = st.text_input(f"Item #{i+1}", key=f"desc_{i}", value=f"Item Description {i+1}")
        with ic2: hsn = st.text_input(f"HSN", key=f"hsn_{i}", value="")
        with ic3: qty = st.number_input(f"Qty", min_value=0.0, step=1.0, value=234.0 if i==0 else 32.0, key=f"qty_{i}")
        with ic4: rate = st.number_input(f"Rate", min_value=0.0, step=10.0, value=23320.0 if i==0 else 432.0, key=f"rate_{i}")
        with ic5: gst_pct = st.selectbox(f"GST%", [0.0, 5.0, 12.0, 18.0, 28.0], index=3, key=f"gst_{i}")
        items.append({"desc": desc, "hsn": hsn, "qty": qty, "rate": rate, "gst_pct": gst_pct, "amount": qty * rate})

    trans_charges = st.number_input("Trans. Charges", min_value=0.0, value=0.0)
    taxable_amt = sum(item["amount"] for item in items)
    sub_total = taxable_amt + trans_charges
    cgst_amt = sum(item["amount"] * (item["gst_pct"] / 200.0) for item in items)
    sgst_amt = cgst_amt
    total_gst = cgst_amt + sgst_amt
    grand_total = round(sub_total + total_gst, 2)
    amt_in_words = num_to_words(grand_total)

    payload = {
        "inv_no": inv_no, "bill_date": bill_date.strftime("%d-%m-%Y"), "term_days": term_days,
        "cust_name": cust_name, "cust_address": cust_address, "cust_mobile": cust_mobile,
        "cust_gstin": cust_gstin, "cust_pan": cust_pan, "state_name": state_name, "state_code": state_code,
        "transport": transport, "lr_no": lr_no, "lr_date": lr_date, "vehicle_no": vehicle_no, "cases": cases,
        "items": items, "taxable_amt": taxable_amt, "sub_total": sub_total, "trans_charges": trans_charges,
        "cgst_amt": cgst_amt, "sgst_amt": sgst_amt, "total_gst": total_gst, "grand_total": grand_total,
        "amt_in_words": amt_in_words
    }

    pdf_bytes = draw_exact_invoice(payload)
    st.download_button("📥 Download Exact A4 PDF Invoice", data=pdf_bytes, file_name=f"{inv_no}_{cust_name.strip()}.pdf", mime="application/pdf", type="primary")
