import streamlit as str_app
import pandas as pd
import xml.etree.ElementTree as ET

# 1. ΓΕΝΙΚΗ ΡΥΘΜΙΣΗ ΣΕΛΙΔΑΣ (Wide Mode για να χωράνε όλες οι στήλες)
str_app.set_page_config(layout="wide")

# ==================================================
# 💾 ΠΛΗΡΗΣ ΒΑΣΗ ΔΕΔΟΜΕΝΩΝ (Με όλη την αυξημένη πληροφορία)
# ==================================================
xml_data_supplier = """<?xml version="1.0" encoding="UTF-8"?>
<products>
    <product>
        <id>CAR-001</id>
        <barcode>5201234567890</barcode>
        <name>FM Transmitter Bluetooth 5.0 Dual USB</name>
        <category>🎧 Ήχος &amp; Επικοινωνία</category>
        <wholesale_price>5.20</wholesale_price>
        <market_min_price>12.90</market_min_price>
        <stock_xml>45</stock_xml>
        <reviews>142</reviews>
        <negative_reviews_pct>28</negative_reviews_pct>
    </product>
    <product>
        <id>CAR-002</id>
        <barcode>5209876543210</barcode>
        <name>Μαγνητική Βάση Αεραγωγού MagSafe 15W</name>
        <category>📱 Βάσεις Στήριξης</category>
        <wholesale_price>7.50</wholesale_price>
        <market_min_price>18.50</market_min_price>
        <stock_xml>12</stock_xml>
        <reviews>85</reviews>
        <negative_reviews_pct>5</negative_reviews_pct>
    </product>
    <product>
        <id>CAR-003</id>
        <barcode>5205556667770</barcode>
        <name>Κάμερα Dashcam 4K WiFi Καταγραφικό</name>
        <category>🛡️ Ασφάλεια &amp; Υποβοήθηση</category>
        <wholesale_price>28.00</wholesale_price>
        <market_min_price>59.00</market_min_price>
        <stock_xml>0</stock_xml>
        <reviews>310</reviews>
        <negative_reviews_pct>42</negative_reviews_pct>
    </product>
    <product>
        <id>CAR-004</id>
        <barcode>5208889991110</barcode>
        <name>Έξυπνος Φορτιστής Αυτοκινήτου USB-C 65W</name>
        <category>⚡ Φόρτιση &amp; Ισχύς</category>
        <wholesale_price>9.10</wholesale_price>
        <market_min_price>22.00</market_min_price>
        <stock_xml>150</stock_xml>
        <reviews>45</reviews>
        <negative_reviews_pct>12</negative_reviews_pct>
    </product>
</products>
"""

# Αρχικοποίηση της δικής μας Αποθήκης με ΟΛΕΣ τις στήλες
if 'complete_inventory' not in str_app.session_state:
    str_app.session_state.complete_inventory = [
        {
            'ID': 'CAR-001', 'Barcode': '5201234567890', 'Όνομα': 'FM Transmitter Bluetooth 5.0 Dual USB', 
            'Κατηγορία': '🎧 Ήχος & Επικοινωνία', 'Χονδρική (€)': 5.20, 'Λιανική Αγοράς (€)': 12.90, 
            'Stock XML': 45, 'Δικό μου Stock': 5, 'Αριθμός Κριτικών': 142, 'Αρνητικές Κριτικές (%)': 28
        },
        {
            'ID': 'CAR-002', 'Barcode': '5209876543210', 'Όνομα': 'Μαγνητική Βάση Αεραγωγού MagSafe 15W', 
            'Κατηγορία': '📱 Βάσεις Στήριξης', 'Χονδρική (€)': 7.50, 'Λιανική Αγοράς (€)': 18.50, 
            'Stock XML': 12, 'Δικό μου Stock': 0, 'Αριθμός Κριτικών': 85, 'Αρνητικές Κριτικές (%)': 5
        }
    ]

if 'orders_db' not in str_app.session_state:
    str_app.session_state.orders_db = [
        {'ID Παραγγελίας': '#1001', 'Πελάτης': 'Γιώργος Παπαδόπουλος', 'Προϊόν': 'Μαγνητική Βάση MagSafe 15W', 'Ποσότητα': 1, 'Σύνολο (€)': 18.50, 'Κατάσταση': '📦 Απεστάλη'},
        {'ID Παραγγελίας': '#1002', 'Πελάτης': 'Νίκος Καρράς', 'Προϊόν': 'FM Transmitter Bluetooth 5.0', 'Ποσότητα': 2, 'Σύνολο (€)': 25.80, 'Κατάσταση': '⏳ Σε επεξεργασία'}
    ]

# ==================================================
# ⚙️ ΥΠΟΛΟΓΙΣΜΟΣ ΔΙΑΘΕΣΙΜΟΤΗΤΑΣ ΓΕΦΥΡΑΣ
# ==================================================
def calculate_eshop_status(my_stock, xml_stock):
    if my_stock > 0:
        return "🟢 Άμεσα Διαθέσιμο"
    elif my_stock == 0 and xml_stock > 0:
        return "🟠 Κατόπιν Παραγγελίας"
    else:
        return "🔴 Εξαντλήθηκε"

# ==================================================
# 🗂️ ΑΡΙΣΤΕΡΗ ΣΤΗΛΗ (SIDEBAR NAVIGATION & ΦΙΛΤΡΑ)
# ==================================================
str_app.sidebar.title("🚗 Carguy.gr Suite v2.0")
str_app.sidebar.markdown("---")

menu_choice = str_app.sidebar.radio(
    "Επιλογή Ενότητας:",
    ["📦 Αποθήκη & Γέφυρα (Αυξημένη Πληροφορία)", "🛒 Ιστορικό Παραγγελιών", "🔍 Ανάλυση Αγοράς (Ρίσκο)"]
)

# ==================================================
# 🖥️ ΚΕΝΤΡΙΚΗ ΟΘΟΝΗ
# ==================================================

if menu_choice == "📦 Αποθήκη & Γέφυρα (Αυξημένη Πληροφορία)":
    str_app.title("📊 Κεντρική Αποθήκη & Γέφυρα Δεδομένων")
    str_app.markdown("---")
    
    col_scan, col_table = str_app.columns([1, 3])
    
    with col_scan:
        str_app.subheader("🔫 Σάρωση Barcode")
        with str_app.form("barcode_form", clear_on_submit=True):
            scanned_barcode = str_app.text_input("Χτύπα το Barcode εδώ:")
            qty_received = str_app.number_input("Ποσότητα Παραλαβής:", min_value=1, value=1)
            submit_scan = str_app.form_submit_button("⚡ Καταχώρηση & Συγχρονισμός")
            
            if submit_scan and scanned_barcode:
                scanned_barcode = scanned_barcode.strip()
                already_exists = False
                
                for prod in str_app.session_state.complete_inventory:
                    if prod['Barcode'] == scanned_barcode:
                        prod['Δικό μου Stock'] += qty_received
                        str_app.success(f"Ενημερώθηκε το στοκ ραφιού για: {prod['Όνομα']}")
                        already_exists = True
                        break
                
                if not already_exists:
                    root = ET.fromstring(xml_data_supplier)
                    found_xml = False
                    for prod in root.findall('product'):
                        if prod.find('barcode').text == scanned_barcode:
                            str_app.session_state.complete_inventory.append({
                                'ID': prod.find('id').text,
                                'Barcode': scanned_barcode,
                                'Όνομα': prod.find('name').text,
                                'Κατηγορία': prod.find('category').text,
                                'Χονδρική (€)': float(prod.find('wholesale_price').text),
                                'Λιανική Αγοράς (€)': float(prod.find('market_min_price').text),
                                'Stock XML': int(prod.find('stock_xml').text),
                                'Δικό μου Stock': qty_received,
                                'Αριθμός Κριτικών': int(prod.find('reviews').text),
                                'Αρνητικές Κριτικές (%)': int(prod.find('negative_reviews_pct').text)
                            })
                            str_app.balloons()
                            str_app.success(f"🎉 Νέο προϊόν εισήχθη με πλήρη δεδομένα!")
                            found_xml = True
                            break
                    if not found_xml:
                        str_app.error("Το Barcode δεν βρέθηκε στο XML του προμηθευτή.")
                str_app.rerun()

    with col_table:
        str_app.subheader("📦 Πλήρης Πίνακας Προϊόντων (All-Data View)")
        
        df = pd.DataFrame(str_app.session_state.complete_inventory)
        
        if not df.empty:
            # Υπολογισμοί "live" στηλών
            df['Καθαρό Κέρδος (€)'] = df['Λιανική Αγοράς (€)'] - df['Χονδρική (€)']
            df['Συνολικό Απόθεμα'] = df['Δικό μου Stock'] + df['Stock XML']
            df['Κατάσταση στο Eshop'] = df.apply(
                lambda row: calculate_eshop_status(row['Δικό μου Stock'], row['Stock XML']), axis=1
            )
            
            # Διάταξη στηλών για να βλέπεις τα πάντα με τη μία
            all_cols = [
                'ID', 'Barcode', 'Όνομα', 'Κατηγορία', 
                'Χονδρική (€)', 'Λιανική Αγοράς (€)', 'Καθαρό Κέρδος (€)', 
                'Δικό μου Stock', 'Stock XML', 'Συνολικό Απόθεμα',
                'Αριθμός Κριτικών', 'Αρνητικές Κριτικές (%)', 'Κατάσταση στο Eshop'
            ]
            
            str_app.dataframe(df[all_cols], use_container_width=True)
        else:
            str_app.info("Η αποθήκη είναι άδεια.")

# --- ΕΠΙΛΟΓΗ 2: ΙΣΤΟΡΙΚΟ ΠΑΡΑΓΓΕΛΙΩΝ ---
elif menu_choice == "🛒 Ιστορικό Παραγγελιών":
    str_app.title("🛒 Ιστορικό & Στατιστικά Πωλήσεων")
    str_app.markdown("---")
    orders_df = pd.DataFrame(str_app.session_state.orders_db)
    
    col1, col2 = str_app.columns(2)
    col1.metric("Συνολικές Παραγγελίες", len(orders_df))
    col2.metric("Τζίρος (€)", f"{orders_df['Σύνολο (€)'].sum()} €")
    
    str_app.dataframe(orders_df, use_container_width=True)

# --- ΕΠΙΛΟΓΗ 3: ΑΝΑΛΥΣΗ ΑΓΟΡΑΣ ---
elif menu_choice == "🔍 Ανάλυση Αγοράς (Ρίσκο)":
    str_app.title("🔍 Φίλτρα Κατηγοριών & Ανάλυση Ρίσκου")
    str_app.markdown("---")
    
    df = pd.DataFrame(str_app.session_state.complete_inventory)
    
    if not df.empty:
        # Φίλτρο Κατηγορίας
        selected_cat = str_app.selectbox("Διάλεξε Κατηγορία για Έρευνα:", ['Όλες'] + list(df['Κατηγορία'].unique()))
        
        filtered_df = df if selected_cat == 'Όλες' else df[df['Κατηγορία'] == selected_cat]
        
        str_app.dataframe(filtered_df[['ID', 'Όνομα', 'Αριθμός Κριτικών', 'Αρνητικές Κριτικές (%)']], use_container_width=True)
        
        # Ανάλυση ρίσκου
        str_app.subheader("⚠️ Αξιολόγηση Προϊόντων")
        for _, row in filtered_df.iterrows():
            if row['Αρνητικές Κριτικές (%)'] >= 25:
                str_app.error(f"🔴 ΥΨΗΛΟ ΡΙΣΚΟ: Το προϊόν **{row['Όνομα']}** έχει {row['Αρνητικές Κριτικές (%)']}% παράπονα!")
            else:
                str_app.success(f"🟢 ΑΣΦΑΛΕΣ: Το προϊόν **{row['Όνομα']}** έχει μόνο {row['Αρνητικές Κριτικές (%)']}% παράπονα.")