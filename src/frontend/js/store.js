// App-wide state. Preferences (theme, language, selected group and the groups an
// anonymous visitor has added) are remembered in localStorage; the account comes from the
// server session.

import { api } from "./api.js";

const STORAGE_KEY = "formelx";

function readPrefs() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {};
  } catch {
    return {};
  }
}

export const state = {
  account: null,
  groups: [],
  group: null,
  prefs: {
    theme: null, // "light" | "dark" | null (follow the system)
    language: null,
    groupId: null,
    savedGroups: [], // [{id, name}] for visitors without an account
    ...readPrefs(),
  },
};

// Every navigation or full re-render gets a new number. Views remember the number they were
// started with and stop when it's outdated: a slow request or a timer must never draw an old
// page over the one the user has moved on to.
let generation = 0;

export function nextGeneration() {
  generation += 1;
  return generation;
}

/** Returns a function that tells whether the current view has been replaced since this call. */
export function staleCheck() {
  const started = generation;
  return () => started !== generation;
}

const listeners = new Set();

export function onChange(listener) {
  listeners.add(listener);
}

export function notify() {
  for (const listener of listeners) listener();
}

export function savePrefs(changes = {}) {
  Object.assign(state.prefs, changes);
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state.prefs));
  } catch {
    // Storage can be unavailable (private mode); the app still works for this visit.
  }
}

export function isOwner() {
  return Boolean(state.account && state.group && state.group.owner_id === state.account.id);
}

export async function loadAccount() {
  const { account } = await api.me();
  state.account = account;
}

/** Reloads the visible groups and keeps the selection valid. */
export async function refreshGroups() {
  if (state.account) {
    state.groups = await api.myGroups();
  } else {
    const ids = state.prefs.savedGroups.map((group) => group.id);
    // Groups deleted by their owner disappear from the saved list.
    state.groups = ids.length ? await api.lookupGroups(ids) : [];
    savePrefs({ savedGroups: state.groups.map(({ id, name }) => ({ id, name })) });
  }
  const selected = state.groups.find((group) => group.id === state.prefs.groupId);
  setGroup(selected || state.groups[0] || null, false);
}

export function setGroup(group, shouldNotify = true) {
  state.group = group;
  savePrefs({ groupId: group ? group.id : null });
  if (shouldNotify) notify();
}

export function saveVisitorGroup(group) {
  const saved = state.prefs.savedGroups.filter((item) => item.id !== group.id);
  saved.push({ id: group.id, name: group.name });
  savePrefs({ savedGroups: saved });
}

export function removeVisitorGroup(group) {
  savePrefs({ savedGroups: state.prefs.savedGroups.filter((item) => item.id !== group.id) });
}
