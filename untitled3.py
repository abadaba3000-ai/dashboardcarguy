import streamlit as st
import pandas as pd
import random
import xml.etree.ElementTree as ET

# --- ΡΥΘΜΙΣΗ ΣΕΛΙΔΑΣ ---
st.set_page_config(layout="wide")

# --- LOGIN ΜΕ ΠΡΟΣΤΑΣΙΑ (ΕΠΙΤΡΕΠΕΙ ΞΑΝΑΠΡΟΣΠΑΘΕΙΑ) ---
def check_password():
    if "password_correct" in st.session_state and st.session_state["password_correct"]:
        return True

    st.title("🔒 Carguy.gr - Είσοδος στο Σύστημα")
    user_input = st.text_input("Username", key="login_user")
    pass_input = st.text_input("Password", type="password", key="login_pass")

    if st.button("Είσοδος"):
        if "auth" in st.secrets and user_input == st.secrets["auth"]["username"] and pass_input == st.secrets["auth"]["password"]:
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("❌ Λάθος στοιχεία. Παρακαλώ ξαναπροσπάθησε.")
    return False

if not check_password():
    st.stop()

# --- ΓΕΦΥΡΑ SITE (WEBHOOK) ---
def send_update_to_website(order_id, product_name, qty, status):
    print(f"[ΓΕΦΥΡΑ] Ενημέρωση site: {order_id} -> {status}. Προϊόν: {product_name}, Qty: {qty}")

# --- ΑΡΧΙΚΟΠΟΙΗΣΗ ΔΕΔΟΜΕΝΩΝ ---
if 'complete_inventory' not in st.session_state:
    st.session_state.complete_inventory = [
        {'ID': 'CAR-001', 'Barcode': '5201234567890', 'Όνομα': 'FM Transmitter', 'Δικό μου Stock': 5, 'Stock XML': 45},
        {'ID': 'CAR-002', 'Barcode': '5209876543210', 'Όνομα': 'Μαγνητική Βάση', 'Δικό μου Stock': 0, 'Stock XML': 12}
    ]
if 'orders_db' not in st.session_state:
    st.session_state.orders_db = [
        {'ID': '#1001', 'Πελάτης': 'Γιώργος', 'Προϊόν': 'Μαγνητική Βάση', 'Ποσότητα': 1, 'Σύνολο (€)': 18.50, 'Κατάσταση': '⏳ Σε επεξεργασία'}
    ]
if 'issued_invoices' not in st.session_state: st.session_state.issued_invoices = []
if 'auto_invoice_data' not in st.session_state: st.session_state.auto_invoice_data = None
if 'current_menu' not in st.session_state: st.session_state.current_menu = "📦 Αποθήκη"

# --- SIDEBAR ΜΕΝΟΥ ---
menu = st.sidebar.radio("Μενού", ["📦 Αποθήκη", "📦 Παραλαβές", "🛒 Παραγγελίες", "🧾 Τιμολογιέρα"])
st.session_state.current_menu = menu

# --- ΛΟΓΙΚΗ ΣΕΛΙΔΩΝ ---
if menu == "📦 Αποθήκη":
    st.title("📦 Κατάσταση Αποθήκης")
    st.dataframe(pd.DataFrame(st.session_state.complete_inventory), use_container_width=True)

elif menu == "📦 Παραλαβές":
    st.title("📦 Νέα Παραλαβή")
    bc = st.text_input("Barcode:")
    qty = st.number_input("Ποσότητα:", min_value=1, value=1)
    if st.button("Καταχώρηση"):
        for p in st.session_state.complete_inventory:
            if p['Barcode'] == bc:
                p['Δικό μου Stock'] += qty
                st.success("Επιτυχία!")
                break

elif menu == "🛒 Παραγγελίες":
    st.title("🛒 Διαχείριση Παραγγελιών")
    for idx, row in enumerate(st.session_state.orders_db):
        col1, col2 = st.columns([3, 1])
        col1.write(f"{row['ID']} - {row['Πελάτης']} - {row['Κατάσταση']}")
        if row['Κατάσταση'] == '⏳ Σε επεξεργασία':
            if col2.button("Εκτέλεση", key=f"btn_{idx}"):
                st.session_state.auto_invoice_data = row
                st.session_state.orders_db[idx]['Κατάσταση'] = '📦 Απεστάλη'
                send_update_to_website(row['ID'], row['Προϊόν'], row['Ποσότητα'], "Απεστάλη")
                st.session_state.current_menu = "🧾 Τιμολογιέρα"
                st.rerun()

elif menu == "🧾 Τιμολογιέρα":
    st.title("🧾 Τιμολογιέρα (myDATA)")
    data = st.session_state.auto_invoice_data
    if data:
        st.write(f"### Τιμολόγηση για: {data['Πελάτης']} - {data['Προϊόν']}")
        if st.button("Έκδοση Παραστατικού"):
            st.session_state.issued_invoices.append(data)
            st.session_state.auto_invoice_data = None
            st.success("Εκδόθηκε με επιτυχία!")
    else:
        st.info("Δεν υπάρχει εκκρεμότητα για τιμολόγηση.")
