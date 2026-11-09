// The create/edit/delete/login dialogs. Each returns a promise that resolves with the
// saved object (or true) when the user submitted, and null when they cancelled.

import { api } from "./api.js";
import { formulaToUnicode } from "./formula.js";
import { t, tj } from "./i18n.js";
import { state } from "./store.js";
import { button, confirmDialog, field, h, messageDialog, openDialog, selectField } from "./ui.js";

export const DIFFICULTIES = ["easy", "medium", "hard"];

/** Shows a translated error for failures nobody handled more specifically. */
export function showError(error) {
  console.error(error);
  const key = error?.isConnectionError ? "connection_error" : "unknown_error";
  return messageDialog(t(key));
}

/**
 * Builds a dialog form. `fields` are field() objects, `submit()` throws or returns the result.
 * Returning undefined from submit keeps the dialog open (validation failed).
 */
function formDialog({ title, fields, submit, submitLabel = t("submit"), extra = null, wide = false }) {
  return openDialog({
    title,
    wide,
    build: (close) => {
      const submitButton = button(submitLabel, { variant: "filled", type: "submit" });
      const form = h("form", { class: "form", novalidate: true },
        h("div", { class: wide ? "form-grid" : "form-stack" }, fields.map((item) => item.element)),
        extra ? extra(close) : null,
        h("div", { class: "dialog-actions" },
          button(t("cancel"), { variant: "text", onclick: () => close(null) }),
          submitButton,
        ),
      );
      form.addEventListener("submit", async (event) => {
        event.preventDefault();
        submitButton.disabled = true;
        try {
          const result = await submit();
          if (result !== undefined) close(result);
        } catch (error) {
          showError(error);
        } finally {
          submitButton.disabled = false;
        }
      });
      return form;
    },
  });
}

/** Marks every empty required field; returns true when all are filled. */
function requireFilled(entries) {
  let valid = true;
  for (const [item, labelKey] of entries) {
    if (!item.value()) {
      item.setError(tj(labelKey, "empty_error"));
      valid = false;
    }
  }
  return valid;
}

// Account -------------------------------------------------------------------

export function loginDialog(startInRegisterMode = false) {
  let registerMode = startInRegisterMode;
  const email = field(t("email_address"), { type: "email", autocomplete: "email", maxlength: 254 });
  const password = field(t("password"), { type: "password", autocomplete: "current-password" });
  const repetition = field(t("password_repetition"), { type: "password", autocomplete: "new-password" });

  return openDialog({
    title: registerMode ? t("registration") : t("login"),
    build: (close) => {
      const title = () => document.getElementById("dialog-title");
      const submitButton = button("", { variant: "filled", type: "submit" });
      const toggle = button("", { variant: "text" });

      const render = () => {
        repetition.element.hidden = !registerMode;
        password.input.autocomplete = registerMode ? "new-password" : "current-password";
        submitButton.querySelector("span").textContent = registerMode ? t("register") : t("login");
        toggle.querySelector("span").textContent = registerMode ? t("go_to_login") : t("go_to_registration");
        if (title()) title().textContent = registerMode ? t("registration") : t("login");
        for (const item of [email, password, repetition]) item.setError(null);
      };
      toggle.addEventListener("click", () => {
        registerMode = !registerMode;
        render();
      });

      const form = h("form", { class: "form", novalidate: true },
        h("div", { class: "form-stack" }, email.element, password.element, repetition.element),
        h("div", { class: "dialog-actions split" },
          toggle,
          h("div", { class: "dialog-actions" },
            button(t("cancel"), { variant: "text", onclick: () => close(null) }),
            submitButton,
          ),
        ),
      );

      form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const required = [[email, "email_address"], [password, "password"]];
        if (registerMode) required.push([repetition, "password_repetition"]);
        if (!requireFilled(required)) return;
        if (registerMode && password.value() !== repetition.value()) {
          const message = tj("password", "and", "password_repetition", "do_not_match_error");
          password.setError(message);
          repetition.setError(message);
          return;
        }
        submitButton.disabled = true;
        try {
          const result = registerMode
            ? await api.register(email.value(), password.value())
            : await api.login(email.value(), password.value());
          close(result.account);
        } catch (error) {
          if (error.status === 401) {
            const message = tj("email_address", "or", "password", "incorrect_error");
            email.setError(message);
            password.setError(message);
          } else if (error.status === 409) {
            email.setError(tj("account", "already_exists_error"));
          } else if (error.detail === "password_too_long") {
            password.setError(t("password_too_long"));
          } else {
            showError(error);
          }
        } finally {
          submitButton.disabled = false;
        }
      });

      queueMicrotask(render);
      return form;
    },
  });
}

// Groups --------------------------------------------------------------------

export function groupDialog(group = null) {
  const name = field(t("group_name"), { value: group?.name, maxlength: 200 });
  return formDialog({
    title: group ? tj("edit", "group") : tj("create", "group"),
    fields: [name],
    submit: async () => {
      if (!requireFilled([[name, "group_name"]])) return undefined;
      try {
        return group ? await api.updateGroup(group.id, name.value()) : await api.createGroup(name.value());
      } catch (error) {
        if (error.status !== 409) throw error;
        name.setError(tj("group_name", "already_exists_error"));
        return undefined;
      }
    },
  });
}

/** Lets a visitor without an account add an existing group by its name. */
export function addGroupDialog() {
  const name = field(t("group_name"), { maxlength: 200 });
  return formDialog({
    title: t("add_group"),
    fields: [name],
    submit: async () => {
      if (!requireFilled([[name, "group_name"]])) return undefined;
      try {
        const group = await api.groupByName(name.value());
        if (state.groups.some((item) => item.id === group.id)) {
          name.setError(tj("group", "already_added_error"));
          return undefined;
        }
        return group;
      } catch (error) {
        if (error.status !== 404) throw error;
        name.setError(tj("group", "does_not_exist_error"));
        return undefined;
      }
    },
  });
}

export function confirmDelete(typeKey, itemName) {
  return confirmDialog({
    title: `${tj("delete", typeKey)}?`,
    message: `${t("delete_text")}"${itemName}"?`,
    confirmLabel: t("delete").trim(),
    danger: true,
  });
}

// Categories ----------------------------------------------------------------

export function categoryDialog(type, category = null) {
  const name = field(t("category_name"), { value: category?.name, maxlength: 200 });
  return formDialog({
    title: category ? tj("edit", "category") : t("add_category"),
    fields: [name],
    submit: async () => {
      if (!requireFilled([[name, "category_name"]])) return undefined;
      try {
        return category
          ? await api.updateCategory(category.id, name.value())
          : await api.createCategory(state.group.id, name.value(), type);
      } catch (error) {
        if (error.status !== 409) throw error;
        name.setError(tj("category", "already_exists_error"));
        return undefined;
      }
    },
  });
}

// Compounds and questions -----------------------------------------------------

const ENTRY_FORMS = {
  compounds: {
    titleKey: "compound",
    addKey: "add_compound",
    fields: [
      ["correct_name", "correct_formula_name", true],
      ["correct_formula", "correct_formula", true, true],
      ["wrong_name1", "first_wrong_formula_name", true],
      ["wrong_formula1", "first_wrong_formula", true, true],
      ["wrong_name2", "second_wrong_formula_name", true],
      ["wrong_formula2", "second_wrong_formula", true, true],
      ["wrong_name3", "third_wrong_formula_name", false],
      ["wrong_formula3", "third_wrong_formula", false, true],
      ["wrong_name4", "fourth_wrong_formula_name", false],
      ["wrong_formula4", "fourth_wrong_formula", false, true],
    ],
  },
  questions: {
    titleKey: "question",
    addKey: "add_question",
    fields: [
      ["question", "question", true],
      ["correct_answer", "correct_answer", true],
      ["wrong_answer1", "first_wrong_answer", true],
      ["wrong_answer2", "second_wrong_answer", true],
      ["wrong_answer3", "third_wrong_answer", false],
      ["wrong_answer4", "fourth_wrong_answer", false],
    ],
  },
};

/** Create or edit a compound/question. `categories` are the group's categories of that type. */
export function entryDialog(kind, categories, entry = null, defaults = {}) {
  const config = ENTRY_FORMS[kind];

  const category = selectField(t("category"), [
    { value: "", label: tj("select", "category") },
    ...categories.map((item) => ({ value: String(item.id), label: item.name })),
  ], { value: String(entry?.category_id ?? defaults.categoryId ?? "") });

  const difficulty = selectField(t("difficulty"), [
    { value: "", label: tj("select", "difficulty") },
    ...DIFFICULTIES.map((value) => ({ value, label: t(value) })),
  ], { value: entry?.difficulty ?? defaults.difficulty ?? "" });

  const inputs = config.fields.map(([key, labelKey, required, isFormula]) => {
    const label = required ? t(labelKey) : `${t(labelKey)} ${t("optional")}`;
    const item = field(label, {
      value: entry?.[key] ?? "",
      multiline: key === "question",
      maxlength: key === "question" ? 1000 : 200,
      preview: isFormula ? formulaToUnicode : null,
      hint: key === "correct_formula" ? t("formula_hint") : null,
      spellcheck: isFormula ? "false" : null,
      autocomplete: "off",
    });
    if (key === "question") item.element.classList.add("span-2");
    return { key, labelKey, required, item };
  });

  return formDialog({
    title: entry ? tj("edit", config.titleKey) : t(config.addKey),
    wide: true,
    fields: [category, difficulty, ...inputs.map((input) => input.item)],
    submit: async () => {
      let valid = requireFilled(inputs.filter((input) => input.required).map((input) => [input.item, input.labelKey]));
      if (!category.value()) {
        category.setError(tj("category", "empty_error"));
        valid = false;
      }
      if (!difficulty.value()) {
        difficulty.setError(tj("difficulty", "empty_error"));
        valid = false;
      }
      if (!valid) return undefined;

      const data = { category_id: Number(category.value()), difficulty: difficulty.value() };
      for (const { key, item } of inputs) data[key] = item.value() || null;
      return entry
        ? await api.updateEntry(kind, entry.id, data)
        : await api.createEntry(kind, state.group.id, data);
    },
  });
}
