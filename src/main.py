from popups.createCompoundPopUpMenu import CreateFormulaPopUpMenu
from popups.createCategoryPopUpMenu import CreateCategoryPopUpMenu
from popups.loginAccountPopUpMenu import LoginAccountPopUpMenu
from screens.mainMenu import MainMenuScreen
from screens.questionMenu import QuestionMenuScreen
from screens.compoundMenu import CompoundMenuScreen
from screens.elementMenu import ElementMenuScreen

from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import MDListItem, MDListItemHeadlineText
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from kivy.lang import Builder
import sqlite3

class MainApp(MDApp):
    connection = None
    cursor = None

    def build(self):
        kv_files = [
            "src/main.kv",
            "src/screens/mainMenu.kv",
            "src/screens/questionMenu.kv",
            "src/screens/compoundMenu.kv",
            "src/screens/elementMenu.kv",
        ]
        for file in kv_files:
            Builder.load_file(file)
        sm = ScreenManager()
        sm.add_widget(MainMenuScreen(name="mainMenu"))
        sm.add_widget(ElementMenuScreen(name="elementMenu"))
        sm.add_widget(CompoundMenuScreen(name="compoundMenu"))
        sm.add_widget(QuestionMenuScreen(name="questionMenu"))
        self.root = sm
        return sm

    def on_start(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = 'Darkblue'

        # Connect to database
        self.connection = sqlite3.connect("formulaX.db")
        self.cursor = self.connection.cursor()

        # Instantiate loginAccountPopUpMenu
        self.login_account_popup_menu = LoginAccountPopUpMenu()

        # Instantiate createFormulaPopUpMenu
        self.create_formula_popup_menu = CreateFormulaPopUpMenu()

        # Instantiate createCategoryPopUpMenu
        self.create_category_popup_menu = CreateCategoryPopUpMenu()

        self.fill_modes_list()
        self.fill_category_list()

    def fill_modes_list(self):
        self.root.get_screen("mainMenu").ids.mode_list.clear_widgets()
        self.root.get_screen("mainMenu").ids.mode_list.add_widget(
            MDListItem(
                MDListItemHeadlineText(text="Elements"),
                on_release=lambda _: self.change_screen("elementMenu")
            )
        )
        self.root.get_screen("mainMenu").ids.mode_list.add_widget(
            MDListItem(
                MDListItemHeadlineText(text="Compounds"),
                on_release=lambda _: self.change_screen("compoundMenu")
            )
        )
        self.root.get_screen("mainMenu").ids.mode_list.add_widget(
            MDListItem(
                MDListItemHeadlineText(text="Questions"),
                on_release=lambda _: self.change_screen("questionMenu")
            )
        )

    def change_screen(self, name):
        self.root.current = name

    def get_all_categories(self):
        self.cursor.execute("SELECT name FROM categories")
        return [row[0] for row in self.cursor.fetchall()]

    def fill_category_list(self):
        self.root.get_screen("compoundMenu").ids.category_list.clear_widgets()
        categories = self.get_all_categories()

        for category in categories:
            item = MDListItem(
                MDListItemHeadlineText(text=category),
                on_release=lambda x=category: self.on_category_selected(x)
            )
            self.root.get_screen("compoundMenu").ids.category_list.add_widget(item)

    def on_category_selected(self, category):
        print(f"Selected category: {category}")

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
            caller=self.root.get_screen(self.root.current).ids.add_button,
            items=add_menu_items
        ).open()

    def change_theme(self):
        self.theme_cls.primary_palette = (
            "Lightblue" if self.theme_cls.primary_palette == "Darkblue" else "Darkblue"
        )
        self.theme_cls.theme_style = (
            "Light" if self.theme_cls.theme_style == "Dark" else "Dark"
        )
        self.root.get_screen(self.root.current).ids.theme_mode.icon = (
            "weather-night" if self.root.get_screen(self.root.current).ids.theme_mode.icon == "weather-sunny" else "weather-sunny"
        )

#app.theme_cls.backgroundColor
MainApp().run()
