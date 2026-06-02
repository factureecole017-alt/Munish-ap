import streamlit as st
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
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURATION DU LIEN GOOGLE SHEET ---
URL_MUNISH = "https://docs.google.com/spreadsheets/d/1tQ9DbooBOdizjOhke2xJCZFNPcuIE0eWYblD3dpRllM/edit"

# --- LOGO ET TITRE ---
col_l, col_t = st.columns([1, 3])
with col_l:
    try:
        st.image("logo.png", width=100)
    except:
        st.title("🥤")

with col_t:
    st.markdown("<h1>MUN'ISH STAND</h1>", unsafe_allow_html=True)
    st.caption("Votre pause rafraîchissante 🧃")

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

# --- HELPER : lire un logo encodé en base64 pour PDF/HTML ---
def get_logo_base64():
    try:
        with open("logo.png", "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None

# --- HELPER : générer le HTML d'un reçu ---
def generer_recu_html(nom_c, art, qte, prix_u, total, mode, recu, rendu, date_str):
    logo_b64 = get_logo_base64()
    logo_html = ""
    if logo_b64:
        logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="width:90px; display:block; margin:0 auto 8px auto;">'

    return f"""
    <html><head><meta charset="utf-8">
    <style>
      body {{ font-family: Arial, sans-serif; max-width: 320px; margin: auto; padding: 20px; }}
      .header {{ text-align: center; border-bottom: 2px dashed #FF9800; padding-bottom: 10px; }}
      h2 {{ color: #0277BD; margin: 4px 0; }}
      .ligne {{ display: flex; justify-content: space-between; padding: 4px 0; }}
      .total {{ font-weight: bold; font-size: 1.1em; border-top: 1px solid #ccc; margin-top: 8px; padding-top: 6px; }}
      .footer {{ text-align: center; font-size: 0.8em; color: #888; margin-top: 12px; border-top: 1px dashed #ccc; padding-top: 8px; }}
    </style></head><body>
    <div class="header">
      {logo_html}
      <h2>MUN'ISH STAND</h2>
      <small>Votre pause rafraîchissante</small><br>
      <small>{date_str}</small>
    </div>
    <br>
    <div class="ligne"><span>Client :</span><span><b>{nom_c}</b></span></div>
    <div class="ligne"><span>Article :</span><span>{art}</span></div>
    <div class="ligne"><span>Qté :</span><span>{qte}</span></div>
    <div class="ligne"><span>Prix unit. :</span><span>{prix_u} FCFA</span></div>
    <div class="ligne total"><span>TOTAL :</span><span>{total} FCFA</span></div>
    <div class="ligne"><span>Mode :</span><span>{mode}</span></div>
    <div class="ligne"><span>Reçu :</span><span>{recu} FCFA</span></div>
    <div class="ligne"><span>Rendu :</span><span>{rendu} FCFA</span></div>
    <div class="footer">Merci pour votre commande ! 🧡<br>À bientôt chez Mun'ish</div>
    </body></html>
    """

# --- HELPER : générer le HTML du relevé hebdomadaire ---
def generer_releve_html(semaine_label, df_v_sem, df_d_sem, t_v, t_d, solde):
    logo_b64 = get_logo_base64()
    logo_html = ""
    if logo_b64:
        logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="width:80px; display:block; margin:0 auto 8px auto;">'

    lignes_v = ""
    for _, r in df_v_sem.iterrows():
        lignes_v += f"<tr><td>{r.get('Date','')}</td><td>{r.get('Client','')}</td><td>{r.get('Article','')}</td><td>{r.get('Quantité','')}</td><td>{r.get('Total','')} F</td></tr>"

    lignes_d = ""
    for _, r in df_d_sem.iterrows():
        lignes_d += f"<tr><td>{r.get('Date','')}</td><td>{r.get('Désignation','')}</td><td>{r.get('Montant','')} F</td></tr>"

    return f"""
    <html><head><meta charset="utf-8">
    <style>
      body {{ font-family: Arial, sans-serif; max-width: 700px; margin: auto; padding: 20px; }}
      .header {{ text-align: center; border-bottom: 2px solid #0277BD; padding-bottom: 12px; }}
      h2 {{ color: #0277BD; }} h3 {{ color: #FF9800; }}
      table {{ width: 100%; border-collapse: collapse; margin-bottom: 16px; }}
      th {{ background-color: #0277BD; color: white; padding: 6px; text-align: left; }}
      td {{ padding: 5px; border-bottom: 1px solid #eee; }}
      .bilan {{ display: flex; gap: 20px; margin: 16px 0; }}
      .bilan-card {{ flex: 1; text-align: center; padding: 10px; border-radius: 8px; }}
      .entrees {{ background: #e8f5e9; }} .sorties {{ background: #fce4ec; }} .solde {{ background: #e3f2fd; }}
      .footer {{ text-align: center; font-size: 0.8em; color: #888; margin-top: 16px; }}
    </style></head><body>
    <div class="header">
      {logo_html}
      <h2>MUN'ISH STAND — Relevé Hebdomadaire</h2>
      <p><b>{semaine_label}</b></p>
    </div>
    <div class="bilan">
      <div class="bilan-card entrees"><b>Entrées</b><br><big>{t_v} FCFA</big></div>
      <div class="bilan-card sorties"><b>Sorties</b><br><big>{t_d} FCFA</big></div>
      <div class="bilan-card solde"><b>Solde</b><br><big>{solde} FCFA</big></div>
    </div>
    <h3>📋 Ventes</h3>
    <table><tr><th>Date</th><th>Client</th><th>Article</th><th>Qté</th><th>Total</th></tr>
    {lignes_v if lignes_v else '<tr><td colspan="5" style="text-align:center">Aucune vente</td></tr>'}
    </table>
    <h3>💸 Dépenses</h3>
    <table><tr><th>Date</th><th>Désignation</th><th>Montant</th></tr>
    {lignes_d if lignes_d else '<tr><td colspan="3" style="text-align:center">Aucune dépense</td></tr>'}
    </table>
    <div class="footer">Relevé généré le {datetime.now().strftime("%d/%m/%Y à %H:%M")} — Mun'ish Stand</div>
    </body></html>
    """

# ---- ONGLETS ----
tabs = st.tabs(["🛒 Caisse", "💸 Dépenses", "📝 Dettes", "📅 Relevé Semaine", "📊 Bilan"])

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

    if st.button("✅ Valider la commande"):
        try:
            date_str = datetime.now().strftime("%d/%m/%Y %H:%M")
            client_final = nom_c if nom_c else "Anonyme"
            nouvelle_v = pd.DataFrame([{
                "Date": date_str,
                "Client": client_final,
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
            st.success("✅ Vente enregistrée !")
            st.balloons()

            # --- REÇU AVEC LOGO ---
            st.markdown("---")
            st.markdown("#### 🧾 Reçu")
            col_logo_recu, col_info_recu = st.columns([1, 3])
            with col_logo_recu:
                try:
                    st.image("logo.png", width=80)
                except:
                    st.write("🥤")
            with col_info_recu:
                st.markdown(f"""
                **MUN'ISH STAND**  
                *Votre pause rafraîchissante*  
                {date_str}
                """)

            st.markdown(f"""
            | | |
            |---|---|
            | **Client** | {client_final} |
            | **Article** | {art} |
            | **Quantité** | {qte} |
            | **Prix unitaire** | {prix_u} FCFA |
            | **TOTAL** | **{total} FCFA** |
            | **Mode** | {mode} |
            | **Reçu** | {recu} FCFA |
            | **Rendu** | {rendu} FCFA |
            """)
            st.caption("Merci pour votre commande ! 🧡 À bientôt chez Mun'ish")

            # Bouton télécharger le reçu en HTML (imprimable)
            recu_html = generer_recu_html(client_final, art, qte, prix_u, total, mode, recu, rendu, date_str)
            st.download_button(
                label="🖨️ Télécharger / Imprimer le reçu",
                data=recu_html,
                file_name=f"recu_{client_final}_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
                mime="text/html"
            )

        except Exception as e:
            st.error(f"Erreur : Vérifiez que l'onglet 'ventes' existe dans le Sheet. {e}")

# --- ONGLET 2 : DÉPENSES ---
with tabs[1]:
    st.subheader("Nouvelle Dépense")
    with st.form("form_d"):
        desig = st.text_input("Désignation")
        montant = st.number_input("Montant", min_value=0)
        if st.form_submit_button("💾 Enregistrer l'achat"):
            try:
                df_d = conn.read(spreadsheet=URL_MUNISH, worksheet="depenses")
                nouvelle_d = pd.DataFrame([{
                    "Date": datetime.now().strftime("%d/%m/%Y"),
                    "Désignation": desig,
                    "Montant": montant
                }])
                df_d = pd.concat([df_d, nouvelle_d], ignore_index=True)
                conn.update(spreadsheet=URL_MUNISH, worksheet="depenses", data=df_d)
                st.success("✅ Dépense enregistrée !")
            except Exception as e:
                st.error(f"Erreur : Vérifiez l'onglet 'depenses'. {e}")

# --- ONGLET 3 : DETTES ---
with tabs[2]:
    st.subheader("Suivi des Dettes")
    with st.expander("➕ Ajouter un impayé"):
        d_nom = st.text_input("Nom débiteur")
        d_art = st.text_input("Article")
        d_somme = st.number_input("Montant dû", min_value=0)
        if st.button("⚠️ Noter la dette"):
            try:
                df_det = conn.read(spreadsheet=URL_MUNISH, worksheet="dettes")
                nouvelle_det = pd.DataFrame([{
                    "Date": datetime.now().strftime("%d/%m/%Y"),
                    "Client": d_nom,
                    "Article": d_art,
                    "Montant": d_somme,
                    "Statut": "NON PAYÉ"
                }])
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

# --- ONGLET 4 : RELEVÉ DE LA SEMAINE ---
with tabs[3]:
    st.subheader("📅 Relevé Hebdomadaire")

    # Sélection de la semaine
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        date_debut = st.date_input(
            "Date de début",
            value=datetime.now().date() - timedelta(days=datetime.now().weekday()),
            help="Choisissez le premier jour de la semaine"
        )
    with col_s2:
        date_fin = st.date_input(
            "Date de fin",
            value=datetime.now().date() - timedelta(days=datetime.now().weekday()) + timedelta(days=6),
            help="Choisissez le dernier jour de la semaine"
        )

    semaine_label = f"Semaine du {date_debut.strftime('%d/%m/%Y')} au {date_fin.strftime('%d/%m/%Y')}"
    st.info(f"📆 {semaine_label}")

    if st.button("🔍 Charger le relevé"):
        try:
            df_v_all = conn.read(spreadsheet=URL_MUNISH, worksheet="ventes")
            df_d_all = conn.read(spreadsheet=URL_MUNISH, worksheet="depenses")

            # Convertir les dates pour filtrage
            def parse_dates(df, col="Date"):
                df = df.copy()
                df[col] = pd.to_datetime(df[col], dayfirst=True, errors="coerce")
                return df

            df_v_all = parse_dates(df_v_all)
            df_d_all = parse_dates(df_d_all)

            debut_dt = pd.Timestamp(date_debut)
            fin_dt = pd.Timestamp(date_fin) + pd.Timedelta(hours=23, minutes=59)

            df_v_sem = df_v_all[
                (df_v_all["Date"] >= debut_dt) & (df_v_all["Date"] <= fin_dt)
            ].copy()
            df_d_sem = df_d_all[
                (df_d_all["Date"] >= debut_dt) & (df_d_all["Date"] <= fin_dt)
            ].copy()

            t_v = pd.to_numeric(df_v_sem["Total"], errors="coerce").sum() if not df_v_sem.empty else 0
            t_d = pd.to_numeric(df_d_sem["Montant"], errors="coerce").sum() if not df_d_sem.empty else 0
            solde = t_v - t_d

            # Affichage bilan
            st.markdown("### 📊 Bilan de la semaine")
            c1, c2, c3 = st.columns(3)
            c1.metric("💚 Entrées (ventes)", f"{int(t_v)} FCFA")
            c2.metric("🔴 Sorties (dépenses)", f"{int(t_d)} FCFA")
            delta_color = "normal" if solde >= 0 else "inverse"
            c3.metric("💰 Solde", f"{int(solde)} FCFA", delta=f"{int(solde)} F", delta_color=delta_color)

            st.markdown("### 🧾 Ventes de la semaine")
            if df_v_sem.empty:
                st.info("Aucune vente sur cette période.")
            else:
                df_v_sem_display = df_v_sem.copy()
                df_v_sem_display["Date"] = df_v_sem_display["Date"].dt.strftime("%d/%m/%Y %H:%M")
                st.dataframe(df_v_sem_display, use_container_width=True)

            st.markdown("### 💸 Dépenses de la semaine")
            if df_d_sem.empty:
                st.info("Aucune dépense sur cette période.")
            else:
                df_d_sem_display = df_d_sem.copy()
                df_d_sem_display["Date"] = df_d_sem_display["Date"].dt.strftime("%d/%m/%Y")
                st.dataframe(df_d_sem_display, use_container_width=True)

            st.markdown("---")
            st.markdown("### ⬇️ Téléchargements")

            col_dl1, col_dl2, col_dl3 = st.columns(3)

            # Export CSV combiné
            with col_dl1:
                csv_buf = io.StringIO()
                csv_buf.write(f"=== RELEVÉ SEMAINE : {semaine_label} ===\n\n")
                csv_buf.write("VENTES\n")
                df_v_sem.to_csv(csv_buf, index=False)
                csv_buf.write("\nDÉPENSES\n")
                df_d_sem.to_csv(csv_buf, index=False)
                csv_buf.write(f"\nBILAN\nEntrées,{int(t_v)}\nSorties,{int(t_d)}\nSolde,{int(solde)}\n")
                st.download_button(
                    "📥 Télécharger CSV",
                    data=csv_buf.getvalue(),
                    file_name=f"releve_semaine_{date_debut.strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )

            # Export HTML imprimable
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
                    "🖨️ Imprimer (HTML)",
                    data=releve_html,
                    file_name=f"releve_semaine_{date_debut.strftime('%Y%m%d')}.html",
                    mime="text/html"
                )

            # Export Excel
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
                        "Solde (FCFA)": int(solde)
                    }]).to_excel(writer, sheet_name="Bilan", index=False)
                st.download_button(
                    "📊 Télécharger Excel",
                    data=excel_buf.getvalue(),
                    file_name=f"releve_semaine_{date_debut.strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        except Exception as e:
            st.error(f"Erreur lors du chargement : {e}")

# --- ONGLET 5 : BILAN ---
with tabs[4]:
    st.subheader("📊 Bilan Financier")
    try:
        df_v = conn.read(spreadsheet=URL_MUNISH, worksheet="ventes")
        df_d = conn.read(spreadsheet=URL_MUNISH, worksheet="depenses")

        t_v = pd.to_numeric(df_v["Total"], errors="coerce").sum()
        t_d = pd.to_numeric(df_d["Montant"], errors="coerce").sum()

        c1, c2, c3 = st.columns(3)
        c1.metric("💚 Entrées", f"{int(t_v)} F")
        c2.metric("🔴 Sorties", f"{int(t_d)} F")
        c3.metric("💰 Solde", f"{int(t_v - t_d)} F")

        st.write("**Historique des ventes :**")
        st.dataframe(df_v.tail(20), use_container_width=True)

    except Exception as e:
        st.info(f"Enregistrez une vente et une dépense pour voir le bilan. ({e})")
