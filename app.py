import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Configuration de la page
st.set_page_config(page_title="Mun'ish - Gestion de Stand", layout="wide")

# Style personnalisé aux couleurs Mun'ish
st.markdown("""
    <style>
    .main { background-color: #f0faff; }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        background-color: #ff9900;
        color: white;
        font-weight: bold;
    }
    h1, h2, h3 { color: #0077b6; }
    </style>
    """, unsafe_allow_html=True)

# Initialisation des fichiers de stockage CSV
FILES = {
    'ventes': 'ventes.csv',
    'depenses': 'depenses.csv',
    'dettes': 'dettes.csv'
}

for key, file in FILES.items():
    if not os.path.exists(file):
        if key == 'ventes':
            df = pd.DataFrame(columns=['Date', 'Client', 'Article', 'Quantité', 'Total', 'Mode', 'Reçu', 'Rendu'])
        elif key == 'depenses':
            df = pd.DataFrame(columns=['Date', 'Désignation', 'Montant'])
        elif key == 'dettes':
            df = pd.DataFrame(columns=['Date', 'Client', 'Article', 'Montant', 'Statut'])
        df.to_csv(file, index=False)

# --- MENU DU STAND ---
MENU = {
    "Smoothies (1500f)": {
        "Banane+Raisin": 1500, "Papaye+Banane": 1500, "Ananas+Papaye+Raisin+Miel": 1500
    },
    "Le PEP'S (1000f)": {
        "Ener": 1000, "Citron+Menthe": 1000, "Citron+Gingembre+Menthe": 1000, "Citron+Bissap+Menthe": 1000
    },
    "Paninis": {
        "Classique (500f)": 500, "Viande (1000f)": 1000, "Poulet/Fromage/Miel (2000f)": 2000, "Box Académicien (1000f)": 1000
    },
    "Spécial (1000f)": {
        "Mun'ish Creamy": 1000, "Noss-Citron": 1000
    }
}

st.title("🥤 Mun'ish - Système de Caisse")

tabs = st.tabs(["🛒 Ventes", "💸 Dépenses", "📝 Dettes", "📊 Bilan"])

# --- ONGLET 1 : VENTES & CAISSE ---
with tabs[0]:
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("Prendre une commande")
        cat = st.selectbox("Catégorie", list(MENU.keys()))
        art = st.selectbox("Article", list(MENU[cat].keys()))
        qte = st.number_input("Quantité", min_value=1, value=1)
        prix_t = MENU[cat][art] * qte
        st.info(f"Total à payer : {prix_t} FCFA")
        
    with col2:
        st.subheader("Paiement")
        nom = st.text_input("Nom Client (optionnel)")
        mode = st.radio("Mode de paiement", ["Espèces", "Orange Money"])
        recu = st.number_input("Somme reçue", min_value=0)
        rendu = recu - prix_t if recu >= prix_t else 0
        if recu > 0:
            st.success(f"Monnaie à rendre : {rendu} FCFA")

    if st.button("Enregistrer la Vente"):
        nouvelle_v = {'Date': datetime.now().strftime("%d/%m/%Y %H:%M"), 'Client': nom if nom else "Anonyme", 
                      'Article': art, 'Quantité': qte, 'Total': prix_t, 'Mode': mode, 'Reçu': recu, 'Rendu': rendu}
        df_v = pd.read_csv(FILES['ventes'])
        df_v = pd.concat([df_v, pd.DataFrame([nouvelle_v])], ignore_index=True)
        df_v.to_csv(FILES['ventes'], index=False)
        st.success("Vente enregistrée avec succès !")
        st.balloons()

# --- ONGLET 2 : DÉPENSES ---
with tabs[1]:
    st.subheader("Achats de la semaine")
    with st.form("depense_form"):
        desig = st.text_input("Désignation (ex: Lait, Sucre)")
        prix_d = st.number_input("Prix d'achat", min_value=0)
        if st.form_submit_button("Ajouter la dépense"):
            df_d = pd.read_csv(FILES['depenses'])
            df_d = pd.concat([df_d, pd.DataFrame([{'Date': datetime.now().strftime("%d/%m/%Y"), 'Désignation': desig, 'Montant': prix_d}])], ignore_index=True)
            df_d.to_csv(FILES['depenses'], index=False)
            st.success("Dépense enregistrée !")

# --- ONGLET 3 : DETTES ---
with tabs[2]:
    st.subheader("Clients qui paieront plus tard")
    col_a, col_b = st.columns(2)
    with col_a:
        d_nom = st.text_input("Nom du client", key="d_nom")
        d_art = st.text_input("Article", key="d_art")
    with col_b:
        d_mont = st.number_input("Montant dû", min_value=0)
        if st.button("Noter la dette"):
            df_det = pd.read_csv(FILES['dettes'])
            df_det = pd.concat([df_det, pd.DataFrame([{'Date': datetime.now().strftime("%d/%m/%Y"), 'Client': d_nom, 'Article': d_art, 'Montant': d_mont, 'Statut': 'NON PAYÉ'}])], ignore_index=True)
            df_det.to_csv(FILES['dettes'], index=False)
            st.warning("Dette ajoutée au registre.")
    
    st.write("---")
    det_view = pd.read_csv(FILES['dettes'])
    st.dataframe(det_view)

# --- ONGLET 4 : BILAN ---
with tabs[3]:
    v_data = pd.read_csv(FILES['ventes'])
    d_data = pd.read_csv(FILES['depenses'])
    
    entrees = v_data['Total'].sum()
    sorties = d_data['Montant'].sum()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Entrées", f"{entrees} F")
    c2.metric("Total Sorties", f"{sorties} F")
    c3.metric("Solde Net", f"{entrees - sorties} F")
    
    st.subheader("Historique des ventes")
    st.dataframe(v_data.sort_values(by='Date', ascending=False))