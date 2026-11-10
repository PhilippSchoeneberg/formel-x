// Translations live in /locales/<code>.json. Every key is a complete phrase or sentence;
// variable parts use named placeholders, e.g. "where_is": "Where is {element}?" with
// t("where_is", { element: "Iron" }). Never build sentences by joining several keys:
// word order and grammar differ between languages.

export const LANGUAGES = {
  de: "Deutsch",
  en: "English",
  es: "Español",
  fr: "Français",
  nl: "Nederlands",
};

const FALLBACK = "en";
const cache = {};
let current = {};
let fallback = {};
let currentCode = FALLBACK;

async function fetchLocale(code) {
  if (!cache[code]) {
    const response = await fetch(`locales/${code}.json`);
    if (!response.ok) throw new Error(`Missing locale ${code}`);
    cache[code] = await response.json();
  }
  return cache[code];
}

export function detectLanguage() {
  for (const lang of navigator.languages || [navigator.language]) {
    const code = (lang || "").slice(0, 2).toLowerCase();
    if (code in LANGUAGES) return code;
  }
  return FALLBACK;
}

export async function setLanguage(code) {
  if (!(code in LANGUAGES)) code = FALLBACK;
  fallback = await fetchLocale(FALLBACK);
  current = await fetchLocale(code);
  currentCode = code;
  document.documentElement.lang = code;
}

export function getLanguage() {
  return currentCode;
}

/** Translates `key` and fills in `{placeholders}` from `params`. Unknown placeholders stay as they are. */
export function t(key, params = {}) {
  const text = current[key] ?? fallback[key] ?? key;
  return text.replace(/\{(\w+)\}/g, (match, name) => (name in params ? String(params[name]) : match));
}
