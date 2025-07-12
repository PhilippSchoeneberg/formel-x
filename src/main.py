from createFormulaPopUpMenu import CreateFormulaPopUpMenu
from createCategoryPopUpMenu import CreateCategoryPopUpMenu

from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import MDListItem, MDListItemHeadlineText

from kivymd.app import MDApp
import sqlite3


class MainApp(MDApp):
    connection = None
    cursor = None

    def on_start(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = 'Darkblue'

        # Connect to database
        self.connection = sqlite3.connect("formulaX.db")
        self.cursor = self.connection.cursor()

        # Instantiate createFormulaPopUpMenu
        self.create_formula_popup_menu = CreateFormulaPopUpMenu()

        # Instantiate createFormulaPopUpMenu
        self.create_category_popup_menu = CreateCategoryPopUpMenu()

        self.fill_category_list()

    def add_menu_open(self):
        add_menu_items = [
            {
                "text": "Add Formula",
                "on_release": lambda: self.create_formula_popup_menu.open(),
            },
            {
                "text": "Add Category",
                "on_release": lambda: self.create_category_popup_menu.open(),
            }
        ]
        MDDropdownMenu(
            caller=self.root.ids.add_button, items=add_menu_items
        ).open()

    def get_all_categories(self):
        self.cursor.execute("SELECT name FROM categories")
        return [row[0] for row in self.cursor.fetchall()]

    def fill_category_list(self):
        self.root.ids.category_list.clear_widgets()
        categories = self.get_all_categories()

        for category in categories:
            item = MDListItem(
                MDListItemHeadlineText(text=category),
                on_release=lambda x=category: self.on_category_selected(x)
            )
            self.root.ids.category_list.add_widget(item)

    def on_category_selected(self, category_name):
        print(f"Selected category: {category_name}")

    def change_theme(self):
        self.theme_cls.primary_palette = (
            "Lightblue" if self.theme_cls.primary_palette == "Darkblue" else "Darkblue"
        )
        self.theme_cls.theme_style = (
            "Light" if self.theme_cls.theme_style == "Dark" else "Dark"
        )
        self.root.ids.theme_mode.icon = (
            "weather-night" if self.root.ids.theme_mode.icon == "weather-sunny" else "weather-sunny"
        )

MainApp().run()
