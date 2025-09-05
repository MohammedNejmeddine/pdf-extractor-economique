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
    
    /* Tableaux personnalisés */
    .data-table {
        background: var(--bg-secondary);
        border: 1px solid var(--border-color);
        border-radius: 1rem;
        overflow: hidden;
    }
    
    .data-table th {
        background: var(--bg-tertiary);
        color: var(--text-secondary);
        padding: 1rem;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.75rem;
    }
    
    .data-table td {
        padding: 1rem;
        border-top: 1px solid var(--border-color);
        color: var(--text-secondary);
    }
    
    .data-table tr:hover {
        background: rgba(55, 65, 81, 0.5);
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
    
    /* Progress bar personnalisée */
    .custom-progress {
        background: var(--bg-tertiary);
        border-radius: 0.5rem;
        height: 0.5rem;
        overflow: hidden;
        margin: 1rem 0;
    }
    
    .custom-progress-bar {
        background: var(--primary-color);
        height: 100%;
        transition: width 0.3s ease;
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
    }
    
    .stTextInput > div > div > input {
        background-color: var(--bg-secondary);
        border-color: var(--border-color);
        color: var(--text-primary);
    }
    
    .stButton > button {
        background-color: var(--primary-color);
        color: var(--bg-primary);
        border: none;
        border-radius: 2rem;
        font-weight: 700;
        padding: 0.75rem 2rem;
    }
    
    .stButton > button:hover {
        background-color: #2dd866;
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
        elif 'export' in secteur.lower() or 'import' in secteur.lower():
            secteur_counts['Trade'] = secteur_counts.get('Trade', 0) + 1
        elif 'indice' in secteur.lower() or 'bourse' in secteur.lower():
            secteur_counts['Finance'] = secteur_counts.get('Finance', 0) + 1
        elif any(sect in secteur.lower() for sect in ['agriculture', 'industrie', 'service']):
            secteur_counts['Sectors'] = secteur_counts.get('Sectors', 0) + 1
        else:
            secteur_counts['Others'] = secteur_counts.get('Others', 0) + 1
    
    if secteur_counts:
        fig = px.bar(
            x=list(secteur_counts.keys()),
            y=list(secteur_counts.values()),
            title="Distribution by Economic Category",
            color_discrete_sequence=["#38e07b"]
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            title_font_size=16,
            xaxis=dict(gridcolor='#4b5563'),
            yaxis=dict(gridcolor='#4b5563')
        )
        
        return fig
    return None

def main():
    # Rendu du header
    render_header()
    
    # Titre principal
    st.markdown('<h1 class="section-title">Economic Data Analysis</h1>', unsafe_allow_html=True)
    st.markdown('<p class="section


