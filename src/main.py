from popups.createCompoundPopUpMenu import CreateFormulaPopUpMenu
from popups.createCategoryPopUpMenu import CreateCategoryPopUpMenu
from popups.createQuestionPopUpMenu import CreateQuestionPopUpMenu
from popups.loginAccountPopUpMenu import LoginAccountPopUpMenu
from screens.mainMenu import MainMenuScreen
from screens.questionLearning import QuestionLearningScreen
from screens.compoundMenu import CompoundMenuScreen
from screens.compoundLearning import CompoundLearningScreen
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
            "src/screens/questionLearning.kv",
            "src/screens/compoundMenu.kv",
            "src/screens/compoundLearning.kv",
            "src/screens/elementMenu.kv",
        ]
        for file in kv_files:
            Builder.load_file(file)

        self.mainMenuScreen = MainMenuScreen(name="mainMenu")
        self.elementMenuScreen = ElementMenuScreen(name="elementMenu")
        self.compoundMenuScreen = CompoundMenuScreen(name="compoundMenu")
        self.compoundLearningScreen = CompoundLearningScreen(name="compoundLearning")
        self.questionLearningScreen = QuestionLearningScreen(name="questionLearning")

        sm = ScreenManager()
        sm.add_widget(self.mainMenuScreen)
        sm.add_widget(self.elementMenuScreen)
        sm.add_widget(self.compoundMenuScreen)
        sm.add_widget(self.compoundLearningScreen)
        sm.add_widget(self.questionLearningScreen)
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

        # Instantiate createCategoryPopUpMenu
        self.create_question_popup_menu = CreateQuestionPopUpMenu()

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
                on_release=lambda _: self.questionLearningScreen.start_learning()
            )
        )

    def change_screen(self, name):
        self.root.current = name

    def get_all_categories(self):
        self.cursor.execute("SELECT id, name, date FROM categories")
        rows = self.cursor.fetchall()

        category_dict = {
            row[0]: {
                "name": row[1],
                "date": row[2],
            }
            for row in rows
        }

        return category_dict

    def get_all_compounds(self):
        self.cursor.execute("SELECT id, correct_name, wrong_name1, wrong_name2, correct_formula, wrong_formula1, wrong_formula2, category, date FROM compounds")
        rows = self.cursor.fetchall()

        compound_dict = {
            row[0]: {
                "correct_name": row[1],
                "wrong_name1": row[2],
                "wrong_name2": row[3],
                "correct_formula": row[4],
                "wrong_formula1": row[5],
                "wrong_formula2": row[6],
                "category": row[7],
                "date": row[8],
            }
            for row in rows
        }

        return compound_dict

    def get_all_questions(self):
        self.cursor.execute("SELECT id, question, correct_answer, wrong_answer1, wrong_answer2, wrong_answer3, wrong_answer4, date FROM questions")
        rows = self.cursor.fetchall()

        compound_dict = {
            row[0]: {
                "question": row[1],
                "correct_answer": row[2],
                "wrong_answer1": row[3],
                "wrong_answer2": row[4],
                "wrong_answer3": row[5],
                "wrong_answer4": row[6],
                "date": row[7],
            }
            for row in rows
        }

        return compound_dict

    def fill_category_list(self):
        self.root.get_screen("compoundMenu").ids.category_list.clear_widgets()
        categories = self.get_all_categories()

        for category_id, category in categories.items():
            item = MDListItem(
                MDListItemHeadlineText(text=category["name"]),
                on_release=lambda _, cat_id=category_id: self.compoundLearningScreen.start_learning(cat_id)
            )
            self.root.get_screen("compoundMenu").ids.category_list.add_widget(item)

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
