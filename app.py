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
    layout="wide"
)

class PDFEconomicExtractor:
    def __init__(self, groq_api_key):
        """Initialize the PDF Economic Extractor with Groq API key"""
        try:
            # Approche simplifiée et robuste pour initialiser Groq
            from groq import Groq
            
            # Méthode 1: Initialisation directe
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
            
            # Appel API simple et robuste
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
        
        # Mots-clés pour valider les termes économiques
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
                    
                    # Validation stricte
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
        
        # Patterns pour trimestres
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
        
        # Patterns pour mois
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
        
        # Années isolées
        annee_pattern = r'\b(20[2-3]\d)\b'
        match = re.search(annee_pattern, phrase_lower)
        if match:
            return match.group(1)
        
        # Fréquences générales
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
        
        # Test simple
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
    # Essayer d'abord depuis les secrets Streamlit
    try:
        default_key = st.secrets.get("GROQ_API_KEY", "")
    except:
        default_key = ""
    
    return default_key

# Interface utilisateur principale
def main():
    st.title("📊 Extracteur de Données Économiques PDF")
    st.markdown("*Analyse automatique par Intelligence Artificielle*")
    st.markdown("---")
    
    # Configuration dans la sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Récupérer la clé par défaut depuis les secrets
        default_api_key = get_api_key()
        
        # Clé API avec valeur par défaut si disponible
        api_key = st.text_input(
            "🔑 Clé API Groq", 
            value=default_api_key,
            type="password",
            help="Votre clé API Groq pour l'analyse IA",
            placeholder="gsk_..."
        )
        
        # Afficher le statut de la clé
        if api_key:
            if api_key == default_api_key and default_api_key:
                st.info("🔧 Clé API chargée depuis la configuration")
            else:
                st.info("🔑 Clé API utilisateur")
        
        # Test de connectivité
        if api_key:
            if st.button("🔍 Tester la connexion API"):
                with st.spinner("Test en cours..."):
                    success, message = test_api_groq(api_key)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
        
        with st.expander("❓ Comment obtenir une clé API Groq ?"):
            st.markdown("""
            **Gratuit et rapide :**
            1. Visitez https://console.groq.com
            2. Créez un compte gratuit
            3. Allez dans "API Keys" → "Create API Key"
            4. Copiez et collez ici
            
            **Limite gratuite :** 14,400 requêtes/jour
            """)
        
        st.markdown("---")
        
        format_sortie = st.selectbox("📁 Format d'export", ["Excel", "CSV"])
        
        st.markdown("### 📋 **Données extraites**")
        st.markdown("""
        ✅ **PIB et croissance**  
        ✅ **Taux d'inflation**  
        ✅ **Politiques monétaires**  
        ✅ **Commerce extérieur**  
        ✅ **Indices boursiers**  
        ✅ **Secteurs économiques**  
        ✅ **Déficit/excédent budgétaire**
        """)
    
    # Zone principale
    col1, col2 = st.columns([1.2, 0.8])
    
    with col1:
        st.subheader("📄 Fichier PDF à analyser")
        uploaded_file = st.file_uploader(
            "Glissez-déposez votre fichier PDF", 
            type="pdf",
            help="Rapports économiques, bulletins de banque centrale, etc."
        )
        
        if uploaded_file:
            st.success(f"✅ **{uploaded_file.name}** chargé")
            
            file_size = len(uploaded_file.getvalue())
            if file_size > 10*1024*1024:
                st.warning("⚠️ Fichier volumineux - analyse plus lente")
            else:
                st.info(f"📊 Taille: {file_size:,} bytes")
    
    with col2:
        st.subheader("🚀 Traitement")
        
        if not api_key:
            st.warning("🔑 Clé API requise")
        elif not uploaded_file:
            st.info("📄 Sélectionnez un PDF")
        else:
            st.success("✅ Prêt à analyser")
        
        analyser = st.button(
            "🔍 ANALYSER LE PDF", 
            type="primary", 
            disabled=not uploaded_file or not api_key,
            use_container_width=True
        )
    
    # Traitement principal
    if analyser and uploaded_file and api_key:
        analyser_pdf(uploaded_file, api_key, format_sortie)

def analyser_pdf(uploaded_file, api_key, format_sortie):
    """Fonction principale d'analyse du PDF"""
    
    # Test préliminaire de l'API
    success, message = test_api_groq(api_key)
    if not success:
        st.error(f"❌ Impossible de se connecter à l'API Groq: {message}")
        return
    
    with st.spinner("🔧 Initialisation de l'extracteur..."):
        try:
            extractor = PDFEconomicExtractor(api_key)
        except Exception as e:
            st.error(f"❌ Erreur d'initialisation : {str(e)}")
            return
    
    process_container = st.container()
    
    with process_container:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # ÉTAPE 1 : Extraction du texte
            status_text.text("📖 Extraction du texte du PDF...")
            progress_bar.progress(15)
            
            pdf_bytes = uploaded_file.getvalue()
            texte_brut = extractor.extract_text_from_pdf(pdf_bytes)
            
            if not texte_brut:
                st.error("❌ Impossible d'extraire le texte du PDF")
                st.info("💡 Vérifiez que le PDF contient du texte (pas seulement des images)")
                return
            
            st.info(f"📄 Texte extrait : **{len(texte_brut):,}** caractères")
            
            # ÉTAPE 2 : Nettoyage
            status_text.text("🧹 Nettoyage et préparation du texte...")
            progress_bar.progress(25)
            
            texte_propre = extractor.clean_text(texte_brut)
            blocs = extractor.decouper_en_blocs(texte_propre)
            
            st.info(f"🔢 Texte découpé en **{len(blocs)}** blocs pour analyse")
            
            # ÉTAPE 3 : Analyse IA par blocs
            status_text.text(f"🤖 Analyse IA en cours...")
            progress_bar.progress(35)
            
            resultats_container = st.empty()
            
            total_indicators = 0
            for i, bloc in enumerate(blocs):
                status_text.text(f"🤖 Analyse du bloc {i+1}/{len(blocs)}...")
                
                reponse_llama = extractor.callback_llama_groq(bloc)
                
                if reponse_llama:
                    donnees_structurees = extractor.analyser_texte_economique(reponse_llama)
                    extractor.tableau_final.extend(donnees_structurees)
                    total_indicators += len(donnees_structurees)
                    
                    if total_indicators > 0:
                        resultats_container.info(f"🎯 **{total_indicators}** indicateurs trouvés jusqu'à présent...")
                
                progress = 35 + (50 * (i + 1) / len(blocs))
                progress_bar.progress(int(progress))
            
            # ÉTAPE 4 : Filtrage et finalisation
            status_text.text("🔍 Filtrage et validation des données...")
            progress_bar.progress(85)
            
            if extractor.tableau_final:
                donnees_filtrees = extractor.filtrer_donnees_qualite(extractor.tableau_final)
                
                if donnees_filtrees:
                    df_brut = pd.DataFrame(donnees_filtrees)
                    df_final = df_brut.drop_duplicates(subset=['Secteur/Indicateur', 'Valeur'])
                    df_final = df_final.sort_values(['Secteur/Indicateur', 'Période']).reset_index(drop=True)
                    
                    status_text.text("✅ Analyse terminée avec succès !")
                    progress_bar.progress(100)
                    
                    st.balloons()
                    
                    col_success1, col_success2 = st.columns(2)
                    
                    with col_success1:
                        st.success(f"🎉 **{len(df_final)} indicateurs** uniques extraits")
                    
                    with col_success2:
                        duplication_rate = round((1 - len(df_final)/len(df_brut)) * 100, 1)
                        st.info(f"🧹 **{duplication_rate}%** de doublons supprimés")
                    
                    # Affichage des résultats
                    st.markdown("---")
                    st.subheader("📊 Données Économiques Extraites")
                    
                    categories = analyser_statistiques(df_final)
                    
                    if categories:
                        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
                        
                        with col_stat1:
                            st.metric("📈 Total indicateurs", len(df_final))
                        
                        with col_stat2:
                            secteurs_uniques = df_final['Secteur/Indicateur'].nunique()
                            st.metric("🏭 Secteurs différents", secteurs_uniques)
                        
                        with col_stat3:
                            periodes = df_final['Période'].value_counts()
                            if not periodes.empty:
                                st.metric("📅 Période principale", periodes.index[0])
                        
                        with col_stat4:
                            cat_principale = max(categories, key=categories.get)
                            st.metric("📋 Catégorie principale", cat_principale)
                    
                    st.dataframe(df_final, use_container_width=True, height=400)
                    
                    # Boutons de téléchargement
                    col_dl1, col_dl2 = st.columns(2)
                    
                    if format_sortie == "Excel":
                        with col_dl1:
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
                    
                    # Analyse détaillée dans un expander
                    with st.expander("📈 Analyse statistique détaillée"):
                        if categories:
                            st.subheader("Répartition par catégorie")
                            
                            cat_df = pd.DataFrame(list(categories.items()), columns=['Catégorie', 'Nombre'])
                            st.bar_chart(cat_df.set_index('Catégorie'))
                            
                            st.subheader("Répartition par période")
                            periodes_counts = df_final['Période'].value_counts()
                            if len(periodes_counts) > 0:
                                st.write(periodes_counts.to_dict())
                    
                    # Aperçu détaillé
                    with st.expander("🔍 Aperçu détaillé des données"):
                        for idx, row in df_final.head(10).iterrows():
                            st.markdown(f"""
                            **{idx + 1}. {row['Secteur/Indicateur']}** : `{row['Valeur']}` *({row['Période']})*
                            > {row['Phrase'][:120]}{'...' if len(row['Phrase']) > 120 else ''}
                            """)
                            st.markdown("---")
                        
                        if len(df_final) > 10:
                            st.info(f"... et {len(df_final) - 10} autres indicateurs dans le fichier complet")
                
                else:
                    st.warning("😔 Aucun indicateur valide après filtrage qualité")
                    st.info("""
                    **Suggestions pour améliorer les résultats :**
                    - Utilisez un rapport économique officiel
                    - Vérifiez que le PDF contient des données chiffrées
                    - Essayez avec un bulletin de banque centrale
                    """)
            
            else:
                st.warning("😔 Aucun indicateur économique détecté")
                st.info("""
                **Le PDF ne semble pas contenir de données économiques exploitables.**
                
                **Types de documents recommandés :**
                - Rapports de banques centrales
                - Bulletins économiques officiels
                - Notes de conjoncture
                - Rapports d'activité économique
                """)
        
        except Exception as e:
            st.error(f"❌ Erreur pendant l'analyse : {str(e)}")
            
            if "api_key" in str(e).lower() or "unauthorized" in str(e).lower():
                st.info("🔑 Problème avec la clé API Groq. Vérifiez qu'elle est valide.")
            elif "rate limit" in str(e).lower():
                st.info("⏳ Limite de taux API atteinte. Attendez quelques minutes avant de réessayer.")
            else:
                st.info("💡 Essayez de réduire la taille du PDF ou de vérifier votre connexion internet.")

if __name__ == "__main__":
    main()