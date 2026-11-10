"""Keyboard and screen reader behavior: focus, names, page titles."""

import re

from playwright.sync_api import Page, expect

from tests.e2e.test_flows import add_demo_group


def test_navigation_moves_focus_to_the_page_heading(page: Page):
    add_demo_group(page)
    page.get_by_role("link", name="Compounds").click()
    heading = page.get_by_role("heading", level=1, name="Compounds")
    expect(heading).to_be_focused()
    expect(page).to_have_title("Compounds – FormelX")


def test_periodic_table_is_one_tab_stop_with_arrow_keys(page: Page):
    add_demo_group(page)
    page.get_by_role("link", name="Periodic table").click()

    table = page.get_by_role("group", name="Periodic table")
    expect(table.locator('[tabindex="0"]')).to_have_count(1)

    iron = page.get_by_role("button", name=re.compile(r"^Fe, Iron, period 4, group 8"))
    iron.focus()
    page.keyboard.press("ArrowRight")
    expect(page.get_by_role("button", name=re.compile(r"^Co, Cobalt"))).to_be_focused()
    page.keyboard.press("ArrowDown")
    expect(page.get_by_role("button", name=re.compile(r"^Rh, Rhodium"))).to_be_focused()
    page.keyboard.press("Home")
    expect(page.get_by_role("button", name=re.compile(r"^Rb, Rubidium"))).to_be_focused()
    # Hydrogen is alone in its row, so moving up from lithium lands on it.
    page.get_by_role("button", name=re.compile(r"^Li, Lithium")).focus()
    page.keyboard.press("ArrowUp")
    expect(page.get_by_role("button", name=re.compile(r"^H, Hydrogen"))).to_be_focused()

    # Visitors hear which elements are in the practice list.
    expect(page.get_by_role("button", name="O, Oxygen, period 2, group 16, in the practice list")).to_be_visible()


def test_practice_mode_names_positions_not_elements(page: Page):
    add_demo_group(page)
    page.get_by_role("link", name="Periodic table").click()
    page.get_by_role("button", name="Practice", exact=True).click()
    expect(page.get_by_role("button", name="Practice", exact=True)).to_be_focused()

    expect(page.get_by_role("button", name="Period 4, group 8", exact=True)).to_be_visible()
    expect(page.get_by_role("button", name="Lanthanides, position 1", exact=True)).to_be_visible()
    expect(page.get_by_role("button", name=re.compile("Iron"))).to_have_count(0)
    # Practice mode has no legend; the empty slot must not render as the text "null".
    expect(page.locator("main")).not_to_contain_text("null")


def test_wrong_quiz_answer_keeps_focus_and_correct_answer_moves_to_next_question(page: Page):
    add_demo_group(page)
    page.get_by_role("link", name="Compounds").click()
    page.get_by_role("link", name=re.compile("Acids")).click()

    wrong = page.get_by_role("button", name="H₂SO₃")
    wrong.focus()
    page.keyboard.press("Enter")
    expect(page.get_by_role("button", name="H₂SO₃ (wrong)")).to_be_focused()
    expect(page.get_by_role("button", name="H₂SO₃ (wrong)")).to_have_attribute("aria-disabled", "true")

    page.get_by_role("button", name="H₂SO₄").press("Enter")
    expect(page.get_by_role("heading", name="Well done!")).to_be_focused()


def test_form_errors_focus_the_first_invalid_field(page: Page):
    page.goto("/")
    page.get_by_role("button", name="Add group").click()
    dialog = page.get_by_role("dialog", name="Add group")
    expect(dialog.get_by_label("Group name")).to_be_focused()
    dialog.get_by_role("button", name="Add group").click()
    name = dialog.get_by_label("Group name")
    expect(name).to_be_focused()
    expect(name).to_have_attribute("aria-invalid", "true")
    expect(name).to_have_accessible_description("This field is required.")
