// Translations live in /locales/<code>.json. Keys are snake_case ids, and many values carry
// intentional leading/trailing spaces because strings are built by concatenation,
// e.g. t("select") + t("category") -> "Wähle Kategorie".

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

export function t(key) {
  return current[key] ?? fallback[key] ?? key;
}

/** Joins translated parts and tidies the doubled/trailing spaces that concatenation leaves. */
export function tj(...keys) {
  return keys.map((key) => t(key)).join("").replace(/\s{2,}/g, " ").trim();
}
