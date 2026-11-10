// Multiple-choice round over the compounds or questions of a category (or all of them).
// The round survives re-renders (language change) as long as the URL stays the same.

import { api } from "../api.js";
import { confirmDelete, entryDialog, showError } from "../dialogs.js";
import { formulaToUnicode } from "../formula.js";
import { t } from "../i18n.js";
import { isOwner, staleCheck, state } from "../store.js";
import { button, focusElement, h, replaceContent, shuffle } from "../ui.js";
import { pageHeader } from "./common.js";
import { KINDS } from "./menu.js";

let round = null;

function roundKey(kind, params) {
  return `${state.group.id}|${kind}|${params.toString()}|${state.prefs.compoundMode || "formula"}`;
}

/** Returns { prompt, options: [{ text, correct }] } for an entry. */
function buildQuestion(kind, entry) {
  if (kind === "questions") {
    const answers = ["correct_answer", "wrong_answer1", "wrong_answer2", "wrong_answer3", "wrong_answer4"];
    return {
      prompt: entry.question,
      options: answers.filter((key) => entry[key]).map((key) => ({ text: entry[key], correct: key === "correct_answer" })),
    };
  }
  // "formula" mode asks for the formula of a named compound, "name" mode the other way round.
  if ((state.prefs.compoundMode || "formula") === "formula") {
    const keys = ["correct_formula", "wrong_formula1", "wrong_formula2", "wrong_formula3", "wrong_formula4"];
    return {
      prompt: t("ask_formula", { name: entry.correct_name }),
      options: keys.filter((key) => entry[key]).map((key) => ({ text: formulaToUnicode(entry[key]), correct: key === "correct_formula" })),
      formula: true,
    };
  }
  const keys = ["correct_name", "wrong_name1", "wrong_name2", "wrong_name3", "wrong_name4"];
  return {
    prompt: t("ask_name", { formula: formulaToUnicode(entry.correct_formula) }),
    options: keys.filter((key) => entry[key]).map((key) => ({ text: entry[key], correct: key === "correct_name" })),
  };
}

async function newRound(kind, params) {
  const categoryId = params.get("category");
  const difficulty = params.get("difficulty");
  const entries = await api.entries(kind, state.group.id, { category_id: categoryId, difficulty });
  return {
    key: roundKey(kind, params),
    entries: shuffle(entries),
    index: 0,
    order: null,
  };
}

/**
 * `focusPrompt` moves focus to the new question after answering, so keyboard and screen reader
 * users continue right there instead of on a button that no longer exists.
 */
export async function renderQuiz(view, kind, params, { focusPrompt = false, fresh = false } = {}) {
  const config = KINDS[kind];
  const owner = isOwner();
  const back = `#/${kind}`;
  const stale = staleCheck();

  // `fresh`: the user opened the quiz from a link, so start over even if the same round exists
  // (otherwise a finished round would greet them with "Well done!" right away).
  if (fresh || !round || round.key !== roundKey(kind, params)) {
    const next = await newRound(kind, params);
    if (stale()) return;
    round = next;
  }

  let title = t(config.titleKey);
  const categoryId = params.get("category");
  const categories = owner || categoryId ? await api.categories(state.group.id, config.type) : [];
  if (categoryId) {
    const category = categories.find((item) => String(item.id) === categoryId);
    if (category) title = category.name;
  }
  if (stale()) return;

  const restart = async () => {
    const next = await newRound(kind, params);
    if (stale()) return;
    round = next;
    renderQuiz(view, kind, params, { focusPrompt: true }).catch(showError);
  };

  if (!round.entries.length) {
    replaceContent(view, 
      pageHeader(title, { back }),
      h("div", { class: "empty-state" },
        h("p", {}, t("no_entries")),
        button(t("back"), { icon: "back", variant: "filled", onclick: () => { location.hash = back; } }),
      ),
    );
    return;
  }

  if (round.index >= round.entries.length) {
    replaceContent(view, 
      pageHeader(title, { back }),
      h("div", { class: "empty-state done" },
        h("h2", { class: "done-title" }, t("well_done")),
        h("p", {}, t("round_complete")),
        h("div", { class: "row center" },
          button(t("play_again"), { icon: "play", variant: "filled", onclick: () => restart().catch(showError) }),
          button(t("back"), { icon: "back", variant: "text", onclick: () => { location.hash = back; } }),
        ),
      ),
    );
    if (focusPrompt) focusElement(view.querySelector(".done-title"));
    return;
  }

  const entry = round.entries[round.index];
  const question = buildQuestion(kind, entry);
  // Keep the option order stable while the same entry is shown (e.g. across a language switch).
  if (!round.order || round.order.id !== entry.id || round.order.size !== question.options.length) {
    round.order = { id: entry.id, size: question.options.length, indexes: shuffle(question.options.map((_, i) => i)) };
  }
  const options = round.order.indexes.map((i) => question.options[i]);

  const feedback = h("p", { class: "feedback", "aria-live": "polite" });
  let answered = false;

  // Answered options get aria-disabled instead of disabled: a disabled button would drop the
  // keyboard focus. The result is shown by color, a ✓/✗ mark and screen-reader-only text.
  const mark = (optionButton, key) => {
    optionButton.setAttribute("aria-disabled", "true");
    optionButton.append(h("span", { class: "sr-only" }, ` ${t(key)}`));
  };
  const optionButtons = options.map((option) => {
    const optionButton = h("button", { type: "button", class: question.formula ? "option formula" : "option" },
      h("span", {}, option.text));
    optionButton.addEventListener("click", () => {
      if (answered || optionButton.getAttribute("aria-disabled") === "true") return;
      if (option.correct) {
        answered = true;
        optionButton.classList.add("correct");
        mark(optionButton, "marked_correct");
        feedback.textContent = t("correct");
        feedback.className = "feedback good";
        for (const other of optionButtons) other.setAttribute("aria-disabled", "true");
        setTimeout(() => {
          if (stale()) return; // the user has moved on
          round.index += 1;
          renderQuiz(view, kind, params, { focusPrompt: true }).catch(showError);
        }, 900);
      } else {
        optionButton.classList.add("wrong");
        mark(optionButton, "marked_wrong");
        feedback.textContent = t("wrong");
        feedback.className = "feedback bad";
      }
    });
    return optionButton;
  });

  const ownerActions = owner ? [
    button(t(config.editKey), {
      icon: "edit", variant: "text", iconOnly: true,
      onclick: async () => {
        const updated = await entryDialog(kind, categories, entry);
        if (!updated || stale()) return;
        round.entries[round.index] = updated;
        round.order = null;
        renderQuiz(view, kind, params, { focusPrompt: true }).catch(showError);
      },
    }),
    button(t(config.deleteKey), {
      icon: "delete", variant: "text-danger", iconOnly: true,
      onclick: async () => {
        const name = kind === "compounds" ? entry.correct_name : entry.question;
        if (!(await confirmDelete(config.deleteKey, name))) return;
        try {
          await api.deleteEntry(kind, entry.id);
          if (stale()) return;
          round.entries.splice(round.index, 1);
          round.order = null;
          renderQuiz(view, kind, params, { focusPrompt: true }).catch(showError);
        } catch (error) {
          showError(error);
        }
      },
    }),
  ] : [];

  const progress = (round.index / round.entries.length) * 100;

  replaceContent(view, 
    pageHeader(title, { back, actions: ownerActions }),
    // Decorative: the "1 of 3" text below says the same for everyone.
    h("div", { class: "progress", "aria-hidden": "true" },
      h("div", { class: "progress-bar", style: `width:${progress}%` })),
    h("p", { class: "progress-text" }, t("progress", { current: round.index + 1, total: round.entries.length })),
    h("section", { class: "card quiz-card" },
      h("h2", { class: "quiz-prompt" }, question.prompt),
      h("div", { class: "options", role: "group", "aria-label": t("answers") }, optionButtons),
      feedback,
    ),
  );
  if (focusPrompt) focusElement(view.querySelector(".quiz-prompt"));
}
