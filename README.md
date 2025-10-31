# 🕷️ GrabLang

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> Un langage de domaine spécifique (DSL) moderne et puissant pour l'extraction et l'analyse de données web

GrabLang transforme l'extraction de données web en une expérience intuitive et déclarative. Conçu avec une architecture modulaire séparant parser et exécuteur, il permet de créer des pipelines de scraping complexes avec une syntaxe claire et expressive.

## ✨ Fonctionnalités

- 🌐 **Chargement web intelligent** - Support HTTP/HTTPS avec gestion d'erreurs robuste
- 🎯 **Sélecteurs CSS avancés** - Navigation précise dans la structure HTML
- 🔍 **Extraction par regex** - Patterns personnalisés avec flags et groupes de capture
- 📊 **Filtrage conditionnel** - Conditions complexes sur attributs et contenu
- 🔄 **Pipelines de traitement** - Chaînage d'opérations pour workflows sophistiqués
- 🛠️ **Architecture modulaire** - Parser et exécuteur séparés pour une maintenabilité optimale
- 🐛 **Mode debug avancé** - Diagnostic détaillé avec inspection d'éléments

## 🚀 Installation rapide

### Prérequis
- **Python 3.8+**
- **pip** pour la gestion des dépendances

### Installation

```bash
# Cloner le projet
git clone https://github.com/votre-username/grablang.git
cd grablang

# Installer les dépendances
pip install -r requirements.txt

# Installation en mode développement
pip install -e .
```

### Première utilisation

```bash
# Exécuter un script GrabLang
grablang examples/demo_complete_fixed.grab

# Mode debug pour développement
grablang examples/demo_complete_fixed.grab --debug
```

## 📖 Guide de démarrage

### Hello World GrabLang

```grab
# Charger une page web
LOAD URL "https://example.com"
SAVE main_page

# Extraire tous les liens
USE main_page
SELECT ALL "a"
GET ATTR "href"
SAVE all_links

# Afficher les résultats
PRINT "Liens trouvés :"
PRINT all_links
```

### Exemple avancé : Analyse de blog

```grab
# Chargement et analyse complète d'un blog
LOAD URL "https://blog.example.com"
SAVE blog_page

USE blog_page

# Extraction des titres d'articles
SELECT ALL "h2.post-title"
GET TEXT
SAVE article_titles

# Extraction des dates
SELECT ALL "time"
GET ATTR "datetime"
EXTRACT REGEX "(\d{4}-\d{2}-\d{2})"
SAVE publication_dates

# Extraction des auteurs
SELECT ALL ".author"
GET TEXT
SAVE authors

# Résumé de l'analyse
PRINT "=== ANALYSE DU BLOG ==="
PRINT "Titres :"
PRINT article_titles
PRINT "Dates :"
PRINT publication_dates
PRINT "Auteurs :"
PRINT authors
```

## 🔧 Architecture

GrabLang utilise une architecture moderne séparant les préoccupations :

```
grablang/
├── core/                 # 🧠 Moteur principal
│   ├── parser.py        # 📝 Analyse lexicale et syntaxique
│   ├── executor.py      # ⚙️ Exécution des instructions
│   └── interpreter.py   # 🎯 Coordinateur principal
├── commands/            # 📦 Handlers modulaires
│   ├── load/           # 🌐 Chargement de données
│   ├── selection/      # 🎯 Sélection d'éléments
│   ├── extraction/     # 🔍 Extraction de données
│   ├── filtering/      # 📊 Filtrage conditionnel
│   └── utilities/      # 🛠️ Utilitaires (SAVE, USE, COUNT)
├── utils/              # 🔧 Classes de base et utilitaires
└── cli/               # 🖥️ Interface en ligne de commande
```

## 📚 Référence des commandes

### 🌐 Chargement de données

| Commande | Description | Exemple |
|----------|-------------|---------|
| `LOAD URL` | Charge une page web | `LOAD URL "https://example.com"` |

### 🎯 Sélection et navigation

| Commande | Description | Exemple |
|----------|-------------|---------|
| `USE` | Définit le contexte de travail | `USE page_variable` |
| `SELECT ALL` | Sélectionne tous les éléments | `SELECT ALL "a"` |
| `SELECT FIRST` | Premier élément | `SELECT FIRST ".title"` |
| `SELECT LAST` | Dernier élément | `SELECT LAST "p"` |

### 🔍 Extraction de données

| Commande | Description | Exemple |
|----------|-------------|---------|
| `GET ATTR` | Extrait des attributs HTML | `GET ATTR "href"` |
| `GET TEXT` | Extrait le texte | `GET TEXT` |
| `EXTRACT REGEX` | Extraction par regex | `EXTRACT REGEX "\d+"` |
| `EXTRACT EMAILS` | Extraction d'emails | `EXTRACT EMAILS` |
| `EXTRACT URLS` | Extraction d'URLs | `EXTRACT URLS` |
| `EXTRACT NUMBERS` | Extraction de nombres | `EXTRACT NUMBERS` |

### 📊 Filtrage et conditions

```grab
# Filtrer par attribut
FILTER ALL WHERE attr href NOT NULL

# Filtrer par contenu textuel
FILTER ALL WHERE text CONTAINS "important"

# Filtrer par classe CSS
FILTER ALL WHERE class CONTAINS "active"
```

### 🛠️ Utilitaires

| Commande | Description | Exemple |
|----------|-------------|---------|
| `SAVE` | Sauvegarde le résultat | `SAVE ma_variable` |
| `COUNT` | Compte les éléments | `COUNT` |
| `PRINT` | Affichage normal | `PRINT ma_variable` |
| `PRINT DEV` | Affichage debug | `PRINT DEV ma_variable` |

## 🎨 Exemples d'usage

### 💰 E-commerce : Extraction de prix

```grab
LOAD URL "https://shop.example.com"
SAVE shop_page

USE shop_page
SELECT ALL ".price"
GET TEXT
EXTRACT REGEX "(\d+(?:\.\d{2})?)\s*€"
SAVE product_prices

SELECT ALL ".product-name"
GET TEXT
SAVE product_names

PRINT "=== PRODUITS ET PRIX ==="
PRINT product_names
PRINT product_prices
```

### 📰 Actualités : Analyse de contenu

```grab
LOAD URL "https://news.example.com"
SAVE news_page

USE news_page

# Titres des articles
SELECT ALL "h2.headline"
GET TEXT
SAVE headlines

# Dates de publication  
SELECT ALL "time"
GET ATTR "datetime"
EXTRACT REGEX "(\d{4}-\d{2}-\d{2})"
SAVE dates

# Extraction d'emails de contact
EXTRACT REGEX "\b[\w.-]+@[\w.-]+\.\w+\b"
SAVE contact_emails

PRINT "=== ANALYSE ACTUALITÉS ==="
PRINT headlines
PRINT dates
PRINT contact_emails
```

### 🔗 SEO : Analyse de liens

```grab
LOAD URL "https://example.com"
SAVE main_site

USE main_site

# Liens internes
SELECT ALL "a"
FILTER ALL WHERE attr href NOT NULL
GET ATTR "href"
FILTER ALL WHERE text NOT CONTAINS "http"
SAVE internal_links

# Liens externes
USE main_site
SELECT ALL "a"
GET ATTR "href"
EXTRACT REGEX "https?://([^/]+)"
SAVE external_domains

PRINT "=== ANALYSE SEO ==="
PRINT "Liens internes :"
PRINT internal_links
PRINT "Domaines externes :"
PRINT external_domains
```

## 🧪 Tests et validation

Le projet inclut une suite de tests complète :

```bash
# Lancer les tests
python -m pytest tests/

# Tests avec couverture
python -m pytest tests/ --cov=grablang

# Test d'un script complexe
grablang examples/test_complexe_fonctionnel.grab
```

### Script de test complexe

Le projet inclut un script de test avancé qui valide toutes les fonctionnalités sur le blog DeepMind :

- ✅ **8 504 caractères** de texte analysés
- ✅ **589 divs**, **88 paragraphes** détectés
- ✅ **183 liens**, **157 URLs** extraites
- ✅ **75 nombres**, **113 images** analysées
- ✅ **14 années** trouvées par regex
- ✅ **79 acronymes** identifiés

## 🤝 Contribution

Les contributions sont les bienvenues ! 

### Développement local

```bash
# Fork du projet
git clone https://github.com/votre-fork/grablang.git

# Installation en mode développement
pip install -e .

# Lancer les tests
python -m pytest

# Vérifier le style de code
black grablang/
flake8 grablang/
```

### Ajout de nouvelles commandes

1. Créer le handler dans `grablang/commands/`
2. Implémenter la classe héritant de `BaseCommand`
3. Ajouter les tests correspondants
4. Mettre à jour la documentation

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🙏 Remerciements

- **BeautifulSoup4** pour le parsing HTML robuste
- **Requests** pour la gestion des requêtes HTTP
- La communauté **Python** pour l'écosystème exceptionnel

---

<div align="center">

**[Documentation complète](docs/) • [Exemples avancés](examples/) • [Contribuer](CONTRIBUTING.md)**

</div>