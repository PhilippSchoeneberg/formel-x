"""The main user flows in a real browser."""

import re

from playwright.sync_api import Page, expect

from src.backend.elements_data import ELEMENTS
from tests.e2e.conftest import OWNER_EMAIL, OWNER_PASSWORD


SYMBOL_BY_NAME = {name: symbol for symbol, name, _, _ in ELEMENTS}


def add_demo_group(page: Page):
    page.goto("/")
    page.get_by_role("button", name="Add group").click()
    page.get_by_label("Group name").fill("Demo")
    page.get_by_role("dialog").get_by_role("button", name="Add group").click()
    expect(page.get_by_role("heading", name="Choose a mode")).to_be_visible()


def log_in(page: Page):
    page.goto("/")
    page.locator("#header-actions").get_by_role("button", name="Log in").click()
    page.get_by_label("Email address").fill(OWNER_EMAIL)
    page.get_by_label("Password", exact=True).fill(OWNER_PASSWORD)
    page.get_by_role("dialog").get_by_role("button", name="Log in").click()
    expect(page.get_by_role("button", name="Log out")).to_be_visible()


def test_visitor_adds_a_group_and_plays_a_compound_round(page: Page):
    page.goto("/")
    page.get_by_role("button", name="Add group").click()
    page.get_by_label("Group name").fill("Unknown")
    page.get_by_role("dialog").get_by_role("button", name="Add group").click()
    expect(page.get_by_text("There is no group with this name.")).to_be_visible()
    page.get_by_role("button", name="Cancel").click()

    add_demo_group(page)
    page.get_by_role("link", name="Compounds").click()
    page.get_by_role("link", name=re.compile("Acids")).click()

    expect(page.get_by_role("heading", name="What is the formula of Sulfuric acid?")).to_be_visible()
    page.get_by_role("button", name="H₂SO₃").click()
    expect(page.get_by_text("Not quite – try again.")).to_be_visible()
    page.get_by_role("button", name="H₂SO₄").click()
    expect(page.get_by_text("You've answered everything in this round.")).to_be_visible()


def test_visitor_groups_are_remembered(page: Page):
    add_demo_group(page)
    page.reload()
    expect(page.get_by_label("Group")).to_have_value(re.compile(r"\d+"))
    expect(page.get_by_role("heading", name="Choose a mode")).to_be_visible()


def test_periodic_table_practice(page: Page):
    add_demo_group(page)
    page.get_by_role("link", name="Periodic table").click()
    page.get_by_role("button", name="Practice", exact=True).click()

    for round_number in range(1, 4):
        expect(page.get_by_text(f"{round_number} of 3")).to_be_visible()
        prompt = page.locator(".prompt").text_content()
        name = re.match(r"Where is (\w+)\?", prompt).group(1)
        page.locator(f'[data-symbol="{SYMBOL_BY_NAME[name]}"]').click()
        if round_number < 3:
            expect(page.get_by_text(f"{round_number + 1} of 3")).to_be_visible()
    expect(page.get_by_text("Well done!")).to_be_visible()


def test_owner_creates_a_category_and_a_compound(page: Page):
    log_in(page)
    page.get_by_role("link", name="Compounds").click()

    page.get_by_role("button", name="New category").click()
    page.get_by_label("Category name").fill("Bases")
    page.get_by_role("button", name="Save").click()
    expect(page.get_by_role("link", name=re.compile("Bases"))).to_be_visible()

    page.get_by_role("button", name="New compound").click()
    dialog = page.get_by_role("dialog")
    dialog.get_by_role("button", name="Save").click()
    expect(dialog.get_by_text("This field is required.").first).to_be_visible()

    dialog.get_by_label("Category").select_option(label="Bases")
    dialog.get_by_label("Difficulty").select_option("easy")
    dialog.get_by_label("Correct name").fill("Sodium hydroxide")
    dialog.get_by_label("Correct formula").fill("NaOH")
    dialog.get_by_label("Wrong name 1", exact=True).fill("Sodium oxide")
    dialog.get_by_label("Wrong formula 1", exact=True).fill("Na_2O")
    dialog.get_by_label("Wrong name 2", exact=True).fill("Sodium chloride")
    dialog.get_by_label("Wrong formula 2", exact=True).fill("NaCl")
    expect(dialog.get_by_text("Na₂O")).to_be_visible()  # live formula preview
    dialog.get_by_role("button", name="Save").click()
    expect(dialog).to_be_hidden()

    page.get_by_role("link", name=re.compile("Bases")).click()
    expect(page.get_by_role("heading", name="What is the formula of Sodium hydroxide?")).to_be_visible()


def test_registration_rules(page: Page):
    page.goto("/")
    page.locator("#header-actions").get_by_role("button", name="Log in").click()
    page.get_by_role("button", name="No account yet? Sign up").click()
    dialog = page.get_by_role("dialog")
    dialog.get_by_label("Email address").fill("not-an-email")
    dialog.get_by_label("Password", exact=True).fill("short")
    dialog.get_by_label("Repeat password").fill("short")
    dialog.get_by_role("button", name="Create account").click()
    expect(dialog.get_by_text("Please enter a valid email address.")).to_be_visible()

    dialog.get_by_label("Email address").fill("new@example.test")
    dialog.get_by_role("button", name="Create account").click()
    expect(dialog.get_by_text("Use at least 8 characters.")).to_be_visible()


def test_language_switch(page: Page):
    add_demo_group(page)
    page.get_by_label("Language").select_option("de")
    expect(page.get_by_role("heading", name="Wähle einen Modus")).to_be_visible()
    page.reload()
    expect(page.get_by_role("heading", name="Wähle einen Modus")).to_be_visible()
