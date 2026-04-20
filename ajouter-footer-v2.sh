#!/bin/bash
# ============================================================
# Script v2 pour ajouter le footer dans toutes les pages HTML
# Corrigé : utilise un fichier temporaire au lieu d'awk multi-lignes
# ============================================================

set -e

# Créer le fichier footer temporaire
FOOTER_FILE=$(mktemp)
cat > "$FOOTER_FILE" << 'FOOTEREOF'

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

# Trouver toutes les pages index.html
FILES=$(find . -name "index.html" -not -path "./.git/*" -not -path "./node_modules/*")

echo "Pages à traiter :"
echo "$FILES"
echo ""
read -p "Continuer ? (o/N) " -n 1 -r
echo

if [[ ! $REPLY =~ ^[OoYy]$ ]]; then
    echo "Annulé."
    rm -f "$FOOTER_FILE"
    exit 0
fi

for FILE in $FILES; do
    echo "→ Traitement de : $FILE"
    
    # Si le footer existe déjà, on passe
    if grep -q '<footer class="site-footer">' "$FILE"; then
        echo "  ⚠️  Footer déjà présent, fichier ignoré"
        continue
    fi
    
    # Vérifier qu'il y a bien </body>
    if ! grep -q '</body>' "$FILE"; then
        echo "  ❌ Pas de </body> trouvé, fichier ignoré"
        continue
    fi
    
    # Utiliser sed pour insérer avant </body>
    # Créer un fichier temporaire avec le contenu footer inséré
    TMP=$(mktemp)
    
    # Lire le fichier jusqu'à </body>, insérer le footer, puis continuer
    python3 << PYEOF
with open('$FILE', 'r') as f:
    content = f.read()

with open('$FOOTER_FILE', 'r') as f:
    footer = f.read()

# Insérer le footer juste avant </body>
new_content = content.replace('</body>', footer + '\n</body>', 1)

with open('$TMP', 'w') as f:
    f.write(new_content)
PYEOF
    
    mv "$TMP" "$FILE"
    echo "  ✅ Footer ajouté"
done

# Nettoyage
rm -f "$FOOTER_FILE"

echo ""
echo "🎉 Terminé !"
echo ""
echo "Vérifie ce qui a changé avec :"
echo "  git status"
echo ""
echo "Si tout est ok, commit et push :"
echo "  git add ."
echo "  git commit -m 'Ajout du footer sur toutes les pages'"
echo "  git push"
