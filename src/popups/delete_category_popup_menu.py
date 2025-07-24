from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivy.app import App
from kivy.uix.widget import Widget
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.menu import MDDropdownMenu


class DeleteCategoryPopUpMenu(MDDialog):
    def __init__(self):
        self.selected_category = None

        self.categories_button_text = MDButtonText(text="Select Category")

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

        super().__init__(
            MDDialogHeadlineText(text="Delete Category", halign="center"),
            MDDialogContentContainer(content_box),
            MDDialogButtonContainer(
                Widget(),
                MDButton(MDButtonText(text="Cancel"), style="text", on_release=self.dismiss),
                MDButton(MDButtonText(text="Delete"), style="text", on_release=self.delete_category),
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


    def open_categories_dropdown(self, *args, **kwargs):
        self.categories_dropdown_menu.open()


    def get_category_items(self):
        app = App.get_running_app()
        categories = app.db.get_all_categories_by_group(app.logged_in_group)
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
        app = App.get_running_app()
        category = self.selected_category

        valid = True
        if not category:
            self.categories_button_text.text = "Please select a category"
            valid = False
        else:
            self.categories_button_text.error = False

        if valid:
            app.db.delete_category(category)
            app.compound_menu_screen.fill_category_list()
            self.dismiss()


    def dismiss(self, *args, **kwargs):
        self.categories_button_text.text = "Select Category"
        self.selected_category = None
        super().dismiss()
