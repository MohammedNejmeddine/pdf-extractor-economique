import streamlit as st
import fitz
import pandas as pd
from io import BytesIO
import re
import textwrap
from datetime import datetime
import os
import plotly.express as px
import plotly.graph_objects as go

# Configuration de la page avec thème sombre moderne
st.set_page_config(
    page_title="DataExtract - Economic PDF Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personnalisé pour reproduire l'interface moderne
st.markdown("""
<style>
    /* Import des polices Google */
    @import url('https://fonts.googleapis.com/css2?family=Spline+Sans:wght@400;500;600;700&display=swap');
    
    /* Variables CSS pour la cohérence des couleurs */
    :root {
        --primary-color: #38e07b;
        --bg-primary: #111827;
        --bg-secondary: #1f2937;
        --bg-tertiary: #374151;
        --text-primary: #ffffff;
        --text-secondary: #9ca3af;
        --border-color: #4b5563;
    }
    
    /* Styles globaux */
    .stApp {
        background-color: var(--bg-primary);
        font-family: 'Spline Sans', sans-serif;
    }
    
    /* Header personnalisé */
    .main-header {
        background: var(--bg-primary);
        border-bottom: 1px solid var(--border-color);
        padding: 1rem 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;
    }
    
    .logo-section {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .logo-icon {
        width: 2rem;
        height: 2rem;
        background: var(--primary-color);
        border-radius: 0.5rem;
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--bg-primary);
        font-weight: bold;
    }
    
    .app-title {
        color: var(--text-primary);
        font-size: 1.25rem;
        font-weight: 700;
        margin: 0;
    }
    
    /* Navigation */
    .nav-menu {
        display: flex;
        gap: 1.5rem;
        align-items: center;
    }
    
    .nav-item {
        color: var(--text-secondary);
        text-decoration: none;
        font-weight: 500;
        transition: color 0.2s;
        padding: 0.5rem 0;
    }
    
    .nav-item:hover, .nav-item.active {
        color: var(--primary-color);
    }
    
    /* Cartes personnalisées */
    .metric-card {
        background: var(--bg-secondary);
        border: 1px solid var(--border-color);
        border-radius: 1rem;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .metric-card h3 {
        color: var(--text-primary);
        font-size: 1.125rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        color: var(--text-primary);
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .metric-change {
        display: flex;
        align-items: center;
        gap: 0.25rem;
        font-size: 0.875rem;
        font-weight: 600;
    }
    
    .metric-change.positive {
        color: var(--primary-color);
    }
    
    .metric-change.negative {
        color: #ef4444;
    }
    
    /* Upload zone personnalisée */
    .upload-zone {
        background: var(--bg-secondary);
        border: 2px dashed var(--border-color);
        border-radius: 1rem;
        padding: 3rem;
        text-align: center;
        margin: 1rem 0;
        transition: border-color 0.2s;
    }
    
    .upload-zone:hover {
        border-color: var(--primary-color);
    }
    
    .upload-icon {
        font-size: 3rem;
        color: var(--text-secondary);
        margin-bottom: 1rem;
    }
    
    .upload-text {
        color: var(--text-secondary);
        margin-bottom: 0.5rem;
    }
    
    .upload-subtext {
        color: var(--text-secondary);
        font-size: 0.875rem;
        opacity: 0.7;
    }
    
    /* Bouton primaire */
    .primary-btn {
        background: var(--primary-color);
        color: var(--bg-primary);
        border: none;
        border-radius: 2rem;
        padding: 0.75rem 2rem;
        font-weight: 700;
        cursor: pointer;
        transition: background 0.2s;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        justify-content: center;
        width: 100%;
        margin: 1rem 0;
    }
    
    .primary-btn:hover {
        background: #2dd866;
    }
    
    /* Sections */
    .section-title {
        color: var(--text-primary);
        font-size: 1.5rem;
        font-weight: 700;
        margin: 2rem 0 1rem 0;
    }
    
    .section-subtitle {
        color: var(--text-secondary);
        margin-bottom: 1.5rem;
    }
    
    /* Status indicators */
    .status-success {
        color: var(--primary-color);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .status-error {
        color: #ef4444;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .status-warning {
        color: #f59e0b;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Masquer les éléments Streamlit par défaut */
    .stDeployButton {display: none;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Ajustements pour les composants Streamlit */
    .stSelectbox > div > div {
        background-color: var(--bg-secondary);
        border-color: var(--border-color);
        color: var(--text-primary);
    }
    
    .stTextInput > div > div > input {
        background-color: var(--bg-secondary);
        border-color: var(--border-color);
        color: var(--text-primary);
    }
    
    .stButton > button {
        background-color: var(--primary-color) !important;
        color: var(--bg-primary) !important;
        border: none !important;
        border-radius: 2rem !important;
        font-weight: 700 !important;
        padding: 0.75rem 2rem !important;
    }
    
    .stButton > button:hover {
        background-color: #2dd866 !important;
    }
    
    .stDataFrame {
        background-color: var(--bg-secondary);
        border: 1px solid var(--border-color);
        border-radius: 1rem;
    }

    /* Table styling */
    .styled-table {
        background: var(--bg-secondary);
        border: 1px solid var(--border-color);
        border-radius: 1rem;
        overflow: hidden;
        width: 100%;
        margin: 1rem 0;
    }
    
    .styled-table th {
        background: var(--bg-tertiary);
        color: var(--text-primary);
        font-weight: 600;
        padding: 1rem;
        text-align: left;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .styled-table td {
        color: var(--text-secondary);
        padding: 1rem;
        border-top: 1px solid var(--border-color);
    }
    
    .styled-table tbody tr:hover {
        background: rgba(55, 65, 81, 0.5);
    }
    
    .chart-container {
        background: var(--bg-secondary);
        border: 1px solid var(--border-color);
        border-radius: 1rem;
        padding: 1.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class PDFEconomicExtractor:
    def __init__(self, groq_api_key):
        """Initialize the PDF Economic Extractor with Groq API key"""
        try:
            from groq import Groq
            self.client = Groq(api_key=groq_api_key)
        except Exception as e:
            st.error(f"❌ Erreur lors de l'initialisation de Groq: {str(e)}")
            st.info("""
            **Solutions possibles:**
            1. Vérifiez que votre clé API est valide
            2. Vérifiez votre connexion internet
            3. La clé API doit commencer par 'gsk_'
            """)
            raise e
        
        self.tableau_final = []

    def callback_llama_groq(self, bloc):
        """Envoie un bloc à l'API Llama via Groq avec prompt amélioré"""
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

CRITÈRES STRICTS D'EXCLUSION:
• Numéros de téléphone, adresses, codes
• Années isolées (2024, 2025) sans indicateur
• Numéros de page, références
• Données non-économiques
• Valeurs sans contexte économique clair

RÈGLES DE QUALITÉ:
1. SECTEUR OBLIGATOIRE: Spécifiez toujours le secteur (agriculture, industrie, services, etc.)
2. PÉRIODE OBLIGATOIRE: Précisez la période (Q1 2025, T4 2024, etc.)
3. VALEURS EXACTES: Copiez les chiffres exacts du texte
4. CONTEXTE COMPLET: Phrase complète contenant l'indicateur

FORMAT STRICT:
Secteur/Indicateur|Valeur|Période|Phrase_complète

EXEMPLES CORRECTS:
PIB national|4,2%|Q1 2025|L'économie nationale aurait enregistré une progression de 4,2% au premier trimestre 2025
Agriculture|3,1%|Q1 2025|Les activités agricoles ont progressé de 3,1% au premier trimestre
Inflation générale|2,2%|Q1 2025|L'inflation aurait atteint +2,2% au premier trimestre 2025

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
                st.error("⏳ Limite de taux API atteinte. Attendez quelques minutes.")
            elif "api key" in error_msg or "unauthorized" in error_msg:
                st.error("🔑 Clé API invalide. Vérifiez votre clé Groq.")
            elif "network" in error_msg or "connection" in error_msg:
                st.error("🌐 Problème de connexion. Vérifiez votre internet.")
            else:
                st.error(f"❌ Erreur API Groq: {e}")
            return ""

    def analyser_texte_economique(self, llama_response):
        """Analyse la réponse de Llama avec validation stricte"""
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
                
                elif len(colonnes) == 3:
                    terme = colonnes[0].strip()
                    valeur = colonnes[1].strip()
                    phrase = colonnes[2].strip()
                    
                    if self._valider_donnee_simple(terme, valeur, phrase, mots_cles_valides):
                        periode = self._extraire_periode(phrase)
                        
                        tableau.append({
                            "Secteur/Indicateur": terme,
                            "Valeur": valeur,
                            "Période": periode,
                            "Phrase": phrase
                        })
        
        return tableau

    def _valider_donnee_economique(self, secteur_indicateur, valeur, periode, phrase, mots_cles_valides):
        """Validation stricte des données économiques"""
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

    def _valider_donnee_simple(self, terme, valeur, phrase, mots_cles_valides):
        """Validation pour l'ancien format à 3 colonnes"""
        if not terme or not valeur or not phrase:
            return False
        
        if any(mot in terme.lower() for mot in ['terme', 'valeur', 'phrase', 'economic']):
            return False
        
        texte_complet = f"{terme} {phrase}".lower()
        if not any(mot in texte_complet for mot in mots_cles_valides):
            return False
        
        if not re.search(r'-?\d+[,.]?\d*', valeur):
            return False
        
        return True

    def _extraire_periode(self, phrase):
        """Extrait la période/temporalité d'une phrase de façon dynamique"""
        phrase_lower = phrase.lower()
        
        trimestre_patterns = [
            r'(premier trimestre (\d{4})|T1 (\d{4})|Q1 (\d{4}))',
            r'(deuxième trimestre (\d{4})|deuxieme trimestre (\d{4})|T2 (\d{4})|Q2 (\d{4}))',
            r'(troisième trimestre (\d{4})|troisieme trimestre (\d{4})|T3 (\d{4})|Q3 (\d{4}))',
            r'(quatrième trimestre (\d{4})|quatrieme trimestre (\d{4})|T4 (\d{4})|Q4 (\d{4}))'
        ]
        
        for pattern in trimestre_patterns:
            match = re.search(pattern, phrase_lower)
            if match:
                return match.group(1)
        
        mois_patterns = [
            r'(janvier (\d{4}))', r'(février (\d{4}))', r'(fevrier (\d{4}))',
            r'(mars (\d{4}))', r'(avril (\d{4}))', r'(mai (\d{4}))',
            r'(juin (\d{4}))', r'(juillet (\d{4}))', r'(août (\d{4}))', r'(aout (\d{4}))',
            r'(septembre (\d{4}))', r'(octobre (\d{4}))', r'(novembre (\d{4}))', 
            r'(décembre (\d{4}))', r'(decembre (\d{4}))'
        ]
        
        for pattern in mois_patterns:
            match = re.search(pattern, phrase_lower)
            if match:
                return match.group(1)
        
        annee_pattern = r'\b(20[2-3]\d)\b'
        match = re.search(annee_pattern, phrase_lower)
        if match:
            return match.group(1)
        
        frequence_pattern = r'\b(annuel|mensuel|trimestriel|semestriel)\b'
        match = re.search(frequence_pattern, phrase_lower)
        if match:
            return match.group(1)
        
        return "Non spécifiée"

    def extract_text_from_pdf(self, pdf_bytes):
        """Extrait le texte d'un PDF depuis bytes"""
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
        """Nettoie le texte extrait"""
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def decouper_en_blocs(self, text, taille_max=1500):
        """Découpe le texte en blocs de taille maximale"""
        blocs = textwrap.wrap(
            text,
            width=taille_max,
            break_long_words=False,
            break_on_hyphens=False
        )
        return blocs

    def filtrer_donnees_qualite(self, donnees):
        """Filtre les données pour ne garder que les plus pertinentes"""
        donnees_filtrees = []
        
        indicateurs_prioritaires = [
            'pib', 'croissance', 'inflation', 'taux directeur', 'export', 'import',
            'indice', 'change', 'bourse', 'déficit', 'masse monétaire'
        ]
        
        secteurs_importants = [
            'agriculture', 'industrie', 'service', 'manufacture', 'construction',
            'extractive', 'hébergement', 'bancaire', 'financier'
        ]
        
        for donnee in donnees:
            secteur_indicateur = donnee.get('Secteur/Indicateur', '').lower()
            phrase = donnee.get('Phrase', '').lower()
            valeur = donnee.get('Valeur', '')
            
            score = 0
            
            for indicateur in indicateurs_prioritaires:
                if indicateur in secteur_indicateur or indicateur in phrase:
                    score += 2
            
            for secteur in secteurs_importants:
                if secteur in secteur_indicateur or secteur in phrase:
                    score += 1
            
            if '%' in valeur or 'point' in valeur:
                score += 1
            
            if any(mot in phrase for mot in ['trimestre', 'annuel', 'mensuel', '2024', '2025']):
                score += 1
            
            if any(mot in phrase for mot in ['téléphone', 'contact', 'adresse', 'email']):
                score -= 5
            
            if score >= 2:
                donnees_filtrees.append(donnee)
        
        return donnees_filtrees

def test_api_groq(api_key):
    """Teste la connectivité avec l'API Groq"""
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
            return True, "✅ API Groq connectée avec succès"
        else:
            return False, "❌ Réponse vide de l'API"
            
    except Exception as e:
        error_msg = str(e).lower()
        if "api key" in error_msg or "unauthorized" in error_msg:
            return False, "🔑 Clé API invalide. Vérifiez votre clé Groq."
        elif "rate limit" in error_msg:
            return False, "⏳ Limite de taux atteinte. Attendez quelques minutes."
        elif "network" in error_msg or "connection" in error_msg:
            return False, "🌐 Problème de connexion internet."
        else:
            return False, f"❌ Erreur: {str(e)}"

def get_api_key():
    """Récupère la clé API depuis les secrets ou l'input utilisateur"""
    try:
        default_key = st.secrets.get("GROQ_API_KEY", "")
    except:
        default_key = ""
    
    return default_key

def render_header():
    """Affiche le header moderne"""
    st.markdown("""
    <div class="main-header">
        <div class="logo-section">
            <div class="logo-icon">📊</div>
            <h1 class="app-title">DataExtract</h1>
        </div>
        <nav class="nav-menu">
            <a href="#" class="nav-item">Dashboard</a>
            <a href="#" class="nav-item">Extraction</a>
            <a href="#" class="nav-item active">Analysis</a>
            <a href="#" class="nav-item">Settings</a>
        </nav>
    </div>
    """, unsafe_allow_html=True)

def render_metrics_cards(df=None):
    """Affiche les cartes de métriques"""
    if df is not None and not df.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Total Indicators</h3>
                <div class="metric-value">{len(df)}</div>
                <div class="metric-change positive">
                    ↗ +{len(df)} extracted
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            secteurs_uniques = df['Secteur/Indicateur'].nunique()
            st.markdown(f"""
            <div class="metric-card">
                <h3>Unique Sectors</h3>
                <div class="metric-value">{secteurs_uniques}</div>
                <div class="metric-change positive">
                    ↗ Different sectors
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            periodes = df['Période'].value_counts()
            periode_principale = periodes.index[0] if not periodes.empty else "N/A"
            st.markdown(f"""
            <div class="metric-card">
                <h3>Main Period</h3>
                <div class="metric-value" style="font-size: 1.5rem;">{periode_principale}</div>
                <div class="metric-change positive">
                    ↗ Most frequent
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            valeurs_avec_pourcentage = len([v for v in df['Valeur'] if '%' in v])
            st.markdown(f"""
            <div class="metric-card">
                <h3>Growth Rates</h3>
                <div class="metric-value">{valeurs_avec_pourcentage}</div>
                <div class="metric-change positive">
                    ↗ Percentage values
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3>Total Indicators</h3>
                <div class="metric-value">--</div>
                <div class="metric-change">
                    Waiting for analysis
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h3>Sectors Found</h3>
                <div class="metric-value">--</div>
                <div class="metric-change">
                    Upload PDF to start
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card">
                <h3>Time Coverage</h3>
                <div class="metric-value">--</div>
                <div class="metric-change">
                    No data yet
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="metric-card">
                <h3>Data Quality</h3>
                <div class="metric-value">--</div>
                <div class="metric-change">
                    Ready to analyze
                </div>
            </div>
            """, unsafe_allow_html=True)

def create_sector_chart(df):
    """Crée un graphique des secteurs"""
    if df is None or df.empty:
        return None
    
    # Analyser les secteurs
    secteur_counts = {}
    for secteur in df['Secteur/Indicateur']:
        if 'pib' in secteur.lower() or 'croissance' in secteur.lower():
            secteur_counts['Growth/GDP'] = secteur_counts.get('Growth/GDP', 0) + 1
        elif 'inflation' in secteur.lower():
            secteur_counts['Inflation'] = secteur_counts.get('Inflation', 0) + 1
        elif 'taux' in secteur.lower():
            secteur_counts['Interest Rates'] = secteur_counts.get('Interest Rates', 0) + 1
        elif any(word in secteur.lower() for word in ['export', 'import', 'commerce']):
            secteur_counts['Trade'] = secteur_counts.get('Trade', 0) + 1
        elif any(word in secteur.lower() for word in ['indice', 'bourse', 'financier']):
            secteur_counts['Financial Markets'] = secteur_counts.get('Financial Markets', 0) + 1
        elif any(word in secteur.lower() for word in ['agriculture', 'industrie', 'service', 'manufacture']):
            secteur_counts['Economic Sectors'] = secteur_counts.get('Economic Sectors', 0) + 1
        else:
            secteur_counts['Others'] = secteur_counts.get('Others', 0) + 1
    
    if not secteur_counts:
        return None
    
    # Créer le graphique en barres avec Plotly
    fig = go.Figure(data=[
        go.Bar(
            x=list(secteur_counts.keys()),
            y=list(secteur_counts.values()),
            marker_color='#38e07b',
            text=list(secteur_counts.values()),
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title="Distribution of Economic Indicators by Category",
        title_font_color='#ffffff',
        title_font_size=16,
        xaxis_title="Categories",
        yaxis_title="Number of Indicators",
        xaxis_title_font_color='#9ca3af',
        yaxis_title_font_color='#9ca3af',
        xaxis_tickfont_color='#9ca3af',
        yaxis_tickfont_color='#9ca3af',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        margin=dict(l=20, r=20, t=40, b=20),
        height=300
    )
    
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor='#374151', zeroline=False)
    
    return fig

def create_time_series_chart(df):
    """Crée un graphique temporel des indicateurs"""
    if df is None or df.empty:
        return None
    
    # Traiter les données temporelles
    df_time = df.copy()
    df_time['Valeur_Numérique'] = df_time['Valeur'].str.extract(r'(-?\d+\.?\d*)').astype(float, errors='ignore')
    
    # Filtrer les valeurs numériques valides
    df_time = df_time.dropna(subset=['Valeur_Numérique'])
    
    if df_time.empty:
        return None
    
    # Grouper par période
    time_data = df_time.groupby('Période')['Valeur_Numérique'].mean().reset_index()
    
    if len(time_data) < 2:
        return None
    
    # Créer le graphique linéaire
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=time_data['Période'],
        y=time_data['Valeur_Numérique'],
        mode='lines+markers',
        line=dict(color='#38e07b', width=3),
        marker=dict(size=8, color='#38e07b'),
        fill='tonexty',
        fillcolor='rgba(56, 224, 123, 0.1)',
        name='Average Economic Growth'
    ))
    
    fig.update_layout(
        title="Economic Indicators Over Time",
        title_font_color='#ffffff',
        title_font_size=16,
        xaxis_title="Period",
        yaxis_title="Average Value (%)",
        xaxis_title_font_color='#9ca3af',
        yaxis_title_font_color='#9ca3af',
        xaxis_tickfont_color='#9ca3af',
        yaxis_tickfont_color='#9ca3af',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        margin=dict(l=20, r=20, t=40, b=20),
        height=300
    )
    
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor='#374151', zeroline=False)
    
    return fig

def render_data_table(df):
    """Affiche le tableau de données avec style moderne"""
    if df is None or df.empty:
        return
    
    # Limiter à 10 lignes pour l'affichage
    df_display = df.head(10)
    
    # Créer le HTML du tableau
    table_html = """
    <div class="styled-table">
        <table style="width: 100%; border-collapse: collapse;">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Sector/Indicator</th>
                    <th>Value</th>
                    <th>Period</th>
                    <th>Change</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for idx, row in df_display.iterrows():
        # Déterminer la couleur du changement
        valeur = row['Valeur']
        if '%' in valeur and valeur.replace('%', '').replace('+', '').replace('-', '').replace(',', '.').replace(' ', '').isdigit():
            num_val = float(valeur.replace('%', '').replace('+', '').replace('-', '').replace(',', '.'))
            change_class = "positive" if '+' in valeur or num_val > 0 else "negative"
            change_symbol = "↗" if '+' in valeur or num_val > 0 else "↘"
        else:
            change_class = ""
            change_symbol = "—"
        
        table_html += f"""
                <tr>
                    <td>2024-01-15</td>
                    <td style="color: #ffffff; font-weight: 500;">{row['Secteur/Indicateur']}</td>
                    <td style="color: #ffffff;">{row['Valeur']}</td>
                    <td>{row['Période']}</td>
                    <td style="color: {'#38e07b' if change_class == 'positive' else '#ef4444' if change_class == 'negative' else '#9ca3af'};">
                        {change_symbol} {row['Valeur'] if change_class else '—'}
                    </td>
                </tr>
        """
    
    table_html += """
            </tbody>
        </table>
    </div>
    """
    
    st.markdown(table_html, unsafe_allow_html=True)
    
    if len(df) > 10:
        st.markdown(f"<p style='color: #9ca3af; font-size: 0.875rem; margin-top: 1rem;'>Showing 10 of {len(df)} total indicators. Download the complete dataset for full results.</p>", unsafe_allow_html=True)

def render_upload_section():
    """Affiche la section d'upload avec style moderne"""
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        <div style="margin-bottom: 1.5rem;">
            <label style="color: #ffffff; font-weight: 600; margin-bottom: 0.5rem; display: block;">API Key</label>
        </div>
        """, unsafe_allow_html=True)
        
        default_api_key = get_api_key()
        api_key = st.text_input(
            "",
            value=default_api_key,
            type="password",
            placeholder="Enter your Groq API key (gsk_...)",
            label_visibility="collapsed"
        )
        
        if api_key:
            success, message = test_api_groq(api_key)
            if success:
                st.markdown('<div class="status-success">✓ API Connected</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="status-error">✗ Connection Failed</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div style="margin-top: 2rem; margin-bottom: 1.5rem;">
            <label style="color: #ffffff; font-weight: 600; margin-bottom: 0.5rem; display: block;">Upload PDF</label>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "",
            type="pdf",
            label_visibility="collapsed"
        )
        
        if uploaded_file:
            file_size = len(uploaded_file.getvalue())
            st.markdown(f"""
            <div class="status-success" style="margin-top: 1rem;">
                ✓ {uploaded_file.name} uploaded ({file_size:,} bytes)
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card" style="height: 100%;">
            <h3>Analysis Summary</h3>
            <p style="color: #9ca3af; font-size: 0.875rem; line-height: 1.5;">
                Upload your economic PDF document to automatically extract key indicators. 
                Our AI will analyze the content and present structured data with visualizations.
            </p>
            <div style="margin-top: 2rem;">
                <p style="color: #38e07b; font-size: 0.875rem; font-weight: 600;">✓ GDP and Growth Indicators</p>
                <p style="color: #38e07b; font-size: 0.875rem; font-weight: 600;">✓ Inflation and Price Data</p>
                <p style="color: #38e07b; font-size: 0.875rem; font-weight: 600;">✓ Trade and Market Metrics</p>
                <p style="color: #38e07b; font-size: 0.875rem; font-weight: 600;">✓ Sector Performance</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Bouton d'analyse
    analyze_button = st.button(
        "🔍 Analyze PDF",
        disabled=not uploaded_file or not api_key,
        use_container_width=True
    )
    
    return api_key, uploaded_file, analyze_button

def main():
    """Fonction principale de l'application"""
    
    # Affichage du header
    render_header()
    
    # Titre principal
    st.markdown("""
    <h1 class="section-title">Economic Data Analysis</h1>
    <p class="section-subtitle">
        Explore detailed insights from extracted economic data. Upload a PDF to get started with AI-powered analysis.
    </p>
    """, unsafe_allow_html=True)
    
    # Section des métriques (vide au démarrage)
    st.markdown('<h2 class="section-title" style="font-size: 1.25rem;">Data Summary</h2>', unsafe_allow_html=True)
    render_metrics_cards()
    
    # Section d'upload et configuration
    st.markdown('<h2 class="section-title" style="font-size: 1.25rem;">Configuration</h2>', unsafe_allow_html=True)
    api_key, uploaded_file, analyze_button = render_upload_section()
    
    # Traitement et analyse
    if analyze_button and uploaded_file and api_key:
        analyze_pdf_with_modern_ui(uploaded_file, api_key)

def analyze_pdf_with_modern_ui(uploaded_file, api_key):
    """Fonction d'analyse avec interface moderne"""
    
    # Test préliminaire de l'API
    success, message = test_api_groq(api_key)
    if not success:
        st.markdown(f'<div class="status-error">{message}</div>', unsafe_allow_html=True)
        return
    
    # Initialisation
    try:
        extractor = PDFEconomicExtractor(api_key)
    except Exception as e:
        st.markdown(f'<div class="status-error">Failed to initialize: {str(e)}</div>', unsafe_allow_html=True)
        return
    
    # Barre de progression moderne
    progress_container = st.empty()
    status_container = st.empty()
    
    try:
        # Extraction du texte
        status_container.markdown('<div class="status-warning">📖 Extracting text from PDF...</div>', unsafe_allow_html=True)
        progress_container.progress(15)
        
        pdf_bytes = uploaded_file.getvalue()
        texte_brut = extractor.extract_text_from_pdf(pdf_bytes)
        
        if not texte_brut:
            st.markdown('<div class="status-error">❌ Could not extract text from PDF</div>', unsafe_allow_html=True)
            return
        
        # Nettoyage
        status_container.markdown('<div class="status-warning">🧹 Processing and cleaning text...</div>', unsafe_allow_html=True)
        progress_container.progress(25)
        
        texte_propre = extractor.clean_text(texte_brut)
        blocs = extractor.decouper_en_blocs(texte_propre)
        
        # Analyse IA
        status_container.markdown('<div class="status-warning">🤖 AI Analysis in progress...</div>', unsafe_allow_html=True)
        progress_container.progress(35)
        
        total_indicators = 0
        for i, bloc in enumerate(blocs):
            reponse_llama = extractor.callback_llama_groq(bloc)
            
            if reponse_llama:
                donnees_structurees = extractor.analyser_texte_economique(reponse_llama)
                extractor.tableau_final.extend(donnees_structurees)
                total_indicators += len(donnees_structurees)
            
            progress = 35 + (50 * (i + 1) / len(blocs))
            progress_container.progress(int(progress))
        
        # Finalisation
        status_container.markdown('<div class="status-warning">🔍 Filtering and validating data...</div>', unsafe_allow_html=True)
        progress_container.progress(90)
        
        if extractor.tableau_final:
            donnees_filtrees = extractor.filtrer_donnees_qualite(extractor.tableau_final)
            
            if donnees_filtrees:
                df_final = pd.DataFrame(donnees_filtrees)
                df_final = df_final.drop_duplicates(subset=['Secteur/Indicateur', 'Valeur'])
                df_final = df_final.sort_values(['Secteur/Indicateur', 'Période']).reset_index(drop=True)
                
                # Finalisation
                progress_container.progress(100)
                status_container.markdown('<div class="status-success">✅ Analysis completed successfully!</div>', unsafe_allow_html=True)
                
                # Affichage des résultats avec nouvelle UI
                st.markdown('<h2 class="section-title">Analysis Results</h2>', unsafe_allow_html=True)
                
                # Nouvelles métriques avec données
                render_metrics_cards(df_final)
                
                # Graphiques avec gestion alternative
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    st.markdown('<h3 style="color: #ffffff; margin-bottom: 1rem;">Sector Distribution</h3>', unsafe_allow_html=True)
                    sector_chart = create_sector_chart(df_final)
                    if sector_chart is not None:
                        if PLOTLY_AVAILABLE and hasattr(sector_chart, 'show'):
                            st.plotly_chart(sector_chart, use_container_width=True)
                        elif isinstance(sector_chart, pd.DataFrame):
                            st.bar_chart(sector_chart.set_index('Category'), color='#38e07b', height=300)
                    else:
                        st.markdown('<p style="color: #9ca3af; text-align: center; padding: 2rem;">No sector data available</p>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    st.markdown('<h3 style="color: #ffffff; margin-bottom: 1rem;">Time Series</h3>', unsafe_allow_html=True)
                    time_chart = create_time_series_chart(df_final)
                    if time_chart is not None:
                        if PLOTLY_AVAILABLE and hasattr(time_chart, 'show'):
                            st.plotly_chart(time_chart, use_container_width=True)
                        elif isinstance(time_chart, pd.DataFrame):
                            st.line_chart(time_chart, color='#38e07b', height=300)
                    else:
                        st.markdown('<p style="color: #9ca3af; text-align: center; padding: 2rem;">Not enough time series data for chart</p>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Tableau de données
                st.markdown('<h2 class="section-title">Detailed Data Table</h2>', unsafe_allow_html=True)
                render_data_table(df_final)
                
                # Boutons de téléchargement
                col1, col2 = st.columns(2)
                
                with col1:
                    csv_data = df_final.to_csv(index=False, sep=';', encoding='utf-8')
                    st.download_button(
                        label="📄 Download CSV",
                        data=csv_data,
                        file_name=f"economic_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                with col2:
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
                status_container.markdown('<div class="status-warning">No valid indicators found after quality filtering</div>', unsafe_allow_html=True)
        
        else:
            status_container.markdown('<div class="status-warning">No economic indicators detected in the PDF</div>', unsafe_allow_html=True)
    
    except Exception as e:
        status_container.markdown(f'<div class="status-error">Error during analysis: {str(e)}</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()



