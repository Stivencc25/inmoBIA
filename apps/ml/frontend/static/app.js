'use strict';

// ── State ──────────────────────────────────────────────────
let currentSessionId = null;
let currentIgCopy    = '';
let amenidades       = [];

// ── DOM refs ───────────────────────────────────────────────
const formSection    = document.getElementById('form-section');
const loadingSection = document.getElementById('loading-section');
const resultsSection = document.getElementById('results-section');
const loadingMsg     = document.getElementById('loading-msg');

// ── Toast ──────────────────────────────────────────────────
function showToast(msg, duration = 2800) {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.classList.remove('hidden');
  el.classList.add('show');
  setTimeout(() => {
    el.classList.remove('show');
    setTimeout(() => el.classList.add('hidden'), 300);
  }, duration);
}

// ── Section helpers ────────────────────────────────────────
function showSection(id) {
  [formSection, loadingSection, resultsSection].forEach(s => s.classList.add('hidden'));
  document.getElementById(id).classList.remove('hidden');
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ── Tag Input (Amenidades) ─────────────────────────────────
const tagWrap  = document.getElementById('tag-wrap');
const tagInput = document.getElementById('tag-input');
const tagsContainer = document.getElementById('tags-container');
const amenidadesHidden = document.getElementById('amenidades');

tagWrap.addEventListener('click', () => tagInput.focus());

tagInput.addEventListener('keydown', e => {
  if (['Enter', ',', 'Tab'].includes(e.key)) {
    e.preventDefault();
    const val = tagInput.value.trim().replace(/,$/, '');
    if (val && !amenidades.includes(val)) {
      amenidades.push(val);
      renderTags();
    }
    tagInput.value = '';
  } else if (e.key === 'Backspace' && !tagInput.value && amenidades.length) {
    amenidades.pop();
    renderTags();
  }
});

function renderTags() {
  tagsContainer.innerHTML = amenidades.map((t, i) => `
    <span class="tag">
      ${escHtml(t)}
      <button class="tag-remove" data-i="${i}" title="Eliminar">×</button>
    </span>
  `).join('');
  amenidadesHidden.value = JSON.stringify(amenidades);

  tagsContainer.querySelectorAll('.tag-remove').forEach(btn => {
    btn.addEventListener('click', () => {
      amenidades.splice(Number(btn.dataset.i), 1);
      renderTags();
    });
  });
}

// ── Photo Upload Previews ──────────────────────────────────
const portadaInput   = document.getElementById('portada');
const portadaPreview = document.getElementById('portada-preview');
const portadaPlaceholder = document.getElementById('portada-placeholder');

portadaInput.addEventListener('change', () => {
  const file = portadaInput.files[0];
  if (!file) return;
  const url = URL.createObjectURL(file);
  portadaPreview.src = url;
  portadaPreview.classList.remove('hidden');
  portadaPlaceholder.classList.add('hidden');
});

const extrasInput = document.getElementById('extras');
const extrasGrid  = document.getElementById('extras-grid');
const extrasPlaceholder = document.getElementById('extras-placeholder');

extrasInput.addEventListener('change', () => {
  const files = Array.from(extrasInput.files).slice(0, 9);
  if (!files.length) return;
  extrasGrid.innerHTML = '';
  files.forEach(f => {
    const img = document.createElement('img');
    img.src = URL.createObjectURL(f);
    img.className = 'extra-thumb';
    img.alt = f.name;
    extrasGrid.appendChild(img);
  });
  extrasGrid.classList.remove('hidden');
  extrasPlaceholder.classList.add('hidden');
});

// ── Form Submit ────────────────────────────────────────────
document.getElementById('listing-form').addEventListener('submit', async e => {
  e.preventDefault();
  const form = e.target;
  if (!form.checkValidity()) {
    form.reportValidity();
    return;
  }

  const fd = new FormData(form);

  // Override amenidades with current array
  fd.set('amenidades', JSON.stringify(amenidades));

  showSection('loading-section');

  const messages = [
    'Analizando la propiedad con IA…',
    'Generando descripción profesional…',
    'Creando imagen para Instagram…',
    'Renderizando PDF del listado…',
    'Casi listo…',
  ];
  let msgIdx = 0;
  loadingMsg.textContent = messages[0];
  const msgInterval = setInterval(() => {
    msgIdx = (msgIdx + 1) % messages.length;
    loadingMsg.textContent = messages[msgIdx];
  }, 2200);

  try {
    const res = await fetch('/api/generate', { method: 'POST', body: fd });
    clearInterval(msgInterval);

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || 'Error del servidor');
    }

    const data = await res.json();
    currentSessionId = data.session_id;
    currentIgCopy    = data.instagram_copy || '';

    displayResults(data);
    showSection('results-section');

  } catch (err) {
    clearInterval(msgInterval);
    showSection('form-section');
    showToast(`Error: ${err.message}`, 5000);
  }
});

// ── Display Results ────────────────────────────────────────
function displayResults(data) {
  // Description
  document.getElementById('desc-display').textContent = data.description || '';
  document.getElementById('desc-edit').value          = data.description || '';

  // Instagram copy
  document.getElementById('ig-display').textContent   = data.instagram_copy || '';
  document.getElementById('ig-edit').value             = data.instagram_copy || '';

  // PDF link
  document.getElementById('pdf-link').href = data.pdf_url;

  // Instagram image
  document.getElementById('ig-img-preview').src  = data.image_url;
  document.getElementById('ig-img-link').href     = data.image_url;

  // Reset video state
  resetVideoState();
}

// ── Editable Sections ──────────────────────────────────────
function setupEditable({ displayId, editId, editBtnId, actionsId, saveBtnId, cancelBtnId }) {
  const display   = document.getElementById(displayId);
  const edit      = document.getElementById(editId);
  const editBtn   = document.getElementById(editBtnId);
  const actions   = document.getElementById(actionsId);
  const saveBtn   = document.getElementById(saveBtnId);
  const cancelBtn = document.getElementById(cancelBtnId);

  editBtn.addEventListener('click', () => {
    edit.value = display.textContent;
    display.classList.add('hidden');
    edit.classList.remove('hidden');
    actions.classList.remove('hidden');
    editBtn.classList.add('hidden');
    edit.focus();
  });

  saveBtn.addEventListener('click', () => {
    display.textContent = edit.value;
    if (displayId === 'ig-display') currentIgCopy = edit.value;
    closeEditor();
  });

  cancelBtn.addEventListener('click', closeEditor);

  function closeEditor() {
    display.classList.remove('hidden');
    edit.classList.add('hidden');
    actions.classList.add('hidden');
    editBtn.classList.remove('hidden');
  }
}

setupEditable({
  displayId: 'desc-display', editId: 'desc-edit',
  editBtnId: 'edit-desc-btn', actionsId: 'desc-actions',
  saveBtnId: 'save-desc-btn', cancelBtnId: 'cancel-desc-btn',
});
setupEditable({
  displayId: 'ig-display', editId: 'ig-edit',
  editBtnId: 'edit-ig-btn', actionsId: 'ig-actions',
  saveBtnId: 'save-ig-btn', cancelBtnId: 'cancel-ig-btn',
});

// ── Copy to Clipboard ──────────────────────────────────────
document.getElementById('copy-ig-btn').addEventListener('click', async () => {
  const text = document.getElementById('ig-display').textContent;
  try {
    await navigator.clipboard.writeText(text);
    showToast('¡Copy de Instagram copiado!');
  } catch {
    showToast('No se pudo copiar. Selecciona el texto manualmente.');
  }
});

// ── Video Generation ───────────────────────────────────────
function resetVideoState() {
  document.getElementById('video-player').classList.add('hidden');
  document.getElementById('video-player').src = '';
  document.getElementById('video-placeholder').classList.remove('hidden');
  document.getElementById('video-link').classList.add('hidden');
  const btn = document.getElementById('gen-video-btn');
  btn.disabled = false;
  btn.innerHTML = `
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
      <polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2"/>
    </svg>
    Generar Video`;
}

document.getElementById('gen-video-btn').addEventListener('click', async () => {
  if (!currentSessionId) return;

  const btn = document.getElementById('gen-video-btn');
  btn.disabled = true;
  btn.innerHTML = `<span class="spinner" style="width:18px;height:18px;border-width:2.5px;margin:0"></span> Generando…`;

  try {
    const res = await fetch('/api/video', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: currentSessionId }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || 'Error del servidor');
    }

    const data = await res.json();

    const player = document.getElementById('video-player');
    player.src   = data.video_url;
    player.classList.remove('hidden');
    document.getElementById('video-placeholder').classList.add('hidden');

    const dlLink = document.getElementById('video-link');
    dlLink.href = data.video_url;
    dlLink.classList.remove('hidden');

    btn.innerHTML = `✓ Video Generado`;
    showToast('¡Video generado exitosamente!');

  } catch (err) {
    btn.disabled = false;
    btn.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2"/></svg> Reintentar Video`;
    showToast(`Error: ${err.message}`, 5000);
  }
});

// ── Instagram Publish ──────────────────────────────────────
document.getElementById('publish-btn').addEventListener('click', async () => {
  if (!currentSessionId) return;

  const btn    = document.getElementById('publish-btn');
  const status = document.getElementById('publish-status');
  const igCopy = document.getElementById('ig-display').textContent || currentIgCopy;

  btn.disabled = true;
  btn.textContent = 'Publicando…';
  status.className = 'publish-status hidden';

  try {
    const res = await fetch('/api/publish', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: currentSessionId, instagram_copy: igCopy }),
    });

    const data = await res.json();

    if (!res.ok) throw new Error(data.detail || 'Error al publicar');

    status.textContent = '¡Publicado en Instagram exitosamente!';
    status.className   = 'publish-status publish-status--ok';
    status.classList.remove('hidden');
    showToast('¡Publicado en Instagram!');

  } catch (err) {
    status.textContent = `Error: ${err.message}`;
    status.className   = 'publish-status publish-status--err';
    status.classList.remove('hidden');
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<svg viewBox="0 0 24 24" fill="currentColor" width="18" height="18"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z"/></svg> Publicar en Instagram`;
  }
});

// ── New Listing ────────────────────────────────────────────
document.getElementById('new-listing-btn').addEventListener('click', () => {
  currentSessionId = null;
  currentIgCopy    = '';
  amenidades       = [];
  renderTags();

  document.getElementById('listing-form').reset();
  portadaPreview.classList.add('hidden');
  portadaPlaceholder.classList.remove('hidden');
  extrasGrid.classList.add('hidden');
  extrasGrid.innerHTML = '';
  extrasPlaceholder.classList.remove('hidden');

  showSection('form-section');
});

// ── Util ───────────────────────────────────────────────────
function escHtml(str) {
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}
