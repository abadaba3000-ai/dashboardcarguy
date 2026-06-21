import streamlit as str_app
import pandas as pd
import xml.etree.ElementTree as ET
import pymysql

# 1. ΓΕΝΙΚΗ ΡΥΘΜΙΣΗ ΣΕΛΙΔΑΣ
str_app.set_page_config(layout="wide", page_title="Carguy.gr ERP & Bridge")

# ==================================================
# 🔑 ΣΥΝΔΕΣΗ ΜΕ ΤΗ ΒΑΣΗ ΔΕΔΟΜΕΝΩΝ ΤΟΥ OPENCART
# ==================================================
# Αντικατάστησε τα στοιχεία με αυτά του server σου (cPanel / MySQL)
def get_db_connection():
    return pymysql.connect(
        host=str_app.secrets["mysql"]["host"],       # π.χ. "localhost" ή την IP του server
        user=str_app.secrets["mysql"]["user"],       # το όνομα χρήστη της βάσης
        password=str_app.secrets["mysql"]["password"], # τον κωδικό της βάσης
        database=str_app.secrets["mysql"]["db"],     # το όνομα της βάσης του OpenCart (π.χ. oc_shop)
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

# 2. ΣΥΣΤΗΜΑ ΑΣΦΑΛΕΙΑΣ (LOGIN)
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

# ==================================================
# 🌐 ΔΕΔΟΜΕΝΑ XML ΠΡΟΜΗΘΕΥΤΗ (ΓΕΦΥΡΑ)
# ==================================================
# Εδώ βάζεις το πραγματικό URL του XML του προμηθευτή σου
XML_URL = "https://www.supplier-domain.com/feed.xml"

def fetch_supplier_xml():
    try:
        # Στην παραγωγή θα χρησιμοποιούσες: root = ET.parse(urllib.request.urlopen(XML_URL)).getroot()
        # Για το παράδειγμα, κρατάμε τη δομή του στατικού XML
        xml_mock = """<?xml version="1.0" encoding="UTF-8"?>
        <products>
            <product><id>CAR-001</id><barcode>5201234567890</barcode><name>FM Transmitter Bluetooth 5.0 Dual USB</name><category>🎧 Ήχος &amp; Επικοινωνία</category><wholesale_price>5.20</wholesale_price><market_min_price>12.90</market_min_price><stock_xml>45</stock_xml><reviews>142</reviews><negative_reviews_pct>28</negative_reviews_pct></product>
            <product><id>CAR-002</id><barcode>5209876543210</barcode><name>Μαγνητική Βάση Αεραγωγού MagSafe 15W</name><category>📱 Βάσεις Στήριξης</category><wholesale_price>7.50</wholesale_price><market_min_price>18.50</market_min_price><stock_xml>12</stock_xml><reviews>85</reviews><negative_reviews_pct>5</negative_reviews_pct></product>
            <product><id>CAR-003</id><barcode>5205556667770</barcode><name>Κάμερα Dashcam 4K WiFi Καταγραφικό</name><category>🛡️ Ασφάλεια &amp; Υποβοήθηση</category><wholesale_price>28.00</wholesale_price><market_min_price>59.00</market_min_price><stock_xml>0</stock_xml><reviews>310</reviews><negative_reviews_pct>42</negative_reviews_pct></product>
            <product><id>CAR-004</id><barcode>5208889991110</barcode><name>Έξυπνος Φορτιστής Αυτοκινήτου USB-C 65W</name><category>⚡ Φόρτιση &amp; Ισχύς</category><wholesale_price>9.10</wholesale_price><market_min_price>22.00</market_min_price><stock_xml>150</stock_xml><reviews>45</reviews><negative_reviews_pct>12</negative_reviews_pct></product>
        </products>
        """
        return ET.fromstring(xml_mock)
    except Exception as e:
        str_app.error(f"Σφάλμα ανάγνωσης XML: {e}")
        return None

def calculate_eshop_status(my_stock, xml_stock):
    if my_stock > 0: return "🟢 Άμεσα Διαθέσιμο"
    elif my_stock == 0 and xml_stock > 0: return "🟠 Κατόπιν Παραγγελίας"
    else: return "🔴 Εξαντλήθηκε"

# ==================================================
# 🗂️ NAVIGATION & UI
# ==================================================
str_app.sidebar.title("🚗 Carguy.gr Live Suite")
menu_choice = str_app.sidebar.radio("Επιλογή Ενότητας:", ["📦 Αποθήκη & Γέφυρα OpenCart", "🛒 Παραγγελίες Site", "🔍 Ανάλυση Ρίσκου"])

# --- ΕΝΟΤΗΤΑ 1: ΑΠΟΘΗΚΗ & LIVE ΣΥΓΧΡΟΝΙΣΜΟΣ ---
if menu_choice == "📦 Αποθήκη & Γέφυρα OpenCart":
    str_app.title("📊 Διαχείριση Αποθήκης & Σύνδεση OpenCart")
    col_scan, col_table = str_app.columns([1, 3])
    
    with col_scan:
        str_app.subheader("🔫 Σάρωση Barcode")
        with str_app.form("barcode_form", clear_on_submit=True):
            scanned_barcode = str_app.text_input("Χτύπα το Barcode:")
            qty = str_app.number_input("Ποσότητα Παραλαβής:", min_value=1, value=1)
            
            if str_app.form_submit_button("⚡ Ενημέρωση OpenCart"):
                scanned_barcode = scanned_barcode.strip()
                connection = get_db_connection()
                try:
                    with connection.cursor() as cursor:
                        # 1. Έλεγχος αν το προϊόν υπάρχει ήδη στο OpenCart με βάση το SKU/Barcode
                        sql_check = "SELECT product_id, quantity FROM oc_product WHERE sku = %s"
                        cursor.execute(sql_check, (scanned_barcode,))
                        result = cursor.fetchone()
                        
                        if result:
                            # Αν υπάρχει, προσθέτουμε το νέο στοκ στο OpenCart
                            new_qty = result['quantity'] + qty
                            sql_update = "UPDATE oc_product SET quantity = %s WHERE product_id = %s"
                            cursor.execute(sql_update, (new_qty, result['product_id']))
                            connection.commit()
                            str_app.success(f"✅ Το στοκ ενημερώθηκε live στο OpenCart! Νέο Σύνολο: {new_qty}")
                        else:
                            # Αν δεν υπάρχει, ψάχνουμε το XML του προμηθευτή για να το εισάγουμε
                            root = fetch_supplier_xml()
                            found_in_xml = False
                            if root is not None:
                                for prod in root.findall('product'):
                                    if prod.find('barcode').text == scanned_barcode:
                                        # Εισαγωγή στον πίνακα oc_product του OpenCart
                                        sql_insert = """INSERT INTO oc_product 
                                        (model, sku, quantity, price, wholesale_price, status, date_added) 
                                        VALUES (%s, %s, %s, %s, %s, 1, NOW())"""
                                        cursor.execute(sql_insert, (
                                            prod.find('id').text, scanned_barcode, qty, 
                                            float(prod.find('market_min_price').text), float(prod.find('wholesale_price').text)
                                        ))
                                        connection.commit()
                                        str_app.success("🎉 Νέο προϊόν εισήχθη επιτυχώς στη βάση του OpenCart!")
                                        found_in_xml = True
                                        break
                                if not found_in_xml:
                                    str_app.error("❌ Το Barcode δεν βρέθηκε ούτε στο OpenCart ούτε στο XML.")
                finally:
                    connection.close()
                str_app.rerun()

    with col_table:
        str_app.subheader("📦 Live Προϊόντα από τη Βάση του OpenCart")
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                # Τραβάμε τα δεδομένα απευθείας από τους πίνακες του OpenCart
                sql_select = """SELECT p.product_id AS ID, p.sku AS Barcode, pd.name AS Όνομα, 
                               p.wholesale_price AS `Χονδρική (€)`, p.price AS `Λιανική (€)`, p.quantity AS `Δικό μου Stock`
                               FROM oc_product p 
                               LEFT JOIN oc_product_description pd ON (p.product_id = pd.product_id)
                               WHERE pd.language_id = 1""" # 1 συνήθως είναι η κύρια γλώσσα
                cursor.execute(sql_select)
                db_data = cursor.fetchall()
                
                if db_data:
                    df = pd.DataFrame(db_data)
                    # Υπολογισμός κέρδους live
                    df['Καθαρό Κέρδος (€)'] = df['Λιανική (€)'] - df['Χονδρική (€)']
                    str_app.dataframe(df, use_container_width=True)
                else:
                    str_app.info("Δεν βρέθηκαν προϊόντα στη βάση δεδομένων.")
        finally:
            connection.close()

# --- ΕΝΟΤΗΤΑ 2: LIVE ΠΑΡΑΓΓΕΛΙΕΣ ΑΠΟ OPENCART ---
elif menu_choice == "🛒 Παραγγελίες Site":
    str_app.title("🛒 Ζωντανές Παραγγελίες από το E-shop")
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Διαβάζουμε τον πίνακα παραγγελιών του OpenCart (oc_order)
            sql_orders = """SELECT order_id AS `ID Παραγγελίας`, firstname AS `Όνομα`, lastname AS `Επώνυμο`, 
                            total AS `Σύνολο (€)`, order_status_id AS `Status ID`, date_added AS `Ημερομηνία` 
                            FROM `oc_order` ORDER BY order_id DESC LIMIT 50"""
            cursor.execute(sql_orders)
            orders_data = cursor.fetchall()
            
            if orders_data:
                orders_df = pd.DataFrame(orders_data)
                str_app.dataframe(orders_df, use_container_width=True)
            else:
                str_app.info("Δεν υπάρχουν καταχωρημένες παραγγελίες.")
    finally:
        connection.close()

# --- ΕΝΟΤΗΤΑ 3: ΑΝΑΛΥΣΗ ΡΙΣΚΟΥ ---
elif menu_choice == "🔍 Ανάλυση Ρίσκου":
    str_app.title("🔍 Στατιστικά & Ανάλυση Ελαττωματικών / Παραπόνων")
    # Εδώ συνδέεις τα δεδομένα των κριτικών από το XML ή από κάποιο custom table
    root = fetch_supplier_xml()
    if root is not None:
        parsed_data = []
        for prod in root.findall('product'):
            parsed_data.append({
                'ID': prod.find('id').text,
                'Όνομα': prod.find('name').text,
                'Αρνητικές Κριτικές (%)': int(prod.find('negative_reviews_pct').text)
            })
        df = pd.DataFrame(parsed_data)
        str_app.dataframe(df, use_container_width=True)
        
        for _, r in df.iterrows():
            if r['Αρνητικές Κριτικές (%)'] >= 25:
                str_app.error(f"🔴 ΥΨΗΛΟ ΡΙΣΚΟ: {r['Όνομα']} ({r['Αρνητικές Κριτικές (%)']}% παράπονα)")
