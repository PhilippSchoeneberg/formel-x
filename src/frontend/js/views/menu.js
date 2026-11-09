// Category menu for compounds and questions: pick a category (or all) and a difficulty, then
// start a round. Owners can add, rename and delete categories and add entries here.

import { api } from "../api.js";
import { DIFFICULTIES, categoryDialog, confirmDelete, entryDialog, showError } from "../dialogs.js";
import { t, tj } from "../i18n.js";
import { isOwner, savePrefs, state } from "../store.js";
import { button, h } from "../ui.js";
import { pageHeader, segmented } from "./common.js";

export const KINDS = {
  compounds: { type: "compound", titleKey: "compounds", addKey: "add_compound" },
  questions: { type: "question", titleKey: "questions", addKey: "add_question" },
};

function learnLink(kind, categoryId) {
  const params = new URLSearchParams();
  if (categoryId) params.set("category", categoryId);
  const difficulty = state.prefs.difficulty;
  if (difficulty) params.set("difficulty", difficulty);
  return `#/${kind}/learn?${params}`;
}

export async function renderMenu(view, kind) {
  const config = KINDS[kind];
  const owner = isOwner();
  const categories = await api.categories(state.group.id, config.type);
  const rerender = () => renderMenu(view, kind).catch(showError);

  const addCategory = async () => {
    if (await categoryDialog(config.type)) rerender();
  };
  const addEntry = () => entryDialog(kind, categories);

  const actions = owner ? [
    button(t("add_category"), { icon: "plus", variant: "tonal", onclick: addCategory }),
    categories.length ? button(t(config.addKey), { icon: "plus", variant: "filled", onclick: addEntry }) : null,
  ] : [];

  const difficulty = h("select", { id: "difficulty-select" },
    h("option", { value: "" }, t("all")),
    DIFFICULTIES.map((value) => h("option", { value }, t(value))),
  );
  difficulty.value = state.prefs.difficulty || "";
  difficulty.addEventListener("change", () => {
    savePrefs({ difficulty: difficulty.value || null });
    rerender();
  });

  const filters = h("div", { class: "toolbar" },
    h("div", { class: "field inline" }, h("label", { for: "difficulty-select" }, t("difficulty")), difficulty),
    kind === "compounds"
      ? segmented(
          [
            { value: "formula", label: t("formula_to_name") },
            { value: "name", label: t("name_to_formula") },
          ],
          state.prefs.compoundMode || "formula",
          (mode) => {
            savePrefs({ compoundMode: mode });
            rerender();
          },
          t("mode"),
        )
      : null,
  );

  let content;
  if (!categories.length) {
    content = h("div", { class: "empty-state" },
      owner
        ? button(tj("create", "category"), { icon: "plus", variant: "filled", onclick: addCategory })
        : h("p", {}, t("no_categories_yet_error")),
    );
  } else {
    const rows = [];
    if (categories.length >= 2) {
      rows.push(h("li", {}, h("a", { class: "list-link", href: learnLink(kind, null) },
        h("span", {}, t("all")), h("span", { class: "list-chevron", "aria-hidden": "true" }, "›"))));
    }
    for (const category of categories) {
      rows.push(h("li", {},
        h("a", { class: "list-link", href: learnLink(kind, category.id) },
          h("span", {}, category.name), h("span", { class: "list-chevron", "aria-hidden": "true" }, "›")),
        owner ? h("div", { class: "row list-actions" },
          button(tj("edit", "category"), {
            icon: "edit", variant: "text", iconOnly: true,
            onclick: async () => { if (await categoryDialog(config.type, category)) rerender(); },
          }),
          button(tj("delete", "category"), {
            icon: "delete", variant: "text-danger", iconOnly: true,
            onclick: async () => {
              if (!(await confirmDelete("category", category.name))) return;
              try {
                await api.deleteCategory(category.id);
                rerender();
              } catch (error) {
                showError(error);
              }
            },
          }),
        ) : null,
      ));
    }
    content = h("section", { class: "card list-card", "aria-labelledby": "category-title" },
      h("h2", { id: "category-title", class: "section-title" }, `${tj("select", "category")}:`),
      h("ul", { class: "list" }, rows),
    );
  }

  view.replaceChildren(pageHeader(t(config.titleKey), { actions }), filters, content);
}
