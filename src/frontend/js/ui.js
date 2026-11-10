// DOM helpers, icons and dialogs shared by all views.

import { t } from "./i18n.js";

/** Creates an element: h("button", { class: "button", onclick }, "Text", child). */
export function h(tag, attrs = {}, ...children) {
  const element = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs || {})) {
    if (value === null || value === undefined || value === false) continue;
    if (key.startsWith("on") && typeof value === "function") {
      element.addEventListener(key.slice(2), value);
    } else if (key === "html") {
      element.innerHTML = value;
    } else if (value === true) {
      element.setAttribute(key, "");
    } else {
      element.setAttribute(key, value);
    }
  }
  for (const child of children.flat()) {
    if (child === null || child === undefined || child === false) continue;
    element.append(child instanceof Node ? child : String(child));
  }
  return element;
}

/**
 * Replaces the content of `container`, skipping null/undefined/false like h() does.
 * (The DOM's own replaceChildren() would insert them as the text "null".)
 */
export function replaceContent(container, ...children) {
  container.replaceChildren(...children.flat().filter((child) => child !== null && child !== undefined && child !== false));
}

const ICON_PATHS = {
  back: "M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z",
  plus: "M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z",
  edit: "M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04a1 1 0 0 0 0-1.41l-2.34-2.34a1 1 0 0 0-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z",
  delete: "M6 19a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z",
  account: "M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z",
  logout: "M17 7l-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.58L17 17l5-5-5-5zM4 5h8V3H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h8v-2H4V5z",
  sun: "M12 7a5 5 0 1 0 0 10 5 5 0 0 0 0-10zM2 13h2a1 1 0 0 0 0-2H2a1 1 0 0 0 0 2zm18 0h2a1 1 0 0 0 0-2h-2a1 1 0 0 0 0 2zM11 2v2a1 1 0 0 0 2 0V2a1 1 0 0 0-2 0zm0 18v2a1 1 0 0 0 2 0v-2a1 1 0 0 0-2 0zM5.99 4.58a1 1 0 0 0-1.41 1.41l1.06 1.06a1 1 0 0 0 1.41-1.41L5.99 4.58zm12.37 12.37a1 1 0 0 0-1.41 1.41l1.06 1.06a1 1 0 0 0 1.41-1.41l-1.06-1.06zm1.06-10.96a1 1 0 0 0-1.41-1.41l-1.06 1.06a1 1 0 0 0 1.41 1.41l1.06-1.06zM7.05 18.36a1 1 0 0 0-1.41-1.41l-1.06 1.06a1 1 0 0 0 1.41 1.41l1.06-1.06z",
  moon: "M12 3a9 9 0 1 0 9 9c0-.46-.04-.92-.1-1.36A5.39 5.39 0 0 1 12.3 4.1 9.06 9.06 0 0 0 12 3z",
  leave: "M10.09 15.59 11.5 17l5-5-5-5-1.41 1.41L12.67 11H3v2h9.67l-2.58 2.59zM19 3H5a2 2 0 0 0-2 2v4h2V5h14v14H5v-4H3v4a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2z",
  play: "M8 5v14l11-7z",
};

export function icon(name) {
  const span = document.createElement("span");
  span.className = "icon";
  span.setAttribute("aria-hidden", "true");
  span.innerHTML = `<svg viewBox="0 0 24 24" width="20" height="20"><path fill="currentColor" d="${ICON_PATHS[name]}"/></svg>`;
  return span;
}

/** A button with an icon and a visible label (or an icon-only button with an accessible label). */
export function button(label, { icon: iconName, variant = "tonal", iconOnly = false, ...attrs } = {}) {
  const classes = ["button", variant, iconOnly ? "icon-only" : null, attrs.class].filter(Boolean).join(" ");
  return h(
    "button",
    { type: "button", ...attrs, class: classes, "aria-label": iconOnly ? label : null, title: iconOnly ? label : null },
    iconName ? icon(iconName) : null,
    iconOnly ? null : h("span", {}, label),
  );
}

// Dialogs ------------------------------------------------------------------

let idCounter = 0;

/** A unique id for linking labels, descriptions and errors. */
export function uid(prefix = "id") {
  idCounter += 1;
  return `${prefix}-${idCounter}`;
}

/**
 * Opens a modal dialog. `build(close, ids)` returns the content; `close(value)` resolves the promise.
 * Escape and clicking the backdrop close it with `null`. Give the main text `id: ids.description`
 * so screen readers read it together with the title.
 */
export function openDialog({ title, build, wide = false, describe = false }) {
  return new Promise((resolve) => {
    const ids = { title: uid("dialog-title"), description: uid("dialog-text") };
    const dialog = h("dialog", {
      class: wide ? "dialog wide" : "dialog",
      "aria-labelledby": ids.title,
      "aria-describedby": describe ? ids.description : null,
    });
    let settled = false;
    const close = (value = null) => {
      if (settled) return;
      settled = true;
      dialog.close();
      dialog.remove();
      resolve(value);
    };
    dialog.append(h("h2", { id: ids.title, class: "dialog-title" }, title), build(close, ids));
    dialog.addEventListener("cancel", (event) => {
      event.preventDefault();
      close(null);
    });
    dialog.addEventListener("mousedown", (event) => {
      if (event.target === dialog) close(null);
    });
    document.body.append(dialog);
    dialog.showModal(); // the browser moves focus into the dialog and restores it on close
    const first = dialog.querySelector("input, select, textarea");
    if (first) first.focus();
  });
}

export function messageDialog(message, title = t("notice")) {
  return openDialog({
    title,
    describe: true,
    build: (close, ids) =>
      h("div", {},
        h("p", { class: "dialog-text", id: ids.description }, message),
        h("div", { class: "dialog-actions" }, button(t("ok"), { variant: "filled", onclick: () => close(true) })),
      ),
  });
}

export function confirmDialog({ title, message, confirmLabel = t("ok"), danger = false }) {
  return openDialog({
    title,
    describe: true,
    build: (close, ids) =>
      h("div", {},
        h("p", { class: "dialog-text", id: ids.description }, message),
        h("div", { class: "dialog-actions" },
          button(t("cancel"), { variant: "text", onclick: () => close(false) }),
          button(confirmLabel, { variant: danger ? "danger" : "filled", onclick: () => close(true) }),
        ),
      ),
  });
}

// Form fields ----------------------------------------------------------------

function describedBy(...ids) {
  return ids.filter(Boolean).join(" ") || null;
}

/**
 * A labelled input with hint and error lines, both linked via aria-describedby.
 * Returns { element, input, value(), setError(msg) }.
 */
export function field(label, { type = "text", value = "", multiline = false, hint = null, preview = null, ...attrs } = {}) {
  const id = uid("field");
  const errorId = `${id}-error`;
  const hintId = hint ? `${id}-hint` : null;
  const props = { id, "aria-describedby": describedBy(hintId, errorId), ...attrs };
  const input = multiline ? h("textarea", { rows: 3, ...props }) : h("input", { type, ...props });
  input.value = value ?? "";
  const error = h("p", { class: "field-error", id: errorId });
  const previewLine = preview ? h("p", { class: "field-preview", "aria-hidden": "true" }) : null;
  if (preview) {
    const update = () => { previewLine.textContent = preview(input.value); };
    input.addEventListener("input", update);
    update();
  }
  const element = h("div", { class: "field" },
    h("label", { for: id }, label),
    input,
    previewLine,
    hint ? h("p", { class: "field-hint", id: hintId }, hint) : null,
    error,
  );
  const setError = (message) => {
    error.textContent = message || "";
    element.classList.toggle("invalid", Boolean(message));
    input.setAttribute("aria-invalid", message ? "true" : "false");
  };
  input.addEventListener("input", () => setError(null));
  return { element, input, value: () => input.value.trim(), setError };
}

/** A labelled <select> with an error line. options: [{ value, label }]. */
export function selectField(label, options, { value = "", ...attrs } = {}) {
  const id = uid("field");
  const errorId = `${id}-error`;
  const select = h("select", { id, "aria-describedby": errorId, ...attrs },
    options.map((option) => h("option", { value: option.value }, option.label)));
  select.value = value;
  const error = h("p", { class: "field-error", id: errorId });
  const element = h("div", { class: "field" }, h("label", { for: id }, label), select, error);
  const setError = (message) => {
    error.textContent = message || "";
    element.classList.toggle("invalid", Boolean(message));
    select.setAttribute("aria-invalid", message ? "true" : "false");
  };
  select.addEventListener("change", () => setError(null));
  return { element, input: select, value: () => select.value, setError };
}

/**
 * Moves focus to the first invalid field in `container`. Screen readers then read its label
 * and error message, and keyboard users land where the problem is.
 */
export function focusFirstInvalid(container) {
  const invalid = container.querySelector('[aria-invalid="true"]');
  if (invalid) invalid.focus();
}

/** Focuses an element that isn't focusable by itself (e.g. a heading) without adding it to the tab order. */
export function focusElement(element) {
  if (!element) return;
  if (!element.hasAttribute("tabindex")) element.setAttribute("tabindex", "-1");
  element.focus({ preventScroll: false });
}

// Toasts ----------------------------------------------------------------------

export function toast(message) {
  const region = document.getElementById("toasts");
  const item = h("div", { class: "toast", role: "status" }, message);
  region.append(item);
  setTimeout(() => item.classList.add("leaving"), 2600);
  setTimeout(() => item.remove(), 3000);
}

export function shuffle(items) {
  const copy = [...items];
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}
