// Periodic table. Study mode shows the table (owners click elements to add them to the
// group's practice list); practice mode hides the symbols and asks "Where is <element>?".
//
// Accessibility: the table is a single Tab stop and the arrow keys move between elements
// (roving tabindex). In practice mode each cell is announced by its position (period and
// group), which is what the question is about, without giving away the element.

import { api } from "../api.js";
import { showError } from "../dialogs.js";
import { getLanguage, t } from "../i18n.js";
import { isOwner, staleCheck, state } from "../store.js";
import { focusElement, h, messageDialog, replaceContent, shuffle, uid } from "../ui.js";
import { pageHeader, segmented } from "./common.js";

// The database stores the f-block in group 3, so order it by atomic number here.
const LANTHANIDES = ["La", "Ce", "Pr", "Nd", "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb", "Lu"];
const ACTINIDES = ["Ac", "Th", "Pa", "U", "Np", "Pu", "Am", "Cm", "Bk", "Cf", "Es", "Fm", "Md", "No", "Lr"];
const SERIES = [
  { key: "lanthanides", symbols: LANTHANIDES, row: 9 },
  { key: "actinides", symbols: ACTINIDES, row: 10 },
];
const NAVIGATION_KEYS = ["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown", "Home", "End"];

let allElements = null;

const session = {
  groupId: null,
  symbols: new Set(),
  mode: "remembering",
  queue: [],
  index: 0,
  wrong: new Set(),
  solved: null,
  focusedSymbol: null,
};

async function loadElements() {
  if (!allElements) allElements = await api.elements();
  return allElements;
}

/** Grid positions: rows 1–7 are the main table, row 8 is a gap, rows 9–10 the f-block. */
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

  for (const series of SERIES) {
    series.symbols.forEach((symbol, index) => {
      const element = bySymbol.get(symbol);
      if (element) cells.push({ element, row: series.row, column: 3 + index, series: series.key, position: index + 1 });
    });
  }
  return cells;
}

function lowercaseName(name) {
  // Element names are capitalized as labels; inside a sentence only German keeps the capital.
  return getLanguage() === "de" ? name : name.toLocaleLowerCase(getLanguage());
}

function startLearning() {
  const queue = (allElements || []).filter((element) => session.symbols.has(element.symbol));
  if (!queue.length) {
    messageDialog(t("no_elements"));
    return false;
  }
  session.queue = shuffle(queue);
  session.index = 0;
  session.wrong = new Set();
  session.solved = null;
  return true;
}

/** Arrow-key target for a cell: same row/column, skipping gaps; nearest column when a row is shorter. */
function neighbour(cells, from, key) {
  const sameRow = cells.filter((cell) => cell.row === from.row).sort((a, b) => a.column - b.column);
  if (key === "ArrowLeft") return [...sameRow].reverse().find((cell) => cell.column < from.column);
  if (key === "ArrowRight") return sameRow.find((cell) => cell.column > from.column);
  if (key === "Home") return sameRow[0];
  if (key === "End") return sameRow[sameRow.length - 1];

  const rows = [...new Set(cells.map((cell) => cell.row))].sort((a, b) => a - b);
  const rowIndex = rows.indexOf(from.row);
  const targetRow = key === "ArrowUp" ? rows[rowIndex - 1] : key === "ArrowDown" ? rows[rowIndex + 1] : undefined;
  if (targetRow === undefined) return undefined;
  const candidates = cells.filter((cell) => cell.row === targetRow);
  return candidates.reduce((best, cell) =>
    !best || Math.abs(cell.column - from.column) < Math.abs(best.column - from.column) ? cell : best, null);
}

export async function renderElements(view, { focus = null } = {}) {
  const stale = staleCheck();
  const [elements, symbols] = await Promise.all([loadElements(), api.groupElements(state.group.id)]);
  if (stale()) return;
  if (session.groupId !== state.group.id) {
    session.groupId = state.group.id;
    session.mode = "remembering";
    session.focusedSymbol = null;
  }
  session.symbols = new Set(symbols);

  const owner = isOwner();
  const learning = session.mode === "learning";
  const cells = layout(elements);
  const elementCells = cells.filter((cell) => cell.element);
  const pending = new Set(); // symbols with a save in progress

  const prompt = h("p", { class: "prompt", "aria-live": "polite" });
  const progress = h("p", { class: "progress-text" });
  const feedback = h("p", { class: "feedback", "aria-live": "polite" });
  const hintId = uid("table-hint");
  const table = h("div", {
    class: learning ? "periodic-table learning" : "periodic-table",
    role: "group",
    "aria-label": t("mode_elements"),
    "aria-describedby": hintId,
  });
  const buttons = new Map();

  const current = () => session.queue[session.index];

  function cellLabel(cell) {
    const { element } = cell;
    if (learning) {
      return cell.series
        ? t("cell_label_f", { series: t(cell.series), position: cell.position })
        : t("cell_label", { period: element.system_period, group: element.system_group });
    }
    const name = t(element.name);
    let label = cell.series
      ? t("element_label_f", { symbol: element.symbol, name, series: t(cell.series) })
      : t("element_label", { symbol: element.symbol, name, period: element.system_period, group: element.system_group });
    // Owners hear "pressed"/"not pressed" (aria-pressed); everyone else gets the state in the name.
    if (!owner && session.symbols.has(element.symbol)) label += `, ${t("in_practice_list")}`;
    return label;
  }

  function paint() {
    for (const cell of elementCells) {
      const { symbol } = cell.element;
      const button = buttons.get(symbol);
      const inGroup = session.symbols.has(symbol);
      const wrong = learning && session.wrong.has(symbol);
      button.classList.toggle("in-group", !learning && inGroup);
      button.classList.toggle("wrong", wrong);
      button.classList.toggle("correct", learning && session.solved === symbol);
      button.setAttribute("aria-label", wrong ? `${cellLabel(cell)} ${t("marked_wrong")}` : cellLabel(cell));
      if (!learning && owner) button.setAttribute("aria-pressed", String(inGroup));
      else button.removeAttribute("aria-pressed");
    }
    if (learning) {
      prompt.textContent = t("where_is", { element: lowercaseName(t(current().name)) });
      progress.textContent = t("progress", { current: session.index + 1, total: session.queue.length });
    } else {
      prompt.textContent = owner ? t("elements_owner_hint") : t("elements_study_hint");
      progress.textContent = "";
    }
  }

  function setTabStop(symbol) {
    for (const [cellSymbol, button] of buttons) button.tabIndex = cellSymbol === symbol ? 0 : -1;
    session.focusedSymbol = symbol;
  }

  async function onCellClick(element) {
    if (learning) {
      if (session.solved) return;
      if (element.symbol === current().symbol) {
        session.solved = element.symbol;
        feedback.textContent = t("correct");
        feedback.className = "feedback good";
        paint();
        setTimeout(async () => {
          if (stale()) return; // the user has moved on
          session.index += 1;
          session.wrong = new Set();
          session.solved = null;
          if (session.index >= session.queue.length) {
            session.mode = "remembering";
            await renderElements(view).catch(showError);
            if (stale()) return;
            await messageDialog(t("round_complete"), t("well_done"));
            focusElement(view.querySelector("h1"));
            return;
          }
          feedback.textContent = "";
          paint();
        }, 900);
      } else {
        session.wrong.add(element.symbol);
        feedback.textContent = t("wrong");
        feedback.className = "feedback bad";
        paint();
      }
      return;
    }
    if (!owner || pending.has(element.symbol)) return;
    // Don't disable the button while saving: a disabled button loses keyboard focus.
    pending.add(element.symbol);
    const adding = !session.symbols.has(element.symbol);
    adding ? session.symbols.add(element.symbol) : session.symbols.delete(element.symbol);
    paint();
    try {
      if (adding) await api.addElement(state.group.id, element.symbol);
      else await api.removeElement(state.group.id, element.symbol);
    } catch (error) {
      adding ? session.symbols.delete(element.symbol) : session.symbols.add(element.symbol);
      paint();
      showError(error);
    } finally {
      pending.delete(element.symbol);
    }
  }

  for (const cell of cells) {
    const style = `grid-row:${cell.row};grid-column:${cell.column}`;
    if (cell.placeholder) {
      table.append(h("div", { class: "element placeholder", style, "aria-hidden": "true" }, cell.placeholder));
      continue;
    }
    const { element } = cell;
    const button = h("button", {
      type: "button",
      class: "element",
      style,
      // In practice mode the tooltip must not reveal the answer.
      title: learning ? null : t(element.name),
      "data-symbol": element.symbol,
      tabindex: "-1",
    }, h("span", { class: "symbol", "aria-hidden": "true" }, element.symbol));
    button.addEventListener("click", () => onCellClick(element));
    button.addEventListener("focus", () => setTabStop(element.symbol));
    button.addEventListener("keydown", (event) => {
      if (!NAVIGATION_KEYS.includes(event.key)) return;
      event.preventDefault();
      const target = neighbour(elementCells, cell, event.key);
      if (target) buttons.get(target.element.symbol).focus();
    });
    buttons.set(element.symbol, button);
    table.append(button);
  }
  setTabStop(buttons.has(session.focusedSymbol) ? session.focusedSymbol : elementCells[0].element.symbol);

  const modeToggle = segmented(
    [
      { value: "remembering", label: t("study_mode") },
      { value: "learning", label: t("practice_mode") },
    ],
    session.mode,
    (mode) => {
      if (mode === "learning" && !startLearning()) return;
      session.mode = mode;
      renderElements(view, { focus: "mode" }).catch(showError);
    },
    t("mode"),
  );

  const legend = !learning && session.symbols.size
    ? h("p", { class: "legend" }, h("span", { class: "legend-swatch", "aria-hidden": "true" }), t("legend_in_practice_list"))
    : null;

  replaceContent(view, 
    pageHeader(t("mode_elements")),
    h("div", { class: "toolbar" }, modeToggle, progress),
    prompt,
    feedback,
    h("p", { class: "sr-only", id: hintId }, t("table_keyboard_hint")),
    h("div", { class: "table-scroll" }, table),
    legend,
  );
  paint();
  // Switching modes rebuilds the page; keep focus on the mode switch.
  if (focus === "mode") view.querySelector(".segmented .selected")?.focus();
}
