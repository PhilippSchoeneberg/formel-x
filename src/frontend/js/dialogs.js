// The create/edit/delete/login dialogs. Each returns a promise that resolves with the
// saved object (or true) when the user submitted, and null when they cancelled.

import { api } from "./api.js";
import { formulaToUnicode } from "./formula.js";
import { t } from "./i18n.js";
import { state } from "./store.js";
import { button, confirmDialog, field, focusFirstInvalid, h, messageDialog, openDialog, selectField } from "./ui.js";

export const DIFFICULTIES = ["easy", "medium", "hard"];

// Must match MIN_PASSWORD_LENGTH and EMAIL_PATTERN in src/backend/schemas.py.
const MIN_PASSWORD_LENGTH = 8;
const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

/** Shows a translated error for failures nobody handled more specifically. */
export function showError(error) {
  console.error(error);
  const key = error?.isConnectionError ? "connection_error" : "unknown_error";
  return messageDialog(t(key), t("error_title"));
}

/**
 * Builds a dialog form. `fields` are field() objects, `submit()` throws or returns the result.
 * Returning undefined from submit keeps the dialog open (validation failed).
 */
function formDialog({ title, fields, submit, submitLabel = t("save"), wide = false }) {
  return openDialog({
    title,
    wide,
    build: (close) => {
      const submitButton = button(submitLabel, { variant: "filled", type: "submit" });
      const form = h("form", { class: "form", novalidate: true },
        h("div", { class: wide ? "form-grid" : "form-stack" }, fields.map((item) => item.element)),
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
          else focusFirstInvalid(form);
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
function requireFilled(items) {
  let valid = true;
  for (const item of items) {
    if (!item.value()) {
      item.setError(t("required"));
      valid = false;
    }
  }
  return valid;
}

// Account -------------------------------------------------------------------

export function loginDialog(startInRegisterMode = false) {
  let registerMode = startInRegisterMode;
  const email = field(t("email"), { type: "email", autocomplete: "email", maxlength: 254 });
  const password = field(t("password"), { type: "password", autocomplete: "current-password" });
  const repetition = field(t("password_repeat"), { type: "password", autocomplete: "new-password" });

  return openDialog({
    title: registerMode ? t("create_account") : t("log_in"),
    build: (close, ids) => {
      const title = () => document.getElementById(ids.title);
      const submitButton = button("", { variant: "filled", type: "submit" });
      const toggle = button("", { variant: "text" });

      const render = () => {
        repetition.element.hidden = !registerMode;
        password.input.autocomplete = registerMode ? "new-password" : "current-password";
        submitButton.querySelector("span").textContent = registerMode ? t("create_account") : t("log_in");
        toggle.querySelector("span").textContent = registerMode ? t("to_login") : t("to_register");
        if (title()) title().textContent = registerMode ? t("create_account") : t("log_in");
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
        const required = registerMode ? [email, password, repetition] : [email, password];
        const invalid = () => focusFirstInvalid(form);
        if (!requireFilled(required)) return invalid();
        if (registerMode && !EMAIL_PATTERN.test(email.value())) {
          email.setError(t("invalid_email"));
          return invalid();
        }
        if (registerMode && password.value().length < MIN_PASSWORD_LENGTH) {
          password.setError(t("password_too_short", { count: MIN_PASSWORD_LENGTH }));
          return invalid();
        }
        if (registerMode && password.value() !== repetition.value()) {
          repetition.setError(t("passwords_mismatch"));
          return invalid();
        }
        submitButton.disabled = true;
        try {
          const result = registerMode
            ? await api.register(email.value(), password.value())
            : await api.login(email.value(), password.value());
          close(result.account);
        } catch (error) {
          if (error.status === 401) {
            password.setError(t("login_failed"));
          } else if (error.status === 409) {
            email.setError(t("account_exists"));
          } else if (error.status === 429) {
            const minutes = Math.max(1, Math.ceil((error.retryAfter || 60) / 60));
            password.setError(t("too_many_attempts", { minutes }));
          } else if (error.detail === "invalid_email") {
            email.setError(t("invalid_email"));
          } else if (error.detail === "password_too_short") {
            password.setError(t("password_too_short", { count: MIN_PASSWORD_LENGTH }));
          } else if (error.detail === "password_too_long") {
            password.setError(t("password_too_long"));
          } else {
            showError(error);
          }
        } finally {
          submitButton.disabled = false;
        }
        focusFirstInvalid(form);
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
    title: group ? t("rename_group") : t("new_group"),
    fields: [name],
    submit: async () => {
      if (!requireFilled([name])) return undefined;
      try {
        return group ? await api.updateGroup(group.id, name.value()) : await api.createGroup(name.value());
      } catch (error) {
        if (error.status !== 409) throw error;
        name.setError(t("group_exists"));
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
    submitLabel: t("add_group"),
    fields: [name],
    submit: async () => {
      if (!requireFilled([name])) return undefined;
      try {
        const group = await api.groupByName(name.value());
        if (state.groups.some((item) => item.id === group.id)) {
          name.setError(t("group_already_added"));
          return undefined;
        }
        return group;
      } catch (error) {
        if (error.status !== 404) throw error;
        name.setError(t("group_not_found"));
        return undefined;
      }
    },
  });
}

/** Asks before deleting. `titleKey` is the action, e.g. "delete_group". */
export function confirmDelete(titleKey, itemName) {
  return confirmDialog({
    title: t(titleKey),
    message: t("confirm_delete", { name: itemName }),
    confirmLabel: t("delete"),
    danger: true,
  });
}

// Categories ----------------------------------------------------------------

export function categoryDialog(type, category = null) {
  const name = field(t("category_name"), { value: category?.name, maxlength: 200 });
  return formDialog({
    title: category ? t("rename_category") : t("new_category"),
    fields: [name],
    submit: async () => {
      if (!requireFilled([name])) return undefined;
      try {
        return category
          ? await api.updateCategory(category.id, name.value())
          : await api.createCategory(state.group.id, name.value(), type);
      } catch (error) {
        if (error.status !== 409) throw error;
        name.setError(t("category_exists"));
        return undefined;
      }
    },
  });
}

// Compounds and questions -----------------------------------------------------

const ENTRY_FORMS = {
  compounds: {
    newKey: "new_compound",
    editKey: "edit_compound",
    // [field, label key, label params, required, is formula]
    fields: [
      ["correct_name", "correct_name", {}, true],
      ["correct_formula", "correct_formula", {}, true, true],
      ["wrong_name1", "wrong_name", { n: 1 }, true],
      ["wrong_formula1", "wrong_formula", { n: 1 }, true, true],
      ["wrong_name2", "wrong_name", { n: 2 }, true],
      ["wrong_formula2", "wrong_formula", { n: 2 }, true, true],
      ["wrong_name3", "wrong_name", { n: 3 }, false],
      ["wrong_formula3", "wrong_formula", { n: 3 }, false, true],
      ["wrong_name4", "wrong_name", { n: 4 }, false],
      ["wrong_formula4", "wrong_formula", { n: 4 }, false, true],
    ],
  },
  questions: {
    newKey: "new_question",
    editKey: "edit_question",
    fields: [
      ["question", "question", {}, true],
      ["correct_answer", "correct_answer", {}, true],
      ["wrong_answer1", "wrong_answer", { n: 1 }, true],
      ["wrong_answer2", "wrong_answer", { n: 2 }, true],
      ["wrong_answer3", "wrong_answer", { n: 3 }, false],
      ["wrong_answer4", "wrong_answer", { n: 4 }, false],
    ],
  },
};

/** Create or edit a compound/question. `categories` are the group's categories of that type. */
export function entryDialog(kind, categories, entry = null, defaults = {}) {
  const config = ENTRY_FORMS[kind];

  const category = selectField(t("category"), [
    { value: "", label: t("choose_category") },
    ...categories.map((item) => ({ value: String(item.id), label: item.name })),
  ], { value: String(entry?.category_id ?? defaults.categoryId ?? "") });

  const difficulty = selectField(t("difficulty"), [
    { value: "", label: t("choose_difficulty") },
    ...DIFFICULTIES.map((value) => ({ value, label: t(value) })),
  ], { value: entry?.difficulty ?? defaults.difficulty ?? "" });

  const inputs = config.fields.map(([key, labelKey, labelParams, required, isFormula]) => {
    const label = required ? t(labelKey, labelParams) : `${t(labelKey, labelParams)} ${t("optional")}`;
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
    return { key, required, item };
  });

  return formDialog({
    title: entry ? t(config.editKey) : t(config.newKey),
    wide: true,
    fields: [category, difficulty, ...inputs.map((input) => input.item)],
    submit: async () => {
      let valid = requireFilled(inputs.filter((input) => input.required).map((input) => input.item));
      for (const select of [category, difficulty]) {
        if (!select.value()) {
          select.setError(t("select_required"));
          valid = false;
        }
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
