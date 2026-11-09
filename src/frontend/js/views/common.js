import { t } from "../i18n.js";
import { state } from "../store.js";
import { button, h } from "../ui.js";

/** Page header with a back link, the title and optional actions on the right. */
export function pageHeader(title, { back = "#/", actions = [] } = {}) {
  return h("div", { class: "page-header" },
    button(t("back"), {
      icon: "back", variant: "text", iconOnly: true,
      onclick: () => { location.hash = back; },
    }),
    h("div", { class: "page-title" },
      h("p", { class: "eyebrow" }, state.group?.name ?? ""),
      h("h1", {}, title),
    ),
    h("div", { class: "row wrap page-actions" }, actions),
  );
}

/** A two-option toggle, e.g. remembering/learning mode. */
export function segmented(options, value, onChange, label) {
  return h("div", { class: "segmented", role: "group", "aria-label": label },
    options.map((option) =>
      h("button", {
        type: "button",
        class: option.value === value ? "selected" : null,
        "aria-pressed": option.value === value ? "true" : "false",
        onclick: () => { if (option.value !== value) onChange(option.value); },
      }, option.label),
    ),
  );
}
