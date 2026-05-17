#!/bin/bash
# ============================================================
# Corrige les villes dans les pages de rubrique
# ============================================================

cd ~/rituel-beaute

echo "🔧 Correction des villes dans les pages de rubrique..."

# Mains & Ongles : Saint-Denis → Saint-Paul
sed -i '' 's/Saint-Denis/Saint-Paul/g' mains-et-ongles/index.html
echo "  ✅ mains-et-ongles/index.html → Saint-Paul"

# Regard & Visage : Saint-Denis → Le Tampon
sed -i '' 's/Saint-Denis/Le Tampon/g' regard-et-visage/index.html
echo "  ✅ regard-et-visage/index.html → Le Tampon"

# Corps & Parfum : Saint-Denis → Saint-Pierre
sed -i '' 's/Saint-Denis/Saint-Pierre/g' corps-et-parfum/index.html
echo "  ✅ corps-et-parfum/index.html → Saint-Pierre"

# Salon & Pro : Saint-Denis → Saint-André
sed -i '' 's/Saint-Denis/Saint-André/g' salon-et-pro/index.html
echo "  ✅ salon-et-pro/index.html → Saint-André"

echo ""
echo "🎉 Terminé !"
echo ""
echo "Vérifie :"
echo "  git diff"
echo ""
echo "Puis commit :"
echo "  git add ."
echo "  git commit -m 'Correction villes dans les pages rubrique'"
echo "  git push"
