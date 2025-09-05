# pdf-extractor-economique
# 📊 Extracteur PDF Économique

Application Streamlit utilisant l'intelligence artificielle pour extraire automatiquement les indicateurs économiques des documents PDF.

## 🌟 Fonctionnalités

- **Extraction automatique** d'indicateurs économiques (PIB, inflation, taux directeurs, etc.)
- **Intelligence Artificielle** avec Groq/Llama 3.3 70B pour l'analyse de texte
- **Export multi-format** : Excel, CSV
- **Interface web intuitive** avec Streamlit
- **Traitement en temps réel** avec barre de progression
- **Validation automatique** des données extraites

## 📋 Types de données extraites

### Indicateurs économiques supportés :
- **Croissance économique** : PIB national et sectoriel
- **Inflation** : Taux d'inflation général, sectoriel, sous-jacent
- **Politique monétaire** : Taux directeurs, masse monétaire
- **Commerce extérieur** : Exportations/importations en pourcentage
- **Marchés financiers** : Indices boursiers (MASI, etc.), taux de change
- **Secteurs économiques** : Agriculture, industrie, services, construction
- **Finances publiques** : Déficit/excédent budgétaire

### Format de sortie :
```
Secteur/Indicateur | Valeur | Période | Phrase complète
Agriculture | 3.1% | Q1 2025 | Les activités agricoles ont progressé de 3.1% au premier trimestre
```

## 🚀 Accès à l'application

**URL de l'application :** https://economic-pdf-analyzer.streamlit.app

L'application est hébergée sur Streamlit Community Cloud et accessible 24h/24.

## 🔧 Utilisation

### 1. Configuration
- Obtenez une clé API gratuite sur [console.groq.com](https://console.groq.com)
- Entrez votre clé API dans le champ dédié
- Testez la connexion avec le bouton "Tester la connexion API"

### 2. Upload du document
- Glissez-déposez votre fichier PDF dans la zone de téléchargement
- Formats acceptés : PDF (texte, pas d'images scannées)
- Taille maximale : 200 MB

### 3. Analyse
- Cliquez sur "ANALYSER LE PDF"
- Attendez la fin du traitement (2-5 minutes selon la taille)
- Consultez les résultats affichés

### 4. Export des données
- Téléchargez les résultats en format Excel ou CSV
- Les données incluent secteur, valeur, période et phrase source

## 📖 Types de documents recommandés

L'application est optimisée pour analyser :
- **Rapports de banques centrales** (Bank Al-Maghrib, BCE, Fed, etc.)
- **Bulletins économiques officiels**
- **Notes de conjoncture économique**
- **Rapports d'activité économique sectoriels**
- **Études économiques gouvernementales**

## ⚙️ Architecture technique

### Technologies utilisées :
- **Frontend** : Streamlit 1.38+
- **IA** : Groq API (Llama 3.3 70B Versatile)
- **PDF** : PyMuPDF (extraction de texte)
- **Data** : Pandas, OpenPyXL
- **Hébergement** : Streamlit Community Cloud

### Workflow de traitement :
1. **Extraction** : Extraction du texte depuis le PDF
2. **Nettoyage** : Suppression des caractères parasites
3. **Segmentation** : Découpage en blocs de 1500 caractères
4. **Analyse IA** : Traitement par blocs via l'API Groq
5. **Validation** : Filtrage des données selon des critères stricts
6. **Déduplication** : Suppression des doublons
7. **Export** : Génération des fichiers de sortie

## 📊 Qualité des extractions

### Critères de validation :
- Présence de mots-clés économiques validés
- Valeurs numériques cohérentes
- Contexte économique vérifié
- Exclusion des données non pertinentes

### Taux de qualité moyen :
- Documents de banques centrales : 85-95%
- Bulletins économiques : 75-85%
- Rapports sectoriels : 70-80%

## 🔐 Sécurité et confidentialité

- **Clés API** : Stockage sécurisé via Streamlit Secrets
- **Documents** : Traitement en mémoire uniquement (pas de sauvegarde)
- **Données** : Transmission chiffrée HTTPS
- **Accès** : Aucune authentification requise (service public)

## 🔄 Développement et déploiement

### Structure du projet :
```
pdf-extractor-economique/
├── app.py              # Application principale
├── requirements.txt    # Dépendances Python
├── .streamlit/
│   └── config.toml    # Configuration Streamlit
├── README.md          # Cette documentation
└── .gitignore         # Exclusions Git
```

### Installation locale :
```bash
# Cloner le repository
git clone https://github.com/VOTRE-USERNAME/pdf-extractor-economique.git
cd pdf-extractor-economique

# Installer les dépendances
pip install -r requirements.txt

# Configurer les secrets
mkdir .streamlit
echo 'GROQ_API_KEY = "gsk_votre_cle"' > .streamlit/secrets.toml

# Lancer l'application
streamlit run app.py
```

### Dépendances :
```
streamlit
pymupdf
pandas  
openpyxl
groq
```

## 🐛 Résolution de problèmes

### Erreurs fréquentes :

**"Clé API invalide"**
- Vérifiez que la clé commence par `gsk_`
- Régénérez une nouvelle clé sur console.groq.com
- Vérifiez l'absence d'espaces avant/après la clé

**"Impossible d'extraire le texte"**
- Vérifiez que le PDF contient du texte (pas seulement des images)
- Essayez avec un PDF plus récent
- Le document peut être protégé ou corrompu

**"Limite de taux API atteinte"**
- Attendez quelques minutes avant de recommencer
- Limite gratuite Groq : 14,400 requêtes/jour
- Divisez les gros documents en plusieurs parties

**"Aucun indicateur détecté"**
- Vérifiez que le document contient des données économiques chiffrées
- Essayez avec un rapport de banque centrale
- Le document peut ne pas être en français

## 📈 Améliorations futures

### Version 2.0 prévue :
- Support multi-langues (anglais, arabe)
- Analyse de graphiques et tableaux
- API REST pour intégrations externes
- Traitement par lots de plusieurs PDF
- Dashboard analytique avancé
- Export vers bases de données

### Contributions :
Les contributions sont les bienvenues via GitHub Issues et Pull Requests.

## 📞 Support et contact

- **Issues GitHub** : Signalement de bugs et demandes de fonctionnalités
- **Email** : nejmeddinemehamede01@gmail.com
- **Documentation** : Ce fichier README



---

**Version** : 1.0  
**Dernière mise à jour** : Septembre 2025  
**Statut** : Production
