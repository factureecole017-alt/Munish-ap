import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Mun'ish - Gestion de Stand", page_icon="🥤", layout="centered")

# --- STYLE PERSONNALISÉ ---
st.markdown("""
    <style>
    .main { background-color: #fdfefe; }
    .stButton>button {
        width: 100%;
        border-radius: 15px;
        background-color: #FF9800;
        color: white;
        font-weight: bold;
        height: 3em;
    }
    .stTabs [data-baseweb="tab"] { font-weight: bold; font-size: 16px; }
    h1 { color: #0277BD; text-align: center; }
    .metric-box { text-align: center; padding: 10px; border-radius: 10px; background-color: #e1f5fe; }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURATION DU LIEN GOOGLE SHEET ---
URL_MUNISH = "https://docs.google.com/spreadsheets/d/1tQ9DbooBOdizjOhke2xJCZFNPcuIE0eWYblD3dpRllM/edit?gid=0#gid=0"

# --- LOGO ET TITRE ---
col_l, col_t = st.columns([1, 3])
with col_l:
    try:
        st.image("logo.png", width=100)
    except:
        st.title("🥤")

with col_t:
    st.markdown("<h1>MUN'ISH STAND</h1>", unsafe_allow_html=True)

# --- CONNEXION GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- MENU DU STAND ---
MENU = {
    "Smoothies (1500f)": {
        "Banane+Raisin": 1500,
        "Papaye+Banane": 1500,
        "Ananas+Papaye+Raisin+Miel": 1500
    },
    "Le PEP'S (1000f)": {
        "Ener": 1000,
        "Citron+Menthe": 1000,
        "Citron+Gingembre+Menthe": 1000,
        "Citron+Bissap+Menthe": 1000
    },
    "Paninis": {
        "Classique": 500,
        "Viande": 1000,
        "Poulet/Fromage/Miel": 2000,
        "Box Académicien": 1000
    },
    "Spécial (1000f)": {
        "Mun'ish Creamy": 1000,
        "Noss-Citron": 1000
    }
}

tabs = st.tabs(["🛒 Caisse", "💸 Dépenses", "📝 Dettes", "📊 Bilan"])

# --- ONGLET 1 : CAISSE ---
with tabs[0]:
    st.subheader("Nouvelle Vente")
    cat = st.selectbox("Catégorie", list(MENU.keys()))
    art = st.selectbox("Article", list(MENU[cat].keys()))
    qte = st.number_input("Quantité", min_value=1, value=1)
    
    prix_u = MENU[cat][art]
    total = prix_u * qte
    
    st.markdown(f"### **Total : {total} FCFA**")
    
    col1, col2 = st.columns(2)
    with col1:
        nom_c = st.text_input("Nom Client")
        mode = st.radio("Mode de paiement", ["Espèces", "Orange Money"])
    with col2:
        recu = st.number_input("Somme reçue", min_value=0, step=500)
        rendu = recu - total if recu >= total else 0
        if recu > 0:
            st.warning(f"Rendu : {rendu} FCFA")

    if st.button("Valider la commande"):
        try:
            nouvelle_v = pd.DataFrame([{
                "Date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Client": nom_c if nom_c else "Anonyme",
                "Article": art,
                "Quantité": qte,
                "Prix_Unitaire": prix_u,
                "Total": total,
                "Mode": mode,
                "Recu": recu,
                "Rendu": rendu
            }])
            df_v = conn.read(spreadsheet=URL_MUNISH, worksheet="ventes")
            df_v = pd.concat([df_v, nouvelle_v], ignore_index=True)
            conn.update(spreadsheet=URL_MUNISH, worksheet="ventes", data=df_v)
            st.success("Vente enregistrée !")
            st.balloons()
        except Exception as e:
            st.error(f"Erreur : Vérifiez que l'onglet 'ventes' existe dans le Sheet. {e}")

# --- ONGLET 2 : DÉPENSES ---
with tabs[1]:
    st.subheader("Nouvelle Dépense")
    with st.form("form_d"):
        desig = st.text_input("Désignation")
        montant = st.number_input("Montant", min_value=0)
        if st.form_submit_button("Enregistrer l'achat"):
            try:
                df_d = conn.read(spreadsheet=URL_MUNISH, worksheet="depenses")
                nouvelle_d = pd.DataFrame([{"Date": datetime.now().strftime("%d/%m/%Y"), "Désignation": desig, "Montant": montant}])
                df_d = pd.concat([df_d, nouvelle_d], ignore_index=True)
                conn.update(spreadsheet=URL_MUNISH, worksheet="depenses", data=df_d)
                st.success("Dépense enregistrée !")
            except Exception as e:
                st.error(f"Erreur : Vérifiez l'onglet 'depenses'. {e}")

# --- ONGLET 3 : DETTES ---
with tabs[2]:
    st.subheader("Suivi des Dettes")
    with st.expander("Ajouter un impayé"):
        d_nom = st.text_input("Nom débiteur")
        d_art = st.text_input("Article")
        d_somme = st.number_input("Montant dû", min_value=0)
        if st.button("Noter la dette"):
            try:
                df_det = conn.read(spreadsheet=URL_MUNISH, worksheet="dettes")
                nouvelle_det = pd.DataFrame([{"Date": datetime.now().strftime("%d/%m/%Y"), "Client": d_nom, "Article": d_art, "Montant": d_somme, "Statut": "NON PAYÉ"}])
                df_det = pd.concat([df_det, nouvelle_det], ignore_index=True)
                conn.update(spreadsheet=URL_MUNISH, worksheet="dettes", data=df_det)
                st.error("Dette ajoutée au registre.")
            except Exception as e:
                st.error(f"Erreur : Vérifiez l'onglet 'dettes'. {e}")

    st.write("---")
    try:
        df_det_display = conn.read(spreadsheet=URL_MUNISH, worksheet="dettes")
        st.dataframe(df_det_display)
    except:
        st.info("Aucune dette à afficher pour le moment.")

# --- ONGLET 4 : BILAN ---
with tabs[3]:
    st.subheader("Bilan Financier")
    try:
        df_v = conn.read(spreadsheet=URL_MUNISH, worksheet="ventes")
        df_d = conn.read(spreadsheet=URL_MUNISH, worksheet="depenses")
        
        t_v = pd.to_numeric(df_v["Total"]).sum()
        t_d = pd.to_numeric(df_d["Montant"]).sum()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Entrées", f"{t_v} F")
        c2.metric("Sorties", f"{t_d} F")
        c3.metric("Solde", f"{t_v - t_d} F")
        
        st.write("**Historique des ventes :**")
        st.dataframe(df_v.tail(20))
    except Exception as e:
        st.info("Enregistrez une vente et une dépense pour voir le bilan.")