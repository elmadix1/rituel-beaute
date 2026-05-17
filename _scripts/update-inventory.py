#!/usr/bin/env python3
"""
============================================================
UPDATE-INVENTORY.PY · Rituel Beauté (v2)
------------------------------------------------------------
Scanne tous les articles HTML et :
  1. Régénère data/produits-cites.json (inventaire chronologique)
  2. Met à jour data/backlinks.json :
     - Trie les articles par date décroissante
     - Régénère le sommaire chronologique en haut

USAGE :
    python3 _scripts/update-inventory.py

S'exécute automatiquement via GitHub Actions à chaque push.
============================================================
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path
from collections import OrderedDict


REPO_ROOT = Path(__file__).resolve().parent.parent
INVENTORY_FILE = REPO_ROOT / "data" / "produits-cites.json"
BACKLINKS_FILE = REPO_ROOT / "data" / "backlinks.json"
ARTICLES_PATTERN = "**/index.html"

IGNORE_PATHS = [
    "index.html",
    "mentions-legales/index.html",
    "_templates/",
    "node_modules/",
]

PRODUCT_COMMENT_PATTERN = re.compile(
    r'<!--\s*PRODUIT BGLAM\s*:\s*(.+?)\s*\|\s*(.+?)\s*\|\s*réf:\s*(.+?)\s*-->',
    re.IGNORECASE
)
LINK_HREF_PATTERN = re.compile(r'href="(https://bglam-re\.com[^"]+)"', re.IGNORECASE)
PUBLISHED_DATE_PATTERN = re.compile(
    r'<meta property="article:published_time" content="([^"]+)"',
    re.IGNORECASE
)
ARTICLE_TITLE_PATTERN = re.compile(
    r'<h1 class="article-title">(.+?)</h1>',
    re.DOTALL | re.IGNORECASE
)


def clean_html(text):
    text = re.sub(r'<[^>]+>', '', text)
    return re.sub(r'\s+', ' ', text).strip()


def should_ignore(filepath):
    relative = str(filepath.relative_to(REPO_ROOT))
    for pattern in IGNORE_PATHS:
        if relative == pattern or relative.startswith(pattern):
            return True
    return False


def is_article_page(filepath):
    try:
        content = filepath.read_text(encoding='utf-8')
        has_product = bool(PRODUCT_COMMENT_PATTERN.search(content))
        has_date = bool(PUBLISHED_DATE_PATTERN.search(content))
        return has_product or has_date
    except Exception:
        return False


def extract_article_info(filepath, content):
    relative = filepath.relative_to(REPO_ROOT)
    article_url = "/" + str(relative.parent) + "/"
    if article_url == "/./":
        article_url = "/"

    date_match = PUBLISHED_DATE_PATTERN.search(content)
    if date_match:
        date_str = date_match.group(1)
        article_date = date_str.split('T')[0]
    else:
        mtime = filepath.stat().st_mtime
        article_date = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')

    title_match = ARTICLE_TITLE_PATTERN.search(content)
    if title_match:
        article_title = clean_html(title_match.group(1))
    else:
        article_title = filepath.parent.name.replace('-', ' ').title()

    article_slug = filepath.parent.name

    return article_url, article_date, article_title, article_slug


def extract_products(content):
    products = []
    for match in PRODUCT_COMMENT_PATTERN.finditer(content):
        nom = match.group(1).strip()
        prix = match.group(2).strip()
        ref = match.group(3).strip()

        after_comment = content[match.end():match.end() + 2000]
        link_match = LINK_HREF_PATTERN.search(after_comment)
        url = link_match.group(1) if link_match else None

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
    """Scanne tous les articles et retourne (produits flat, articles dict)."""
    all_products = []
    articles_data = {}

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

        article_url, article_date, article_title, article_slug = extract_article_info(filepath, content)
        products = extract_products(content)

        for p in products:
            all_products.append({
                "date": article_date,
                "article": article_title,
                "article_url": article_url,
                **p
            })

        articles_data[article_slug] = {
            "date": article_date,
            "title": article_title,
            "url": article_url,
            "products": products
        }

        print(f"   📄 {article_title} ({article_date}) : {len(products)} produit(s)")

    return all_products, articles_data


def write_inventory(all_products):
    """Écrit data/produits-cites.json (liste chronologique flat)."""
    all_products.sort(key=lambda p: p['date'], reverse=True)

    output = {
        "_README": "Inventaire chronologique des produits BGlam cités dans les articles. Régénéré automatiquement à chaque push via GitHub Actions.",
        "_total": len(all_products),
        "_derniere_generation": datetime.now().isoformat(timespec='seconds'),
        "_legende_statuts": {
            "✅ verified": "URL produit vérifiée",
            "⚠️ search": "Lien de recherche catalogue",
            "❌ no-url-found": "URL non trouvée dans le HTML"
        },
        "produits": all_products
    }

    INVENTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(INVENTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n✅ {INVENTORY_FILE.name} : {len(all_products)} produits")


def update_backlinks_sommaire(articles_data):
    """Met à jour data/backlinks.json :
       - Régénère le _sommaire_chronologique
       - Trie les articles par date décroissante
       (sans toucher aux URLs et statuts manuels)"""

    if not BACKLINKS_FILE.exists():
        print(f"⚠️  {BACKLINKS_FILE.name} n'existe pas, on ne fait rien.")
        return

    with open(BACKLINKS_FILE, 'r', encoding='utf-8') as f:
        backlinks = json.load(f)

    sorted_slugs = sorted(
        articles_data.keys(),
        key=lambda s: articles_data[s]['date'],
        reverse=True
    )

    sommaire = ["📅 ARTICLES DU PLUS RÉCENT AU PLUS ANCIEN", ""]
    for slug in sorted_slugs:
        a = articles_data[slug]
        existing = backlinks.get("articles", {}).get(slug, {})
        rubrique = existing.get("_rubrique", "?")
        ville = existing.get("_ville", "?")
        sommaire.append(f"{a['date']} → {slug} ({rubrique} · {ville})")
    sommaire.append("")
    sommaire.append(f"Total : {len(sorted_slugs)} articles publiés")

    backlinks["_sommaire_chronologique"] = sommaire

    if "_meta" not in backlinks:
        backlinks["_meta"] = {}
    backlinks["_meta"]["derniere_maj"] = datetime.now().strftime('%Y-%m-%d')

    if "articles" in backlinks:
        old_articles = backlinks["articles"]
        new_articles = OrderedDict()

        for slug in sorted_slugs:
            if slug in old_articles:
                old_articles[slug]["_publie_le"] = articles_data[slug]['date']
                new_articles[slug] = old_articles[slug]

        for slug, data in old_articles.items():
            if slug not in new_articles:
                new_articles[slug] = data

        backlinks["articles"] = new_articles

    with open(BACKLINKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(backlinks, f, ensure_ascii=False, indent=2)

    print(f"\n✅ {BACKLINKS_FILE.name} : sommaire et tri mis à jour")
    print(f"   Articles triés par date : {len(sorted_slugs)}")


def sync_rubrique_pages(articles_data):
    """Synchronise les pages de rubrique avec les infos des articles.
    Pour chaque article, trouve la page rubrique parente et met à jour
    la ville et la date dans la carte article."""

    # Pattern pour trouver la ville dans un article : "Saint-Paul · 974" ou "Le Tampon · 974"
    VILLE_PATTERN = re.compile(
        r'<span>((?:Saint-[A-Za-zéèê]+|Le Tampon|La Possession|Le Port|Cilaos|Sainte-[A-Za-zéèê]+)\s*·\s*974)</span>',
        re.IGNORECASE
    )

    # Pattern pour trouver la ville dans la carte de la page rubrique
    # C'est le dernier <span> dans article-card-meta
    CARD_META_PATTERN = re.compile(
        r'(<div class="article-card-meta">.*?<span>)((?:Saint-[A-Za-zéèê]+|Le Tampon|La Possession|Le Port|Cilaos|Sainte-[A-Za-zéèê]+)(?:\s*·\s*974)?)(</span>\s*</div>)',
        re.DOTALL | re.IGNORECASE
    )

    synced = 0

    for slug, data in articles_data.items():
        article_url = data['url']  # ex: /mains-et-ongles/semi-permanent-climat-tropical/

        # Trouver la rubrique parente
        parts = article_url.strip('/').split('/')
        if len(parts) < 2:
            continue
        rubrique = parts[0]  # ex: mains-et-ongles

        # Lire l'article pour trouver la ville
        article_path = REPO_ROOT / article_url.strip('/') / "index.html"
        if not article_path.exists():
            continue

        article_content = article_path.read_text(encoding='utf-8')
        ville_match = VILLE_PATTERN.search(article_content)
        if not ville_match:
            continue

        article_ville = ville_match.group(1)  # ex: "Saint-Paul · 974"
        # Extraire juste le nom de ville sans "· 974"
        ville_name = article_ville.split('·')[0].strip()

        # Lire la page rubrique
        rubrique_path = REPO_ROOT / rubrique / "index.html"
        if not rubrique_path.exists():
            continue

        rubrique_content = rubrique_path.read_text(encoding='utf-8')

        # Chercher et remplacer la ville dans la carte article
        # On cherche le dernier <span> dans chaque article-card-meta
        # qui contient un nom de ville
        modified = False

        # Approche simple : remplacer toutes les occurrences de villes
        # connues dans les card-meta par la bonne ville
        villes_connues = [
            'Saint-Denis', 'Saint-Paul', 'Saint-Pierre', 'Saint-André',
            'Le Tampon', 'La Possession', 'Le Port', 'Sainte-Marie',
            'Sainte-Suzanne', 'Saint-Louis', 'Saint-Benoît', 'Saint-Gilles',
            'Cilaos', 'Saint-Leu', 'Saint-Joseph'
        ]

        for v in villes_connues:
            if v == ville_name:
                continue
            # Remplacer dans les spans du card-meta
            old_span = f'<span>{v}</span>'
            new_span = f'<span>{ville_name}</span>'
            if old_span in rubrique_content:
                rubrique_content = rubrique_content.replace(old_span, new_span)
                modified = True

        if modified:
            with open(rubrique_path, 'w', encoding='utf-8') as f:
                f.write(rubrique_content)
            synced += 1
            print(f"   🔄 {rubrique}/index.html → ville synchronisée : {ville_name}")

    if synced > 0:
        print(f"\n✅ {synced} page(s) de rubrique synchronisée(s)")
    else:
        print(f"\n✅ Pages de rubrique déjà à jour")


def main():
    print("🔍 Scan des articles...\n")

    all_products, articles_data = scan_articles()

    write_inventory(all_products)
    update_backlinks_sommaire(articles_data)
    sync_rubrique_pages(articles_data)

    print("\n📊 Récapitulatif :")
    print(f"   Articles scannés    : {len(articles_data)}")
    print(f"   Produits référencés : {len(all_products)}")

    if all_products:
        print("\n📅 Articles du plus récent au plus ancien :")
        sorted_articles = sorted(articles_data.items(), key=lambda x: x[1]['date'], reverse=True)
        for slug, a in sorted_articles[:5]:
            print(f"   {a['date']} → {a['title'][:60]}")


if __name__ == "__main__":
    main()
