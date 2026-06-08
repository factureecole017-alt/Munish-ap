import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import io
import base64
import os

# Chemin absolu vers le logo — fonctionne sur Replit ET Streamlit Cloud
LOGO_PATH = os.path.join(os.path.dirname(__file__), "logo.png")

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Mun'ish - Gestion de Stand", page_icon="🥤", layout="centered"
)

# --- STYLE PERSONNALISÉ ---
st.markdown(
    """
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
    .recu-box {
        border: 2px solid #FF9800;
        border-radius: 10px;
        padding: 15px;
        background-color: #fff8f0;
        margin-top: 10px;
    }
    .releve-box {
        border: 1px solid #0277BD;
        border-radius: 10px;
        padding: 15px;
        background-color: #e8f4fd;
        margin-top: 10px;
    }
    .del-btn > button {
        background-color: #e53935 !important;
        height: 2.2em !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- SESSION STATE ---
if "vente_key" not in st.session_state:
    st.session_state.vente_key = 0
if "last_recu" not in st.session_state:
    st.session_state.last_recu = None
if "show_balloons" not in st.session_state:
    st.session_state.show_balloons = False

# --- CONFIGURATION DU LIEN GOOGLE SHEET ---
URL_MUNISH = "https://docs.google.com/spreadsheets/d/1tQ9DbooBOdizjOhke2xJCZFNPcuIE0eWYblD3dpRllM/edit"

# --- CONNEXION GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- LOGO ET TITRE ---
col_l, col_t = st.columns([1, 3])
with col_l:
    try:
        st.image(LOGO_PATH, width=100)
    except Exception:
        st.markdown("# 🥤")

with col_t:
    st.markdown("<h1>MUN'ISH STAND</h1>", unsafe_allow_html=True)
    st.caption("Votre pause rafraîchissante 🧃")

# --- MENU DU STAND ---
MENU = {
    "Smoothies (1500f)": {
        "Banane+Raisin": 1500,
        "Papaye+Banane": 1500,
        "Ananas+Papaye+Raisin+Miel": 1500,
    },
    "Le PEP'S (1000f)": {
        "Ener": 1000,import streamlit as st
        from streamlit_gsheets import GSheetsConnection
        import pandas as pd
        from datetime import datetime, timedelta
        import io
        import base64

        # --- CONFIGURATION DE LA PAGE ---
        st.set_page_config(page_title="Mun'ish - Gestion de Stand", page_icon="🥤", layout="centered")

        # --- STYLE PERSONNALISÉ ---
        st.markdown("""
            <style>
            .main { background-color: #fdfefe; }
            .stButton>button {
                width: 100%;
                border-radius: 15px;
                backg'<img src="data:image/png;base64,' + logo_b64 + '" '
        'style="width:90px;display:block;margin:0 auto 8px auto;">'
        if logo_b64 else ""
    )
    # CSS séparé du f-string pour compatibilité Python 3.14
    css = (
        "<style>"
        "body { font-family: Arial, sans-serif; max-width: 320px; margin: auto; padding: 20px; }"
        ".header { text-align: center; border-bottom: 2px dashed #FF9800; padding-bottom: 10px; }"
        "h2 { color: #0277BD; margin: 4px 0; }"
        ".ligne { display: flex; justify-content: space-between; padding: 4px 0; }"
        ".total { font-weight: bold; font-size: 1.1em; border-top: 1px solid #ccc; margin-top: 8px; padding-top: 6px; }"
        ".footer { text-align: center; font-size: 0.8em; color: #888; margin-top: 12px; border-top: 1px dashed #ccc; padding-top: 8px; }"
        "</style>"
    )
    return (
        "<html><head><meta charset=\"utf-8\">" + css + "</head><body>"
        "<div class=\"header\">"
        + logo_html +
        "<h2>MUN'ISH STAND</h2>"
        "<small>Votre pause rafraîchissante</small><br>"
        f"<small>{date_str}</small>"
        "</div><br>"
        f"<div class=\"ligne\"><span>Client :</span><span><b>{nom_c}</b></span></div>"
        f"<div class=\"ligne\"><span>Article :</span><span>{art}</span></div>"
        f"<div class=\"ligne\"><span>Qté :</span><span>{qte}</span></div>"
        f"<div class=\"ligne\"><span>Prix unit. :</span><span>{prix_u} FCFA</span></div>"
        f"<div class=\"ligne total\"><span>TOTAL :</span><span>{total} FCFA</span></div>"
        f"<div class=\"ligne\"><span>Mode :</span><span>{mode}</span></div>"
        f"<div class=\"ligne\"><span>Reçu :</span><span>{recu} FCFA</span></div>"
        f"<div class=\"ligne\"><span>Rendu :</span><span>{rendu} FCFA</span></div>"
        "<div class=\"footer\">Merci pour votre commande ! 🧡<br>À bientôt chez Mun'ish</div>"
        "</body></html>"
    )

def generer_releve_html(semaine_label, df_v_sem, df_d_sem, t_v, t_d, solde):
    logo_b64 = get_logo_base64()
    logo_html = (
        '<img src="data:image/png;base64,' + logo_b64 + '" '
        'style="width:80px;display:block;margin:0 auto 8px auto;">'
        if logo_b64 else ""
    )
    lignes_v = "".join(
        "<tr><td>" + str(r.get("Date", "")) + "</td><td>" + str(r.get("Client", "")) + "</td>"
        "<td>" + str(r.get("Article", "")) + "</td><td>" + str(r.get("Quantité", "")) + "</td>"
        "<td>" + str(r.get("Total", "")) + " F</td></tr>"
        for _, r in df_v_sem.iterrows()
    )
    lignes_d = "".join(
        "<tr><td>" + str(r.get("Date", "")) + "</td><td>" + str(r.get("Désignation", "")) + "</td>"
        "<td>" + str(r.get("Montant", "")) + " F</td></tr>"
        for _, r in df_d_sem.iterrows()
    )
    ventes_vides = "<tr><td colspan=\"5\" style=\"text-align:center\">Aucune vente</td></tr>"
    depenses_vides = "<tr><td colspan=\"3\" style=\"text-align:center\">Aucune dépense</td></tr>"
    # CSS séparé du f-string pour compatibilité Python 3.14
    css = (
        "<style>"
        "body { font-family: Arial; max-width: 700px; margin: auto; padding: 20px; }"
        ".header { text-align: center; border-bottom: 2px solid #0277BD; padding-bottom: 12px; }"
        "h2 { color: #0277BD; } h3 { color: #FF9800; }"
        "table { width: 100%; border-collapse: collapse; margin-bottom: 16px; }"
        "th { background: #0277BD; color: white; padding: 6px; text-align: left; }"
        "td { padding: 5px; border-bottom: 1px solid #eee; }"
        ".bilan { display: flex; gap: 20px; margin: 16px 0; }"
        ".bilan-card { flex:1; text-align:center; padding:10px; border-radius:8px; }"
        ".entrees { background:#e8f5e9; } .sorties { background:#fce4ec; } .solde { background:#e3f2fd; }"
        ".footer { text-align:center; font-size:.8em; color:#888; margin-top:16px; }"
        "</style>"
    )
    date_gen = datetime.now().strftime("%d/%m/%Y à %H:%M")
    return (
        "<html><head><meta charset=\"utf-8\">" + css + "</head><body>"
        "<div class=\"header\">" + logo_html +
        f"<h2>MUN'ISH STAND — Relevé Hebdomadaire</h2><p><b>{semaine_label}</b></p></div>"
        "<div class=\"bilan\">"
        f"<div class=\"bilan-card entrees\"><b>Entrées</b><br><big>{t_v} FCFA</big></div>"
        f"<div class=\"bilan-card sorties\"><b>Sorties</b><br><big>{t_d} FCFA</big></div>"
        f"<div class=\"bilan-card solde\"><b>Solde</b><br><big>{solde} FCFA</big></div>"
        "</div>"
        "<h3>📋 Ventes</h3>"
        "<table><tr><th>Date</th><th>Client</th><th>Article</th><th>Qté</th><th>Total</th></tr>"
        + (lignes_v or ventes_vides) +
        "</table>"
        "<h3>💸 Dépenses</h3>"
        "<table><tr><th>Date</th><th>Désignation</th><th>Montant</th></tr>"
        + (lignes_d or depenses_vides) +
        "</table>"
        f"<div class=\"footer\">Relevé généré le {date_gen} — Mun'ish Stand</div>"
        "</body></html>"
    )


# ============================================================
# ONGLETS
# ============================================================
tabs = st.tabs(["🛒 Caisse", "💸 Dépenses", "📝 Dettes", "📅 Relevé Semaine", "📊 Bilan"])


# ============================================================
# ONGLET 1 : CAISSE
# ============================================================
with tabs[0]:

    # Ballons une seule fois après une vente
    if st.session_state.show_balloons:
        st.balloons()
        st.session_state.show_balloons = False

    # Reçu de la dernière vente
    if st.session_state.last_recu:
        r = st.session_state.last_recu
        st.success("✅ Vente enregistrée avec succès !")
        st.markdown("---")
        st.markdown("#### 🧾 Reçu")
        col_logo_recu, col_info_recu = st.columns([1, 3])
        with col_logo_recu:
            try:
                st.image(LOGO_PATH, width=80)
            except Exception:
                st.write("🥤")
        with col_info_recu:
            st.markdown(f"**MUN'ISH STAND**  \n*Votre pause rafraîchissante*  \n{r['date_str']}")
        st.markdown(f"""
| | |
|---|---|
| **Client** | {r['client']} |
| **Article** | {r['art']} |
| **Quantité** | {r['qte']} |
| **Prix unitaire** | {r['prix_u']} FCFA |
| **TOTAL** | **{r['total']} FCFA** |
| **Mode** | {r['mode']} |
| **Reçu** | {r['recu']} FCFA |
| **Rendu** | {r['rendu']} FCFA |
""")
        s
            """

        # --- HELPER : relevé HTML ---
        def generer_releve_html(semaine_label, df_v_sem, df_d_sem, t_v, t_d, solde):
            logo_b64 = get_logo_base64()
            logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="width:80px;display:block;margin:0 auto 8px auto;">' if logo_b64 else ""
            lignes_v = "".join(f"<tr><td>{r.get('Date','')}</td><td>{r.get('Client','')}</td><td>{r.get('Article','')}</td><td>{r.get('Quantité','')}</td><td>{r.get('Total','')} F</td></tr>" for _, r in df_v_sem.iterrows())
            lignes_d = "".join(f"<tr><td>{r.get('Date','')}</td><td>{r.get('Désignation','')}</td><td>{r.get('Montant','')} F</td></tr>" for _, r in df_d_sem.iterrows())
run(     <html><head><meta charset="utf-8">
            <style>
              body {{ font-family: Arial; max-width: 700px; margin: auto; padding: 20px; }}
              .header {{ text-align: center; border-bottom: 2px solid #0277BD; padding-bottom: 12px; }}
              h2 {{ color: #0277BD; }} h3 {{ color: #FF9800; }}
              table {{ width: 100%; border-collapse: collapse; margin-bottom: 16px; }}
              th {{ background: #0277BD; color: white; padding: 6px; text-align: left; }}
              td {{ padding: 5px; border-bottom: 1px solid #eee; }}
              .bilan {{ display: flex; gap: 20px; margin: 16px 0; }}
              .bilan-card {{ flex:1; text-align:center; padding:10px; border-radius:8px; }}
              .entrees {{ background:#e8f5e9; }} .sorties {{ background:#fce4ec; }} .solde {{ background:#e3f2fd; }}
              .footer {{ text-align:center; font-size:.8em; color:#888; margin-top:16px; }}
            </style></head><body>
            <div class="header">{logo_html}<h2>MUN'ISH STAND — Relevé Hebdomadaire</h2><p><b>{semaine_label}</b></p></div>
            <div class="bilan">
              <div class="bilan-card entrees"><b>Entrées</b><br><big>{t_v} FCFA</big></div>
              <div class="bilan-card sorties"><b>Sorties</b><br><big>{t_d} FCFA</big></div>
              <div class="bilan-card solde"><b>Solde</b><br><big>{solde} FCFA</big></div>
            </div>
            <h3>📋 Ventes</h3>
            <table><tr><th>Date</th><th>Client</th><th>Article</th><th>Qté</th><th>Total</th></tr>
            {lignes_v or '<tr><td colspan="5" style="text-align:center">Aucune vente</td></tr>'}</table>
            <h3>💸 Dépenses</h3>
            <table><tr><th>Date</th><th>Désignation</th><th>Montant</th></tr>
            {lignes_d or '<tr><td colspan="3" style="text-align:center">Aucune dépense</td></tr>'}</table>
            <div class="footer">Relevé généré le {datetime.now().strftime("%d/%m/%Y à %H:%M")} — Mun'ish Stand</div>
            </body></html>
           