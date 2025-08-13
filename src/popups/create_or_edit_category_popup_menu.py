from kivy.app import App
from kivy.uix.widget import Widget
from ext.kivymd.uix.menu import MDDropdownMenu
from ext.kivymd.uix.boxlayout import MDBoxLayout
from ext.kivymd.uix.button import MDButton, MDButtonText
from ext.kivymd.uix.textfield import MDTextField, MDTextFieldHintText, MDTextFieldHelperText
from ext.kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer


class CreateOrEditCategoryPopupMenu(MDDialog):
    def __init__(self):
        self.app = App.get_running_app()
        self.selected_category = None
        self.category_type = None
        self.edit = False

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


    def open(self, category_type=None, edit=False):
        if self.app.general_dropdown_menu:
            self.app.general_dropdown_menu.dismiss()
        if self.app.root.get_screen("compoundMenu").create_dropdown_menu:
            self.app.root.get_screen("compoundMenu").create_dropdown_menu.dismiss()
        if self.app.root.get_screen("questionMenu").create_dropdown_menu:
            self.app.root.get_screen("questionMenu").create_dropdown_menu.dismiss()

        self.category_type = category_type
        self.edit = edit
        if self.edit:
            self.headline_text.text = self.app.language_manager.translate("edit") + self.app.language_manager.translate("category")
            self.content_box.add_widget(self.categories_button)
        else:
            self.headline_text.text = self.app.language_manager.translate("create") + self.app.language_manager.translate("category")

        self.categories_dropdown_menu.items = self.get_category_items()
        super().open()


    def open_categories_dropdown(self, *args, **kwargs):
        self.categories_dropdown_menu.open()


    def get_category_items(self):
        raw_categories = self.app.db.get_all_categories_by_type_and_group(self.category_type, self.app.logged_in_group)
        categories = [
            {
                "text": category["name"],
                "on_release": lambda x=category: self.set_category(x),
            }
            for category in raw_categories
        ]
        return sorted(categories, key=lambda x: x["text"])


    def set_category(self, category):
        self.selected_category = category
        self.categories_button_text.text = category["name"]
        self.name_field.text = category["name"]
        self.categories_dropdown_menu.dismiss()


    def add_category(self, *args, **kwargs):
        name = self.name_field.text.strip()
        category = self.selected_category
        valid = True

        if not name:
            self.name_helper_text.text = self.app.language_manager.translate("category_name") + self.app.language_manager.translate("empty_error")
            self.name_field.error = False
            self.name_field.error = True
            valid = False

        categories = self.app.db.get_all_categories_by_type_and_group(self.category_type, self.app.logged_in_group)
        for cat in categories:
            if cat["name"] == name:
                self.name_helper_text.text = self.app.language_manager.translate("category") + self.app.language_manager.translate("already_exists_error")
                self.name_field.error = False
                self.name_field.error = True
                valid = False

        if not self.edit:
            if valid:
                self.app.db.create_category(name, self.category_type, self.app.logged_in_group)
                self.app.root.get_screen(self.app.root.current).fill_category_list()
                self.dismiss()
        else:
            if not category:
                valid = False
            if valid:
                self.app.db.update_category(category["id"], name, self.category_type, self.app.logged_in_group)
                self.app.compound_menu_screen.fill_category_list()
                self.app.question_menu_screen.fill_category_list()
                self.dismiss()


    def dismiss(self, *args, **kwargs):
        self.content_box.remove_widget(self.categories_button)
        self.name_field.text = ""
        self.name_field.error = False
        self.selected_category = None
        self.category_type = None
        super().dismiss()
