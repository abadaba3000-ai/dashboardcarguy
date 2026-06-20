import streamlit as str_app
import pandas as pd
import xml.etree.ElementTree as ET

# ==================================================
# 🔐 ΡΥΘΜΙΣΗ ΑΣΦΑΛΕΙΑΣ (USERNAME & PASSWORD)
# ==================================================
ADMIN_USERNAME = "ADMIN"
ADMIN_PASSWORD = "carguypassword"

def check_password():
    if "password_correct" not in str_app.session_state:
        str_app.title("🔒 Carguy.gr - Είσοδος στο Σύστημα")
        user_input = str_app.text_input("Όνομα Χρήστη (Username)", key="input_user")
        pass_input = str_app.text_input("Κωδικός Πρόσβασης (Password)", type="password", key="input_pass")
        if str_app.button("Είσοδος"):
            if user_input == ADMIN_USERNAME and pass_input == ADMIN_PASSWORD:
                str_app.session_state["password_correct"] = True
                str_app.rerun()
            else:
                str_app.error("❌ Λάθος Όνομα Χρήστη ή Κωδικός!")
        return False
    return True

if not check_password():
    str_app.stop()

# ==================================================
# 🚗 Η ΕΦΑΡΜΟΓΗ ΣΟΥ (ΤΡΕΧΕΙ ΜΟΝΟ ΑΝ ΔΩΘΕΙ Ο ΚΩΔΙΚΟΣ)
# ==================================================
str_app.set_page_config(layout="wide")

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

def calculate_eshop_status(my_stock, xml_stock):
    if my_stock > 0:
        return "🟢 Άμεσα Διαθέσιμο"
    elif my_stock == 0 and xml_stock > 0:
        return "🟠 Κατόπιν Παραγγελίας"
    else:
        return "🔴 Εξαντλήθηκε"

# ==================================================
# 🗂️ SIDEBAR NAVIGATION
# ==================================================
str_app.sidebar.title("🚗 Carguy.gr Suite v3.1")
str_app.sidebar.markdown("---")

menu_choice = str_app.sidebar.radio(
    "Επιλογή Ενότητας:",
    [
        "🔄 Γέφυρα & Σάρωση", 
        "📦 Καθαρός Πίνακας Αποθήκης", 
        "🛒 Ιστορικό Παραγγελιών", 
        "🔍 Ανάλυση Ρίσκου & Κερδοφορίας"
    ]
)

df_global = pd.DataFrame(str_app.session_state.complete_inventory)
if not df_global.empty:
    df_global['Καθαρό Κέρδος (€)'] = df_global['Λιανική Αγοράς (€)'] - df_global['Χονδρική (€)']
    df_global['Ποσοστό Κέρδους (%)'] = ((df_global['Καθαρό Κέρδος (€)'] / df_global['Χονδρική (€)']) * 100).round(1)
    df_global['Συνολικό Απόθεμα'] = df_global['Δικό μου Stock'] + df_global['Stock XML']
    df_global['Κατάσταση στο Eshop'] = df_global.apply(lambda row: calculate_eshop_status(row['Δικό μου Stock'], row['Stock XML']), axis=1)

# --- ΕΝΟΤΗΤΑ 1: ΓΕΦΥΡΑ & ΣΑΡΩΣΗ ---
if menu_choice == "🔄 Γέφυρα & Σάρωση":
    str_app.title("🔄 Γέφυρα Δεδομένων & Καταχώρηση")
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
                            str_app.success(f"🎉 Νέο προϊόν εισήχθη!")
                            found_xml = True
                            break
                    if not found_xml:
                        str_app.error("Το Barcode δεν βρέθηκε στο XML του προμηθευτή.")
                str_app.rerun()

    with col_table:
        str_app.subheader("📊 All-Data Live View")
        if not df_global.empty:
            all_cols = ['ID', 'Barcode', 'Όνομα', 'Κατηγορία', 'Χονδρική (€)', 'Λιανική Αγοράς (€)', 'Καθαρό Κέρδος (€)', 'Δικό μου Stock', 'Stock XML', 'Συνολικό Απόθεμα', 'Κατάσταση στο Eshop']
            str_app.dataframe(df_global[all_cols], use_container_width=True)
        else:
            str_app.info("Η αποθήκη είναι άδεια.")

# --- ΕΝΟΤΗΤΑ 2: ΚΑΘΑΡΟΣ ΠΙΝΑΚΑΣ ΑΠΟΘΗΚΗΣ ---
elif menu_choice == "📦 Καθαρός Πίνακας Αποθήκης":
    str_app.title("📦 Κατάσταση Αποθεμάτων (Υπόλοιπα)")
    str_app.markdown("---")
    str_app.subheader("📋 Λίστα Ειδών με Υπόλοιπο Ραφιού & Υπόλοιπο Προμηθευτή")
    
    if not df_global.empty:
        stock_cols = ['ID', 'Όνομα', 'Δικό μου Stock', 'Stock XML', 'Συνολικό Απόθεμα', 'Κατάσταση στο Eshop']
        # Διορθώθηκε το σφάλμα εδώ αφαιρώντας το background_gradient που δημιουργούσε πρόβλημα συμβατότητας
        str_app.dataframe(df_global[stock_cols], use_container_width=True)
    else:
        str_app.info("Δεν υπάρχουν προϊόντα στην αποθήκη.")

# --- ΕΝΟΤΗΤΑ 3: ΙΣΤΟΡΙΚΟ ΠΑΡΑΓΓΕΛΙΩΝ ---
elif menu_choice == "🛒 Ιστορικό Παραγγελιών":
    str_app.title("🛒 Ιστορικό & Στατιστικά Πωλήσεων")
    str_app.markdown("---")
    orders_df = pd.DataFrame(str_app.session_state.orders_db)
    col1, col2 = str_app.columns(2)
    col1.metric("Συνολικές Παραγγελίες", len(orders_df))
    col2.metric("Τζίρος (€)", f"{orders_df['Σύνολο (€)'].sum()} €")
    str_app.dataframe(orders_df, use_container_width=True)

# --- ΕΝΟΤΗΤΑ 4: ΑΝΑΛΥΣΗ ΡΙΣΚΟΥ & ΚΕΡΔΟΦΟΡΙΑΣ ---
elif menu_choice == "🔍 Ανάλυση Ρίσκου & Κερδοφορίας":
    str_app.title("🔍 Στρατηγική Ανάλυση: Ρίσκο, Κερδοφορία & Προσφορές")
    str_app.markdown("---")
    
    if not df_global.empty:
        selected_cat = str_app.selectbox("Φίλτρο Κατηγορίας:", ['Όλες'] + list(df_global['Κατηγορία'].unique()))
        filtered_df = df_global if selected_cat == 'Όλες' else df_global[df_global['Κατηγορία'] == selected_cat]
        
        str_app.subheader("📈 Πίνακας Κερδοφορίας & Παραπόνων")
        str_app.dataframe(filtered_df[['ID', 'Όνομα', 'Ποσοστό Κέρδους (%)', 'Αρνητικές Κριτικές (%)']], use_container_width=True)
        
        str_app.markdown("---")
        str_app.subheader("💡 Έξυπνες Προτάσεις Προσφορών (Promo Opportunities)")
        
        col_cards = str_app.columns(3)
        card_idx = 0
        
        for _, row in filtered_df.iterrows():
            if row['Δικό μου Stock'] >= 5:
                with col_cards[card_idx % 3]:
                    str_app.info(f"🏷️ **Προσφορά Ξεστοκαρίσματος**\n\nΤο προϊόν **{row['Όνομα']}** έχει {row['Δικό μου Stock']} τμχ στο ράφι. Προτείνεται έκπτωση **10%-15%**.")
                card_idx += 1
            
            if row['Ποσοστό Κέρδους (%)'] >= 100 and row['Αρνητικές Κριτικές (%)'] <= 15:
                with col_cards[card_idx % 3]:
                    str_app.success(f"🔥 **Ευκαιρία για Flash Sale**\n\nΤο προϊόν **{row['Όνομα']}** έχει τεράστιο κέρδος ({row['Ποσοστό Κέρδους (%)']}%) και λίγα παράπονα. Τρέξε ένα -20%!")
                card_idx += 1

        if card_idx == 0:
            str_app.write("Δεν υπάρχουν προτάσεις προσφορών για τα τρέχοντα φίλτρα.")
            
        str_app.markdown("---")
        str_app.subheader("⚠️ Αξιολόγηση Ποιότητας Προϊόντων")
        for _, row in filtered_df.iterrows():
            if row['Αρνητικές Κριτικές (%)'] >= 25:
                str_app.error(f"🔴 ΥΨΗΛΟ ΡΙΣΚΟ: Το προϊόν **{row['Όνομα']}** έχει {row['Αρνητικές Κριτικές (%)']}% παράπονα!")
            else:
                str_app.success(f"🟢 ΑΣΦΑΛΕΣ: Το προϊόν **{row['Όνομα']}** έχει μόνο {row['Αρνητικές Κριτικές (%)']}% παράπονα.")
    else:
        str_app.info("Η αποθήκη είναι άδεια.")
