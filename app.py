import streamlit as st
import fitz
import pandas as pd
from io import BytesIO
import re
import textwrap
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuration de la page avec thème sombre
st.set_page_config(
    page_title="DataExtract - Economic PDF Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS pour reproduire le design moderne
st.markdown("""
<style>
    /* Import des polices */
    @import url('https://fonts.googleapis.com/css2?family=Spline+Sans:wght@400;500;700&display=swap');
    
    /* Variables CSS */
    :root {
        --primary-color: #38e07b;
        --bg-dark: #111827;
        --bg-card: #1f2937;
        --border-color: #374151;
        --text-primary: #ffffff;
        --text-secondary: #9ca3af;
    }
    
    /* Styles globaux */
    .stApp {
        background-color: var(--bg-dark);
        font-family: 'Spline Sans', sans-serif;
    }
    
    /* Header */
    .main-header {
        background: var(--bg-dark);
        border-bottom: 1px solid var(--border-color);
        padding: 1rem 2rem;
        margin: -1rem -1rem 2rem -1rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .logo-section {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .logo-icon {
        width: 32px;
        height: 32px;
        color: var(--primary-color);
    }
    
    .logo-text {
        color: var(--text-primary);
        font-size: 1.25rem;
        font-weight: bold;
        margin: 0;
    }
    
    .nav-section {
        display: flex;
        align-items: center;
        gap: 2rem;
    }
    
    .nav-link {
        color: var(--text-secondary);
        text-decoration: none;
        font-size: 0.875rem;
        font-weight: 500;
        transition: color 0.2s;
    }
    
    .nav-link:hover, .nav-link.active {
        color: var(--text-primary);
    }
    
    .nav-link.active {
        color: var(--primary-color);
        font-weight: 600;
    }
    
    /* Titre principal */
    .main-title {
        color: var(--text-primary);
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .main-subtitle {
        color: var(--text-secondary);
        font-size: 1.125rem;
        text-align: center;
        max-width: 48rem;
        margin: 0 auto 3rem auto;
    }
    
    /* Cartes */
    .metric-card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 1rem;
        padding: 1.5rem;
        height: 100%;
    }
    
    .metric-title {
        color: var(--text-secondary);
        font-size: 0.875rem;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        color: var(--text-primary);
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.25rem;
    }
    
    .metric-change {
        display: flex;
        align-items: center;
        gap: 0.25rem;
        font-size: 0.875rem;
        font-weight: 600;
    }
    
    .metric-change.positive {
        color: #10b981;
    }
    
    .metric-change.negative {
        color: #ef4444;
    }
    
    /* Section d'upload */
    .upload-section {
        background: var(--bg-card);
        border: 2px dashed var(--border-color);
        border-radius: 0.5rem;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
        transition: border-color 0.2s;
    }
    
    .upload-section:hover {
        border-color: var(--primary-color);
    }
    
    /* Formulaire */
    .form-group {
        margin-bottom: 1.5rem;
    }
    
    .form-label {
        display: block;
        color: var(--text-primary);
        font-size: 0.875rem;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
    
    .form-input {
        width: 100%;
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 0.5rem;
        padding: 0.75rem 1rem;
        color: var(--text-primary);
        font-size: 1rem;
    }
    
    .form-input:focus {
        outline: none;
        border-color: var(--primary-color);
        box-shadow: 0 0 0 2px rgba(56, 224, 123, 0.2);
    }
    
    /* Boutons */
    .btn-primary {
        background: var(--primary-color);
        color: var(--bg-dark);
        border: none;
        border-radius: 9999px;
        padding: 0.75rem 1.5rem;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.2s;
        width: 100%;
        font-size: 1rem;
    }
    
    .btn-primary:hover {
        background: #22c55e;
        transform: translateY(-1px);
    }
    
    /* Tableau */
    .data-table {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 1rem;
        overflow: hidden;
    }
    
    .table-header {
        background: #1f2937;
        color: var(--text-secondary);
        font-size: 0.75rem;
        font-weight: 500;
        text-transform: uppercase;
        padding: 1rem;
    }
    
    .table-row {
        border-bottom: 1px solid var(--border-color);
        padding: 1rem;
        transition: background-color 0.2s;
    }
    
    .table-row:hover {
        background: rgba(31, 41, 55, 0.5);
    }
    
    /* Status indicators */
    .status-success {
        color: #10b981;
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.2);
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .status-error {
        color: #ef4444;
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.2);
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .status-warning {
        color: #f59e0b;
        background: rgba(245, 158, 11, 0.1);
        border: 1px solid rgba(245, 158, 11, 0.2);
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    /* Masquer les éléments Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Styles pour les graphiques Plotly */
    .js-plotly-plot {
        background: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

class PDFEconomicExtractor:
    def __init__(self, groq_api_key):
        try:
            from groq import Groq
            self.client = Groq(api_key=groq_api_key)
        except Exception as e:
            st.error(f"Erreur lors de l'initialisation de Groq: {str(e)}")
            raise e
        self.tableau_final = []

    def callback_llama_groq(self, bloc):
        try:
            prompt = f"""
MISSION: Extraire UNIQUEMENT les indicateurs économiques OFFICIELS et PRÉCIS du texte.

CRITÈRES STRICTS D'INCLUSION:
• PIB et croissance économique (avec période précise)
• Taux d'inflation (général, sectoriel, sous-jacent)  
• Taux directeurs et politiques monétaires
• Commerce extérieur (exportations/importations en %)
• Indices boursiers (MASI, etc.)
• Taux de change et devises
• Contribution sectorielle à la croissance
• Masse monétaire et crédit
• Déficit/excédent budgétaire

FORMAT STRICT:
Secteur/Indicateur|Valeur|Période|Phrase_complète

Texte à analyser:
{bloc}

Répondez UNIQUEMENT avec les données au format demandé, une ligne par indicateur VALIDE.
"""
            
            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.05,
                max_tokens=1024
            )
            
            return completion.choices[0].message.content
            
        except Exception as e:
            error_msg = str(e).lower()
            if "rate limit" in error_msg:
                st.error("Limite de taux API atteinte. Attendez quelques minutes.")
            elif "api key" in error_msg or "unauthorized" in error_msg:
                st.error("Clé API invalide. Vérifiez votre clé Groq.")
            else:
                st.error(f"Erreur API Groq: {e}")
            return ""

    def analyser_texte_economique(self, llama_response):
        if not llama_response:
            return []
        
        lignes = llama_response.strip().split('\n')
        tableau = []
        
        mots_cles_valides = [
            'pib', 'inflation', 'croissance', 'taux', 'export', 'import', 
            'indice', 'bourse', 'change', 'monétaire', 'budgétaire', 
            'déficit', 'excédent', 'investissement', 'consommation',
            'agriculture', 'industrie', 'service', 'manufacture', 'construction'
        ]
        
        for ligne in lignes:
            ligne = ligne.strip()
            if ligne and '|' in ligne:
                ligne = ligne.strip('| ')
                colonnes = [col.strip() for col in ligne.split('|')]
                
                if len(colonnes) >= 4:
                    secteur_indicateur = colonnes[0].strip()
                    valeur = colonnes[1].strip()
                    periode = colonnes[2].strip()
                    phrase = colonnes[3].strip()
                    
                    if self._valider_donnee_economique(secteur_indicateur, valeur, periode, phrase, mots_cles_valides):
                        tableau.append({
                            "Secteur/Indicateur": secteur_indicateur,
                            "Valeur": valeur,
                            "Période": periode,
                            "Phrase": phrase
                        })
        
        return tableau

    def _valider_donnee_economique(self, secteur_indicateur, valeur, periode, phrase, mots_cles_valides):
        if any(mot in secteur_indicateur.lower() for mot in ['secteur', 'indicateur', 'terme', 'valeur']):
            return False
        
        texte_complet = f"{secteur_indicateur} {phrase}".lower()
        if not any(mot in texte_complet for mot in mots_cles_valides):
            return False
        
        if not re.search(r'-?\d+[,.]?\d*', valeur):
            return False
        
        exclusions = ['téléphone', 'adresse', 'email', 'contact', 'page', 'référence']
        if any(mot in texte_complet for mot in exclusions):
            return False
        
        if len(secteur_indicateur) < 3 or len(phrase) < 20:
            return False
        
        return True

    def extract_text_from_pdf(self, pdf_bytes):
        try:
            document = fitz.open(stream=pdf_bytes, filetype="pdf")
            text = ""
            for page in document:
                text += page.get_text()
            document.close()
            return text
        except Exception as e:
            st.error(f"Erreur lors de l'extraction du PDF: {e}")
            return ""

    def clean_text(self, text):
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def decouper_en_blocs(self, text, taille_max=1500):
        blocs = textwrap.wrap(
            text,
            width=taille_max,
            break_long_words=False,
            break_on_hyphens=False
        )
        return blocs

    def filtrer_donnees_qualite(self, donnees):
        donnees_filtrees = []
        
        indicateurs_prioritaires = [
            'pib', 'croissance', 'inflation', 'taux directeur', 'export', 'import',
            'indice', 'change', 'bourse', 'déficit', 'masse monétaire'
        ]
        
        for donnee in donnees:
            secteur_indicateur = donnee.get('Secteur/Indicateur', '').lower()
            phrase = donnee.get('Phrase', '').lower()
            valeur = donnee.get('Valeur', '')
            
            score = 0
            
            for indicateur in indicateurs_prioritaires:
                if indicateur in secteur_indicateur or indicateur in phrase:
                    score += 2
            
            if '%' in valeur or 'point' in valeur:
                score += 1
            
            if any(mot in phrase for mot in ['trimestre', 'annuel', 'mensuel', '2024', '2025']):
                score += 1
            
            if score >= 2:
                donnees_filtrees.append(donnee)
        
        return donnees_filtrees

def test_api_groq(api_key):
    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Test de connectivité. Répondez simplement 'OK'."}],
            max_tokens=5,
            temperature=0
        )
        
        if completion.choices[0].message.content:
            return True, "API Groq connectée avec succès"
        else:
            return False, "Réponse vide de l'API"
    except Exception as e:
        error_msg = str(e).lower()
        if "api key" in error_msg or "unauthorized" in error_msg:
            return False, "Clé API invalide. Vérifiez votre clé Groq."
        elif "rate limit" in error_msg:
            return False, "Limite de taux atteinte. Attendez quelques minutes."
        else:
            return False, f"Erreur: {str(e)}"

def get_api_key():
    try:
        default_key = st.secrets.get("GROQ_API_KEY", "")
    except:
        default_key = ""
    return default_key

def create_header():
    st.markdown("""
    <div class="main-header">
        <div class="logo-section">
            <svg class="logo-icon" fill="none" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
                <g clip-path="url(#clip0_12_2)">
                    <path d="M4 14C4 12.8954 4.89543 12 6 12H42C43.1046 12 44 12.8954 44 14V34C44 35.1046 43.1046 36 42 36H6C4.89543 36 4 35.1046 4 34V14Z" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="4"/>
                    <path d="M12 12V36" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="4"/>
                    <path d="M22 12V36" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="4"/>
                    <path d="M32 12V36" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="4"/>
                </g>
            </svg>
            <h2 class="logo-text">DataExtract</h2>
        </div>
        <nav class="nav-section">
            <a href="#" class="nav-link">Dashboard</a>
            <a href="#" class="nav-link">Extraction</a>
            <a href="#" class="nav-link active">Analysis</a>
            <a href="#" class="nav-link">Settings</a>
        </nav>
    </div>
    """, unsafe_allow_html=True)

def create_metrics_section(df):
    if df is not None and not df.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Total Indicators</div>
                <div class="metric-value">{len(df)}</div>
                <div class="metric-change positive">+{len(df)} new</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            secteurs_uniques = df['Secteur/Indicateur'].nunique()
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Unique Sectors</div>
                <div class="metric-value">{secteurs_uniques}</div>
                <div class="metric-change positive">+{secteurs_uniques} sectors</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            periodes = df['Période'].value_counts()
            periode_principale = periodes.index[0] if not periodes.empty else "N/A"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Main Period</div>
                <div class="metric-value">{periode_principale}</div>
                <div class="metric-change">Current</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            growth_indicators = len(df[df['Secteur/Indicateur'].str.contains('croissance|pib', case=False)])
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Growth Metrics</div>
                <div class="metric-value">{growth_indicators}</div>
                <div class="metric-change positive">+{growth_indicators} metrics</div>
            </div>
            """, unsafe_allow_html=True)

def create_charts(df):
    if df is None or df.empty:
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Graphique de répartition par secteur
        secteur_counts = df['Secteur/Indicateur'].value_counts().head(7)
        
        fig = go.Figure(data=[
            go.Bar(
                x=secteur_counts.index,
                y=secteur_counts.values,
                marker_color='#38e07b',
                text=secteur_counts.values,
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title="Sector Performance",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            title_font_size=16,
            height=350
        )
        
        fig.update_xaxes(showgrid=False, color='#9ca3af')
        fig.update_yaxes(showgrid=True, gridcolor='#374151', color='#9ca3af')
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Graphique temporel
        periode_counts = df['Période'].value_counts()
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=list(range(len(periode_counts))),
            y=periode_counts.values,
            mode='lines+markers',
            line_color='#38e07b',
            fill='tonexty',
            fillcolor='rgba(56, 224, 123, 0.3)'
        ))
        
        fig.update_layout(
            title="Economic Growth Over Time",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            title_font_size=16,
            height=350,
            showlegend=False
        )
        
        fig.update_xaxes(showgrid=False, color='#9ca3af')
        fig.update_yaxes(showgrid=True, gridcolor='#374151', color='#9ca3af')
        
        st.plotly_chart(fig, use_container_width=True)

def main():
    # Header
    create_header()
    
    # Titre principal
    st.markdown("""
    <h1 class="main-title">Economic Data Analysis</h1>
    <p class="main-subtitle">
        Upload your PDF document to automatically extract key economic indicators. 
        Our powerful AI will analyze the content and present it in a clear, structured format.
    </p>
    """, unsafe_allow_html=True)
    
    # Section principale avec deux colonnes
    col_form, col_summary = st.columns([1.2, 0.8])
    
    with col_form:
        # Formulaire d'upload
        st.markdown('<div class="form-group">', unsafe_allow_html=True)
        st.markdown('<label class="form-label">API Key</label>', unsafe_allow_html=True)
        
        default_api_key = get_api_key()
        api_key = st.text_input(
            "",
            value=default_api_key,
            type="password",
            placeholder="Enter your API key",
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Statut de l'API
        if api_key:
            if st.button("🔍 Test API Connection", key="test_api"):
                with st.spinner("Testing..."):
                    success, message = test_api_groq(api_key)
                    if success:
                        st.markdown(f'<div class="status-success">{message}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="status-error">{message}</div>', unsafe_allow_html=True)
        
        # Upload de fichier
        st.markdown('<div class="form-group">', unsafe_allow_html=True)
        st.markdown('<label class="form-label">Upload PDF</label>', unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "",
            type="pdf",
            help="PDF files only (MAX 10MB)",
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        if uploaded_file:
            file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
            st.markdown(f'<div class="status-success">✅ {uploaded_file.name} loaded ({file_size_mb:.1f} MB)</div>', 
                       unsafe_allow_html=True)
        
        # Bouton d'analyse
        analyze_button = st.button("🔍 Analyze PDF", type="primary", disabled=not uploaded_file or not api_key)
    
    with col_summary:
        # Section de résumé
        st.markdown("""
        <div class="metric-card">
            <h2 style="color: white; margin-bottom: 1rem;">Analysis Summary</h2>
            <p style="color: #9ca3af; line-height: 1.6;">
                This analysis will extract key economic indicators from the uploaded PDF, 
                focusing on financial performance metrics and market trends. The data includes 
                revenue, profit margins, and growth rates, providing a comprehensive overview 
                of the document's economic content.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Traitement de l'analyse
    if analyze_button and uploaded_file and api_key:
        # Test préliminaire de l'API
        success, message = test_api_groq(api_key)
        if not success:
            st.markdown(f'<div class="status-error">Impossible de se connecter à l\'API Groq: {message}</div>', 
                       unsafe_allow_html=True)
            return
        
        with st.spinner("Analyzing PDF..."):
            try:
                extractor = PDFEconomicExtractor(api_key)
                
                # Extraction du texte
                pdf_bytes = uploaded_file.getvalue()
                texte_brut = extractor.extract_text_from_pdf(pdf_bytes)
                
                if not texte_brut:
                    st.markdown('<div class="status-error">Impossible d\'extraire le texte du PDF</div>', 
                               unsafe_allow_html=True)
                    return
                
                # Nettoyage et découpage
                texte_propre = extractor.clean_text(texte_brut)
                blocs = extractor.decouper_en_blocs(texte_propre)
                
                # Analyse par blocs
                progress_bar = st.progress(0)
                for i, bloc in enumerate(blocs):
                    reponse_llama = extractor.callback_llama_groq(bloc)
                    if reponse_llama:
                        donnees_structurees = extractor.analyser_texte_economique(reponse_llama)
                        extractor.tableau_final.extend(donnees_structurees)
                    
                    progress_bar.progress((i + 1) / len(blocs))
                
                # Filtrage et finalisation
                if extractor.tableau_final:
                    donnees_filtrees = extractor.filtrer_donnees_qualite(extractor.tableau_final)
                    
                    if donnees_filtrees:
                        df_final = pd.DataFrame(donnees_filtrees)
                        df_final = df_final.drop_duplicates(subset=['Secteur/Indicateur', 'Valeur'])
                        df_final = df_final.sort_values(['Secteur/Indicateur', 'Période']).reset_index(drop=True)
                        
                        st.success(f"✅ Analysis completed! {len(df_final)} indicators extracted.")
                        
                        # Affichage des résultats
                        st.markdown("## Data Summary")
                        create_metrics_section(df_final)
                        
                        st.markdown("---")
                        create_charts(df_final)
                        
                        st.markdown("---")
                        st.markdown("## Detailed Data Table")
                        
                        # Barre de recherche
                        search_term = st.text_input("🔍 Search data entries...", "")
                        
                        # Filtrage des données
                        if search_term:
                            df_display = df_final[
                                df_final.apply(lambda row: search_term.lower() in row.to_string().lower(), axis=1)
                            ]
                        else:
                            df_display = df_final
                        
                        # Affichage du tableau
                        st.dataframe(
                            df_display,
                            use_container_width=True,
                            height=400
                        )
                        
                        # Boutons de téléchargement
                        col_dl1, col_dl2 = st.columns(2)
                        
                        with col_dl1:
                            csv_data = df_final.to_csv(index=False, sep=';', encoding='utf-8')
                            st.download_button(
                                label="📄 Download CSV",
                                data=csv_data,
                                file_name=f"economic_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                                mime="text/csv",
                                use_container_width=True
                            )
                        
                        with col_dl2:
                            excel_buffer = BytesIO()
                            df_final.to_excel(excel_buffer, index=False, engine='openpyxl')
                            excel_buffer.seek(0)
                            
                            st.download_button(
                                label="📊 Download Excel",
                                data=excel_buffer,
                                file_name=f"economic_data_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True
                            )
                    
                    else:
                        st.markdown('<div class="status-warning">Aucun indicateur valide après filtrage qualité</div>', 
                                   unsafe_allow_html=True)
                        st.info("Essayez avec un rapport économique officiel ou un bulletin de banque centrale.")
                
                else:
                    st.markdown('<div class="status-warning">Aucun indicateur économique détecté</div>', 
                               unsafe_allow_html=True)
                    st.info("Le PDF ne semble pas contenir de données économiques exploitables.")
            
            except Exception as e:
                st.markdown(f'<div class="status-error">Erreur pendant l\'analyse : {str(e)}</div>', 
                           unsafe_allow_html=True)
                if "api_key" in str(e).lower():
                    st.info("Problème avec la clé API Groq. Vérifiez qu'elle est valide.")
                elif "rate limit" in str(e).lower():
                    st.info("Limite de taux API atteinte. Attendez quelques minutes.")

if __name__ == "__main__":
    main()

