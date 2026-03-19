/* ============================================================
   English Vocabulary Agent – Frontend Script
   ============================================================ */

const API_BASE = "";   // empty → same origin; change to http://localhost:5000 for local dev

// ---------------------------------------------------------------------------
// DOM helpers
// ---------------------------------------------------------------------------

const $  = (id) => document.getElementById(id);

const show = (el) => el.classList.remove("hidden");
const hide = (el) => el.classList.add("hidden");

// ---------------------------------------------------------------------------
// Parse the textarea input into a clean word array
// ---------------------------------------------------------------------------

function parseWords() {
  const raw = $("word-input").value;
  const words = raw
    .split(/[\n,]+/)
    .map((w) => w.trim())
    .filter(Boolean);
  return [...new Set(words)];   // deduplicate
}

// ---------------------------------------------------------------------------
// Display helpers
// ---------------------------------------------------------------------------

function showError(msg) {
  const banner = $("error-banner");
  banner.textContent = `⚠️  ${msg}`;
  show(banner);
}

function clearError() {
  hide($("error-banner"));
}

function renderVocabulary(vocabData) {
  const container = $("vocab-output");
  container.innerHTML = "";

  Object.entries(vocabData).forEach(([word, info]) => {
    const card = document.createElement("div");
    card.className = "word-card";

    const synonymTags = (info.similar_words || [])
      .map((s) => `<span class="tag">${s}</span>`)
      .join("");

    card.innerHTML = `
      <div class="word-title">${escHtml(word)}</div>
      <div class="word-translation">🌏 ${escHtml(info.translation || "—")}</div>
      <div class="word-explanation">${escHtml(info.explanation || "—")}</div>
      <div class="word-synonyms">${synonymTags}</div>
    `;
    container.appendChild(card);
  });

  show($("vocab-section"));
}

function renderHomework(hwData) {
  const container = $("homework-output");
  container.innerHTML = "";

  container.innerHTML += `
    <div class="hw-title">${escHtml(hwData.title || "Homework")}</div>
    <div class="hw-instructions">${escHtml(hwData.instructions || "")}</div>
  `;

  (hwData.exercises || []).forEach((ex) => {
    const exDiv = document.createElement("div");
    exDiv.className = "exercise";

    const questions = (ex.questions || [])
      .map((q) => `<li>${escHtml(q)}</li>`)
      .join("");

    exDiv.innerHTML = `
      <span class="exercise-type">${escHtml(ex.type || "exercise")}</span>
      <div class="exercise-description">${escHtml(ex.description || "")}</div>
      <ol>${questions}</ol>
    `;
    container.appendChild(exDiv);
  });

  show($("homework-section"));
}

function escHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

// ---------------------------------------------------------------------------
// API calls
// ---------------------------------------------------------------------------

async function apiFetch(path, words) {
  const resp = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ words }),
  });
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ error: resp.statusText }));
    throw new Error(err.error || resp.statusText);
  }
  return resp.json();
}

// ---------------------------------------------------------------------------
// Button handlers
// ---------------------------------------------------------------------------

async function handleProcess() {
  const words = parseWords();
  if (!words.length) { showError("Please enter at least one word."); return; }

  clearError();
  hide($("vocab-section"));
  hide($("homework-section"));
  show($("loading"));

  try {
    const data = await apiFetch("/api/process", words);

    if (data.vocabulary_error) showError(`Vocabulary agent: ${data.vocabulary_error}`);
    if (data.homework_error)   showError(`Homework agent: ${data.homework_error}`);

    if (data.vocabulary) renderVocabulary(data.vocabulary);
    if (data.homework)   renderHomework(data.homework);
  } catch (err) {
    showError(err.message);
  } finally {
    hide($("loading"));
  }
}

async function handleVocabOnly() {
  const words = parseWords();
  if (!words.length) { showError("Please enter at least one word."); return; }

  clearError();
  hide($("vocab-section"));
  show($("loading"));

  try {
    const data = await apiFetch("/api/vocabulary", words);
    if (data.vocabulary) renderVocabulary(data.vocabulary);
  } catch (err) {
    showError(err.message);
  } finally {
    hide($("loading"));
  }
}

async function handleHomeworkOnly() {
  const words = parseWords();
  if (!words.length) { showError("Please enter at least one word."); return; }

  clearError();
  hide($("homework-section"));
  show($("loading"));

  try {
    const data = await apiFetch("/api/homework", words);
    if (data.homework) renderHomework(data.homework);
  } catch (err) {
    showError(err.message);
  } finally {
    hide($("loading"));
  }
}

// ---------------------------------------------------------------------------
// Bind events
// ---------------------------------------------------------------------------

document.addEventListener("DOMContentLoaded", () => {
  $("btn-process").addEventListener("click", handleProcess);
  $("btn-vocab").addEventListener("click", handleVocabOnly);
  $("btn-homework").addEventListener("click", handleHomeworkOnly);
});
