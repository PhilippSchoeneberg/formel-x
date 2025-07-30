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
        self.app = App.get_running_app()
        self.edit = False
        self.selected_category = None

        self.name_hint_text = MDTextFieldHintText(text=self.app.language_manager.translate("category_name"))
        self.name_helper_text = MDTextFieldHelperText(text=self.app.language_manager.translate("category_name") + self.app.language_manager.translate("empty_error"), mode="on_error")

        self.name_field = MDTextField(
            self.name_hint_text,
            self.name_helper_text,
            mode="outlined",
            size_hint_x=1,
            pos_hint={"center_x": 0.5},
        )

        self.categories_button_text = MDButtonText(text=self.app.language_manager.translate("select") + self.app.language_manager.translate("category"))

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

        self.headline_text = MDDialogHeadlineText(text=self.app.language_manager.translate("create") + self.app.language_manager.translate("category"), halign="center")
        self.cancel_button_text = MDButtonText(text=self.app.language_manager.translate("cancel"))
        self.submit_button_text = MDButtonText(text=self.app.language_manager.translate("submit"))

        super().__init__(
            self.headline_text,
            MDDialogContentContainer(self.content_box),
            MDDialogButtonContainer(
                Widget(),
                MDButton(self.cancel_button_text, style="text", on_release=self.dismiss),
                MDButton(self.submit_button_text, style="text", on_release=self.add_category),
                spacing="8dp",
            ),
        )

        self.categories_dropdown_menu = MDDropdownMenu(
            caller=self.categories_button,
            items=[],
            width_mult=4,
        )


    def open(self, edit=False):
        self.app.general_dropdown_menu.dismiss()
        self.edit = edit
        self.name_hint_text.text = self.app.language_manager.translate("category_name")
        self.name_helper_text.text = self.app.language_manager.translate("category_name") + self.app.language_manager.translate("empty_error")
        self.categories_button_text.text = self.app.language_manager.translate("select") + self.app.language_manager.translate("category")
        if self.edit:
            self.headline_text.text = self.app.language_manager.translate("edit") + self.app.language_manager.translate("category")
            self.content_box.add_widget(self.categories_button)
        else:
            self.headline_text.text = self.app.language_manager.translate("create") + self.app.language_manager.translate("category")
        self.cancel_button_text.text = self.app.language_manager.translate("cancel")
        self.submit_button_text.text = self.app.language_manager.translate("submit")
        self.categories_dropdown_menu.items = self.get_category_items()
        super().open()


    def open_categories_dropdown(self, *args, **kwargs):
        self.categories_dropdown_menu.open()


    def get_category_items(self):
        categories = self.app.db.get_all_categories_by_group(self.app.logged_in_group)
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
        name = self.name_field.text.strip()
        category = self.selected_category
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        valid = True

        if not name:
            self.name_helper_text.text = self.app.language_manager.translate("category_name") + self.app.language_manager.translate("empty_error")
            self.name_field.error = False
            self.name_field.error = True
            valid = False

        categories = self.app.db.get_all_categories_by_group(self.app.logged_in_group)
        for cat in categories.values():
            if cat["name"] == name:
                self.name_helper_text.text = self.app.language_manager.translate("category") + self.app.language_manager.translate("already_exists_error")
                self.name_field.error = False
                self.name_field.error = True
                valid = False

        if not self.edit:
            if valid:
                self.app.db.cursor.execute(
                    "INSERT INTO categories (name, group_id, date) VALUES (?, ?, ?)",
                    (name, self.app.logged_in_group["id"], date)
                )
                self.app.db.connection.commit()
                self.app.compound_menu_screen.fill_category_list()
                self.dismiss()
        else:
            if not category:
                valid = False
            if valid:
                self.app.db.cursor.execute(
                    "UPDATE categories SET name = ?, group_id = ?, date = ? WHERE id = ?",
                    (name, self.app.logged_in_group["id"], date, category["id"])
                )
                self.app.db.connection.commit()
                self.app.compound_menu_screen.fill_category_list()
                self.dismiss()


    def dismiss(self, *args, **kwargs):
        self.content_box.remove_widget(self.categories_button)
        self.name_field.text = ""
        self.name_field.error = False
        self.selected_category = None
        super().dismiss()
