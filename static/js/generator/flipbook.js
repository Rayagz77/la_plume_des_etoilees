/* ---------- flipbook.js  —  version « livre ouvert » ---------- */

function buildBook(storyText) {
    // Nettoyage
    document.getElementById('book')?.remove();
  
    /* --- Découpe par chapitres : GPT insère ### CHAPITRE --- */
    let chapters = storyText.split('\n### CHAPITRE')
                            .map(c => c.trim())
                            .filter(Boolean);
    if (chapters.length < 2) {                     // secours : paragraphes
      chapters = storyText.split(/\n\s*\n/).map(t => t.trim()).filter(Boolean);
    }
  
    /* --- Structure DOM --- */
    const wrap = document.getElementById('story-container');
    wrap.innerHTML = '';
    const book = document.createElement('div');
    book.id = 'book';
    wrap.appendChild(book);
  
    addPage(book, 'Couverture', 'cover');          // page 0   (gauche)
    chapters.forEach(ch => addPage(book, ch));     // pages 1..n
    const morale = chapters.at(-1).split('\n').pop();
    addPage(book, 'Morale :<br>' + morale, 'morale'); // dernière
  
    const pages = [...book.querySelectorAll('.page')];
  
    /* --- Positionnement empilé --- */
    pages.forEach((p, i) => {
      p.style.zIndex = pages.length - i;           // cover au dessus
    });
  
    /* --- Navigation flèches & clavier --- */
    let index = 0;                                 // page tournée
    updateFlip();
  
    const prev = makeArrow('◀', () => { index = Math.max(0,   index-1); updateFlip(); });
    const next = makeArrow('▶', () => { index = Math.min(pages.length-1, index+1); updateFlip(); });
    wrap.append(prev, next);
  
    document.addEventListener('keydown', e => {
      if (e.key === 'ArrowRight') next.click();
      if (e.key === 'ArrowLeft')  prev.click();
    });
  
    function updateFlip() {
      pages.forEach((pg, i) => pg.classList.toggle('flipped', i <= index));
    }
  }
  
  /*  Helpers  */
  function addPage(book, html, extra='') {
    const pg = document.createElement('div');
    pg.className = `page ${extra}`;
    pg.innerHTML = html.replace(/\n/g, '<br>');
    book.appendChild(pg);
  }
  function makeArrow(text, onClick) {
    const btn = document.createElement('button');
    btn.textContent = text;
    btn.className = 'nav-btn';
    btn.onclick = onClick;
    return btn;
  }
  
  window.buildBook = buildBook;
  