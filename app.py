import streamlit as st
import pandas as pd
from datetime import date, timedelta
import io
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="JAY MATAJI WELDING WORKS - Invoicing", layout="wide")

COMPANY_NAME = "JAY MATAJI WELDING WORKS"
COMPANY_GSTIN = "24BWUPM5424M1ZW"
COMPANY_PAN = "BWUPM5424M"
COMPANY_ADDRESS = "Plot No. 6, Oorja 10 Industrial Park, Near De-well Tools, Pardi - Padavala Road, Pardi, Rajkot, Gujarat-360024."
COMPANY_PHONES = "+91 99242 50886  +91 82649 39760"
COMPANY_EMAIL = "info@jmww.in"
COMPANY_WEBSITE = "www.jmww.in"
BANK_LINE1 = "INDIAN OVERSEAS BANK (IOB)"
BANK_LINE2 = "A/C No. : 181802000000600"
BANK_LINE3 = "IFSC CODE : IOBA0001818"
BANK_LINE4 = "BRANCH : P.D. MALAVIYA COLLEGE, RAJKOT."

DB_FILE = "invoice_records.csv"

# --- HELPER FUNCTIONS ---
def num_to_words(num):
    units = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten",
             "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
    
    def convert_below_thousand(n):
        res = ""
        if n >= 100:
            res += units[n // 100] + " Hundred "
            n %= 100
        if n >= 20:
            res += tens[n // 10] + " "
            n %= 10
        if n > 0:
            res += units[n] + " "
        return res

    n = int(num)
    paise = int(round((num - n) * 100))
    
    if n == 0:
        words = "Zero Rupees"
    else:
        crore = n // 10000000
        n %= 10000000
        lakh = n // 100000
        n %= 100000
        thousand = n // 1000
        n %= 1000
        rem = n
        
        words = ""
        if crore > 0: words += convert_below_thousand(crore) + "Crore "
        if lakh > 0: words += convert_below_thousand(lakh) + "Lakh "
        if thousand > 0: words += convert_below_thousand(thousand) + "Thousand "
        if rem > 0: words += convert_below_thousand(rem)
        words = words.strip() + " Rupees"

    if paise > 0:
        words += f" and {convert_below_thousand(paise).strip()} Paise"
    return words + " Only"

def load_records():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["IN NO", "NAME", "AMOUNT", "BILL DATE", "DUE DATE", "PAID", "TIME"])

def save_record(record):
    df = load_records()
    df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
    df.to_csv(DB_FILE, index=False)

def generate_exact_visual_pdf(data):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter # 612 x 792

    # Dimensions
    x = 25
    y_top = 765
    w = 562
    h_total = 735
    y_bot = y_top - h_total

    # Outer Border Box
    p.setLineWidth(1)
    p.setStrokeColor(colors.black)
    p.rect(x, y_bot, w, h_total)

    # 1. Top Badges (DEBIT / ORIGINAL)
    p.setFont("Helvetica-Bold", 8)
    p.rect(x, y_top - 18, 55, 18)
    p.drawCentredString(x + 27.5, y_top - 13, "DEBIT")

    p.rect(x + w - 65, y_top - 18, 65, 18)
    p.drawCentredString(x + w - 32.5, y_top - 13, "ORIGINAL")

    # 2. Header Section
    if os.path.exists("header.png"):
        p.drawImage("header.png", x + 10, y_top - 78, width=70, height=58, preserveAspectRatio=True, mask='auto')
    
    p.setFont("Helvetica-Bold", 14)
    p.setFillColor(colors.HexColor("#A82D08"))
    p.drawString(x + 90, y_top - 38, "JAY MATAJI WELDING WORKS")
    
    p.setFillColor(colors.black)
    p.setFont("Helvetica", 7.5)
    p.drawRightString(x + w - 10, y_top - 33, COMPANY_PHONES)
    p.drawRightString(x + w - 10, y_top - 45, COMPANY_EMAIL)
    p.drawRightString(x + w - 10, y_top - 57, COMPANY_WEBSITE)

    # TAX INVOICE Title Bar
    p.line(x, y_top - 80, x + w, y_top - 80)
    p.setFont("Helvetica-Bold", 11)
    p.drawCentredString(x + (w / 2), y_top - 93, "TAX INVOICE")
    p.line(x, y_top - 98, x + w, y_top - 98)

    # 3. Party & Meta Data Two-Column Box
    meta_box_h = 100
    meta_y = y_top - 98 - meta_box_h
    p.line(x, meta_y, x + w, meta_y)
    p.line(x + 280, y_top - 98, x + 280, meta_y) # Split column

    # Left Column (Customer)
    p.setFont("Helvetica-Bold", 7.5)
    p.drawString(x + 5, y_top - 108, "To,")
    p.drawString(x + 25, y_top - 108, f"{data['cust_name']}")
    p.setFont("Helvetica", 7.5)
    p.drawString(x + 25, y_top - 118, f"{data['cust_address']}")
    
    p.setFont("Helvetica-Bold", 7.5)
    p.drawString(x + 5, y_top - 145, "State:")
    p.setFont("Helvetica", 7.5)
    p.drawString(x + 40, y_top - 145, f"{data['state_name']}")
    p.setFont("Helvetica-Bold", 7.5)
    p.drawString(x + 160, y_top - 145, "Code:")
    p.setFont("Helvetica", 7.5)
    p.drawString(x + 190, y_top - 145, f"{data['state_code']}")

    p.setFont("Helvetica-Bold", 7.5)
    p.drawString(x + 5, y_top - 160, "Mo. No.:")
    p.setFont("Helvetica", 7.5)
    p.drawString(x + 45, y_top - 160, f"{data['cust_mobile']}")
    p.setFont("Helvetica-Bold", 7.5)
    p.drawString(x + 160, y_top - 160, "Term:")
    p.setFont("Helvetica", 7.5)
    p.drawString(x + 190, y_top - 160, f"{data['term_days']} Days")

    p.setFont("Helvetica-Bold", 7.5)
    p.drawString(x + 5, y_top - 175, "Party's GSTIN No:")
    p.setFont("Helvetica", 7.5)
    p.drawString(x + 85, y_top - 175, f"{data['cust_gstin']}")

    p.setFont("Helvetica-Bold", 7.5)
    p.drawString(x + 5, y_top - 190, "Party's PAN No:")
    p.setFont("Helvetica", 7.5)
    p.drawString(x + 85, y_top - 190, f"{data['cust_pan']}")

    # Right Column (Transport / Inv Info)
    p.setFont("Helvetica-Bold", 7.5)
    p.drawString(x + 285, y_top - 108, "INVOICE NO:")
    p.setFont("Helvetica-Bold", 8)
    p.drawString(x + 350, y_top - 108, f"{data['inv_no']}")
    p.setFont("Helvetica-Bold", 7.5)
    p.drawString(x + 430, y_top - 108, "Date:")
    p.setFont("Helvetica", 7.5)
    p.drawString(x + 460, y_top - 108, f"{data['bill_date']}")

    p.setFont("Helvetica-Bold", 7.5)
    p.drawString(x + 285, y_top - 125, "TRANSPORT :")
    p.setFont("Helvetica", 7.5)
    p.drawString(x + 360, y_top - 125, f"{data['transport']}")

    p.setFont("Helvetica-Bold", 7.5)
    p.drawString(x + 285, y_top - 140, "LR. NO. :")
    p.setFont("Helvetica", 7.5)
    p.drawString(x + 340, y_top - 140, f"{data['lr_no']}")
    p.setFont("Helvetica-Bold", 7.5)
    p.drawString(x + 430, y_top - 140, "LR. DATE :")
    p.setFont("Helvetica", 7.5)
    p.drawString(x + 480, y_top - 140, f"{data['lr_date']}")

    p.setFont("Helvetica-Bold", 7.5)
    p.drawString(x + 285, y_top - 158, "VEHICLE NO. :")
    p.setFont("Helvetica", 7.5)
    p.drawString(x + 360, y_top - 158, f"{data['vehicle_no']}")

    p.setFont("Helvetica-Bold", 7.5)
    p.drawString(x + 285, y_top - 175, "CASES :")
    p.setFont("Helvetica", 7.5)
    p.drawString(x + 340, y_top - 175, f"{data['cases']}")

    p.setFont("Helvetica-Bold", 7.5)
    p.drawString(x + 285, y_top - 190, "AGAINST FORM:")

    # 4. Item Table Layout
    table_top = meta_y
    header_h = 18
    p.rect(x, table_top - header_h, w, header_h, fill=0)
    
    # Columns definitions: x-start
    cols = [x, x + 25, x + 240, x + 310, x + 375, x + 440, x + 490, x + w]

    # Draw Column Headers
    headers = ["Sr.", "Iteam Description", "HSN Code", "Quantity", "Rate", "GST%", "Amount"]
    p.setFont("Helvetica-Bold", 7.5)
    for i in range(len(headers)):
        align_x = (cols[i] + cols[i+1])/2 if i not in [1, 6] else (cols[i] + 5 if i == 1 else cols[i+1] - 5)
        if i in [1]:
            p.drawString(align_x, table_top - 13, headers[i])
        elif i in [6]:
            p.drawRightString(align_x, table_top - 13, headers[i])
        else:
            p.drawCentredString(align_x, table_top - 13, headers[i])

    table_bottom = table_top - 240
    for cx in cols[1:-1]:
        p.line(cx, table_top, cx, table_bottom)

    # Watermark Logo inside Item Table Area
    if os.path.exists("header.png"):
        p.saveState()
        p.setFillAlpha(0.10)
        p.drawImage("header.png", x + (w/2) - 80, table_top - 190, width=160, height=130, preserveAspectRatio=True, mask='auto')
        p.restoreState()

    # Fill Items
    curr_y = table_top - header_h - 12
    total_qty = 0
    for idx, item in enumerate(data['items']):
        p.setFont("Helvetica", 7.5)
        p.drawCentredString((cols[0] + cols[1])/2, curr_y, str(idx + 1))
        p.drawString(cols[1] + 5, curr_y, str(item['desc']))
        p.drawCentredString((cols[2] + cols[3])/2, curr_y, str(item['hsn']))
        p.drawCentredString((cols[3] + cols[4])/2, curr_y, f"{item['qty']:.2f}")
        p.drawRightString(cols[5] - 5, curr_y, f"{item['rate']:,.2f}")
        p.drawCentredString((cols[5] + cols[6])/2, curr_y, f"{item['gst_pct']:.0f}%")
        p.drawRightString(cols[7] - 5, curr_y, f"{item['amount']:,.2f}")
        total_qty += item['qty']
        curr_y -= 14

    # Table Footer / Subtotals
    p.line(x, table_bottom, x + w, table_bottom)
    p.line(x, table_bottom + 18, x + w, table_bottom + 18)
    
    p.setFont("Helvetica-Bold", 7.5)
    p.drawCentredString((cols[3] + cols[4])/2, table_bottom + 5, f"{total_qty:.2f}")
    p.drawString(cols[4] + 10, table_bottom + 5, "Total Amnt.")
    p.drawRightString(cols[7] - 5, table_bottom + 5, f"{data['taxable_amt']:,.2f}")

    # 5. Bank Details & Subtotal Right Stack
    b_box_h = 70
    b_y = table_bottom - b_box_h
    p.line(x, b_y, x + w, b_y)
    p.line(x + 360, table_bottom, x + 360, b_y)

    # Bank info on Left
    p.setFont("Helvetica-Bold", 7.5)
    p.drawString(x + 5, table_bottom - 12, "Bank Details:")
    p.drawString(x + 5, table_bottom - 24, BANK_LINE1)
    p.setFont("Helvetica", 7.5)
    p.drawString(x + 5, table_bottom - 36, BANK_LINE2)
    p.drawString(x + 5, table_bottom - 48, BANK_LINE3)
    p.drawString(x + 5, table_bottom - 60, BANK_LINE4)

    # Right side subtotals
    p.line(x + 460, table_bottom, x + 460, b_y)
    p.setFont("Helvetica-Bold", 7.5)
    p.drawString(x + 365, table_bottom - 12, "Trans. Charges")
    p.drawRightString(x + w - 5, table_bottom - 12, f"{data['trans_charges']:,.2f}")
    p.line(x + 360, table_bottom - 18, x + w, table_bottom - 18)

    p.drawString(x + 365, table_bottom - 30, "Sub Total")
    p.drawRightString(x + w - 5, table_bottom - 30, f"{data['sub_total']:,.2f}")
    p.line(x + 360, table_bottom - 36, x + w, table_bottom - 36)

    p.drawString(x + 365, table_bottom - 48, "CGST")
    p.drawRightString(x + w - 5, table_bottom - 48, f"{data['cgst_amt']:,.2f}")
    p.line(x + 360, table_bottom - 54, x + w, table_bottom - 54)

    p.drawString(x + 365, table_bottom - 64, "SGST")
    p.drawRightString(x + w - 5, table_bottom - 64, f"{data['sgst_amt']:,.2f}")

    # 6. GST Summary Matrix & Grand Total Box
    gst_matrix_h = 55
    gst_y = b_y - gst_matrix_h
    p.line(x, gst_y, x + w, gst_y)
    p.line(x + 360, b_y, x + 360, gst_y)

    # GST Summary Left Sub-table
    p.setFont("Helvetica-Bold", 7)
    gcols = [x, x + 65, x + 130, x + 165, x + 215, x + 250, x + 300, x + 360]
    p.line(x, b_y - 14, x + 360, b_y - 14)
    p.line(x, b_y - 32, x + 360, b_y - 32)
    for gcx in gcols[1:-1]:
        p.line(gcx, b_y, gcx, gst_y)

    p.drawString(x + 3, b_y - 10, "GST Summary")
    p.drawString(gcols[1] + 3, b_y - 10, "Taxable Amnt")
    p.drawString(gcols[2] + 3, b_y - 10, "CGST")
    p.drawString(gcols[3] + 3, b_y - 10, "CGST Amnt")
    p.drawString(gcols[4] + 3, b_y - 10, "SGST")
    p.drawString(gcols[5] + 3, b_y - 10, "SGST Amnt")
    p.drawString(gcols[6] + 3, b_y - 10, "Total GST")

    p.setFont("Helvetica", 7)
    p.drawString(x + 3, b_y - 25, "GST")
    p.drawString(gcols[1] + 3, b_y - 25, f"{data['taxable_amt']:,.2f}")
    p.drawString(gcols[2] + 3, b_y - 25, "9.0%")
    p.drawString(gcols[3] + 3, b_y - 25, f"{data['cgst_amt']:,.2f}")
    p.drawString(gcols[4] + 3, b_y - 25, "9.0%")
    p.drawString(gcols[5] + 3, b_y - 25, f"{data['sgst_amt']:,.2f}")
    p.drawString(gcols[6] + 3, b_y - 25, f"{data['total_gst']:,.2f}")

    p.setFont("Helvetica-Bold", 7)
    p.drawString(x + 3, b_y - 45, "Total :")
    p.drawString(gcols[1] + 3, b_y - 45, f"{data['taxable_amt']:,.2f}")
    p.drawString(gcols[3] + 3, b_y - 45, f"{data['cgst_amt']:,.2f}")
    p.drawString(gcols[5] + 3, b_y - 45, f"{data['sgst_amt']:,.2f}")
    p.drawString(gcols[6] + 3, b_y - 45, f"{data['total_gst']:,.2f}")

    # Grand Total on Right
    p.line(x + 460, b_y, x + 460, gst_y)
    p.setFont("Helvetica-Bold", 9)
    p.drawString(x + 365, b_y - 30, "Grand Total")
    p.drawRightString(x + w - 5, b_y - 30, f"INR {data['grand_total']:,.2f}")

    # 7. Amount in Words Line
    words_h = 20
    words_y = gst_y - words_h
    p.line(x, words_y, x + w, words_y)
    p.setFont("Helvetica-Bold", 7.5)
    p.drawString(x + 5, words_y + 6, "Amnt In Words:")
    p.setFont("Helvetica-Oblique", 7.5)
    p.drawString(x + 75, words_y + 6, f"{data['amt_in_words']}")

    # 8. Bottom Company & Signatory Footer
    p.line(x + 360, words_y, x + 360, y_bot)
    
    p.setFont("Helvetica-Bold", 7.5)
    p.drawString(x + 5, words_y - 12, "Company's GSTIN No.:")
    p.setFont("Helvetica", 7.5)
    p.drawString(x + 105, words_y - 12, COMPANY_GSTIN)

    p.setFont("Helvetica-Bold", 7.5)
    p.drawString(x + 5, words_y - 25, "Company's PAN No. :")
    p.setFont("Helvetica", 7.5)
    p.drawString(x + 105, words_y - 25, COMPANY_PAN)

    p.setFont("Helvetica-Bold", 7.5)
    p.drawString(x + 5, words_y - 38, "Company's Address :")
    p.setFont("Helvetica", 7.5)
    p.drawString(x + 105, words_y - 38, "Plot No. 6, Oorja 10 Industrial Park, Near De-well")
    p.drawString(x + 105, words_y - 48, "Tools, Pardi - Padavala Road, Pardi, Rajkot, Gujarat-")
    p.drawString(x + 105, words_y - 58, "360024.")

    p.setFont("Helvetica-Bold", 8)
    p.drawCentredString(x + 460, words_y - 15, "For, JAY MATAJI WELDING WORKS")
    p.setFont("Helvetica", 8)
    p.drawCentredString(x + 460, y_bot + 12, "Authorised Signatory")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

# --- USER INTERFACE ---
menu = st.sidebar.radio("Navigation", ["Create New Invoice", "Invoice Records & History"])

if os.path.exists("header.png"):
    st.image("header.png", use_container_width=True)
else:
    st.markdown(f"<h2 style='text-align: center; color: #1E3A8A;'>{COMPANY_NAME}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center;'>{COMPANY_ADDRESS}<br>📞 {COMPANY_PHONES} | ✉️ {COMPANY_EMAIL} | 🌐 {COMPANY_WEBSITE}</p>", unsafe_allow_html=True)

st.divider()

if menu == "Create New Invoice":
    st.subheader("📄 TAX INVOICE GENERATOR")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        inv_no = st.number_input("Invoice No.", min_value=1, step=1, value=1)
        bill_date = st.date_input("Invoice Date", value=date.today())
        term_days = st.number_input("Payment Term (Days)", min_value=0, value=2)
        due_date = bill_date + timedelta(days=int(term_days))

    with col2:
        cust_name = st.text_input("Customer / Party Name", value="Rushabh Mandaviya")
        cust_address = st.text_area("Customer Address", value="satyam hills g1304")
        cust_mobile = st.text_input("Customer Mobile No.", value="8264605156")

    with col3:
        cust_gstin = st.text_input("Party GSTIN No.", value="dfauhfjqwaaw")
        cust_pan = st.text_input("Party PAN No.", value="")
        state_name = st.text_input("State Name", value="Gujarat")
        state_code = st.text_input("State Code", value="24")

    st.markdown("### 🚚 Transport & Logistics")
    t1, t2, t3, t4, t5 = st.columns(5)
    with t1: transport = st.text_input("Transport", value="")
    with t2: lr_no = st.text_input("LR. No.", value="")
    with t3: lr_date = st.date_input("LR. Date", value=date.today())
    with t4: vehicle_no = st.text_input("Vehicle No.", value="")
    with t5: cases = st.text_input("Cases / Packages", value="")

    st.markdown("### 📦 Item Rows")
    num_items = st.number_input("Number of Items", min_value=1, max_value=15, value=2)
    
    items = []
    for i in range(num_items):
        ic1, ic2, ic3, ic4, ic5 = st.columns([3, 1.5, 1, 1.5, 1.5])
        with ic1: desc = st.text_input(f"Item #{i+1} Description", key=f"desc_{i}", value=f"Item {i+1}")
        with ic2: hsn = st.text_input(f"HSN Code", key=f"hsn_{i}", value="")
        with ic3: qty = st.number_input(f"Qty", min_value=0.0, step=1.0, value=234.0 if i==0 else 32.0, key=f"qty_{i}")
        with ic4: rate = st.number_input(f"Rate (₹)", min_value=0.0, step=10.0, value=23320.0 if i==0 else 432.0, key=f"rate_{i}")
        with ic5: gst_pct = st.selectbox(f"GST %", [0.0, 5.0, 12.0, 18.0, 28.0], index=3, key=f"gst_{i}")
        
        items.append({"desc": desc, "hsn": hsn, "qty": qty, "rate": rate, "gst_pct": gst_pct, "amount": qty * rate})

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

    st.markdown("---")
    r1, r2 = st.columns(2)
    with r1:
        st.write(f"**Taxable Total:** ₹{taxable_amt:,.2f}")
        st.write(f"**Total GST (9% + 9%):** ₹{total_gst:,.2f}")
    with r2:
        st.metric("Grand Total", f"₹{grand_total:,.2f}")
        st.caption(f"**In Words:** {amt_in_words}")

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

    b1, b2 = st.columns(2)
    with b1:
        if st.button("💾 Save Invoice", type="primary", use_container_width=True):
            record = {
                "IN NO": inv_no,
                "NAME": cust_name,
                "AMOUNT": f"₹{grand_total:,.2f}",
                "BILL DATE": bill_date.strftime("%m/%d/%Y"),
                "DUE DATE": due_date.strftime("%m/%d/%Y"),
                "PAID": "NO",
                "TIME": pd.Timestamp.now().strftime("%m/%d/%Y %H:%M")
            }
            save_record(record)
            st.success(f"Invoice #{inv_no} recorded!")

    with b2:
        pdf_file = generate_exact_visual_pdf(inv_payload)
        st.download_button(
            label="📥 Download Invoice PDF",
            data=pdf_file,
            file_name=f"{inv_no}_{cust_name}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

elif menu == "Invoice Records & History":
    st.subheader("📑 Saved Invoice Ledger")
    records_df = load_records()
    if not records_df.empty:
        st.dataframe(records_df, use_container_width=True)
        st.download_button("📥 Export CSV", data=records_df.to_csv(index=False).encode('utf-8'), file_name="Invoice_Ledger.csv", mime="text/csv")
    else:
        st.info("No records saved yet.")
