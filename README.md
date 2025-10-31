# GrabLang - Langage DSL pour l'extraction de données web

**GrabLang** est un langage de domaine spécifique (DSL) conçu pour l'extraction et l'analyse de données web de manière intuitive et puissante. Il permet de charger des pages web, de naviguer dans leur structure HTML, d'extraire des données et d'appliquer des filtres complexes.

## 🚀 Installation et utilisation

### Prérequis
- Python 3.8+
- Modules listés dans `requirements.txt`

### Installation
```bash
pip install -r requirements.txt
```

### Exécution d'un script
```bash
python src/core/interpreter.py script/mon_script.grab
python src/core/interpreter.py script/mon_script.grab --debug
```

## 📋 Fonctionnalités du langage

### 1. **Chargement de données (LOAD)**

#### LOAD URL
Charge le contenu HTML d'une URL dans une variable.

```grab
# Charge une URL dans une variable nommée
LOAD URL ma_page "https://example.com"

# Charge directement (stockage automatique)
LOAD URL "https://example.com"
```

**Syntaxe :**
- `LOAD URL variable_name "url"`
- `LOAD URL "url"`

---

### 2. **Navigation et contexte (USE)**

#### USE
Définit le document HTML de travail pour les opérations suivantes.

```grab
# Utilise une page précédemment chargée
USE ma_page

# Toutes les commandes SELECT, FILTER, etc. opèrent sur 'ma_page'
```

**Syntaxe :**
- `USE variable_name`

---

### 3. **Sélection d'éléments (SELECT)**

#### SELECT ALL
Sélectionne tous les éléments correspondant à un sélecteur CSS.

```grab
# Sélectionne tous les liens
SELECT ALL "a"

# Sélectionne tous les paragraphes
SELECT ALL "p"

# Sélectionne par classe CSS
SELECT ALL ".ma-classe"

# Sélectionne par ID
SELECT ALL "#mon-id"
```

#### SELECT FIRST
Sélectionne le premier élément correspondant.

```grab
# Premier div de la page
SELECT FIRST "div"

# Premier élément avec une classe spécifique
SELECT FIRST ".navigation"
```

#### SELECT LAST
Sélectionne le dernier élément correspondant.

```grab
# Dernier paragraphe
SELECT LAST "p"

# Dernier lien
SELECT LAST "a"
```

#### SELECT ONCE
Sélectionne un élément à un index spécifique (indexation à partir de 1).

```grab
# 5ème élément div
SELECT ONCE 5 "div"

# 3ème image
SELECT ONCE 3 "img"
```

**Syntaxe :**
- `SELECT ALL "selecteur"`
- `SELECT FIRST "selecteur"`
- `SELECT LAST "selecteur"`
- `SELECT ONCE index "selecteur"`

---

### 4. **Filtrage d'éléments (FILTER)**

Les commandes FILTER permettent d'affiner une sélection existante selon des critères.

#### FILTER ALL
Filtre tous les éléments qui correspondent à une condition.

```grab
# Garde seulement les liens avec un attribut href
SELECT ALL "a"
FILTER ALL WHERE attr href NOT NULL

# Garde les éléments contenant un texte spécifique
SELECT ALL "p"
FILTER ALL WHERE text CONTAINS "important"

# Garde les éléments avec une classe spécifique
SELECT ALL "div"
FILTER ALL WHERE class CONTAINS "active"
```

#### FILTER FIRST
Garde seulement le premier élément qui correspond à la condition.

```grab
# Premier lien externe
SELECT ALL "a"
FILTER FIRST WHERE attr href CONTAINS "http"
```

#### FILTER LAST
Garde seulement le dernier élément qui correspond à la condition.

```grab
# Dernier élément avec du texte
SELECT ALL "span"
FILTER LAST WHERE text MATCHES ".+"
```

#### FILTER ONCE
Garde un élément spécifique parmi ceux qui correspondent.

```grab
# 3ème élément contenant du texte
SELECT ALL "p"
FILTER ONCE 3 WHERE text NOT EMPTY
```

**Conditions de filtrage :**
- `attr attribut EQUALS "valeur"` - Attribut égal à une valeur
- `attr attribut CONTAINS "texte"` - Attribut contient du texte
- `attr attribut NOT NULL` - Attribut existe
- `class CONTAINS "classe"` - Classe CSS contient une valeur
- `text CONTAINS "texte"` - Texte contient une chaîne
- `text MATCHES "regex"` - Texte correspond à une regex
- `text NOT EMPTY` - Texte non vide
- `text EQUALS "valeur"` - Texte égal à une valeur

**Syntaxe :**
- `FILTER ALL WHERE condition`
- `FILTER FIRST WHERE condition`
- `FILTER LAST WHERE condition`
- `FILTER ONCE index WHERE condition`

---

### 5. **Extraction de données (GET)**

#### GET ATTR
Extrait des attributs HTML des éléments sélectionnés.

```grab
# Récupère tous les attributs href des liens
SELECT ALL "a"
GET ATTR "href"

# Récupère les attributs src des images
SELECT ALL "img"
GET ATTR "src"

# Récupère les attributs alt des images
SELECT ALL "img"
GET ATTR "alt"
```

#### GET ATTR_FIRST / GET ATTR_LAST / GET ATTR_ONCE
Extrait l'attribut du premier/dernier/nième élément.

```grab
# Premier href
SELECT ALL "a"
GET ATTR_FIRST "href"

# Dernier src d'image
SELECT ALL "img"
GET ATTR_LAST "src"

# 5ème attribut href
SELECT ALL "a"
GET ATTR_ONCE 5 "href"
```

#### GET TEXT
Extrait le texte des éléments sélectionnés.

```grab
# Texte de tous les paragraphes
SELECT ALL "p"
GET TEXT

# Texte des titres
SELECT ALL "h1, h2, h3"
GET TEXT
```

#### GET DATE
Extrait et parse des dates depuis les éléments.

```grab
# Dates depuis les éléments time
SELECT ALL "time"
GET DATE

# Première date trouvée
SELECT ALL "span"
GET DATE_FIRST
```

**Syntaxe :**
- `GET ATTR "attribut"`
- `GET ATTR_FIRST "attribut"`
- `GET ATTR_LAST "attribut"`
- `GET ATTR_ONCE index "attribut"`
- `GET TEXT`
- `GET DATE`
- `GET DATE_FIRST`
- `GET DATE_LAST`
- `GET DATE_ONCE index`

---

### 6. **Extraction par expressions régulières (EXTRACT)**

#### EXTRACT REGEX
Extrait du contenu en utilisant des expressions régulières.

```grab
# Extraction d'URLs
USE ma_page
EXTRACT REGEX "https?://[^\s]+"

# Extraction d'emails
EXTRACT REGEX "\b\w+@\w+\.\w+\b"

# Extraction de numéros de téléphone français
EXTRACT REGEX "0[1-9](?:[0-9\s.-]{8,})"

# Extraction de prix
EXTRACT REGEX "(\d+(?:\.\d{2})?)\s*[€$£]"

# Extraction de dates DD/MM/YYYY
EXTRACT REGEX "(\d{1,2})[/-](\d{1,2})[/-](\d{4})"

# Extraction avec flags (insensible à la casse)
EXTRACT REGEX "\b[A-Z]{2,}\b" i

# Extraction multiline avec flags
EXTRACT REGEX "<script[^>]*>(.*?)</script>" ms
```

**Flags disponibles :**
- `i` - Insensible à la casse (IGNORECASE)
- `m` - Mode multiline (MULTILINE)
- `s` - Le point correspond aux retours à la ligne (DOTALL)
- `x` - Mode verbose (VERBOSE)
- `a` - Mode ASCII (ASCII)

#### EXTRACT EMAILS
Extraction spécialisée d'adresses email.

```grab
EXTRACT EMAILS
```

#### EXTRACT URLS
Extraction spécialisée d'URLs.

```grab
EXTRACT URLS
```

#### EXTRACT NUMBERS
Extraction de nombres.

```grab
EXTRACT NUMBERS
```

**Syntaxe :**
- `EXTRACT REGEX "pattern"`
- `EXTRACT REGEX "pattern" flags`
- `EXTRACT EMAILS`
- `EXTRACT URLS`
- `EXTRACT NUMBERS`

---

### 7. **Sauvegarde et gestion des variables (SAVE)**

#### SAVE
Sauvegarde le résultat de la dernière opération dans une variable.

```grab
# Sauvegarde une sélection
SELECT ALL "a"
SAVE tous_les_liens

# Sauvegarde une extraction
EXTRACT REGEX "\d+"
SAVE nombres_extraits

# Sauvegarde un filtrage
SELECT ALL "p"
FILTER ALL WHERE text NOT EMPTY
SAVE paragraphes_avec_texte
```

**Syntaxe :**
- `SAVE variable_name`

---

### 8. **Affichage et debugging (PRINT)**

#### PRINT
Affiche le contenu d'une variable ou un texte littéral.

```grab
# Affichage d'un texte littéral
PRINT "=== ANALYSE DES LIENS ==="
PRINT "Début du traitement"

# Affichage d'une variable (mode normal)
PRINT ma_variable

# Affichage détaillé pour debugging (mode développeur)
PRINT DEV ma_variable
```

**Formats d'affichage :**
- **Texte littéral** : Affichage direct du texte
- **Mode normal** : Résumé de la variable (type, nombre d'éléments, aperçu)
- **Mode DEV** : Affichage détaillé avec structure, attributs, statistiques

**Syntaxe :**
- `PRINT "texte littéral"`
- `PRINT variable_name`
- `PRINT DEV variable_name`

---

## 🔄 Chaînage d'opérations

GrabLang permet de chaîner les opérations pour créer des pipelines de traitement complexes :

```grab
# Pipeline complexe : Charge → Sélectionne → Filtre → Extrait → Sauvegarde
LOAD URL site "https://example.com"
USE site
SELECT ALL "a"
FILTER ALL WHERE attr href CONTAINS "blog"
GET ATTR "href"
EXTRACT REGEX "/([^/]+)/?$"
SAVE blog_slugs
PRINT "Slugs de blog extraits :"
PRINT blog_slugs
```

### Exemples de chaînages courants

#### Extraction d'informations de liens
```grab
USE ma_page
SELECT ALL "a"
FILTER ALL WHERE attr href NOT NULL
GET ATTR "href"
EXTRACT REGEX "https://([^/]+)"
SAVE domaines
```

#### Analyse de contenu textuel
```grab
SELECT ALL "p"
FILTER ALL WHERE text NOT EMPTY
GET TEXT
EXTRACT REGEX "\b[A-Z][a-z]+\b"
SAVE mots_capitalises
```

#### Extraction de métadonnées
```grab
SELECT ALL "meta"
FILTER ALL WHERE attr name EQUALS "keywords"
GET ATTR "content"
SAVE meta_keywords
```

---

## 📝 Structure d'un script GrabLang

### Script basique
```grab
# Commentaires commencent par #
# Charge une page web
LOAD URL ma_page "https://example.com"

# Utilise cette page pour les opérations
USE ma_page

# Sélectionne tous les liens
SELECT ALL "a"
SAVE tous_les_liens

# Affiche le résultat
PRINT "Liens trouvés :"
PRINT tous_les_liens
```

### Script avancé avec analyses multiples
```grab
# =================================================================
# SCRIPT D'ANALYSE COMPLETE
# =================================================================

# Chargement de données
LOAD URL site "https://example.com"
LOAD URL blog "https://blog.example.com"

PRINT "=== ANALYSE DU SITE PRINCIPAL ==="
USE site

# Analyse des liens
SELECT ALL "a"
FILTER ALL WHERE attr href NOT NULL
GET ATTR "href"
SAVE liens_site
PRINT "Liens du site :"
PRINT liens_site

# Extraction d'emails
EXTRACT REGEX "\b\w+@\w+\.\w+\b"
SAVE emails_site
PRINT "Emails trouvés :"
PRINT emails_site

PRINT "=== ANALYSE DU BLOG ==="
USE blog

# Analyse des articles
SELECT ALL "article"
SAVE articles_blog
PRINT DEV articles_blog

# Extraction des titres
SELECT ALL "h1, h2"
GET TEXT
SAVE titres_blog
PRINT "Titres des articles :"
PRINT titres_blog

PRINT "=== FIN DE L'ANALYSE ==="
```

---

## 🛠️ Exemples d'utilisation

### Extraction de données e-commerce
```grab
LOAD URL shop "https://shop.example.com/products"
USE shop

# Extraction des prix
SELECT ALL ".price"
GET TEXT
EXTRACT REGEX "(\d+(?:\.\d{2})?)\s*€"
SAVE prix_produits

# Extraction des noms de produits
SELECT ALL ".product-title"
GET TEXT
SAVE noms_produits

PRINT "Produits et prix extraits :"
PRINT prix_produits
PRINT noms_produits
```

### Analyse de contenu d'actualités
```grab
LOAD URL news "https://news.example.com"
USE news

# Extraction des titres d'articles
SELECT ALL "h2.article-title"
GET TEXT
SAVE titres_actualites

# Extraction des dates de publication
SELECT ALL "time"
GET ATTR "datetime"
EXTRACT REGEX "(\d{4}-\d{2}-\d{2})"
SAVE dates_publication

# Extraction des auteurs
SELECT ALL ".author"
GET TEXT
EXTRACT REGEX "Par\s+(.+)"
SAVE auteurs

PRINT "Analyse des actualités :"
PRINT titres_actualites
PRINT dates_publication
PRINT auteurs
```

### Extraction de données de contact
```grab
LOAD URL contact "https://example.com/contact"
USE contact

# Emails
EXTRACT REGEX "\b[\w.-]+@[\w.-]+\.\w+\b"
SAVE emails_contact

# Téléphones
EXTRACT REGEX "0[1-9](?:[0-9\s.-]{8,})"
SAVE telephones_contact

# Adresses
SELECT ALL ".address"
GET TEXT
SAVE adresses_contact

PRINT "Informations de contact :"
PRINT emails_contact
PRINT telephones_contact
PRINT adresses_contact
```

---

## 🎯 Types de données supportés

### Types d'entrée
- **URLs HTTP/HTTPS** : Pages web dynamiques ou statiques
- **Fichiers HTML locaux** : Documents HTML stockés localement

### Types de sélecteurs CSS supportés
- **Éléments** : `div`, `p`, `a`, `img`, etc.
- **Classes** : `.ma-classe`, `.nav-item`
- **IDs** : `#mon-id`, `#header`
- **Attributs** : `[href]`, `[src*="image"]`
- **Combinateurs** : `div p`, `nav > a`
- **Pseudo-classes** : `:first-child`, `:last-child`

### Types de sortie
- **Listes de chaînes** : Textes, URLs, emails extraits
- **Éléments HTML** : Objets BeautifulSoup pour manipulation avancée
- **Attributs** : Valeurs d'attributs HTML
- **Données parsées** : Dates, nombres, patterns regex

---

## 🚨 Gestion d'erreurs

GrabLang fournit des messages d'erreur détaillés :

```grab
# Erreur de variable inexistante
USE page_inexistante
# Erreur: USE: Variable 'page_inexistante' non trouvée

# Erreur de sélecteur vide
SELECT ALL "element-inexistant"
# Erreur: SELECT ALL: Aucun élément 'element-inexistant' trouvé

# Erreur de regex invalide
EXTRACT REGEX "[invalid-regex"
# Erreur: EXTRACT REGEX: Expression régulière invalide
```

### Mode debug
Utilisez le flag `--debug` pour un diagnostic détaillé :

```bash
python src/core/interpreter.py script.grab --debug
```

---

## 📚 Référence rapide

### Commandes essentielles
| Commande | Description | Exemple |
|----------|-------------|---------|
| `LOAD URL` | Charge une page web | `LOAD URL page "https://example.com"` |
| `USE` | Sélectionne le document de travail | `USE page` |
| `SELECT ALL` | Sélectionne tous les éléments | `SELECT ALL "a"` |
| `FILTER ALL` | Filtre les éléments | `FILTER ALL WHERE text NOT EMPTY` |
| `GET ATTR` | Extrait des attributs | `GET ATTR "href"` |
| `GET TEXT` | Extrait le texte | `GET TEXT` |
| `EXTRACT REGEX` | Extraction par regex | `EXTRACT REGEX "\d+"` |
| `SAVE` | Sauvegarde le résultat | `SAVE ma_variable` |
| `PRINT` | Affiche le contenu | `PRINT ma_variable` |

### Conditions de filtrage
- `attr name EQUALS "value"`
- `attr name CONTAINS "text"`
- `attr name NOT NULL`
- `class CONTAINS "classname"`
- `text CONTAINS "substring"`
- `text MATCHES "regex"`
- `text NOT EMPTY`
- `text EQUALS "exact"`

### Flags regex
- `i` : Insensible à la casse
- `m` : Multiline
- `s` : Dotall (. inclut les retours à la ligne)
- `x` : Verbose
- `a` : ASCII

---

*GrabLang v1.0 - Langage DSL pour l'extraction de données web*