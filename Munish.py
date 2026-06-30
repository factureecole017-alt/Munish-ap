import os
import io
import base64
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta

# Chemin absolu vers le logo (fonctionne sur Replit ET Streamlit Cloud)
LOGO_PATH = os.path.join(os.path.dirname(__file__), "logo.png")

# ============================================================
# CONFIG PAGE
# ============================================================
st.set_page_config(page_title="Mun'ish - Gestion de Stand", page_icon="🥤", layout="centered")

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
.recu-box {
    border: 2px solid #FF9800;
    border-radius: 10px;
    padding: 15px;
    background-color: #fff8f0;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# SESSION STATE
# ============================================================
if "vente_key" not in st.session_state:
    st.session_state.vente_key = 0
if "last_recu" not in st.session_state:
    st.session_state.last_recu = None
if "show_balloons" not in st.session_state:
    st.session_state.show_balloons = False

# ============================================================
# GOOGLE SHEETS
# ============================================================
URL_MUNISH = "https://docs.google.com/spreadsheets/d/1tQ9DbooBOdizjOhke2xJCZFNPcuIE0eWYblD3dpRllM/edit"
conn = st.connection("gsheets", type=GSheetsConnection)

# ============================================================
# LOGO + TITRE
# ============================================================
col_l, col_t = st.columns([1, 3])
with col_l:
    try:
        st.image(LOGO_PATH, width=100)
    except Exception:
        st.markdown("# 🥤")
with col_t:
    st.markdown("<h1>MUN'ISH STAND</h1>", unsafe_allow_html=True)
    st.caption("Votre pause rafraîchissante 🧃")

# ============================================================
# MENU
# ============================================================
MENU = {
    "Smoothies (1500f)": {
        "Banane+Raisin": 1500,
        "Papaye+Banane": 1500,
        "Ananas+Papaye+Raisin+Miel": 1500,
    },
    "Le PEP'S (1000f)": {
        "Ener": 1000,
        "Citron+Menthe": 1000,
        "Citron+Gingembre+Menthe": 1000,
        "Citron+Bissap+Menthe": 1000,
    },
    "Paninis": {
        "Classique": 500,
        "Viande": 1000,
        "Poulet/Fromage/Miel": 2000,
        "Box Académicien": 1000,
    },
    "Spécial (1000f)": {
        "Mun'ish Creamy": 1000,
        "Noss-Citron": 1000,
    },
}

# ============================================================
# HELPERS
# ============================================================

def get_logo_base64():
    try:
        with open(LOGO_PATH, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return None


def lire(worksheet):
    """Lire depuis Google Sheets (cache 5 s pour éviter le quota)."""
    df = conn.read(spreadsheet=URL_MUNISH, worksheet=worksheet, ttl=5)
    if df is None:
        return pd.DataFrame()
    return df.dropna(how="all").reset_index(drop=True)


def ecrire(worksheet, df):
    """Écrire dans Google Sheets puis vider le cache."""
    conn.update(spreadsheet=URL_MUNISH, worksheet=worksheet, data=df)
    st.cache_data.clear()


def _col(df, name, default=""):
    """Lire une colonne sans KeyError."""
    if name in df.columns:
        return df[name]
    return pd.Series([default] * len(df))


def generer_recu_html(nom_c, art, qte, prix_u, total, mode, recu, rendu, date_str):
    logo_b64 = get_logo_base64()
    logo_html = (
        '<img src="data:image/png;base64,' + logo_b64 + '" '
        'style="width:90px;display:block;margin:0 auto 8px auto;">'
        if logo_b64 else ""
    )
    css = (
        "<style>"
        "body { font-family: Arial, sans-serif; max-width: 320px; margin: auto; padding: 20px; }"
        ".header { text-align: center; border-bottom: 2px dashed #FF9800; padding-bottom: 10px; }"
        "h2 { color: #0277BD; margin: 4px 0; }"
        ".ligne { display: flex; justify-content: space-between; padding: 4px 0; }"
        ".total { font-weight: bold; font-size: 1.1em; border-top: 1px solid #ccc; margin-top: 8px; padding-top: 6px; }"
        ".footer { text-align: center; font-size: 0.8em; color: #888; margin-top: 12px; "
        "border-top: 1px dashed #ccc; padding-top: 8px; }"
        "</style>"
    )
    return (
        "<html><head><meta charset=\"utf-8\">" + css + "</head><body>"
        "<div class=\"header\">" + logo_html +
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
        "<tr><td>" + str(r.get("Date", "")) + "</td>"
        "<td>" + str(r.get("Client", "")) + "</td>"
        "<td>" + str(r.get("Article", "")) + "</td>"
        "<td>" + str(r.get("Quantité", "")) + "</td>"
        "<td>" + str(r.get("Total", "")) + " F</td></tr>"
        for _, r in df_v_sem.iterrows()
    )
    lignes_d = "".join(
        "<tr><td>" + str(r.get("Date", "")) + "</td>"
        "<td>" + str(r.get("Désignation", "")) + "</td>"
        "<td>" + str(r.get("Montant", "")) + " F</td></tr>"
        for _, r in df_d_sem.iterrows()
    )
    vides_v = "<tr><td colspan=\"5\" style=\"text-align:center\">Aucune vente</td></tr>"
    vides_d = "<tr><td colspan=\"3\" style=\"text-align:center\">Aucune dépense</td></tr>"
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
        + (lignes_v or vides_v) +
        "</table>"
        "<h3>💸 Dépenses</h3>"
        "<table><tr><th>Date</th><th>Désignation</th><th>Montant</th></tr>"
        + (lignes_d or vides_d) +
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
        st.caption("Merci pour votre commande ! 🧡 À bientôt chez Mun'ish")
        col_dl, col_close = st.columns(2)
        with col_dl:
            recu_html = generer_recu_html(
                r['client'], r['art'], r['qte'], r['prix_u'],
                r['total'], r['mode'], r['recu'], r['rendu'], r['date_str']
            )
            st.download_button(
                "🖨️ Télécharger / Imprimer le reçu",
                data=recu_html,
                file_name=f"recu_{r['client']}_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
                mime="text/html",
            )
        with col_close:
            if st.button("✖️ Fermer le reçu"):
                st.session_state.last_recu = None
                st.rerun()
        st.markdown("---")

    # Formulaire nouvelle vente — clé dynamique = reset auto après chaque vente
    vk = st.session_state.vente_key
    st.subheader("Nouvelle Vente")
    cat = st.selectbox("Catégorie", list(MENU.keys()), key=f"cat_{vk}")
    art = st.selectbox("Article", list(MENU[cat].keys()), key=f"art_{vk}")
    qte = st.number_input("Quantité", min_value=1, value=1, key=f"qte_{vk}")
    prix_u = MENU[cat][art]
    total = prix_u * qte
    st.markdown(f"### **Total : {total} FCFA**")

    col1, col2 = st.columns(2)
    with col1:
        nom_c = st.text_input("Nom Client", key=f"nom_{vk}")
        mode = st.radio("Mode de paiement", ["Espèces", "Orange Money"], key=f"mode_{vk}")
    with col2:
        recu_val = st.number_input("Somme reçue", min_value=0, step=500, key=f"recu_{vk}")
        rendu = recu_val - total if recu_val >= total else 0
        if recu_val > 0:
            st.warning(f"Rendu : {rendu} FCFA")

    if st.button("✅ Valider la commande"):
        try:
            date_str = datetime.now().strftime("%d/%m/%Y %H:%M")
            client_final = nom_c.strip() if nom_c.strip() else "Anonyme"
            nouvelle_v = pd.DataFrame([{
                "Date": date_str,
                "Client": client_final,
                "Article": art,
                "Quantité": qte,
                "Prix_Unitaire": prix_u,
                "Total": total,
                "Mode": mode,
                "Recu": recu_val,
                "Rendu": rendu,
            }])
            df_v = lire("ventes")
            df_v = pd.concat([df_v, nouvelle_v], ignore_index=True)
            ecrire("ventes", df_v)
            st.session_state.last_recu = {
                "client": client_final, "art": art, "qte": qte,
                "prix_u": prix_u, "total": total, "mode": mode,
                "recu": recu_val, "rendu": rendu, "date_str": date_str,
            }
            st.session_state.vente_key += 1   # reset le formulaire
            st.session_state.show_balloons = True
            st.rerun()
        except Exception as e:
            st.error(f"Erreur lors de l'enregistrement : {e}")

    # Historique du jour
    st.markdown("---")
    st.markdown("#### 📋 Ventes d'aujourd'hui")
    try:
        df_all_v = lire("ventes")
        today_str = datetime.now().strftime("%d/%m/%Y")
        if "Date" not in df_all_v.columns or df_all_v.empty:
            st.info("Aucune vente enregistrée aujourd'hui.")
        else:
            mask = df_all_v["Date"].astype(str).str.startswith(today_str)
            df_today = df_all_v[mask]
            if df_today.empty:
                st.info("Aucune vente enregistrée aujourd'hui.")
            else:
                total_jour = pd.to_numeric(df_today["Total"], errors="coerce").sum()
                st.caption(f"💰 Total du jour : **{int(total_jour)} FCFA** — {len(df_today)} vente(s)")
                for orig_idx, row in df_today.iterrows():
                    col_r, col_d = st.columns([5, 1])
                    with col_r:
                        st.write(
                            f"🕐 `{str(row.get('Date', ''))[-5:]}` — "
                            f"**{row.get('Client', '')}** — "
                            f"{row.get('Article', '')} × {row.get('Quantité', '')} = "
                            f"**{row.get('Total', '')} FCFA**"
                        )
                    with col_d:
                        if st.button("🗑️", key=f"del_v_{orig_idx}", help="Supprimer cette vente"):
                            df_new = df_all_v.drop(index=orig_idx).reset_index(drop=True)
                            ecrire("ventes", df_new)
                            st.rerun()
    except Exception as e:
        st.info(f"Impossible de charger les ventes du jour. ({e})")


# ============================================================
# ONGLET 2 : DÉPENSES
# ============================================================
with tabs[1]:
    st.subheader("Nouvelle Dépense")
    with st.form("form_depense"):
        desig = st.text_input("Désignation")
        montant = st.number_input("Montant (FCFA)", min_value=0)
        if st.form_submit_button("💾 Enregistrer la dépense"):
            if desig.strip():
                try:
                    df_d = lire("depenses")
                    nouvelle_d = pd.DataFrame([{
                        "Date": datetime.now().strftime("%d/%m/%Y"),
                        "Désignation": desig.strip(),
                        "Montant": montant,
                    }])
                    df_d = pd.concat([df_d, nouvelle_d], ignore_index=True)
                    ecrire("depenses", df_d)
                    st.success("✅ Dépense enregistrée !")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur : Vérifiez l'onglet 'depenses'. {e}")
            else:
                st.warning("Veuillez saisir une désignation.")

    st.markdown("---")
    st.markdown("#### 📋 Dépenses du jour")
    try:
        df_all_d = lire("depenses")
        today_str = datetime.now().strftime("%d/%m/%Y")
        if "Date" not in df_all_d.columns or df_all_d.empty:
            st.info("Aucune dépense enregistrée aujourd'hui.")
        else:
            df_dep_today = df_all_d[df_all_d["Date"].astype(str).str.startswith(today_str)]
            if df_dep_today.empty:
                st.info("Aucune dépense enregistrée aujourd'hui.")
            else:
                total_dep = pd.to_numeric(df_dep_today["Montant"], errors="coerce").sum()
                st.caption(f"💸 Total dépenses du jour : **{int(total_dep)} FCFA**")
                for orig_idx, row in df_dep_today.iterrows():
                    col_r, col_d = st.columns([5, 1])
                    with col_r:
                        st.write(f"**{row.get('Désignation', '')}** — {row.get('Montant', '')} FCFA")
                    with col_d:
                        if st.button("🗑️", key=f"del_d_{orig_idx}", help="Supprimer"):
                            df_new_d = df_all_d.drop(index=orig_idx).reset_index(drop=True)
                            ecrire("depenses", df_new_d)
                            st.rerun()
    except Exception as e:
        st.info(f"Impossible de charger les dépenses. ({e})")


# ============================================================
# ONGLET 3 : DETTES
# ============================================================
with tabs[2]:
    st.subheader("Suivi des Dettes")
    with st.expander("➕ Ajouter un impayé"):
        with st.form("form_dette"):
            d_nom = st.text_input("Nom du débiteur")
            d_art = st.text_input("Article / Description")
            d_somme = st.number_input("Montant dû (FCFA)", min_value=0)
            if st.form_submit_button("⚠️ Enregistrer la dette"):
                if d_nom.strip():
                    try:
                        df_det = lire("dettes")
                        nouvelle_det = pd.DataFrame([{
                            "Date": datetime.now().strftime("%d/%m/%Y"),
                            "Client": d_nom.strip(),
                            "Article": d_art.strip(),
                            "Montant": d_somme,
                            "Statut": "NON PAYÉ",
                        }])
                        df_det = pd.concat([df_det, nouvelle_det], ignore_index=True)
                        ecrire("dettes", df_det)
                        st.warning("Dette ajoutée au registre.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erreur : Vérifiez l'onglet 'dettes'. {e}")
                else:
                    st.warning("Veuillez saisir le nom du débiteur.")

    st.markdown("---")
    try:
        df_all_det = lire("dettes")
        if df_all_det.empty:
            st.info("Aucune dette enregistrée. 🎉")
        else:
            if "Statut" not in df_all_det.columns:
                df_all_det["Statut"] = "NON PAYÉ"
            statuts = df_all_det["Statut"].astype(str).str.upper()
            non_payes = df_all_det[statuts != "PAYÉ"]
            payes = df_all_det[statuts == "PAYÉ"]

            total_dettes = pd.to_numeric(
                non_payes["Montant"] if not non_payes.empty else pd.Series(dtype=float),
                errors="coerce"
            ).sum()
            st.markdown(f"#### ⚠️ Impayés — Total dû : **{int(total_dettes)} FCFA**")

            if non_payes.empty:
                st.success("Toutes les dettes sont réglées ! 🎉")
            else:
                for orig_idx, row in non_payes.iterrows():
                    col_info, col_paye, col_supp = st.columns([4, 1, 1])
                    with col_info:
                        st.write(
                            f"📅 {row.get('Date', '')} — **{row.get('Client', '')}** — "
                            f"{row.get('Article', '')} — **{row.get('Montant', '')} FCFA**"
                        )
                    with col_paye:
                        if st.button("✅", key=f"pay_det_{orig_idx}", help="Marquer comme payé"):
                            df_all_det.at[orig_idx, "Statut"] = "PAYÉ"
                            ecrire("dettes", df_all_det)
                            st.rerun()
                    with col_supp:
                        if st.button("🗑️", key=f"del_det_{orig_idx}", help="Supprimer"):
                            df_new_det = df_all_det.drop(index=orig_idx).reset_index(drop=True)
                            ecrire("dettes", df_new_det)
                            st.rerun()

            if not payes.empty:
                with st.expander(f"✅ Dettes réglées ({len(payes)})"):
                    for orig_idx, row in payes.iterrows():
                        col_info, col_supp = st.columns([5, 1])
                        with col_info:
                            st.write(
                                f"~~{row.get('Date', '')} — {row.get('Client', '')} — "
                                f"{row.get('Article', '')} — {row.get('Montant', '')} FCFA~~"
                            )
                        with col_supp:
                            if st.button("🗑️", key=f"del_detP_{orig_idx}", help="Supprimer"):
                                df_new_det = df_all_det.drop(index=orig_idx).reset_index(drop=True)
                                ecrire("dettes", df_new_det)
                                st.rerun()
    except Exception as e:
        st.info(f"Aucune dette à afficher. ({e})")


# ============================================================
# ONGLET 4 : RELEVÉ DE LA SEMAINE
# ============================================================
with tabs[3]:
    st.subheader("📅 Relevé Hebdomadaire")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        date_debut = st.date_input(
            "Date de début",
            value=datetime.now().date() - timedelta(days=datetime.now().weekday()),
        )
    with col_s2:
        date_fin = st.date_input(
            "Date de fin",
            value=datetime.now().date() - timedelta(days=datetime.now().weekday()) + timedelta(days=6),
        )

    semaine_label = f"Semaine du {date_debut.strftime('%d/%m/%Y')} au {date_fin.strftime('%d/%m/%Y')}"
    st.info(f"📆 {semaine_label}")

    if st.button("🔍 Charger le relevé"):
        try:
            df_v_all = lire("ventes")
            df_d_all = lire("depenses")

            def parse_dates(df, col="Date"):
                df = df.copy()
                df[col] = pd.to_datetime(df[col], dayfirst=True, errors="coerce")
                return df

            df_v_all = parse_dates(df_v_all)
            df_d_all = parse_dates(df_d_all)

            debut_dt = pd.Timestamp(date_debut)
            fin_dt = pd.Timestamp(date_fin) + pd.Timedelta(hours=23, minutes=59)

            df_v_sem = df_v_all[(df_v_all["Date"] >= debut_dt) & (df_v_all["Date"] <= fin_dt)].copy()
            df_d_sem = df_d_all[(df_d_all["Date"] >= debut_dt) & (df_d_all["Date"] <= fin_dt)].copy()

            t_v = pd.to_numeric(df_v_sem["Total"], errors="coerce").sum() if not df_v_sem.empty else 0
            t_d = pd.to_numeric(df_d_sem["Montant"], errors="coerce").sum() if not df_d_sem.empty else 0
            solde = t_v - t_d

            st.markdown("### 📊 Bilan de la semaine")
            c1, c2, c3 = st.columns(3)
            c1.metric("💚 Entrées (ventes)", f"{int(t_v)} FCFA")
            c2.metric("🔴 Sorties (dépenses)", f"{int(t_d)} FCFA")
            c3.metric("💰 Solde", f"{int(solde)} FCFA",
                      delta=f"{int(solde)} F",
                      delta_color="normal" if solde >= 0 else "inverse")

            st.markdown("### 🧾 Ventes de la semaine")
            if df_v_sem.empty:
                st.info("Aucune vente sur cette période.")
            else:
                df_v_display = df_v_sem.copy()
                df_v_display["Date"] = df_v_display["Date"].dt.strftime("%d/%m/%Y %H:%M")
                st.dataframe(df_v_display, use_container_width=True)

            st.markdown("### 💸 Dépenses de la semaine")
            if df_d_sem.empty:
                st.info("Aucune dépense sur cette période.")
            else:
                df_d_display = df_d_sem.copy()
                df_d_display["Date"] = df_d_display["Date"].dt.strftime("%d/%m/%Y")
                st.dataframe(df_d_display, use_container_width=True)

            st.markdown("---")
            st.markdown("### ⬇️ Téléchargements")
            col_dl1, col_dl2, col_dl3 = st.columns(3)

            with col_dl1:
                csv_buf = io.StringIO()
                csv_buf.write(f"=== RELEVÉ : {semaine_label} ===\n\nVENTES\n")
                df_v_sem.to_csv(csv_buf, index=False)
                csv_buf.write("\nDÉPENSES\n")
                df_d_sem.to_csv(csv_buf, index=False)
                csv_buf.write(f"\nBILAN\nEntrées,{int(t_v)}\nSorties,{int(t_d)}\nSolde,{int(solde)}\n")
                st.download_button(
                    "📥 CSV", data=csv_buf.getvalue(),
                    file_name=f"releve_{date_debut.strftime('%Y%m%d')}.csv", mime="text/csv"
                )

            with col_dl2:
                df_v_print = df_v_sem.copy()
                df_d_print = df_d_sem.copy()
                if not df_v_print.empty:
                    df_v_print["Date"] = df_v_print["Date"].dt.strftime("%d/%m/%Y %H:%M")
                if not df_d_print.empty:
                    df_d_print["Date"] = df_d_print["Date"].dt.strftime("%d/%m/%Y")
                releve_html = generer_releve_html(
                    semaine_label, df_v_print, df_d_print, int(t_v), int(t_d), int(solde)
                )
                st.download_button(
                    "🖨️ HTML", data=releve_html,
                    file_name=f"releve_{date_debut.strftime('%Y%m%d')}.html", mime="text/html"
                )

            with col_dl3:
                excel_buf = io.BytesIO()
                with pd.ExcelWriter(excel_buf, engine="openpyxl") as writer:
                    if not df_v_sem.empty:
                        df_v_sem.to_excel(writer, sheet_name="Ventes", index=False)
                    if not df_d_sem.empty:
                        df_d_sem.to_excel(writer, sheet_name="Depenses", index=False)
                    pd.DataFrame([{
                        "Entrées (FCFA)": int(t_v),
                        "Sorties (FCFA)": int(t_d),
                        "Solde (FCFA)": int(solde),
                    }]).to_excel(writer, sheet_name="Bilan", index=False)
                st.download_button(
                    "📊 Excel", data=excel_buf.getvalue(),
                    file_name=f"releve_{date_debut.strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        except Exception as e:
            st.error(f"Erreur lors du chargement : {e}")


# ============================================================
# ONGLET 5 : BILAN
# ============================================================
with tabs[4]:
    st.subheader("📊 Bilan Financier Global")
    try:
        df_v = lire("ventes")
        df_d = lire("depenses")
        t_v = pd.to_numeric(df_v["Total"], errors="coerce").sum() if "Total" in df_v.columns else 0
        t_d = pd.to_numeric(df_d["Montant"], errors="coerce").sum() if "Montant" in df_d.columns else 0
        c1, c2, c3 = st.columns(3)
        c1.metric("💚 Entrées", f"{int(t_v)} F")
        c2.metric("🔴 Sorties", f"{int(t_d)} F")
        c3.metric("💰 Solde", f"{int(t_v - t_d)} F")
        st.markdown("**Historique des 20 dernières ventes :**")
        st.dataframe(df_v.tail(20), use_container_width=True)
    except Exception as e:
        st.info(f"Enregistrez une vente et une dépense pour voir le bilan. ({e})")
