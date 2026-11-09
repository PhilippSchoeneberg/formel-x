// Periodic table. Remembering mode shows the table (owners click elements to add them to the
// group's learning list); learning mode hides the symbols and asks "Where is <element>?".

import { api } from "../api.js";
import { showError } from "../dialogs.js";
import { t, tj } from "../i18n.js";
import { isOwner, state } from "../store.js";
import { h, messageDialog, shuffle } from "../ui.js";
import { pageHeader, segmented } from "./common.js";

// The database stores the f-block in group 3, so order it by atomic number here.
const LANTHANIDES = ["La", "Ce", "Pr", "Nd", "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb", "Lu"];
const ACTINIDES = ["Ac", "Th", "Pa", "U", "Np", "Pu", "Am", "Cm", "Bk", "Cf", "Es", "Fm", "Md", "No", "Lr"];

let allElements = null;

const session = {
  groupId: null,
  symbols: new Set(),
  mode: "remembering",
  queue: [],
  index: 0,
  wrong: new Set(),
  solved: null,
};

async function loadElements() {
  if (!allElements) allElements = await api.elements();
  return allElements;
}

function layout(elements) {
  const bySymbol = new Map(elements.map((element) => [element.symbol, element]));
  const fBlock = new Set([...LANTHANIDES, ...ACTINIDES]);
  const cells = [];

  for (const element of elements) {
    if (fBlock.has(element.symbol)) continue;
    cells.push({ element, row: element.system_period, column: element.system_group });
  }
  cells.push({ placeholder: "57–71", row: 6, column: 3 });
  cells.push({ placeholder: "89–103", row: 7, column: 3 });

  // Two separate rows below the main table, with a small gap (row 8 is left empty).
  [LANTHANIDES, ACTINIDES].forEach((series, seriesIndex) => {
    series.forEach((symbol, index) => {
      const element = bySymbol.get(symbol);
      if (element) cells.push({ element, row: 9 + seriesIndex, column: 3 + index });
    });
  });
  return cells;
}

function startLearning() {
  const queue = (allElements || []).filter((element) => session.symbols.has(element.symbol));
  if (!queue.length) {
    messageDialog(t("no_elements_yet_error"));
    return false;
  }
  session.queue = shuffle(queue);
  session.index = 0;
  session.wrong = new Set();
  session.solved = null;
  return true;
}

export async function renderElements(view) {
  const [elements, symbols] = await Promise.all([loadElements(), api.groupElements(state.group.id)]);
  if (session.groupId !== state.group.id) {
    session.groupId = state.group.id;
    session.mode = "remembering";
  }
  session.symbols = new Set(symbols);

  const owner = isOwner();
  const cells = layout(elements);

  const prompt = h("p", { class: "prompt", "aria-live": "polite" });
  const progress = h("p", { class: "progress-text" });
  const table = h("div", { class: "periodic-table", role: "grid" });
  const buttons = new Map();

  const current = () => session.queue[session.index];

  function paint() {
    const learning = session.mode === "learning";
    table.classList.toggle("learning", learning);
    for (const [symbol, cell] of buttons) {
      const inGroup = session.symbols.has(symbol);
      cell.classList.toggle("in-group", !learning && inGroup);
      cell.classList.toggle("wrong", learning && session.wrong.has(symbol));
      cell.classList.toggle("correct", learning && session.solved === symbol);
      if (!learning && owner) cell.setAttribute("aria-pressed", String(inGroup));
      else cell.removeAttribute("aria-pressed");
    }
    if (learning) {
      const element = current();
      prompt.textContent = `${t("element_learning_mode_list_text")}${t(element.name)}?`;
      progress.textContent = `${session.index + 1} / ${session.queue.length}`;
    } else {
      prompt.textContent = owner ? t("add_element_to_learning_mode_hint") : t("element_remembering_mode_list_text");
      progress.textContent = "";
    }
  }

  async function onCellClick(element, cell) {
    if (session.mode === "learning") {
      if (session.solved) return;
      if (element.symbol === current().symbol) {
        session.solved = element.symbol;
        paint();
        setTimeout(() => {
          session.index += 1;
          session.wrong = new Set();
          session.solved = null;
          if (session.index >= session.queue.length) {
            session.mode = "remembering";
            renderElements(view).catch(showError);
            messageDialog(t("round_complete"), t("correct_feedback"));
            return;
          }
          paint();
        }, 900);
      } else {
        session.wrong.add(element.symbol);
        paint();
      }
      return;
    }
    if (!owner) return;
    const adding = !session.symbols.has(element.symbol);
    adding ? session.symbols.add(element.symbol) : session.symbols.delete(element.symbol);
    paint();
    cell.disabled = true;
    try {
      if (adding) await api.addElement(state.group.id, element.symbol);
      else await api.removeElement(state.group.id, element.symbol);
    } catch (error) {
      adding ? session.symbols.delete(element.symbol) : session.symbols.add(element.symbol);
      paint();
      showError(error);
    } finally {
      cell.disabled = false;
    }
  }

  for (const item of cells) {
    const style = `grid-row:${item.row};grid-column:${item.column}`;
    if (item.placeholder) {
      table.append(h("div", { class: "element placeholder", style, "aria-hidden": "true" }, item.placeholder));
      continue;
    }
    const { element } = item;
    const name = t(element.name);
    const cell = h("button", {
      type: "button",
      class: "element",
      style,
      title: name,
      "aria-label": session.mode === "learning" ? name : `${element.symbol}, ${name}`,
    }, h("span", { class: "symbol" }, element.symbol));
    cell.addEventListener("click", () => onCellClick(element, cell));
    buttons.set(element.symbol, cell);
    table.append(cell);
  }
  // Learning mode must not reveal the answer through the accessible name either.
  if (session.mode === "learning") {
    for (const cell of buttons.values()) cell.setAttribute("aria-label", "?");
  }

  const modeToggle = segmented(
    [
      { value: "remembering", label: t("remembering_mode") },
      { value: "learning", label: t("learning_mode") },
    ],
    session.mode,
    (mode) => {
      if (mode === "learning" && !startLearning()) return;
      session.mode = mode;
      renderElements(view).catch(showError);
    },
    tj("select", "mode"),
  );

  view.replaceChildren(
    pageHeader(t("elements")),
    h("div", { class: "toolbar" }, modeToggle, progress),
    prompt,
    h("div", { class: "table-scroll" }, table),
  );
  paint();
}
