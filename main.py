from src.popups.add_group_popup_menu import AddGroupPopupMenu
from src.popups.register_or_login_account_popup_menu import RegisterOrLoginAccountPopupMenu

from src.screens.modes_menu import ModesMenuScreen
from src.screens.question_menu import QuestionMenuScreen
from src.screens.element_menu import ElementMenuScreen
from src.screens.compound_menu import CompoundMenuScreen
from src.screens.compound_learning import CompoundLearningScreen
from src.screens.question_learning import QuestionLearningScreen

from src.database.database import Database
from src.utils.language_manager import LanguageManager
from src.utils.json_parser import load_state, save_state

import os
from ext.kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.text import LabelBase
from ext.kivymd.uix.menu import MDDropdownMenu
from kivy.uix.screenmanager import ScreenManager
from ext.kivymd.font_definitions import theme_font_styles


LabelBase.register(name="RobotoDownloaded", fn_regular="assets/Roboto-VariableFont_wdth,wght.ttf")

class MainApp(MDApp):
    def __init__(self):
        super().__init__()

        # Load variables
        self.state = load_state()
        self.dark_mode = self.state["dark_mode"]
        if self.state.get("language"):
            self.language = self.state["language"]
        else:
            pass
        if self.state.get("logged_in_user_id"):
            self.logged_in_user_id = self.state["logged_in_user_id"]
        else:
            self.logged_in_user_id = None
        if self.state.get("logged_in_group"):
            self.logged_in_group = self.state["logged_in_group"]
        else:
            self.logged_in_group = None
        if self.state.get("groups"):
            self.groups = self.state["groups"]
        else:
            self.groups = {}

        # Instantiate variables
        self.screens = []
        self.theme_icon = None
        self.learning_mode = False
        self.general_dropdown_menu = None
        self.formula_to_name_query_mode = True

        # Instantiate Language Manager
        self.language_manager = LanguageManager(self.language)

        # Instantiate database
        url = "https://jbweqnndqbvbsorzngff.supabase.co"
        api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Impid2Vxbm5kcWJ2YnNvcnpuZ2ZmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQzMjEzNzcsImV4cCI6MjA2OTg5NzM3N30.Fkno72iJDHwY4bq0EPd2GHadTqdwqDuvnrFoeREAIQU"
        self.db = Database(url, api_key)

        # Instantiate screens
        self.modes_menu_screen = None
        self.element_menu_screen = None
        self.compound_menu_screen = None
        self.compound_learning_screen = None
        self.question_menu_screen = None
        self.question_learning_screen = None


        # Instantiate popup menus
        self.register_or_login_account_popup_menu = None
        self.create_or_edit_group_popup_menu = None
        self.add_group_popup_menu = None
        self.create_or_edit_compound_popup_menu = None
        self.create_or_edit_category_popup_menu = None
        self.delete_category_popup_menu = None
        self.create_or_edit_question_popup_menu = None
        self.confirm_delete_popup_menu = None


    def build(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(current_dir, "..", "assets", "logo20250712.png")
        self.icon = os.path.normpath(icon_path)

        for style in theme_font_styles:
            if style != "Icon":
                for role in theme_font_styles[style]:
                    theme_font_styles[style][role]["font-name"] = "RobotoDownloaded"

        kv_files = [
            "src/kivy/main.kv",
            "src/kivy/modes_menu.kv",
            "src/kivy/element_menu.kv",
            "src/kivy/compound_menu.kv",
            "src/kivy/compound_learning.kv",
            "src/kivy/question_menu.kv",
            "src/kivy/question_learning.kv",
        ]
        for file in kv_files:
            Builder.load_file(file)

        self.modes_menu_screen = ModesMenuScreen(name="modesMenu")
        self.element_menu_screen = ElementMenuScreen(name="elementMenu")
        self.compound_menu_screen = CompoundMenuScreen(name="compoundMenu")
        self.compound_learning_screen = CompoundLearningScreen(name="compoundLearning")
        self.question_menu_screen = QuestionMenuScreen(name="questionMenu")
        self.question_learning_screen = QuestionLearningScreen(name="questionLearning")

        self.screens.append(self.modes_menu_screen)
        self.screens.append(self.element_menu_screen)
        self.screens.append(self.compound_menu_screen)
        self.screens.append(self.compound_learning_screen)
        self.screens.append(self.question_menu_screen)
        self.screens.append(self.question_learning_screen)

        sm = ScreenManager()
        sm.add_widget(self.modes_menu_screen)
        sm.add_widget(self.element_menu_screen)
        sm.add_widget(self.compound_menu_screen)
        sm.add_widget(self.compound_learning_screen)
        sm.add_widget(self.question_menu_screen)
        sm.add_widget(self.question_learning_screen)
        self.root = sm
        return sm


    def on_start(self):
        self.set_theme()
        if self.logged_in_user_id:
            self.login(self.logged_in_user_id)
        else:
            self.logout()
        if self.logged_in_group:
            self.modes_menu_screen.set_group(self.logged_in_group)


    def login(self, loggedInUserId):
        self.logged_in_user_id = loggedInUserId
        self.state["logged_in_user_id"] = self.logged_in_user_id
        save_state(self.state)

        for screen in self.screens:
            screen.refresh()

        self.root.get_screen("modesMenu").ids.account_button.icon = "logout"
        self.root.get_screen("modesMenu").ids.account_button.on_release = self.logout


    def logout(self):
        self.logged_in_user_id = None
        self.state["logged_in_user_id"] = self.logged_in_user_id
        save_state(self.state)

        for screen in self.screens:
            screen.refresh()

        self.root.get_screen("modesMenu").ids.account_button.icon = "account"
        self.root.get_screen("modesMenu").ids.account_button.on_release = RegisterOrLoginAccountPopupMenu().open


    def change_screen(self, name):
        self.root.current = name


    def general_menu_open(self):
        caller = self.root.get_screen(self.root.current).ids.general_menu_button
        general_menu_items = [
            {
                "leading_icon": self.theme_icon,
                "text": self.language_manager.translate("theme"),
                "on_release": lambda: self.change_theme(),
            },
            {
                "leading_icon": "translate",
                "text": self.language_manager.translate("language"),
                "on_release": lambda: self.language_menu_open(caller),
            },
        ]

        if self.logged_in_user_id:
            if self.root.current != "elementMenu":
                general_menu_items = general_menu_items + [
                    {
                        "leading_icon": "plus-circle",
                        "text": self.language_manager.translate("create"),
                        "on_release": lambda: self.root.get_screen(self.root.current).create(caller),
                    },
                    {
                        "leading_icon": "border-color",
                        "text": self.language_manager.translate("edit"),
                        "on_release": lambda: self.root.get_screen(self.root.current).edit(),
                    },
                    {
                        "leading_icon": "delete",
                        "text": self.language_manager.translate("delete"),
                        "on_release": lambda: self.root.get_screen(self.root.current).delete(),
                    }
                ]
        elif self.root.get_screen(self.root.current) == self.root.get_screen("modesMenu"):
            general_menu_items = general_menu_items + [
                {
                    "leading_icon": "plus",
                    "text": self.language_manager.translate("add"),
                    "on_release": lambda: AddGroupPopupMenu().open(),
                },
                {
                    "leading_icon": "exit-to-app",
                    "text": self.language_manager.translate("leave"),
                    "on_release": lambda: self.root.get_screen(self.root.current).remove(self.logged_in_group),
                }
            ]

        self.general_dropdown_menu = MDDropdownMenu(
            caller=caller,
            items=general_menu_items
        )
        self.general_dropdown_menu.open()


    def change_theme(self):
        self.dark_mode = False if self.dark_mode else True
        self.state["dark_mode"] = self.dark_mode
        save_state(self.state)
        self.set_theme()
        self.general_dropdown_menu.dismiss()


    def set_theme(self):
        self.theme_cls.primary_palette = "Darkblue" if self.dark_mode else "Lightblue"
        self.theme_cls.theme_style = "Dark" if self.dark_mode else "Light"
        self.theme_icon = "weather-sunny" if self.dark_mode else "weather-night"
        bg_color = (18 / 255, 18 / 255, 18 / 255, 1) if self.dark_mode else (1, 1, 1, 1)
        for screen in self.screens:
            screen.md_bg_color = bg_color


    def language_menu_open(self, original_caller):
        language_menu_items = []
        for language in self.language_manager.get_available_languages():
            language_menu_items.append({"text": language,
                                     "on_release": lambda x=language: self.set_language(x)})
        self.language_dropdown_menu = MDDropdownMenu(
            caller=original_caller,
            items=language_menu_items
        )
        self.general_dropdown_menu.dismiss()
        self.language_dropdown_menu.open()


    def set_language(self, language):
        self.language = language
        self.state["language"] = self.language
        save_state(self.state)
        self.language_manager.set_language(self.language)
        for screen in self.screens:
            screen.refresh()
        self.language_dropdown_menu.dismiss()


MainApp().run()
