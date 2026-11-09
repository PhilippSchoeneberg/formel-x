// Multiple-choice round over the compounds or questions of a category (or all of them).
// The round survives re-renders (language change) as long as the URL stays the same.

import { api } from "../api.js";
import { confirmDelete, entryDialog, showError } from "../dialogs.js";
import { formulaToUnicode } from "../formula.js";
import { t, tj } from "../i18n.js";
import { isOwner, state } from "../store.js";
import { button, h, shuffle } from "../ui.js";
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
      prompt: `${t("compound_learning_mode_list_formula_text")}${entry.correct_name}?`,
      options: keys.filter((key) => entry[key]).map((key) => ({ text: formulaToUnicode(entry[key]), correct: key === "correct_formula" })),
      formula: true,
    };
  }
  const keys = ["correct_name", "wrong_name1", "wrong_name2", "wrong_name3", "wrong_name4"];
  return {
    prompt: `${t("compound_learning_mode_list_name_text")}${formulaToUnicode(entry.correct_formula)}?`,
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

export async function renderQuiz(view, kind, params) {
  const config = KINDS[kind];
  const owner = isOwner();
  const back = `#/${kind}`;

  if (!round || round.key !== roundKey(kind, params)) round = await newRound(kind, params);

  let title = t(config.titleKey);
  const categoryId = params.get("category");
  const categories = owner || categoryId ? await api.categories(state.group.id, config.type) : [];
  if (categoryId) {
    const category = categories.find((item) => String(item.id) === categoryId);
    if (category) title = category.name;
  }

  const restart = async () => {
    round = await newRound(kind, params);
    renderQuiz(view, kind, params).catch(showError);
  };

  if (!round.entries.length) {
    view.replaceChildren(
      pageHeader(title, { back }),
      h("div", { class: "empty-state" },
        h("p", {}, t("no_entries_yet_error")),
        button(t("back"), { icon: "back", variant: "filled", onclick: () => { location.hash = back; } }),
      ),
    );
    return;
  }

  if (round.index >= round.entries.length) {
    view.replaceChildren(
      pageHeader(title, { back }),
      h("div", { class: "empty-state done" },
        h("p", { class: "done-title" }, t("correct_feedback")),
        h("p", {}, t("round_complete")),
        h("div", { class: "row center" },
          button(t("restart"), { icon: "play", variant: "filled", onclick: () => restart().catch(showError) }),
          button(t("back"), { icon: "back", variant: "text", onclick: () => { location.hash = back; } }),
        ),
      ),
    );
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

  const optionButtons = options.map((option) => {
    const optionButton = h("button", { type: "button", class: question.formula ? "option formula" : "option" }, option.text);
    optionButton.addEventListener("click", () => {
      if (answered) return;
      if (option.correct) {
        answered = true;
        optionButton.classList.add("correct");
        feedback.textContent = t("correct_feedback");
        feedback.className = "feedback good";
        for (const other of optionButtons) other.disabled = other !== optionButton;
        setTimeout(() => {
          round.index += 1;
          renderQuiz(view, kind, params).catch(showError);
        }, 900);
      } else {
        optionButton.classList.add("wrong");
        optionButton.disabled = true;
        feedback.textContent = t("wrong_feedback");
        feedback.className = "feedback bad";
      }
    });
    return optionButton;
  });

  const ownerActions = owner ? [
    button(tj("edit", config.titleKey === "compounds" ? "compound" : "question"), {
      icon: "edit", variant: "text", iconOnly: true,
      onclick: async () => {
        const updated = await entryDialog(kind, categories, entry);
        if (!updated) return;
        round.entries[round.index] = updated;
        round.order = null;
        renderQuiz(view, kind, params).catch(showError);
      },
    }),
    button(tj("delete", config.titleKey === "compounds" ? "compound" : "question"), {
      icon: "delete", variant: "text-danger", iconOnly: true,
      onclick: async () => {
        const name = kind === "compounds" ? entry.correct_name : entry.question;
        if (!(await confirmDelete(kind === "compounds" ? "compound" : "question", name))) return;
        try {
          await api.deleteEntry(kind, entry.id);
          round.entries.splice(round.index, 1);
          round.order = null;
          renderQuiz(view, kind, params).catch(showError);
        } catch (error) {
          showError(error);
        }
      },
    }),
  ] : [];

  const progress = (round.index / round.entries.length) * 100;

  view.replaceChildren(
    pageHeader(title, { back, actions: ownerActions }),
    h("div", { class: "progress", role: "progressbar", "aria-valuemin": "0", "aria-valuemax": String(round.entries.length), "aria-valuenow": String(round.index) },
      h("div", { class: "progress-bar", style: `width:${progress}%` })),
    h("p", { class: "progress-text" }, `${round.index + 1} / ${round.entries.length}`),
    h("section", { class: "card quiz-card" },
      h("h2", { class: "quiz-prompt" }, question.prompt),
      h("div", { class: "options" }, optionButtons),
      feedback,
    ),
  );
}
