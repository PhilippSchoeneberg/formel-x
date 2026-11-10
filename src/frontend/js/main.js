// Boots the app: preferences, language, session, groups, header and the hash router.

import { api } from "./api.js";
import { loginDialog, showError } from "./dialogs.js";
import { LANGUAGES, detectLanguage, setLanguage, t } from "./i18n.js";
import { loadAccount, notify, onChange, refreshGroups, savePrefs, state } from "./store.js";
import { button, h, messageDialog } from "./ui.js";
import { renderElements } from "./views/elements.js";
import { renderHome } from "./views/home.js";
import { renderMenu } from "./views/menu.js";
import { renderQuiz } from "./views/quiz.js";

const view = document.getElementById("view");

// Routing ---------------------------------------------------------------------

const ROUTES = [
  { pattern: /^\/$/, render: () => renderHome(view) },
  { pattern: /^\/elements$/, render: () => renderElements(view), needsGroup: true },
  { pattern: /^\/(compounds|questions)$/, render: ([kind]) => renderMenu(view, kind), needsGroup: true },
  { pattern: /^\/(compounds|questions)\/learn$/, render: ([kind], params) => renderQuiz(view, kind, params), needsGroup: true },
];

function parseHash() {
  const [path, search = ""] = (location.hash.slice(1) || "/").split("?");
  return { path: path || "/", params: new URLSearchParams(search) };
}

let renderToken = 0;

async function render() {
  const token = ++renderToken;
  const { path, params } = parseHash();
  const route = ROUTES.find((item) => item.pattern.test(path));
  if (!route || (route.needsGroup && !state.group)) {
    if (path !== "/") {
      location.hash = "#/";
      return;
    }
  }
  const match = path.match(route.pattern).slice(1);
  try {
    await route.render(match, params, () => token === renderToken);
  } catch (error) {
    if (token === renderToken) showError(error);
  }
}

// Header ----------------------------------------------------------------------

function applyTheme() {
  const theme = state.prefs.theme;
  if (theme) document.documentElement.dataset.theme = theme;
  else delete document.documentElement.dataset.theme;
}

function currentTheme() {
  if (state.prefs.theme) return state.prefs.theme;
  return matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function renderHeader() {
  const actions = document.getElementById("header-actions");
  document.querySelector(".skip-link").textContent = t("skip_to_content");

  const language = h("select", { class: "language-select", "aria-label": t("language") },
    Object.entries(LANGUAGES).map(([code, name]) => h("option", { value: code }, name)));
  language.value = state.prefs.language;
  language.addEventListener("change", async () => {
    savePrefs({ language: language.value });
    await setLanguage(language.value);
    notify();
  });

  const dark = currentTheme() === "dark";
  const theme = button(dark ? t("theme_light") : t("theme_dark"), {
    icon: dark ? "sun" : "moon",
    variant: "text",
    iconOnly: true,
    onclick: () => {
      savePrefs({ theme: currentTheme() === "dark" ? "light" : "dark" });
      applyTheme();
      renderHeader();
    },
  });

  const account = state.account
    ? button(t("log_out"), {
        icon: "logout",
        variant: "text",
        class: "account-button",
        title: state.account.email,
        onclick: async () => {
          try {
            await api.logout();
            state.account = null;
            await refreshGroups();
            notify();
          } catch (error) {
            showError(error);
          }
        },
      })
    : button(t("log_in"), {
        icon: "account",
        variant: "tonal",
        class: "account-button",
        onclick: async () => {
          const account = await loginDialog();
          if (!account) return;
          state.account = account;
          try {
            await refreshGroups();
          } catch (error) {
            showError(error);
          }
          notify();
        },
      });

  actions.replaceChildren(language, theme, account);
}

// Start -------------------------------------------------------------------------

async function loadSession() {
  await loadAccount();
  await refreshGroups();
}

async function start() {
  if (!state.prefs.language) savePrefs({ language: detectLanguage() });
  applyTheme();
  await setLanguage(state.prefs.language);
  renderHeader();

  // Without the server nothing works, so keep offering a retry.
  for (;;) {
    try {
      await loadSession();
      break;
    } catch (error) {
      await messageDialog(t(error?.isConnectionError ? "connection_error" : "unknown_error"), t("error_title"));
    }
  }

  onChange(() => {
    renderHeader();
    render();
  });
  window.addEventListener("hashchange", render);
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", renderHeader);
  renderHeader();
  render();
}

start();
