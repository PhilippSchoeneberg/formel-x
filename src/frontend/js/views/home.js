// Home: pick the group and a learning mode. Owners manage their groups here; visitors
// without an account add groups by name and can leave them again.

import { api } from "../api.js";
import { addGroupDialog, confirmDelete, groupDialog, loginDialog, showError } from "../dialogs.js";
import { t, tj } from "../i18n.js";
import {
  isOwner, notify, refreshGroups, removeVisitorGroup, saveVisitorGroup, setGroup, state,
} from "../store.js";
import { button, h } from "../ui.js";

const MODES = [
  { route: "#/elements", key: "elements", glyph: "Fe", accent: "accent-1" },
  { route: "#/compounds", key: "compounds", glyph: "H₂O", accent: "accent-2" },
  { route: "#/questions", key: "questions", glyph: "?", accent: "accent-3" },
];

async function run(action) {
  try {
    await action();
  } catch (error) {
    showError(error);
  }
}

async function createGroup() {
  const group = await groupDialog();
  if (!group) return;
  await run(async () => {
    await refreshGroups();
    setGroup(state.groups.find((item) => item.id === group.id) || null);
  });
}

async function addGroup() {
  const group = await addGroupDialog();
  if (!group) return;
  saveVisitorGroup(group);
  await run(async () => {
    await refreshGroups();
    setGroup(state.groups.find((item) => item.id === group.id) || null);
  });
}

function groupActions() {
  if (state.account) {
    return [
      button(tj("create", "group"), { icon: "plus", variant: "tonal", onclick: createGroup }),
      isOwner() && button(tj("edit", "group"), {
        icon: "edit", variant: "text",
        onclick: async () => {
          const updated = await groupDialog(state.group);
          if (!updated) return;
          await run(async () => {
            await refreshGroups();
            notify();
          });
        },
      }),
      isOwner() && button(tj("delete", "group"), {
        icon: "delete", variant: "text-danger",
        onclick: async () => {
          if (!(await confirmDelete("group", state.group.name))) return;
          await run(async () => {
            await api.deleteGroup(state.group.id);
            await refreshGroups();
            notify();
          });
        },
      }),
    ];
  }
  return [
    button(t("add_group"), { icon: "plus", variant: "tonal", onclick: addGroup }),
    state.group && button(tj("leave", "group"), {
      icon: "leave", variant: "text",
      onclick: async () => {
        removeVisitorGroup(state.group);
        await run(async () => {
          await refreshGroups();
          notify();
        });
      },
    }),
  ];
}

function groupPicker() {
  const select = h("select", { id: "group-select", class: "group-select" },
    state.groups.map((group) => h("option", { value: String(group.id) }, group.name)));
  select.value = String(state.group.id);
  select.addEventListener("change", () => {
    setGroup(state.groups.find((group) => String(group.id) === select.value));
  });
  return h("div", { class: "field" }, h("label", { for: "group-select" }, t("group")), select);
}

function emptyState() {
  return h("div", { class: "empty-state" },
    h("p", {}, t("no_groups_yet_error")),
    state.account
      ? button(tj("create", "group"), { icon: "plus", variant: "filled", onclick: createGroup })
      : h("div", { class: "row center" },
          button(t("add_group"), { icon: "plus", variant: "filled", onclick: addGroup }),
          button(t("login"), {
            icon: "account", variant: "text",
            onclick: async () => {
              const account = await loginDialog();
              if (!account) return;
              state.account = account;
              await run(refreshGroups);
              notify();
            },
          }),
        ),
  );
}

export function renderHome(view) {
  if (!state.group) {
    view.replaceChildren(
      h("section", { class: "hero" },
        h("img", { class: "hero-logo", src: "assets/logo.png", alt: "" }),
        h("h1", {}, "FormelX"),
        emptyState(),
      ),
    );
    return;
  }

  view.replaceChildren(
    h("section", { class: "card group-card" },
      groupPicker(),
      h("div", { class: "row wrap" }, groupActions()),
    ),
    h("section", { "aria-labelledby": "modes-title" },
      h("h2", { id: "modes-title", class: "section-title" }, tj("select", "mode")),
      h("div", { class: "mode-grid" },
        MODES.map((mode) =>
          h("a", { class: `mode-card ${mode.accent}`, href: mode.route },
            h("span", { class: "mode-glyph", "aria-hidden": "true" }, mode.glyph),
            h("span", { class: "mode-label" }, t(mode.key)),
          ),
        ),
      ),
    ),
  );
}
