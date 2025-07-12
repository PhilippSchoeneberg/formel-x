from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivy.app import App
from kivy.uix.widget import Widget
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText, MDTextFieldHelperText
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.menu import MDDropdownMenu
import datetime


class CreateFormulaPopUpMenu(MDDialog):
    def __init__(self):
        self.selected_category = None

        self.name_field = MDTextField(
            MDTextFieldHintText(text="Formula name"),
            MDTextFieldHelperText(text="Formula name can't be empty", mode="on_error"),
            mode="outlined",
            size_hint_x=1,
            pos_hint={"center_x": 0.5},
        )

        self.formula_field = MDTextField(
            MDTextFieldHintText(text="Formula"),
            MDTextFieldHelperText(text="Formula can't be empty", mode="on_error"),
            mode="outlined",
            multiline=True,
            size_hint_x=1,
            pos_hint={"center_x": 0.5},
        )

        self.categories_button_text = MDButtonText(text="Select Category")

        self.categories_button = MDButton(
            self.categories_button_text,
            style="outlined",
            on_release=self.open_categories_dropdown,
        )

        content_box = MDBoxLayout(
            self.name_field,
            self.formula_field,
            self.categories_button,
            orientation="vertical",
            spacing="30dp",
            adaptive_height=True,
            size_hint_y=None,
        )

        super().__init__(
            MDDialogHeadlineText(text="Create Formula", halign="center"),
            MDDialogContentContainer(content_box),
            MDDialogButtonContainer(
                Widget(),
                MDButton(MDButtonText(text="Cancel"), style="text", on_release=self.dismiss),
                MDButton(MDButtonText(text="Submit"), style="text", on_release=self.add_note),
                spacing="8dp",
            ),
        )

        self.categories_dropdown_menu = MDDropdownMenu(
            caller=self.categories_button,
            items=[],
            width_mult=4,
        )

    def open(self):
        self.categories_dropdown_menu.items = self.get_category_items()
        super().open()

    def open_categories_dropdown(self, *args):
        self.categories_dropdown_menu.open()

    def get_category_items(self):
        app = App.get_running_app()
        app.cursor.execute("SELECT name FROM categories")
        categories = [row[0] for row in app.cursor.fetchall()]
        return [
            {
                "text": cat,
                "on_release": lambda x=cat: self.set_category(x),
            }
            for cat in categories
        ]

    def set_category(self, category):
        self.selected_category = category
        self.categories_button_text.text = category
        self.categories_dropdown_menu.dismiss()

    def add_note(self, *args, **kwargs):
        app = App.get_running_app()
        name = self.name_field.text.strip()
        formula = self.formula_field.text.strip()
        category = self.selected_category
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        valid = True
        if not name:
            self.name_field.error = True
            valid = False
        if not formula:
            self.formula_field.error = True
            valid = False
        if not category:
            self.categories_button_text.text = "Please select a category"
            valid = False

        if valid:
            app.cursor.execute("SELECT id FROM categories WHERE name = ?", (category,))
            result = app.cursor.fetchone()
            if result:
                category_id = result[0]
            app.cursor.execute(
                "INSERT INTO formulas (name, formula, category, date) VALUES (?, ?, ?, ?)",
                (name, formula, category_id, date)
            )
            app.connection.commit()
            self.dismiss()

    def dismiss(self, *args, **kwargs):
        self.name_field.text = ""
        self.formula_field.text = ""
        self.name_field.error = False
        self.formula_field.error = False
        self.categories_button_text.text = "Select Category"
        self.selected_category = None
        super().dismiss()
