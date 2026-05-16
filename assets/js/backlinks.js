/* ============================================================
   BACKLINKS.JS - Rituel Beauté
   Met à jour les liens BGlam à partir de /data/backlinks.json
   ============================================================ */

(function() {
  'use strict';

  function getArticleSlug() {
    const path = window.location.pathname;
    const parts = path.replace(/\/$/, '').split('/').filter(Boolean);
    return parts[parts.length - 1] || null;
  }

  async function loadBacklinks() {
    try {
      const response = await fetch('/data/backlinks.json');
      if (!response.ok) return null;
      return await response.json();
    } catch (error) {
      console.warn('[backlinks.js] Erreur:', error);
      return null;
    }
  }

  function updateLinks(backlinks, articleSlug) {
    if (!backlinks || !backlinks.articles) return;
    const articleData = backlinks.articles[articleSlug];
    if (!articleData) return;

    const linksWithId = document.querySelectorAll('a[data-backlink-id]');
    let updatedCount = 0;

    linksWithId.forEach(link => {
      const id = link.getAttribute('data-backlink-id');
      const productData = articleData[id];
      if (!productData) return;

      const currentHref = link.getAttribute('href');
      if (currentHref !== productData.url) {
        link.setAttribute('href', productData.url);
        updatedCount++;
      }
    });

    if (updatedCount > 0) {
      console.info(`[backlinks.js] ${updatedCount} lien(s) corrigé(s)`);
    }
  }

  document.addEventListener('DOMContentLoaded', async function() {
    const articleSlug = getArticleSlug();
    if (!articleSlug) return;
    const backlinks = await loadBacklinks();
    if (backlinks) updateLinks(backlinks, articleSlug);
  });

})();
