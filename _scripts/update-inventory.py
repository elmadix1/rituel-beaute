#!/usr/bin/env python3
"""
============================================================
UPDATE-INVENTORY.PY · Rituel Beauté
------------------------------------------------------------
Scanne tous les articles HTML du site, extrait les produits
BGlam cités (via les commentaires HTML), et regénère le fichier
data/produits-cites.json trié par date décroissante.

DÉTECTION :
- Lit les commentaires <!-- PRODUIT BGLAM : nom | prix | réf: xxx -->
- Lit la date <meta property="article:published_time" content="...">
- Lit le <title> et <h1 class="article-title"> pour le nom de l'article
- Lit le lien <a> juste après le commentaire pour l'URL

USAGE :
    python3 _scripts/update-inventory.py

S'exécute aussi automatiquement via GitHub Actions à chaque push.
============================================================
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path


# Configuration
REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_FILE = REPO_ROOT / "data" / "produits-cites.json"
ARTICLES_PATTERN = "**/index.html"

# Dossiers à ignorer (racine + rubriques sans articles)
IGNORE_PATHS = [
    "index.html",                       # Homepage
    "mentions-legales/index.html",      # Mentions légales
    "_templates/",                       # Templates
    "node_modules/",
]

# Pattern de détection des commentaires produits
PRODUCT_COMMENT_PATTERN = re.compile(
    r'<!--\s*PRODUIT BGLAM\s*:\s*(.+?)\s*\|\s*(.+?)\s*\|\s*réf:\s*(.+?)\s*-->',
    re.IGNORECASE
)

# Pattern pour trouver le href du lien juste après
LINK_HREF_PATTERN = re.compile(r'href="(https://bglam-re\.com[^"]+)"', re.IGNORECASE)

# Pattern pour la date de publication
PUBLISHED_DATE_PATTERN = re.compile(
    r'<meta property="article:published_time" content="([^"]+)"',
    re.IGNORECASE
)

# Pattern pour le titre de l'article
ARTICLE_TITLE_PATTERN = re.compile(
    r'<h1 class="article-title">(.+?)</h1>',
    re.DOTALL | re.IGNORECASE
)


def clean_html(text):
    """Supprime les balises HTML d'un texte."""
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def should_ignore(filepath):
    """Vérifie si le fichier doit être ignoré."""
    relative = str(filepath.relative_to(REPO_ROOT))
    for pattern in IGNORE_PATHS:
        if relative == pattern or relative.startswith(pattern):
            return True
    return False


def is_article_page(filepath):
    """
    Détermine si un fichier HTML est un article ou une page de rubrique.
    Un article a un commentaire PRODUIT BGLAM ou un meta:published_time.
    """
    try:
        content = filepath.read_text(encoding='utf-8')
        # Si on trouve un commentaire produit OU une date de publi, c'est un article
        has_product = bool(PRODUCT_COMMENT_PATTERN.search(content))
        has_date = bool(PUBLISHED_DATE_PATTERN.search(content))
        return has_product or has_date
    except Exception:
        return False


def extract_article_info(filepath, content):
    """Extrait les informations générales de l'article."""
    # URL de l'article : chemin depuis la racine
    relative = filepath.relative_to(REPO_ROOT)
    article_url = "/" + str(relative.parent) + "/"
    if article_url == "/./":
        article_url = "/"

    # Date de publication
    date_match = PUBLISHED_DATE_PATTERN.search(content)
    if date_match:
        date_str = date_match.group(1)
        # Garder juste la date YYYY-MM-DD
        article_date = date_str.split('T')[0]
    else:
        # Fallback : date du fichier
        mtime = filepath.stat().st_mtime
        article_date = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')

    # Titre de l'article
    title_match = ARTICLE_TITLE_PATTERN.search(content)
    if title_match:
        article_title = clean_html(title_match.group(1))
    else:
        article_title = filepath.parent.name.replace('-', ' ').title()

    return article_url, article_date, article_title


def extract_products(content):
    """Extrait tous les produits BGlam cités dans le contenu."""
    products = []

    for match in PRODUCT_COMMENT_PATTERN.finditer(content):
        nom = match.group(1).strip()
        prix = match.group(2).strip()
        ref = match.group(3).strip()

        # Chercher le href du lien BGlam juste après ce commentaire
        # On regarde les 800 caractères qui suivent
        after_comment = content[match.end():match.end() + 2000]
        link_match = LINK_HREF_PATTERN.search(after_comment)
        url = link_match.group(1) if link_match else None

        # Déterminer le statut
        if url and "/search?" in url:
            statut = "⚠️ search"
        elif url:
            statut = "✅ verified"
        else:
            statut = "❌ no-url-found"

        products.append({
            "ref": ref,
            "nom": nom,
            "prix": prix,
            "url": url,
            "statut": statut
        })

    return products


def scan_articles():
    """Scanne tous les articles du repo et extrait les produits."""
    all_products = []
    articles_scanned = 0

    # Trouver tous les fichiers HTML
    html_files = list(REPO_ROOT.glob(ARTICLES_PATTERN))

    for filepath in html_files:
        if should_ignore(filepath):
            continue

        if not is_article_page(filepath):
            continue

        try:
            content = filepath.read_text(encoding='utf-8')
        except Exception as e:
            print(f"⚠️  Erreur lecture {filepath}: {e}")
            continue

        articles_scanned += 1

        # Extraire les infos de l'article
        article_url, article_date, article_title = extract_article_info(filepath, content)

        # Extraire les produits
        products = extract_products(content)

        if not products:
            print(f"   📄 {article_title} : aucun produit cité")
            continue

        print(f"   📄 {article_title} ({article_date}) : {len(products)} produit(s)")

        # Ajouter au tableau global avec les infos article
        for p in products:
            all_products.append({
                "date": article_date,
                "article": article_title,
                "article_url": article_url,
                **p
            })

    return all_products, articles_scanned


def main():
    print("🔍 Scan des articles...")
    print(f"   Racine du repo : {REPO_ROOT}")
    print()

    all_products, articles_scanned = scan_articles()

    # Trier par date décroissante (récent en haut)
    all_products.sort(key=lambda p: p['date'], reverse=True)

    # Construire le JSON final
    output = {
        "_README": "Inventaire chronologique des produits BGlam cités dans les articles. Régénéré automatiquement à chaque push via GitHub Actions.",
        "_total": len(all_products),
        "_articles_scannes": articles_scanned,
        "_derniere_generation": datetime.now().isoformat(timespec='seconds'),
        "_legende_statuts": {
            "✅ verified": "URL produit vérifiée",
            "⚠️ search": "Lien de recherche catalogue",
            "❌ no-url-found": "URL non trouvée dans le HTML"
        },
        "produits": all_products
    }

    # Écrire le fichier
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print()
    print(f"✅ Inventaire mis à jour : {OUTPUT_FILE}")
    print(f"   Articles scannés : {articles_scanned}")
    print(f"   Produits cités   : {len(all_products)}")
    print()

    # Petit résumé console
    if all_products:
        print("📊 5 derniers produits cités :")
        for p in all_products[:5]:
            print(f"   {p['date']} | {p['statut']} | {p['nom']} ({p['prix']})")


if __name__ == "__main__":
    main()
