from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivy.app import App
from kivy.uix.widget import Widget
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.menu import MDDropdownMenu


class DeleteCategoryPopupMenu(MDDialog):
    def __init__(self):
        self.app = App.get_running_app()
        self.selected_category = None
        self.category_type = None

        self.categories_button_text = MDButtonText(text=self.app.language_manager.translate("select") + self.app.language_manager.translate("category"))

        self.categories_button = MDButton(
            self.categories_button_text,
            style="outlined",
            on_release=self.open_categories_dropdown,
        )

        content_box = MDBoxLayout(
            self.categories_button,
            orientation="vertical",
            spacing="30dp",
            adaptive_height=True,
            size_hint_y=None,
        )

        self.headline_text = MDDialogHeadlineText(text=self.app.language_manager.translate("delete") + self.app.language_manager.translate("category"), halign="center")
        self.cancel_button_text = MDButtonText(text=self.app.language_manager.translate("cancel"))
        self.submit_button_text = MDButtonText(text=self.app.language_manager.translate("submit"))

        super().__init__(
            self.headline_text,
            MDDialogContentContainer(content_box),
            MDDialogButtonContainer(
                Widget(),
                MDButton(self.cancel_button_text, style="text", on_release=self.dismiss),
                MDButton(self.submit_button_text, style="text", on_release=self.delete_category),
                spacing="8dp",
            ),
        )

        self.categories_dropdown_menu = MDDropdownMenu(
            caller=self.categories_button,
            items=[],
            width_mult=4,
        )


    def open(self, category_type=None):
        self.category_type = category_type
        self.categories_dropdown_menu.items = self.get_category_items()
        super().open()


    def open_categories_dropdown(self, *args, **kwargs):
        self.categories_dropdown_menu.open()


    def get_category_items(self):
        categories = self.app.db.get_all_categories_by_type_and_group(self.category_type, self.app.logged_in_group)
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
        self.categories_dropdown_menu.dismiss()


    def delete_category(self, *args, **kwargs):
        category = self.selected_category

        valid = True
        if not category:
            valid = False
        else:
            self.categories_button_text.error = False

        if valid:
            self.app.db.delete_category(category)
            self.app.compound_menu_screen.fill_category_list()
            self.app.question_menu_screen.fill_category_list()
            self.dismiss()


    def dismiss(self, *args, **kwargs):
        self.categories_button_text.text = self.app.language_manager.translate("select") + self.app.language_manager.translate("category")
        self.selected_category = None
        super().dismiss()
