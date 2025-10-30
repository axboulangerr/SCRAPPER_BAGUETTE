# GrabLang 🕷️ - Le PostgreSQL du Web Scraping

**GrabLang** est un langage de domaine spécifique (DSL) conçu pour le web scraping avancé. Inspiré par la puissance et l'expressivité de PostgreSQL, GrabLang offre une syntaxe simple mais extrêmement puissante pour extraire, transformer et analyser des données web.

## 🎯 Vision

Créer un langage de scraping aussi expressif et puissant que PostgreSQL l'est pour les bases de données :
- **Requêtes déclaratives** : Décrivez ce que vous voulez, pas comment l'obtenir
- **Pipeline de transformation** : Chaînez les opérations comme des requêtes SQL
- **Typage intelligent** : Détection automatique des types de données
- **Optimisation automatique** : Le moteur optimise vos requêtes de scraping

## 🚀 Fonctionnalités Actuelles

### 📥 Chargement de Données (LOAD)
```grab
LOAD URL "https://example.com"
LOAD FILE "page.html"
LOAD JSON "data.json"
```

### 🎯 Sélection d'Éléments (SELECT)
```grab
SELECT ALL "div.article"           # Tous les articles
SELECT FIRST "h1"                  # Premier titre
SELECT LAST "img"                  # Dernière image
SELECT ONCE "a" 3                  # Troisième lien (index 1-based)
```

### 🔍 Extraction de Données (GET)
```grab
# Extraction d'attributs
GET ATTR "href"                    # Attributs des éléments sélectionnés
GET ATTR FIRST "a" "href"          # URL du premier lien
GET ATTR LAST "img" "src"          # Source de la dernière image
GET ATTR ONCE "button" 2 "class"   # Classes du 2ème bouton

# Détection intelligente de dates
GET DATE "article"                 # Articles contenant des dates
GET DATE FIRST "span"              # Premier span avec une date
GET DATE LAST "time"               # Dernier élément time avec date
GET DATE ONCE "p" 1                # Vérifie si le 1er paragraphe a une date
```

### 💾 Gestion des Variables (SAVE/USE)
```grab
SELECT ALL "a"
GET ATTR "href"
SAVE all_links                     # Sauvegarde dans une variable

USE all_links                      # Réutilise la variable
FILTER CONTAINS "github"           # Filtre les liens GitHub
SAVE github_links
```

### 🎨 Système de Debug Coloré
- **Mode debug** avec couleurs distinctives pour chaque type de commande
- **Traçabilité complète** de l'exécution
- **Messages d'erreur** précis et contextuels

## 🛣️ Roadmap - Vers la Puissance PostgreSQL

### 🔄 Phase 1 : Transformations (En cours)
```grab
# Filtrage avancé
FILTER WHERE class CONTAINS "active"
FILTER WHERE text MATCHES "^[0-9]+$"
FILTER WHERE attr href NOT NULL

# Extraction de texte
EXTRACT TEXT                       # Contenu textuel
EXTRACT TEXT CLEAN                 # Texte nettoyé (sans espaces extra)
EXTRACT NUMBERS                    # Extraction de nombres
EXTRACT EMAILS                     # Extraction d'emails
EXTRACT URLS                       # Extraction d'URLs dans le texte
```

### 📊 Phase 2 : Agrégations et Analyses
```grab
# Fonctions d'agrégation (comme SQL)
COUNT                              # Nombre d'éléments
COUNT DISTINCT attr href           # URLs uniques
SUM NUMBERS                        # Somme des nombres trouvés
AVG NUMBERS                        # Moyenne des nombres
GROUP BY attr class                # Groupement par classes CSS

# Statistiques avancées
STATS TEXT LENGTH                  # Statistiques de longueur de texte
STATS LINKS                        # Analyse des liens (domaines, types)
STATS IMAGES                       # Analyse des images (formats, tailles)
```

### 🔗 Phase 3 : Relations et Jointures
```grab
# Relations entre éléments (comme JOIN)
RELATE PARENT "div"                # Éléments parents
RELATE CHILDREN "span"             # Éléments enfants
RELATE SIBLINGS "li"               # Éléments frères

# Jointures avec données externes
JOIN WITH FILE "urls.csv" ON href
JOIN WITH API "https://api.example.com" ON id
```

### 🧠 Phase 4 : Intelligence Artificielle
```grab
# Classification automatique
CLASSIFY SENTIMENT                 # Analyse de sentiment
CLASSIFY CATEGORY                  # Catégorisation automatique
CLASSIFY LANGUAGE                  # Détection de langue

# Extraction sémantique
EXTRACT ENTITIES                   # Entités nommées (personnes, lieux)
EXTRACT KEYWORDS                   # Mots-clés importants
EXTRACT SUMMARY                    # Résumé automatique
```

### 📈 Phase 5 : Optimisation et Performance
```grab
# Cache intelligent
CACHE STRATEGY LRU                 # Stratégie de cache
CACHE TTL 3600                     # Time-to-live

# Parallélisation
PARALLEL WORKERS 4                 # Scraping parallèle
BATCH SIZE 100                     # Traitement par lots

# Monitoring
MONITOR PERFORMANCE                # Métriques de performance
MONITOR ERRORS                     # Suivi des erreurs
```

### 🏗️ Phase 6 : Fonctions et Procédures
```grab
# Fonctions personnalisées
FUNCTION extract_price(text)
    EXTRACT NUMBERS
    FILTER WHERE value > 0
    RETURN FIRST
END

# Procédures stockées
PROCEDURE scrape_ecommerce(url)
    LOAD URL url
    SELECT ALL ".product"
    EXTRACT price USING extract_price(text)
    SAVE products
END
```

### 📡 Phase 7 : Intégrations et APIs
```grab
# Intégrations bases de données
OUTPUT TO POSTGRES "postgresql://..."
OUTPUT TO MONGODB "mongodb://..."
OUTPUT TO ELASTICSEARCH "http://..."

# APIs et webhooks
POST TO API "https://api.example.com/data"
WEBHOOK ON ERROR "https://alerts.example.com"

# Formats d'export
EXPORT AS JSON "data.json"
EXPORT AS CSV "data.csv"
EXPORT AS PARQUET "data.parquet"
```

## 🏛️ Architecture

### 🧩 Système Modulaire
- **Handlers dynamiques** : Chaque commande est un module indépendant
- **Chargement automatique** : Découverte automatique des commandes
- **Extensibilité** : Ajout facile de nouvelles fonctionnalités

### 🎨 Système de Types
- **Types primitifs** : string, number, boolean, date
- **Types complexes** : Element, ElementList, URL, Email
- **Types composés** : Table, Graph, Tree
- **Inférence de types** : Détection automatique

### ⚡ Moteur d'Optimisation
- **Plan d'exécution** : Optimisation des requêtes complexes
- **Cache multi-niveaux** : DOM, HTTP, résultats
- **Parallélisation intelligente** : Optimisation automatique

## 💡 Exemples d'Usage

### 🏢 Scraping E-commerce
```grab
LOAD URL "https://shop.example.com/products"
SELECT ALL ".product-card"
GET ATTR "data-product-id"
SAVE product_ids

USE product_ids
FOREACH id
    LOAD URL "https://shop.example.com/product/" + id
    EXTRACT price FROM ".price"
    EXTRACT title FROM "h1"
    EXTRACT rating FROM ".stars"
    SAVE TO products_table
END
```

### 📰 Analyse de News
```grab
LOAD URL "https://news.example.com"
SELECT ALL "article"
FILTER WHERE GET DATE NOT NULL
GET DATE FIRST "time"
EXTRACT headline FROM "h2"
EXTRACT summary FROM ".excerpt"
CLASSIFY SENTIMENT ON summary
GROUP BY sentiment
EXPORT AS JSON "news_analysis.json"
```

### 🔍 Monitoring de Compétition
```grab
PROCEDURE monitor_competitor(url)
    LOAD URL url
    SELECT ALL ".product"
    EXTRACT price USING extract_price(text)
    COMPARE WITH PREVIOUS_RUN
    IF price_change > 5%
        ALERT "Price change detected: " + price_change
    END
END

SCHEDULE DAILY monitor_competitor("https://competitor.com")
```

## 🛠️ Installation et Usage

```bash
# Installation
pip install -r requirements.txt

# Exécution d'un script
python src/core/interpreter.py script/example.grab

# Mode debug
python src/core/interpreter.py script/example.grab --debug
```

## 🎯 Objectifs à Long Terme

1. **Expressivité PostgreSQL** : Toute la puissance des requêtes SQL pour le web
2. **Performance** : Scraping à grande échelle avec optimisations automatiques
3. **Intelligence** : IA intégrée pour la compréhension sémantique
4. **Écosystème** : Bibliothèque de fonctions et connecteurs
5. **Standards** : Format d'échange inter-outils de scraping

## 🤝 Contribution

GrabLang est conçu pour être extensible. Chaque nouvelle fonctionnalité suit l'architecture modulaire :

1. **Créer un handler** dans `src/commands/`
2. **Implémenter les sous-commandes** 
3. **Ajouter les tests** correspondants
4. **Documenter** la nouvelle fonctionnalité

## 📜 Licence

[Votre licence ici]

---

**GrabLang** - *"Query the web like a database"* 🌐💫