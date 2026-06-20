import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET

# Ρύθμιση σελίδας
st.set_page_config(layout="wide", page_title="Carguy.gr Suite")

# Συνάρτηση ελέγχου σύνδεσης
def check_password():
    if "password_correct" in st.session_state and st.session_state["password_correct"]:
        return True
    st.title("🔒 Carguy.gr - Είσοδος στο Σύστημα")
    username = st.text_input("Username", key="u")
    password = st.text_input("Password", type="password", key="p")
    if st.button("Είσοδος"):
        if ("auth" in st.secrets and username == st.secrets["auth"]["username"] and
                password == st.secrets["auth"]["password"]):
            st.session_state["password_correct"] = True
            st.experimental_rerun()
        else:
            st.error("❌ Λάθος στοιχεία!")
    return False

if not check_password():
    st.stop()

# XML Δεδομένα
xml_data = """<?xml version="1.0" encoding="UTF-8"?>
<products>
    <product><id>CAR-001</id><barcode>5201234567890</barcode><name>FM Transmitter Bluetooth 5.0 Dual USB</name><category>🎧 Ήχος &amp; Επικοινωνία</category><wholesale_price>5.20</wholesale_price><market_min_price>12.90</market_min_price><stock_xml>45</stock_xml><reviews>142</reviews><negative_reviews_pct>28</negative_reviews_pct></product>
    <product><id>CAR-002</id><barcode>5209876543210</barcode><name>Μαγνητική Βάση Αεραγωγού MagSafe 15W</name><category>📱 Βάσεις Στήριξης</category><wholesale_price>7.50</wholesale_price><market_min_price>18.50</market_min_price><stock_xml>12</stock_xml><reviews>85</reviews><negative_reviews_pct>5</negative_reviews_pct></product>
    <product><id>CAR-003</id><barcode>5205556667770</barcode><name>Κάμερα Dashcam 4K WiFi Καταγραφικό</name><category>🛡️ Ασφάλεια &amp; Υποβοήθηση</category><wholesale_price>28.00</wholesale_price><market_min_price>59.00</market_min_price><stock_xml>0</stock_xml><reviews>310</reviews><negative_reviews_pct>42</negative_reviews_pct></product>
    <product><id>CAR-004</id><barcode>5208889991110</barcode><name>Έξυπνος Φορτιστής Αυτοκινήτου USB-C 65W</name><category>⚡ Φόρτιση &amp; Ισχύς</category><wholesale_price>9.10</wholesale_price><market_min_price>22.00</market_min_price><stock_xml>150</stock_xml><reviews>45</reviews><negative_reviews_pct>12</negative_reviews_pct></product>
</products>
"""

# Αποθηκευτικά δεδομένα
if 'complete_inventory' not in st.session_state:
    st.session_state.complete_inventory = [
        {'ID': 'CAR-001', 'Barcode': '5201234567890', 'Όνομα': 'FM Transmitter Bluetooth 5.0 Dual USB',
         'Κατηγορία': '🎧 Ήχος & Επικοινωνία', 'Χονδρική (€)': 5.20, 'Λιανική Αγοράς (€)': 12.90,
         'Stock XML': 45, 'Δικό μου Stock': 5, 'Αριθμός Κριτικών': 142, 'Αρνητικές Κριτικές (%)': 28},
        {'ID': 'CAR-002', 'Barcode': '5209876543210', 'Όνομα': 'Μαγνητική Βάση Αεραγωγού MagSafe 15W',
         'Κατηγορία': '📱 Βάσεις Στήριξης', 'Χονδρική (€)': 7.50, 'Λιανική Αγοράς (€)': 18.50,
         'Stock XML': 12, 'Δικό μου Stock': 0, 'Αριθμός Κριτικών': 85, 'Αρνητικές Κριτικές (%)': 5}
    ]

# Παραγγελίες
if 'orders_db' not in st.session_state:
    st.session_state.orders_db = [
        {'ID Παραγγελίας': '#1001', 'Πελάτης': 'Γιώργος Παπαδόπουλος', 'Προϊόν': 'Μαγνητική Βάση MagSafe 15W', 'Ποσότητα': 1, 'Σύνολο (€)': 18.50, 'Κατάσταση': '📦 Απεστάλη'},
        {'ID Παραγγελίας': '#1002', 'Πελάτης': 'Νίκος Καρράς', 'Προϊόν': 'FM Transmitter Bluetooth 5.0', 'Ποσότητα': 2, 'Σύνολο (€)': 25.80, 'Κατάσταση': '⏳ Σε επεξεργασία'}
    ]

# Συνάρτηση για κατάσταση προϊόντος
def calculate_eshop_status(my_stock, xml_stock):
    if my_stock > 0:
        return "🟢 Άμεσα Διαθέσιμο"
    elif my_stock == 0 and xml_stock > 0:
        return "🟠 Κατόπιν Παραγγελίας"
    else:
        return "🔴 Εξαντλήθηκε"

# Κεντρικό μενού
st.sidebar.title("🚗 Carguy.gr Suite v2.0")
menu_choice = st.sidebar.radio(
    "Επιλογή Ενότητας:",
    ["📦 Αποθήκη & Γέφυρα", "🛒 Ιστορικό Παραγγελιών", "🔍 Ανάλυση Αγοράς (Ρίσκο)", "📈 Πωλήσεις ανά Κατηγορία", "🎁 Προϊόντα & Εκπτώσεις"]
)

# 1. Αποθήκη & Γέφυρα
if menu_choice == "📦 Αποθήκη & Γέφυρα":
    st.title("📊 Κεντρική Αποθήκη & Γέφυρα")
    col_scan, col_table = st.columns([1, 3])
    with col_scan:
        with st.form("barcode_form", clear_on_submit=True):
            scanned = st.text_input("Barcode")
            qty = st.number_input("Ποσότητα", min_value=1, value=1)
            if st.form_submit_button("⚡ Καταχώρηση"):
                found = False
                for prod in st.session_state.complete_inventory:
                    if prod['Barcode'] == scanned:
                        prod['Δικό μου Stock'] += qty
                        found = True
                        break
                # Αν δεν βρεθεί, αναζήτηση στο XML
                if not found:
                    root = ET.fromstring(xml_data)
                    for prod_xml in root.findall('product'):
                        if prod_xml.find('barcode').text == scanned:
                            st.session_state.complete_inventory.append({
                                'ID': prod_xml.find('id').text,
                                'Barcode': scanned,
                                'Όνομα': prod_xml.find('name').text,
                                'Κατηγορία': prod_xml.find('category').text,
                                'Χονδρική (€)': float(prod_xml.find('wholesale_price').text),
                                'Λιανική Αγοράς (€)': float(prod_xml.find('market_min_price').text),
                                'Stock XML': int(prod_xml.find('stock_xml').text),
                                'Δικό μου Stock': qty,
                                'Αριθμός Κριτικών': int(prod_xml.find('reviews').text),
                                'Αρνητικές Κριτικές (%)': int(prod_xml.find('negative_reviews_pct').text)
                            })
                            found = True
                            break
                if found:
                    st.success("Ενημερώθηκε!")
                else:
                    st.error("Δεν βρέθηκε προϊόν με αυτό το barcode.")
                st.experimental_rerun()
    with col_table:
        df = pd.DataFrame(st.session_state.complete_inventory)
        df['Καθαρό Κέρδος (€)'] = df['Λιανική Αγοράς (€)'] - df['Χονδρική (€)']
        df['Κατάσταση στο Eshop'] = df.apply(lambda row: calculate_eshop_status(row['Δικό μου Stock'], row['Stock XML']), axis=1)
        st.dataframe(df, use_container_width=True)

# 2. Ιστορικό Παραγγελιών
elif menu_choice == "🛒 Ιστορικό Παραγγελιών":
    st.title("🛒 Ιστορικό Παραγγελιών")
    df_orders = pd.DataFrame(st.session_state.orders_db)
    st.dataframe(df_orders, use_container_width=True)

# 3. Ανάλυση Αγοράς
elif menu_choice == "🔍 Ανάλυση Αγοράς (Ρίσκο)":
    st.title("🔍 Ανάλυση Αγοράς")
    # Υποθετικά δεδομένα αγοράς
    market_data = [
        {'προϊόν': 'Αντάπτορας USB-C', 'χαμηλότερη τιμή': 4.5, 'τιμή προμηθευτή': 5.2, 'κριτικές': 120, 'αξιολόγηση': 4.2},
        {'προϊόν': 'Bluetooth ηχεία', 'χαμηλότερη τιμή': 15.0, 'τιμή προμηθευτή': 18.0, 'κριτικές': 90, 'αξιολόγηση': 4.0},
        # πρόσθετα δεδομένα
    ]
    for item in market_data:
        κέρδος_pct = (1 - item['τιμή προμηθευτή'] / item['χαμηλότερη τιμή']) * 100
        st.write(f"{item['προϊόν']}: Κέρδος {κέρδος_pct:.2f}%, Κριτικές {item['κριτικές']}, Αξιολόγηση {item['αξιολόγηση']}")

# 4. Πωλήσεις ανά Κατηγορία
elif menu_choice == "📈 Πωλήσεις ανά Κατηγορία":
    st.title("Πωλήσεις ανά Κατηγορία")
    # Υποθετικά δεδομένα
    sales = [
        {'κατηγορία': '🎧 Ήχος', 'προϊόντα': 10, 'πωλήσεις': 1500},
        {'κατηγορία': '📱 Βάσεις', 'προϊόντα': 5, 'πωλήσεις': 800},
        {'κατηγορία': '🛡️ Ασφάλεια', 'προϊόντα': 3, 'πωλήσεις': 900}
    ]
    for s in sales:
        st.subheader(s['κατηγορία'])
        st.write(f"Προϊόντα: {s['προϊόντα']}")
        st.write(f"Συνολικές Πωλήσεις: {s['πωλήσεις']} €")

# 5. Προϊόντα και Εκπτώσεις
elif menu_choice == "🎁 Προϊόντα & Εκπτώσεις":
    st.title("Προϊόντα & Εκπτώσεις")
    # Φόρμα επιλογής προϊόντος
    product_names = [prod.find('name').text for prod in ET.fromstring(xml_data).findall('product')]
    selected_product = st.selectbox("Επιλογή Προϊόντος", product_names)
    discount_pct = st.slider("Ποσοστό Έκπτωσης (%)", 0, 50, 10)
    if st.button("Εφαρμογή Εκπτώσεων"):
        # Βρες το προϊόν και ενημέρωσε την τιμή
        for prod in ET.fromstring(xml_data).findall('product'):
            if prod.find('name').text == selected_product:
                original_price = float(prod.find('market_min_price').text)
                new_price = original_price * (1 - discount_pct/100)
                st.info(f"Νέα τιμή {selected_product}: {new_price:.2f} € μετά από {discount_pct}% έκπτωση")
                break
