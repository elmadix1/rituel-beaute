# Rituel Beauté — Magazine francophone de la beauté quotidienne

Site statique HTML/CSS pur, hébergé sur GitHub Pages, domaine personnalisé `rituel-beaute.online`.

## Structure du site

```
/
├── index.html              # Page d'accueil
├── assets/
│   └── style.css           # Feuille de style globale
├── art-de-vivre/           # Niche Art de vivre
│   └── rituel-dimanche-soir/
│       └── index.html
├── mains-et-ongles/        # Niche Mains & Ongles
├── regard-et-visage/       # Niche Regard & Visage
├── corps-et-parfum/        # Niche Corps & Parfum
├── salon-et-pro/           # Niche Salon & Pro
├── CNAME                   # Domaine custom (rituel-beaute.online)
└── .github/workflows/
    └── deploy.yml          # Auto-déploiement GitHub Pages
```

## Comment publier un nouvel article

1. Créer un dossier dans la bonne niche : `/mains-et-ongles/mon-article/`
2. Y mettre un fichier `index.html` basé sur le template de `rituel-dimanche-soir/`
3. Commit + push → le site est en ligne 1-2 minutes plus tard

## Les 3 styles de mention produit BGlam

### Style 1 — Intégré (pour le paradigme Déclic, discret)
```html
<a href="https://bglam-re.com/..." class="produit-integre" target="_blank">
  une huile simple
</a>
```

### Style 2 — Inline (pour le paradigme Art de vivre)
```html
<a href="https://bglam-re.com/..." class="produit-inline" target="_blank" rel="noopener">
  <div class="produit-inline-img"></div>
  <div class="produit-inline-body">
    <div class="produit-inline-label">L'objet du rituel</div>
    <div class="produit-inline-name">Nom du produit</div>
    <div class="produit-inline-price">X € · BGlam</div>
  </div>
  <div class="produit-inline-arrow">→</div>
</a>
```

### Style 3 — Détaillé (pour le paradigme Expertise)
```html
<div class="produit-detaille">
  <div class="corner tl"></div><div class="corner tr"></div>
  <div class="corner bl"></div><div class="corner br"></div>
  <div class="produit-detaille-img"></div>
  <div class="produit-detaille-body">
    <div class="label">Recommandation BGlam</div>
    <h4>Nom du produit</h4>
    <p>Pourquoi il convient dans ce contexte précis.</p>
    <div class="produit-detaille-footer">
      <div class="produit-detaille-price">X €</div>
      <a href="https://bglam-re.com/..." class="produit-detaille-btn" target="_blank">Voir sur BGlam</a>
    </div>
  </div>
</div>
```

## Règles éditoriales (à ne jamais oublier)

1. Le produit n'est JAMAIS le sujet de l'article
2. Maximum 3 mentions de produits par article
3. La première mention vient après 500 mots minimum
4. Ton narratif, jamais commercial
5. Pas de superlatifs creux ("le meilleur", "la révolution")

## Déploiement

GitHub Actions déploie automatiquement à chaque push sur `main`.

Domaine : https://rituel-beaute.online
