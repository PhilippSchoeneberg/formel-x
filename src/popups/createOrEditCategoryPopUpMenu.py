from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivy.app import App
from kivy.uix.widget import Widget
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText, MDTextFieldHelperText
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.menu import MDDropdownMenu
import datetime


class CreateOrEditCategoryPopUpMenu(MDDialog):
    def __init__(self):
        self.edit = False
        self.selected_category = None
        self.name_helper_text = MDTextFieldHelperText(text="Category name can't be empty", mode="on_error")

        self.name_field = MDTextField(
            MDTextFieldHintText(text="Category name"),
            self.name_helper_text,
            mode="outlined",
            size_hint_x=1,
            pos_hint={"center_x": 0.5},
        )

        self.categories_button_text = MDButtonText(text="Select Category")

        self.categories_button = MDButton(
            self.categories_button_text,
            style="outlined",
            on_release=self.open_categories_dropdown,
        )

        self.content_box = MDBoxLayout(
            self.name_field,
            orientation="vertical",
            spacing="30dp",
            adaptive_height=True,
            size_hint_y=None,
        )

        self.headline = MDDialogHeadlineText(text="Create Category", halign="center")

        super().__init__(
            self.headline,
            MDDialogContentContainer(self.content_box),
            MDDialogButtonContainer(
                Widget(),
                MDButton(MDButtonText(text="Cancel"), style="text", on_release=self.dismiss),
                MDButton(MDButtonText(text="Submit"), style="text", on_release=self.add_category),
                spacing="8dp",
            ),
        )

        self.categories_dropdown_menu = MDDropdownMenu(
            caller=self.categories_button,
            items=[],
            width_mult=4,
        )


    def open(self, edit=False):
        self.edit = edit
        if self.edit:
            self.headline.text = "Edit Category"
            self.content_box.add_widget(self.categories_button)
        self.categories_dropdown_menu.items = self.get_category_items()
        super().open()


    def open_categories_dropdown(self, *args, **kwargs):
        self.categories_dropdown_menu.open()


    def get_category_items(self):
        app = App.get_running_app()
        categories = app.db.get_all_categories_by_group(app.loggedInGroup)
        return [
            {
                "text": category["name"],
                "on_release": lambda x=category: self.set_category(x),
            }
            for category in categories.values()
        ]


    def set_category(self, category):
        self.selected_category = category
        self.categories_button_text.text = category["name"]
        self.name_field.text = category["name"]
        self.categories_dropdown_menu.dismiss()


    def add_category(self, *args, **kwargs):
        app = App.get_running_app()
        name = self.name_field.text.strip()
        category = self.selected_category
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        valid = True

        if not name:
            self.name_helper_text.text = "Category name can't be empty"
            self.name_field.error = False
            self.name_field.error = True
            valid = False

        categories = app.db.get_all_categories_by_group(app.loggedInGroup)
        for cat in categories.values():
            if cat["name"] == name:
                self.name_helper_text.text = "Group name already exists"
                self.name_field.error = False
                self.name_field.error = True
                valid = False

        if not category:
            self.categories_button_text.text = "Please select a category"
            valid = False

        if valid:
            if not self.edit:
                app.db.cursor.execute(
                    "INSERT INTO categories (name, group_id, date) VALUES (?, ?, ?)",
                    (name, app.loggedInGroup["id"], date)
                )
            else:
                app.db.cursor.execute(
                    "UPDATE categories SET name = ?, group_id = ?, date = ? WHERE id = ?",
                    (name, app.loggedInGroup["id"], date, category["id"])
                )
            app.db.connection.commit()
            app.compoundMenuScreen.fill_category_list()
            self.dismiss()



    def dismiss(self, *args, **kwargs):
        self.headline.text = "Create Category"
        self.content_box.remove_widget(self.categories_button)
        self.name_field.text = ""
        self.name_field.error = False
        self.categories_button_text.text = "Select Category"
        self.selected_category = None
        super().dismiss()
