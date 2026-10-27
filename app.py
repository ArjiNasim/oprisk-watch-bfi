import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# CONFIGURATION DE LA PAGE & STYLE BFI
# ==========================================
st.set_page_config(
    page_title="OpRisk-Watch | BFI Risk ORM Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

THEME_COLORS = {
    "primary": "#1f385c",
    "secondary": "#46698e",
    "accent": "#d9534f",
    "success": "#5cb85c",
    "warning": "#f0ad4e",
    "background": "#f8f9fa",
    "card_bg": "#ffffff"
}

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .metric-card {
        background-color: #ffffff;
        border: 1px solid #e1e4e8;
        border-radius: 6px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .stAlert { border-radius: 6px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# GÉNÉRATION DES JEUX DE DONNÉES SIMULÉS (MOCK)
# ==========================================
@st.cache_data
def load_mock_data():
    np.random.seed(42)
    
    perimetres = ["Cash Management", "Trade Finance", "Fonctions Transversales"]
    processus_list = [
        "Paiements SWIFT / TARGET2",
        "Émission de Crédits Documentaires (Credoc)",
        "Gestion des Garanties / SBLC",
        "Onboarding & KYC Client BFI",
        "Rapprochements de Trésorerie Intraday",
        "Traitement des Opérations de Change (FX)",
        "Gestion des Exceptions de Rapprochement Nostro",
        "Validation des Mandats de Signature Électronique"
    ]
    
    # 1. Données RCSA
    rcsa_data = []
    for i in range(1, 35):
        perim = np.random.choice(perimetres)
        proc = np.random.choice(processus_list)
        inherent = np.random.randint(3, 6)
        net_metier = max(1, inherent - np.random.randint(1, 3))
        delta = np.random.choice([0, 1, 2], p=[0.5, 0.3, 0.2])
        net_risque = min(5, net_metier + delta)
        
        rcsa_data.append({
            "ID_Processus": f"PRC-{100+i}",
            "Périmètre": perim,
            "Intitulé_Processus": f"{proc} - {i}",
            "Risque_Inhérent": inherent,
            "Évaluation_Métier (1L)": net_metier,
            "Évaluation_Challenge (2L)": net_risque,
            "Écart_Delta": net_risque - net_metier,
            "Statut_Validation": "Validé" if net_risque == net_metier else "Rehaussé par ORM"
        })
    df_rcsa = pd.DataFrame(rcsa_data)
    
    # 2. Données Incidents Historiques
    typologies = ["Erreur humaine", "Défaillance technique / IT", "Fraude externe", "Processus non respecté", "Erreur de paramétrage"]
    incidents_data = []
    for j in range(1, 50):
        perim = np.random.choice(perimetres)
        typo = np.random.choice(typologies)
        impact = np.random.exponential(scale=45.0)
        statut = np.random.choice(["Clôturé", "En cours d'investigation", "Plan d'action actif"], p=[0.6, 0.25, 0.15])
        incidents_data.append({
            "ID_Incident": f"INC-2026-{500+j}",
            "Périmètre": perim,
            "Typologie_Bâle": typo,
            "Impact_Financier_kEUR": round(impact, 2),
            "Statut": statut,
            "Date_Survenance": pd.Timestamp("2026-01-01") + pd.Timedelta(days=int(np.random.randint(0, 260)))
        })
    df_incidents = pd.DataFrame(incidents_data)
    
    # 3. Plans d'Action
    actions_data = []
    for k in range(1, 25):
        perim = np.random.choice(perimetres)
        source = np.random.choice(["Contrôle Permanent (2L)", "Inspection Générale (3L)", "RCSA Action"])
        etat = np.random.choice(["Clôturé", "En cours", "En retard / Overdue"], p=[0.45, 0.4, 0.15])
        actions_data.append({
            "ID_Action": f"ACT-{300+k}",
            "Périmètre": perim,
            "Source": source,
            "Intitulé": f"Remédiation - Déficit de contrôle #{k}",
            "État_Avancement": etat,
            "Échéance": pd.Timestamp("2026-03-01") + pd.Timedelta(days=int(np.random.randint(0, 300)))
        })
    df_actions = pd.DataFrame(actions_data)
    
    return df_rcsa, df_incidents, df_actions

df_rcsa, df_incidents, df_actions = load_mock_data()

# ==========================================
# BARRE LATÉRALE DE NAVIGATION
# ==========================================
st.sidebar.markdown("### 🛡️ OpRisk-Watch BFI")
st.sidebar.markdown("*Supervision des Risques Opérationnels (2e Ligne - ORM)*")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Navigation Principale",
    [
        "📊 Vue d'ensemble (KPIs)",
        "📋 Module 1 : Challenge RCSA",
        "⚠️ Module 2 : Incidents Historiques",
        "🎯 Module 3 : Plans d'Action & Audit",
        "⚖️ Module 4 : Aide à la Décision (Dérogations)"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("**Périmètre couvert :**\n- Cash Management\n- Trade Finance\n- Fonctions Transversales")

# ==========================================
# VUE 1 : VUE D'ENSEMBLE
# ==========================================
if menu == "📊 Vue d'ensemble (KPIs)":
    st.title("📊 Tableau de Bord Consolidé - Risques Opérationnels")
    st.markdown("Vue synthétique de l'exposition aux risques opérationnels pour la BFI.")
    
    total_process = len(df_rcsa)
    avg_score_brut = round(df_rcsa["Risque_Inhérent"].mean(), 2)
    avg_score_net = round(df_rcsa["Évaluation_Challenge (2L)"].mean(), 2)
    open_incidents = len(df_incidents[df_incidents["Statut"] != "Clôturé"])
    total_actions = len(df_actions)
    overdue_actions = len(df_actions[df_actions["État_Avancement"] == "En retard / Overdue"])
    taux_cloture_actions = round((len(df_actions[df_actions["État_Avancement"] == "Clôturé"]) / total_actions) * 100, 1)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1: st.metric("Processus Supervisés", total_process)
    with col2: st.metric("Score Risque Net (2L)", f"{avg_score_net} / 5", delta=f"Brut: {avg_score_brut}", delta_color="inverse")
    with col3: st.metric("Incidents Actifs", open_incidents, delta="À surveiller")
    with col4: st.metric("Taux Clôture Actions", f"{taux_cloture_actions}%")
    with col5: st.metric("Actions en Retard", overdue_actions, delta="Critique" if overdue_actions > 0 else "OK", delta_color="inverse")
    
    st.markdown("---")
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Répartition du Risque Net Moyen par Périmètre")
        df_perim_rcsa = df_rcsa.groupby("Périmètre")["Évaluation_Challenge (2L)"].mean().reset_index()
        fig_perim = px.bar(df_perim_rcsa, x="Périmètre", y="Évaluation_Challenge (2L)", color="Périmètre", color_discrete_sequence=px.colors.sequential.Blues_r, text_auto=".2f")
        fig_perim.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_perim, use_container_width=True)
        
    with col_b:
        st.subheader("Impact Financier Cumulés des Incidents (k€)")
        df_perim_inc = df_incidents.groupby("Périmètre")["Impact_Financier_kEUR"].sum().reset_index()
        fig_inc = px.pie(df_perim_inc, names="Périmètre", values="Impact_Financier_kEUR", hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
        fig_inc.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_inc, use_container_width=True)

# ==========================================
# MODULE 1 : CHALLENGE RCSA
# ==========================================
elif menu == "📋 Module 1 : Challenge RCSA":
    st.title("📋 Module 1 : Revue & Challenge des RCSA")
    st.markdown("Ce module permet à la 2e ligne de défense (Risk ORM) de challenger les auto-évaluations des risques.")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        selected_perim = st.selectbox("Filtrer par Périmètre", ["Tous"] + list(df_rcsa["Périmètre"].unique()))
    with col_f2:
        min_delta_filter = st.slider("Filtrer par Écart minimal (Delta 2L vs 1L)", 0, 3, 0)
        
    filtered_df = df_rcsa.copy()
    if selected_perim != "Tous":
        filtered_df = filtered_df[filtered_df["Périmètre"] == selected_perim]
    filtered_df = filtered_df[filtered_df["Écart_Delta"] >= min_delta_filter]
    
    st.subheader(f"Matrice de Challenge RCSA (Processus affichés : {len(filtered_df)})")
    st.dataframe(filtered_df[["ID_Processus", "Périmètre", "Intitulé_Processus", "Risque_Inhérent", "Évaluation_Métier (1L)", "Évaluation_Challenge (2L)", "Écart_Delta", "Statut_Validation"]], use_container_width=True, hide_index=True)
    
    st.subheader("Distribution des Écarts de Notation (Sous-estimations par le Métier)")
    fig_delta = px.histogram(df_rcsa, x="Écart_Delta", color="Périmètre", nbins=4, barmode="group", color_discrete_sequence=px.colors.qualitative.Prism)
    fig_delta.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_delta, use_container_width=True)

# ==========================================
# MODULE 2 : ANALYSE DES INCIDENTS HISTORIQUES
# ==========================================
elif menu == "⚠️ Module 2 : Incidents Historiques":
    st.title("⚠️ Module 2 : Analyse des Incidents Historiques (IH)")
    st.markdown("Analyse de la récurrence des pertes opérationnelles selon la taxonomie Bâloise.")
    
    col_m2_1, col_m2_2 = st.columns(2)
    with col_m2_1:
        st.subheader("Récurrence et Impact par Typologie Bâloise")
        df_typo = df_incidents.groupby("Typologie_Bâle").agg(
            Nombre_Incidents=("ID_Incident", "count"),
            Impact_Total_kEUR=("Impact_Financier_kEUR", "sum")
        ).reset_index()
        fig_typo = px.bar(df_typo, x="Impact_Total_kEUR", y="Typologie_Bâle", orientation="h", color="Nombre_Incidents", color_continuous_scale="Reds", text="Impact_Total_kEUR")
        fig_typo.update_layout(yaxis={"categoryorder": "total ascending"}, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_typo, use_container_width=True)
        
    with col_m2_2:
        st.subheader("Chronologie des Pertes Financières (k€)")
        fig_time = px.scatter(df_incidents, x="Date_Survenance", y="Impact_Financier_kEUR", color="Périmètre", size="Impact_Financier_kEUR", hover_data=["ID_Incident", "Typologie_Bâle", "Statut"], color_discrete_sequence=px.colors.qualitative.Bold)
        fig_time.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_time, use_container_width=True)
        
    st.subheader("Registre des Incidents Majeurs & Statut de Remédiation")
    status_filter = st.selectbox("Filtrer par Statut d'Incident", ["Tous"] + list(df_incidents["Statut"].unique()))
    table_inc = df_incidents.copy()
    if status_filter != "Tous":
        table_inc = table_inc[table_inc["Statut"] == status_filter]
    st.dataframe(table_inc.sort_values(by="Impact_Financier_kEUR", ascending=False), use_container_width=True, hide_index=True)

# ==========================================
# MODULE 3 : PLANS D'ACTION
# ==========================================
elif menu == "🎯 Module 3 : Plans d'Action & Audit":
    st.title("🎯 Module 3 : Suivi des Plans d'Action et Recommandations d'Audit")
    st.markdown("Suivi rigoureux des actions correctives issues du Contrôle Permanent (2L) et de l'Audit (3L).")
    
    col_a1, col_a2 = st.columns([2, 1])
    with col_a1:
        st.subheader("État d'Avancement global par Périmètre")
        df_actions_grouped = df_actions.groupby(["Périmètre", "État_Avancement"]).size().reset_index(name="Nombre")
        fig_act = px.bar(df_actions_grouped, x="Périmètre", y="Nombre", color="État_Avancement", barmode="stack", color_discrete_map={"Clôturé": THEME_COLORS["success"], "En cours": THEME_COLORS["secondary"], "En retard / Overdue": THEME_COLORS["accent"]})
        fig_act.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_act, use_container_width=True)
        
    with col_a2:
        st.subheader("Synthèse des Retards")
        overdue_count = len(df_actions[df_actions["État_Avancement"] == "En retard / Overdue"])
        st.error(f"⚠️ **{overdue_count} actions correctives** dépassent l'échéance cible fixée et nécessitent une escalade.")
        
    st.subheader("Liste détaillée des Recommandations et Plans d'Action")
    st.dataframe(df_actions, use_container_width=True, hide_index=True)

# ==========================================
# MODULE 4 : AIDE À LA DÉCISION (DÉROGATIONS)
# ==========================================
elif menu == "⚖️ Module 4 : Aide à la Décision (Dérogations)":
    st.title("⚖️ Module 4 : Aide à la Décision (Nouvelles Activités & Dérogations)")
    st.markdown("Outil de scoring prédictif pour l'évaluation des risques liés à une Nouvelle Activité (NPA) ou une dérogation.")
    
    with st.form("derogation_form"):
        st.subheader("Formulaire d'Évaluation du Risque Opérationnel")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            activite_nom = st.text_input("Intitulé de la Nouvelle Activité ou de la Dérogation", "Ex: Lancement nouveau canal de paiement instantané SWIFT gpi")
            perim_choice = st.selectbox("Périmètre concerné", ["Cash Management", "Trade Finance", "Fonctions Transversales"])
            complexite = st.slider("Complexité Opérationnelle & Systèmes (1 à 5)", 1, 5, 3)
        with col_f2:
            exposition_fin = st.selectbox("Exposition Financière / Volumétrie potentielle", ["Faible (< 10 M€)", "Moyenne (10M€ - 100M€)", "Élevée (> 100 M€)"])
            robustesse_ctrl = st.slider("Robustesse des Contrôles de 1re Ligne (1 à 5)", 1, 5, 3)
            
        submit_eval = st.form_submit_button("Calculer le Score de Risque Synthétique & Avis ORM")
        
    if submit_eval:
        exp_weight = 1 if "Faible" in exposition_fin else (2 if "Moyenne" in exposition_fin else 3)
        score_brut = (complexite * 2) + (exp_weight * 1.5) - (robustesse_ctrl)
        score_normalise = max(1.0, min(5.0, round(score_brut / 2.0, 1)))
        
        if score_normalise < 2.5:
            niveau_risque = "Faible"
            badge_color = "success"
            avis = "Avis Favorable de la 2e Ligne - Processus validé sans réserve."
        elif score_normalise < 3.8:
            niveau_risque = "Modéré"
            badge_color = "warning"
            avis = "Avis Favorable sous réserve de mise en place de contrôles compensatoires."
        else:
            niveau_risque = "Élevé / Critique"
            badge_color = "error"
            avis = "Avis Défavorable ou Réserves Majeures - Escalade requise au Comité des Risques (ORMC)."
            
        st.markdown("---")
        st.subheader("Résultat de l'Évaluation & Avis de la 2e Ligne")
        res_col1, res_col2 = st.columns(2)
        with res_col1:
            st.metric("Score de Risque Synthétique (ORM)", f"{score_normalise} / 5")
            st.markdown(f"**Niveau de Risque :** `{niveau_risque}`")
        with res_col2:
            if badge_color == "success": st.success(avis)
            elif badge_color == "warning": st.warning(avis)
            else: st.error(avis)
