import streamlit as str_app
import pandas as pd
import xml.etree.ElementTree as ET

# 1. SETUP ΣΕΛΙΔΑΣ
str_app.set_page_config(layout="wide", page_title="Carguy.gr Suite")

# 2. LOGIN (Secrets)
def check_password():
    if "password_correct" in str_app.session_state and str_app.session_state["password_correct"]:
        return True
    str_app.title("🔒 Carguy.gr - Είσοδος στο Σύστημα")
    user = str_app.text_input("Username", key="u")
    pwd = str_app.text_input("Password", type="password", key="p")
    if str_app.button("Είσοδος"):
        if "auth" in str_app.secrets and user == str_app.secrets["auth"]["username"] and pwd == str_app.secrets["auth"]["password"]:
            str_app.session_state["password_correct"] = True
            str_app.rerun()
        else:
            str_app.error("❌ Λάθος στοιχεία!")
    return False

if not check_password(): str_app.stop()

# 3. ΒΑΣΗ ΔΕΔΟΜΕΝΩΝ (XML & SESSION STATE)
xml_data_supplier = """<?xml version="1.0" encoding="UTF-8"?>
<products>
    <product><id>CAR-001</id><barcode>5201234567890</barcode><name>FM Transmitter Bluetooth 5.0 Dual USB</name><category>🎧 Ήχος &amp; Επικοινωνία</category><wholesale_price>5.20</wholesale_price><market_min_price>12.90</market_min_price><stock_xml>45</stock_xml><reviews>142</reviews><negative_reviews_pct>28</negative_reviews_pct></product>
    <product><id>CAR-002</id><barcode>5209876543210</barcode><name>Μαγνητική Βάση Αεραγωγού MagSafe 15W</name><category>📱 Βάσεις Στήριξης</category><wholesale_price>7.50</wholesale_price><market_min_price>18.50</market_min_price><stock_xml>12</stock_xml><reviews>85</reviews><negative_reviews_pct>5</negative_reviews_pct></product>
    <product><id>CAR-003</id><barcode>5205556667770</barcode><name>Κάμερα Dashcam 4K WiFi Καταγραφικό</name><category>🛡️ Ασφάλεια &amp; Υποβοήθηση</category><wholesale_price>28.00</wholesale_price><market_min_price>59.00</market_min_price><stock_xml>0</stock_xml><reviews>310</reviews><negative_reviews_pct>42</negative_reviews_pct></product>
    <product><id>CAR-004</id><barcode>5208889991110</barcode><name>Έξυπνος Φορτιστής Αυτοκινήτου USB-C 65W</name><category>⚡ Φόρτιση &amp; Ισχύς</category><wholesale_price>9.10</wholesale_price><market_min_price>22.00</market_min_price><stock_xml>150</stock_xml><reviews>45</reviews><negative_reviews_pct>12</negative_reviews_pct></product>
</products>
"""

if 'complete_inventory' not in str_app.session_state:
    str_app.session_state.complete_inventory = [
        {'ID': 'CAR-001', 'Barcode': '5201234567890', 'Όνομα': 'FM Transmitter Bluetooth 5.0 Dual USB', 'Κατηγορία': '🎧 Ήχος & Επικοινωνία', 'Χονδρική (€)': 5.20, 'Λιανική Αγοράς (€)': 12.90, 'Stock XML': 45, 'Δικό μου Stock': 5, 'Αριθμός Κριτικών': 142, 'Αρνητικές Κριτικές (%)': 28},
        {'ID': 'CAR-002', 'Barcode': '5209876543210', 'Όνομα': 'Μαγνητική Βάση Αεραγωγού MagSafe 15W', 'Κατηγορία': '📱 Βάσεις Στήριξης', 'Χονδρική (€)': 7.50, 'Λιανική Αγοράς (€)': 18.50, 'Stock XML': 12, 'Δικό μου Stock': 0, 'Αριθμός Κριτικών': 85, 'Αρνητικές Κριτικές (%)': 5}
    ]

if 'orders_db' not in str_app.session_state:
    str_app.session_state.orders_db = [
        {'ID Παραγγελίας': '#1001', 'Πελάτης': 'Γιώργος Παπαδόπουλος', 'Προϊόν': 'Μαγνητική Βάση MagSafe 15W', 'Ποσότητα': 1, 'Σύνολο (€)': 18.50, 'Κατάσταση': '📦 Απεστάλη'},
        {'ID Παραγγελίας': '#1002', 'Πελάτης': 'Νίκος Καρράς', 'Προϊόν': 'FM Transmitter Bluetooth 5.0', 'Ποσότητα': 2, 'Σύνολο (€)': 25.80, 'Κατάσταση': '⏳ Σε επεξεργασία'}
    ]

def calculate_eshop_status(my_stock, xml_stock):
    if my_stock > 0: return "🟢 Άμεσα Διαθέσιμο"
    elif my_stock == 0 and xml_stock > 0: return "🟠 Κατόπιν Παραγγελίας"
    else: return "🔴 Εξαντλήθηκε"

# 4. SIDEBAR & MENU
str_app.sidebar.title("🚗 Carguy.gr Suite v2.0")
menu_choice = str_app.sidebar.radio("Επιλογή Ενότητας:", ["📦 Αποθήκη & Γέφυρα", "🛒 Ιστορικό Παραγγελιών", "🔍 Ανάλυση Αγοράς (Ρίσκο)"])

# 5. ΚΕΝΤΡΙΚΗ ΛΟΓΙΚΗ
if menu_choice == "📦 Αποθήκη & Γέφυρα":
    str_app.title("📊 Κεντρική Αποθήκη & Γέφυρα")
    col_scan, col_table = str_app.columns([1, 3])
    with col_scan:
        with str_app.form("barcode_form", clear_on_submit=True):
            scanned = str_app.text_input("Barcode:")
            qty = str_app.number_input("Ποσότητα:", min_value=1, value=1)
            if str_app.form_submit_button("⚡ Καταχώρηση"):
                found = False
                for prod in str_app.session_state.complete_inventory:
                    if prod['Barcode'] == scanned:
                        prod['Δικό μου Stock'] += qty
                        found = True
                        break
                if not found:
                    root = ET.fromstring(xml_data_supplier)
                    for prod in root.findall('product'):
                        if prod.find('barcode').text == scanned:
                            str_app.session_state.complete_inventory.append({
                                'ID': prod.find('id').text, 'Barcode': scanned, 'Όνομα': prod.find('name').text,
                                'Κατηγορία': prod.find('category').text, 'Χονδρική (€)': float(prod.find('wholesale_price').text),
                                'Λιανική Αγοράς (€)': float(prod.find('market_min_price').text), 'Stock XML': int(prod.find('stock_xml').text),
                                'Δικό μου Stock': qty, 'Αριθμός Κριτικών': int(prod.find('reviews').text), 'Αρνητικές Κριτικές (%)': int(prod.find('negative_reviews_pct').text)
                            })
                            found = True
                            break
                str_app.success("Ενημερώθηκε!") if found else str_app.error("Δεν βρέθηκε.")
                str_app.rerun()
    with col_table:
        df = pd.DataFrame(str_app.session_state.complete_inventory)
        df['Καθαρό Κέρδος (€)'] = df['Λιανική Αγοράς (€)'] - df['Χονδρική (€)']
        df['Κατάσταση στο Eshop'] = df.apply(lambda row: calculate_eshop_status(row['Δικό μου Stock'], row['Stock XML']), axis=1)
        str_app.dataframe(df, use_container_width=True)

elif menu_choice == "🛒 Ιστορικό Παραγγελιών":
    str_app.title("🛒 Ιστορικό Παραγγελιών")
    str_app.dataframe(pd.DataFrame(str_app.session_state.orders_db), use_container_width=True)

elif menu_choice == "🔍 Ανάλυση Αγοράς (Ρίσκο)":
    str_app.title("🔍 Ανάλυση Ρίσκου")
    df = pd.DataFrame(str_app.session_state.complete_inventory)
    cat = str_app.selectbox("Κατηγορία:", ['Όλες'] + list(df['Κατηγορία'].unique()))
    fdf = df if cat == 'Όλες' else df[df['Κατηγορία'] == cat]
    str_app.dataframe(fdf[['ID', 'Όνομα', 'Αρνητικές Κριτικές (%)']], use_container_width=True)
    for _, r in fdf.iterrows():
        if r['Αρνητικές Κριτικές (%)'] >= 25: str_app.error(f"🔴 Ρίσκο: {r['Όνομα']} ({r['Αρνητικές Κριτικές (%)']}% παράπονα)")
        else: str_app.success(f"🟢 Ασφαλές: {r['Όνομα']}")
