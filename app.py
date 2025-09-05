import streamlit as st
import fitz
import pandas as pd
from io import BytesIO
import re
import textwrap
from datetime import datetime
import os

# Configuration de la page
st.set_page_config(
    page_title="Extracteur PDF Économique",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour améliorer l'apparence
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f77b4, #2ca02c);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
        font-weight: bold;
    }
    
    .main-header p {
        color: #f0f0f0;
        margin: 0.5rem 0 0 0;
        font-size: 1.2rem;
    }
    
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .status-box {
        padding: 1rem;
        border-radius: 8px;
        border-left: 5px solid #28a745;
        background-color: #d4edda;
        margin: 1rem 0;
    }
    
    .upload-section {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        border: 2px dashed #dee2e6;
        text-align: center;
        margin: 1rem 0;
    }
    
    .feature-box {
        background: linear-gradient(135deg, #74b9ff, #0984e3);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    .api-status {
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.5rem 0;
        text-align: center;
    }
    
    .api-success {
        background-color: #d1ecf1;
        color: #0c5460;
        border: 1px solid #bee5eb;
    }
    
    .api-error {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    
    .progress-section {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    .results-header {
        background: linear-gradient(90deg, #ff7675, #fd79a8);
        color: white;
        padding: 1rem;
        border-radius: 8px 8px 0 0;
        margin-top: 2rem;
    }
    
    div.stButton > button {
        background: linear-gradient(90deg, #00b894, #00cec9);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: all 0.3s;
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
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
            st.error(f"Erreur lors de l'initialisation de Groq: {str(e)}")
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
                st.error("Limite de taux API atteinte. Attendez quelques minutes.")
            elif "api key" in error_msg or "unauthorized" in error_msg:
                st.error("Clé API invalide. Vérifiez votre clé Groq.")
            elif "network" in error_msg or "connection" in error_msg:
                st.error("Problème de connexion. Vérifiez votre internet.")
            else:
                st.error(f"Erreur API Groq: {e}")
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

def analyser_statistiques(df):
    """Analyse statistique des données extraites pour Streamlit"""
    if df.empty:
        return {}
        
    categories = {}
    for secteur in df['Secteur/Indicateur']:
        if 'pib' in secteur.lower() or 'croissance' in secteur.lower():
            categories['Croissance/PIB'] = categories.get('Croissance/PIB', 0) + 1
        elif 'inflation' in secteur.lower() or 'prix' in secteur.lower():
            categories['Inflation/Prix'] = categories.get('Inflation/Prix', 0) + 1
        elif 'taux' in secteur.lower():
            categories['Taux d\'intérêt'] = categories.get('Taux d\'intérêt', 0) + 1
        elif 'export' in secteur.lower() or 'import' in secteur.lower():
            categories['Commerce extérieur'] = categories.get('Commerce extérieur', 0) + 1
        elif 'indice' in secteur.lower() or 'bourse' in secteur.lower():
            categories['Marchés financiers'] = categories.get('Marchés financiers', 0) + 1
        elif any(sect in secteur.lower() for sect in ['agriculture', 'industrie', 'service']):
            categories['Secteurs économiques'] = categories.get('Secteurs économiques', 0) + 1
        else:
            categories['Autres'] = categories.get('Autres', 0) + 1
    
    return categories

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
            return True, "API Groq connectée avec succès"
        else:
            return False, "Réponse vide de l'API"
            
    except Exception as e:
        error_msg = str(e).lower()
        if "api key" in error_msg or "unauthorized" in error_msg:
            return False, "Clé API invalide. Vérifiez votre clé Groq."
        elif "rate limit" in error_msg:
            return False, "Limite de taux atteinte. Attendez quelques minutes."
        elif "network" in error_msg or "connection" in error_msg:
            return False, "Problème de connexion internet."
        else:
            return False, f"Erreur: {str(e)}"

def get_api_key():
    """Récupère la clé API depuis les secrets ou l'input utilisateur"""
    try:
        default_key = st.secrets.get("GROQ_API_KEY", "")
    except:
        default_key = ""
    
    return default_key

def main():
    # En-tête principal avec style personnalisé
    st.markdown("""
    <div class="main-header">
        <h1>📊 Extracteur PDF Économique</h1>
        <p>Analyse automatique par Intelligence Artificielle - Propulsé par Groq AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Configuration dans la sidebar avec style amélioré
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        
        # Récupérer la clé par défaut depuis les secrets
        default_api_key = get_api_key()
        
        # Section API Key avec indicateur de statut
        api_key = st.text_input(
            "🔑 Clé API Groq", 
            value=default_api_key,
            type="password",
            help="Votre clé API Groq pour l'analyse IA",
            placeholder="gsk_..."
        )
        
        # Indicateur de statut de la clé API
        if api_key:
            if api_key == default_api_key and default_api_key:
                st.markdown('<div class="api-status api-success">🔧 Clé API configurée</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="api-status api-success">🔑 Clé API utilisateur active</div>', unsafe_allow_html=True)
            
            # Test de connectivité avec design amélioré
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("🔍 Tester API", type="secondary", use_container_width=True):
                    with st.spinner("Test en cours..."):
                        success, message = test_api_groq(api_key)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
        else:
            st.markdown('<div class="api-status api-error">⚠️ Clé API requise</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Options d'export avec icônes
        format_sortie = st.selectbox(
            "📁 Format d'export", 
            ["Excel", "CSV"],
            help="Choisissez le format de téléchargement"
        )
        
        st.markdown("---")
        
        # Section fonctionnalités avec design attractif
        st.markdown("### 🎯 **Données extraites**")
        
        features = [
            "📈 PIB et croissance",
            "📊 Taux d'inflation", 
            "💰 Politiques monétaires",
            "🌍 Commerce extérieur",
            "📉 Indices boursiers",
            "🏭 Secteurs économiques",
            "💼 Déficit/excédent budgétaire"
        ]
        
        for feature in features:
            st.markdown(f'<div class="feature-box">{feature}</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Guide d'utilisation
        with st.expander("❓ Guide d'utilisation"):
            st.markdown("""
            **Comment utiliser l'application :**
            
            1. **Clé API** : Entrez votre clé Groq (obtenue sur console.groq.com)
            2. **PDF** : Uploadez un document économique (rapport de banque centrale, bulletin économique)
            3. **Analyse** : Cliquez sur "Analyser" et attendez les résultats
            4. **Export** : Téléchargez les données en Excel ou CSV
            
            **Types de documents recommandés :**
            - Rapports de banques centrales
            - Bulletins économiques officiels
            - Notes de conjoncture
            - Rapports d'activité économique
            """)
        
        with st.expander("🔑 Obtenir une clé API Groq"):
            st.markdown("""
            **Gratuit et rapide :**
            1. Visitez https://console.groq.com
            2. Créez un compte gratuit
            3. Allez dans "API Keys" → "Create API Key"
            4. Copiez et collez ici
            
            **Limite gratuite :** 14,400 requêtes/jour
            """)
    
    # Zone principale avec layout amélioré
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="upload-section">
            <h3>📄 Zone de téléchargement</h3>
            <p>Glissez-déposez votre document PDF économique ici</p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "", 
            type="pdf",
            help="Formats acceptés: PDF. Taille max: 200MB",
            label_visibility="collapsed"
        )
        
        if uploaded_file:
            col_info1, col_info2 = st.columns([1, 1])
            
            with col_info1:
                st.markdown(f'<div class="status-box">✅ **{uploaded_file.name}** chargé avec succès</div>', 
                           unsafe_allow_html=True)
            
            with col_info2:
                file_size = len(uploaded_file.getvalue())
                file_size_mb = file_size / (1024 * 1024)
                
                if file_size_mb > 10:
                    st.warning(f"⚠️ Fichier volumineux ({file_size_mb:.1f} MB) - analyse plus lente")
                else:
                    st.info(f"📊 Taille: {file_size_mb:.1f} MB")
    
    with col2:
        st.markdown("### 🚀 Centre de contrôle")
        
        # Statut de l'application
        if not api_key:
            st.markdown('<div class="metric-container">🔑 Clé API requise</div>', unsafe_allow_html=True)
        elif not uploaded_file:
            st.markdown('<div class="metric-container">📄 PDF à sélectionner</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="metric-container">✅ Prêt à analyser</div>', unsafe_allow_html=True)
        
        # Bouton d'analyse principal avec style personnalisé
        analyser = st.button(
            "🔍 ANALYSER LE PDF", 
            type="primary", 
            disabled=not uploaded_file or not api_key,
            use_container_width=True,
            help="Lancer l'analyse IA du document"
        )
        
        # Informations système
        st.markdown("---")
        st.markdown("**ℹ️ Informations système**")
        st.text(f"Modèle IA: Llama 3.3 70B")
        st.text(f"Provider: Groq")
        st.text(f"Date: {datetime.now().strftime('%d/%m/%Y')}")
    
    # Traitement principal
    if analyser and uploaded_file and api_key:
        analyser_pdf_improved(uploaded_file, api_key, format_sortie)

def analyser_pdf_improved(uploaded_file, api_key, format_sortie):
    """Fonction principale d'analyse avec interface améliorée"""
    
    # Test préliminaire de l'API
    success, message = test_api_groq(api_key)
    if not success:
        st.error(f"Impossible de se connecter à l'API Groq: {message}")
        return
    
    # Interface de traitement améliorée
    with st.container():
        st.markdown('<div class="progress-section">', unsafe_allow_html=True)
        st.markdown("### 🔄 Traitement en cours")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        metrics_container = st.container()
        
        try:
            # Initialisation
            status_text.markdown("**🔧 Initialisation de l'extracteur...**")
            extractor = PDFEconomicExtractor(api_key)
            progress_bar.progress(10)
            
            # ÉTAPE 1 : Extraction du texte
            status_text.markdown("**📖 Extraction du texte du PDF...**")
            progress_bar.progress(20)
            
            pdf_bytes = uploaded_file.getvalue()
            texte_brut = extractor.extract_text_from_pdf(pdf_bytes)
            
            if not texte_brut:
                st.error("Impossible d'extraire le texte du PDF")
                st.info("💡 Vérifiez que le PDF contient du texte lisible")
                return
            
            # Métriques d'extraction
            with metrics_container:
                col_m1, col_m2, col_m3 = st.columns(3)
                with col_m1:
                    st.metric("📄 Caractères extraits", f"{len(texte_brut):,}")
                with col_m2:
                    st.metric("📃 Pages estimées", f"{len(texte_brut) // 2000}")
                with col_m3:
                    st.metric("⏱️ Temps estimé", "2-5 min")
            
            # ÉTAPE 2 : Préparation
            status_text.markdown("**🧹 Nettoyage et préparation du texte...**")
            progress_bar.progress(30)
            
            texte_propre = extractor.clean_text(texte_brut)
            blocs = extractor.decouper_en_blocs(texte_propre)
            
            st.info(f"🔢 Texte découpé en **{len(blocs)}** blocs pour analyse optimale")
            
            # ÉTAPE 3 : Analyse IA
            status_text.markdown("**🤖 Analyse IA en cours... (Ne fermez pas cette page)**")
            progress_bar.progress(40)
            
            resultats_container = st.empty()
            
            total_indicators = 0
            for i, bloc in enumerate(blocs):
                status_text.markdown(f"**🤖 Analyse du bloc {i+1}/{len(blocs)} par l'IA...**")
                
                reponse_llama = extractor.callback_llama_groq(bloc)
                
                if reponse_llama:
                    donnees_structurees = extractor.analyser_texte_economique(reponse_llama)
                    extractor.tableau_final.extend(donnees_structurees)
                    total_indicators += len(donnees_structurees)
                    
                    if total_indicators > 0:
                        resultats_container.success(f"🎯 **{total_indicators}** indicateurs économiques détectés")
                
                progress = 40 + (45 * (i + 1) / len(blocs))
                progress_bar.progress(int(progress))
            
            # ÉTAPE 4 : Finalisation
            status_text.markdown("**🔍 Filtrage et validation des données...**")
            progress_bar.progress(90)
            
            if extractor.tableau_final:
                donnees_filtrees = extractor.filtrer_donnees_qualite(extractor.tableau_final)
                
                if donnees_filtrees:
                    df_brut = pd.DataFrame(donnees_filtrees)
                    df_final = df_brut.drop_duplicates(subset=['Secteur/Indicateur', 'Valeur'])
                    df_final = df_final.sort_values(['Secteur/Indicateur', 'Période']).reset_index(drop=True)
                    
                    status_text.markdown("**✅ Analyse terminée avec succès !**")
                    progress_bar.progress(100)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.balloons()
                    
                    # Résultats avec interface améliorée
                    display_results_improved(df_final, df_brut, format_sortie)
                
                else:
                    st.warning("Aucun indicateur valide après filtrage qualité")
                    st.markdown("""
                    **💡 Suggestions pour améliorer les résultats :**
                    - Utilisez un rapport économique officiel
                    - Vérifiez que le PDF contient des données chiffrées
                    - Essayez avec un bulletin de banque centrale
                    """)
            
            else:
                st.warning("Aucun indicateur économique détecté")
                st.markdown("""
                **Le PDF ne semble pas contenir de données économiques exploitables.**
                
                **Types de documents recommandés :**
                - Rapports de banques centrales  
                - Bulletins économiques officiels
                - Notes de conjoncture
                - Rapports d'activité économique
                """)
                
            st.markdown('</div>', unsafe_allow_html=True)
        
        except Exception as e:
            st.error(f"Erreur pendant l'analyse : {str(e)}")
            
            if "api_key" in str(e).lower() or "unauthorized" in str(e).lower():
                st.info("🔑 Problème avec la clé API Groq. Vérifiez qu'elle est valide.")
            elif "rate limit" in str(e).lower():
                st.info("⏳ Limite de taux API atteinte. Attendez quelques minutes.")
            else:
                st.info("💡 Essayez avec un PDF plus petit ou vérifiez votre connexion internet.")

def display_results_improved(df_final, df_brut, format_sortie):
    """Affichage des résultats avec interface moderne"""
    
    # En-tête des résultats
    st.markdown("""
    <div class="results-header">
        <h2>📊 Résultats de l'extraction</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Métriques principales avec design moderne
    col1, col2, col3, col4 = st.columns(4)
    
    duplication_rate = round((1 - len(df_final)/len(df_brut)) * 100, 1)
    
    with col1:
        st.markdown(f"""
        <div class="metric-container">
            <h3>🎯 {len(df_final)}</h3>
            <p>Indicateurs uniques</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        secteurs_uniques = df_final['Secteur/Indicateur'].nunique()
        st.markdown(f"""
        <div class="metric-container">
            <h3>🏭 {secteurs_uniques}</h3>
            <p>Secteurs différents</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        periodes = df_final['Période'].value_counts()
        periode_principale = periodes.index[0] if not periodes.empty else "N/A"
        st.markdown(f"""
        <div class="metric-container">
            <h3>📅 {periode_principale}</h3>
            <p>Période principale</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-container">
            <h3>🧹 {duplication_rate}%</h3>
            <p>Doublons supprimés</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Analyse statistique
    categories = analyser_statistiques(df_final)
    
    if categories:
        st.markdown("### 📈 Répartition par catégorie")
        
        col_chart1, col_chart2 = st.columns([2, 1])
        
        with col_chart1:
            cat_df = pd.DataFrame(list(categories.items()), columns=['Catégorie', 'Nombre'])
            st.bar_chart(cat_df.set_index('Catégorie'), height=300)
        
        with col_chart2:
            for cat, count in categories.items():
                percentage = (count / len(df_final)) * 100
                st.metric(cat, f"{count} ({percentage:.1f}%)")
    
    # Tableau des données avec options de filtrage
    st.markdown("### 📊 Données extraites")
    
    # Filtres
    col_filter1, col_filter2 = st.columns([1, 1])
    
    with col_filter1:
        secteurs_disponibles = ['Tous'] + sorted(df_final['Secteur/Indicateur'].unique().tolist())
        secteur_filtre = st.selectbox("Filtrer par secteur", secteurs_disponibles)
    
    with col_filter2:
        periodes_disponibles = ['Toutes'] + sorted(df_final['Période'].unique().tolist())
        periode_filtre = st.selectbox("Filtrer par période", periodes_disponibles)
    
    # Application des filtres
    df_affichage = df_final.copy()
    
    if secteur_filtre != 'Tous':
        df_affichage = df_affichage[df_affichage['Secteur/Indicateur'] == secteur_filtre]
    
    if periode_filtre != 'Toutes':
        df_affichage = df_affichage[df_affichage['Période'] == periode_filtre]
    
    # Affichage du tableau avec style
    st.dataframe(
        df_affichage,
        use_container_width=True,
        height=400,
        column_config={
            "Secteur/Indicateur": st.column_config.TextColumn("Secteur/Indicateur", width="medium"),
            "Valeur": st.column_config.TextColumn("Valeur", width="small"),
            "Période": st.column_config.TextColumn("Période", width="small"),
            "Phrase": st.column_config.TextColumn("Phrase", width="large")
        }
    )
    
    # Boutons de téléchargement avec design amélioré
    st.markdown("### 💾 Téléchargement des données")
    
    col_dl1, col_dl2, col_dl3 = st.columns([1, 1, 1])
    
    with col_dl1:
        if format_sortie == "Excel" or st.button("📊 Excel", use_container_width=True):
            excel_buffer = BytesIO()
            df_final.to_excel(excel_buffer, index=False, engine='openpyxl')
            excel_buffer.seek(0)
            
            st.download_button(
                label="📥 Télécharger Excel",
                data=excel_buffer,
                file_name=f"donnees_economiques_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
    
    with col_dl2:
        csv_data = df_final.to_csv(index=False, sep=';', encoding='utf-8')
        st.download_button(
            label="📄 Télécharger CSV",
            data=csv_data,
            file_name=f"donnees_economiques_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col_dl3:
        # Option bonus : téléchargement JSON
        json_data = df_final.to_json(orient='records', force_ascii=False, indent=2)
        st.download_button(
            label="⚡ Télécharger JSON",
            data=json_data,
            file_name=f"donnees_economiques_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    # Analyse détaillée dans un expander stylisé
    with st.expander("📈 Analyse statistique avancée", expanded=False):
        col_stat1, col_stat2 = st.columns([1, 1])
        
        with col_stat1:
            st.markdown("**Répartition temporelle**")
            periodes_counts = df_final['Période'].value_counts()
            if len(periodes_counts) > 0:
                st.bar_chart(periodes_counts)
        
        with col_stat2:
            st.markdown("**Statistiques détaillées**")
            st.write(f"• Total d'indicateurs bruts: {len(df_brut)}")
            st.write(f"• Indicateurs après filtrage: {len(df_final)}")
            st.write(f"• Taux de qualité: {(len(df_final)/len(df_brut)*100):.1f}%")
            st.write(f"• Nombre de secteurs uniques: {df_final['Secteur/Indicateur'].nunique()}")
            st.write(f"• Nombre de périodes uniques: {df_final['Période'].nunique()}")
    
    # Aperçu détaillé stylisé
    with st.expander("🔍 Aperçu détaillé des données", expanded=False):
        for idx, row in df_final.head(5).iterrows():
            with st.container():
                st.markdown(f"""
                **{idx + 1}. {row['Secteur/Indicateur']}** : `{row['Valeur']}` *({row['Période']})*
                
                > {row['Phrase'][:200]}{'...' if len(row['Phrase']) > 200 else ''}
                """)
                st.markdown("---")
        
        if len(df_final) > 5:
            st.info(f"... et {len(df_final) - 5} autres indicateurs dans le fichier complet")

if __name__ == "__main__":
    main()
