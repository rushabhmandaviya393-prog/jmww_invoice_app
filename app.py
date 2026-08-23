import streamlit as st
import pandas as pd
from datetime import date, timedelta
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="JAY MATAJI WELDING WORKS - Invoicing", layout="wide")

# --- CONSTANTS & COMPANY PROFILE ---
COMPANY_NAME = "JAY MATAJI WELDING WORKS"
COMPANY_GSTIN = "24BWUPM5424M1ZW"
COMPANY_PAN = "BWUPM5424M"
COMPANY_ADDRESS = "Plot No. 6, Oorja 10 Industrial Park, Near De-well Tools, Pardi - Padavala Road, Pardi, Rajkot, Gujarat-360024."
COMPANY_PHONES = "+91 99242 50886 / +91 82649 39760"
COMPANY_EMAIL = "info@jmww.in"
COMPANY_WEBSITE = "www.jmww.in"
BANK_DETAILS = "INDIAN OVERSEAS BANK (IOB) | A/C No.: 181802000000600 | IFSC: IOBA0001818 | Branch: P.D. MALAVIYA COLLEGE, RAJKOT."

DB_FILE = "invoice_records.csv"

# --- HELPER FUNCTIONS ---
def num_to_words(num):
    # Basic integer to words converter for INR
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
        
    return result.strip() + " Rupees Only"

def load_records():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["IN NO", "NAME", "AMOUNT", "BILL DATE", "DUE DATE", "PAID", "TIME"])

def save_record(record):
    df = load_records()
    df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
    df.to_csv(DB_FILE, index=False)

# --- NAVIGATION ---
menu = st.sidebar.radio("Navigation", ["Create New Invoice", "Invoice Records & History"])

# --- HEADER IMAGE / LOGO ---
# To use your custom image header, place "header.png" in the same folder
if os.path.exists("header.png"):
    st.image("header.png", use_container_width=True)
else:
    st.markdown(f"<h2 style='text-align: center; color: #1E3A8A;'>{COMPANY_NAME}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center;'>{COMPANY_ADDRESS}<br>📞 {COMPANY_PHONES} | ✉️ {COMPANY_EMAIL} | 🌐 {COMPANY_WEBSITE}</p>", unsafe_allow_html=True)

st.divider()

if menu == "Create New Invoice":
    st.subheader("📄 TAX INVOICE (DEBIT / ORIGINAL)")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        inv_no = st.number_input("Invoice No.", min_value=1, step=1, value=1)
        bill_date = st.date_input("Invoice Date", value=date.today())
        term_days = st.number_input("Payment Term (Days)", min_value=0, value=2)
        due_date = bill_date + timedelta(days=int(term_days))
        st.caption(f"Due Date: **{due_date}**")

    with col2:
        cust_name = st.text_input("Customer / Party Name")
        cust_address = st.text_area("Customer Address")
        cust_mobile = st.text_input("Customer Mobile No.")

    with col3:
        cust_gstin = st.text_input("Party GSTIN No.")
        cust_pan = st.text_input("Party PAN No.")
        state_name = st.text_input("State Name", value="Gujarat")
        state_code = st.text_input("State Code", value="24")

    st.markdown("### 🚚 Transport & Logistics")
    t1, t2, t3, t4, t5 = st.columns(5)
    with t1: transport = st.text_input("Transport")
    with t2: lr_no = st.text_input("LR. No.")
    with t3: lr_date = st.date_input("LR. Date", value=date.today())
    with t4: vehicle_no = st.text_input("Vehicle No.")
    with t5: cases = st.text_input("Cases / Packages")

    st.markdown("### 📦 Item Details")
    num_items = st.number_input("Number of Items", min_value=1, max_value=20, value=1)
    
    items = []
    for i in range(num_items):
        ic1, ic2, ic3, ic4, ic5 = st.columns([3, 1.5, 1, 1.5, 1.5])
        with ic1: desc = st.text_input(f"Item #{i+1} Description", key=f"desc_{i}")
        with ic2: hsn = st.text_input(f"HSN Code", key=f"hsn_{i}")
        with ic3: qty = st.number_input(f"Qty", min_value=0.0, step=1.0, value=1.0, key=f"qty_{i}")
        with ic4: rate = st.number_input(f"Rate (₹)", min_value=0.0, step=10.0, value=0.0, key=f"rate_{i}")
        with ic5: gst_pct = st.selectbox(f"GST %", [0.0, 5.0, 12.0, 18.0, 28.0], index=3, key=f"gst_{i}")
        
        item_amt = qty * rate
        items.append({"desc": desc, "hsn": hsn, "qty": qty, "rate": rate, "gst_pct": gst_pct, "amount": item_amt})

    # Calculations
    taxable_amt = sum(item["amount"] for item in items)
    trans_charges = st.number_input("Transport Charges (₹)", min_value=0.0, value=0.0)
    sub_total = taxable_amt + trans_charges

    # Intra-state (CGST + SGST) vs Inter-state (IGST)
    is_intrastate = (state_code == "24")
    cgst_amt = sum((item["amount"] * (item["gst_pct"] / 200.0)) for item in items) if is_intrastate else 0.0
    sgst_amt = cgst_amt
    igst_amt = sum((item["amount"] * (item["gst_pct"] / 100.0)) for item in items) if not is_intrastate else 0.0
    
    total_gst = (cgst_amt + sgst_amt) if is_intrastate else igst_amt
    grand_total = round(sub_total + total_gst, 2)
    amt_in_words = num_to_words(grand_total)

    st.markdown("---")
    res1, res2 = st.columns(2)
    with res1:
        st.write(f"**Taxable Amount:** ₹{taxable_amt:,.2f}")
        if is_intrastate:
            st.write(f"**CGST Amount:** ₹{cgst_amt:,.2f}")
            st.write(f"**SGST Amount:** ₹{sgst_amt:,.2f}")
        else:
            st.write(f"**IGST Amount:** ₹{igst_amt:,.2f}")
        st.write(f"**Total GST:** ₹{total_gst:,.2f}")
    with res2:
        st.metric(label="Grand Total", value=f"₹{grand_total:,.2f}")
        st.caption(f"**Amount in Words:** {amt_in_words}")

    if st.button("💾 Save Invoice & Record", type="primary"):
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
        st.success(f"Invoice #{inv_no} for {cust_name} has been saved successfully!")

elif menu == "Invoice Records & History":
    st.subheader("📑 Invoice History Ledger")
    records_df = load_records()
    if not records_df.empty:
        st.dataframe(records_df, use_container_width=True)
        csv_data = records_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Master Record CSV", data=csv_data, file_name="Master_Invoice_Records.csv", mime="text/csv")
    else:
        st.info("No invoice records created yet.")
