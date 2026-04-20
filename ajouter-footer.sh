#!/bin/bash
# ============================================================
# Script pour ajouter le footer dans toutes les pages HTML
# ------------------------------------------------------------
# À exécuter depuis la racine de ton repo : cd ~/rituel-beaute
# ============================================================

set -e

FOOTER_CONTENT=$(cat << 'FOOTEREOF'

<!-- ========== FOOTER ========== -->
<footer class="site-footer">
  <div class="footer-inner">

    <div class="footer-brand-block">
      <div class="footer-brand">
        <span class="brand-rituel">Rituel</span>
        <span class="brand-beaute">Beauté</span>
      </div>
      <div class="footer-tagline">Le magazine beauté de La Réunion</div>
      <p class="footer-description">Rituels, gestes et objets pensés pour le climat tropical et le quotidien créole. Publié depuis Saint-Denis, 974.</p>
    </div>

    <div class="footer-col">
      <h5>Les univers</h5>
      <ul>
        <li><a href="/mains-et-ongles/">Mains &amp; Ongles</a></li>
        <li><a href="/regard-et-visage/">Regard &amp; Visage</a></li>
        <li><a href="/corps-et-parfum/">Corps &amp; Parfum</a></li>
        <li><a href="/salon-et-pro/">Salon &amp; Pro</a></li>
        <li><a href="/art-de-vivre/">Art de vivre</a></li>
      </ul>
    </div>

    <div class="footer-col">
      <h5>Le magazine</h5>
      <ul>
        <li><a href="/mentions-legales/">Mentions légales</a></li>
        <li><a href="mailto:contact@rituel-beaute.online">Contact</a></li>
      </ul>
    </div>

  </div>

  <div class="footer-bottom">
    <div class="footer-bottom-left">
      © 2026 Rituel Beauté
      <span class="dot">·</span>
      Tous droits réservés
    </div>
    <div class="footer-bottom-right">
      Édité à La Réunion
      <span class="footer-island-mark">974</span>
    </div>
  </div>
</footer>

FOOTEREOF
)

# Trouve tous les fichiers index.html du site
FILES=$(find . -name "index.html" -not -path "./.git/*")

echo "Pages à traiter :"
echo "$FILES"
echo ""
read -p "Continuer ? (o/N) " -n 1 -r
echo

if [[ ! $REPLY =~ ^[OoYy]$ ]]; then
    echo "Annulé."
    exit 0
fi

for FILE in $FILES; do
    echo "→ Traitement de : $FILE"
    
    # Si le footer existe déjà, on passe
    if grep -q '<footer class="site-footer">' "$FILE"; then
        echo "  ⚠️  Footer déjà présent, fichier ignoré"
        continue
    fi
    
    # Insérer le footer juste avant </body>
    # On utilise un fichier temporaire pour la compatibilité macOS/Linux
    TMP=$(mktemp)
    awk -v footer="$FOOTER_CONTENT" '
        /<\/body>/ && !done {
            print footer
            print $0
            done = 1
            next
        }
        { print }
    ' "$FILE" > "$TMP"
    
    mv "$TMP" "$FILE"
    echo "  ✅ Footer ajouté"
done

echo ""
echo "🎉 Terminé !"
echo "Vérifie le résultat avec : git diff"
