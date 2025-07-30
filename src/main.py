from popups.add_group_popup_menu import AddGroupPopUpMenu
from popups.confirm_delete_popup_menu import ConfirmDeletePopUpMenu
from popups.delete_category_popup_menu import DeleteCategoryPopUpMenu
from popups.create_or_edit_group_popup_menu import CreateOrEditGroupPopUpMenu
from popups.create_or_edit_compound_popup_menu import CreateOrEditCompoundPopUpMenu
from popups.create_or_edit_category_popup_menu import CreateOrEditCategoryPopUpMenu
from popups.create_or_edit_question_popup_menu import CreateOrEditQuestionPopUpMenu
from popups.register_or_login_account_popup_menu import RegisterOrLoginAccountPopUpMenu

from screens.modes_menu import ModesMenuScreen
from screens.element_menu import ElementMenuScreen
from screens.compound_menu import CompoundMenuScreen
from screens.compound_learning import CompoundLearningScreen
from screens.question_menu import QuestionMenuScreen
from screens.question_learning import QuestionLearningScreen

from database.database import Database
from utils.language_manager import LanguageManager
from utils.json_parser import load_state, save_state

from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivymd.uix.button import MDIconButton
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.screenmanager import ScreenManager


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
        self.db = Database()

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
        kv_files = [
            "src/main.kv",
            "src/screens/modes_menu.kv",
            "src/screens/element_menu.kv",
            "src/screens/compound_menu.kv",
            "src/screens/compound_learning.kv",
            "src/screens/question_menu.kv",
            "src/screens/question_learning.kv",
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

        self.register_or_login_account_popup_menu = RegisterOrLoginAccountPopUpMenu()
        self.create_or_edit_group_popup_menu = CreateOrEditGroupPopUpMenu()
        self.add_group_popup_menu = AddGroupPopUpMenu()
        self.create_or_edit_compound_popup_menu = CreateOrEditCompoundPopUpMenu()
        self.create_or_edit_category_popup_menu = CreateOrEditCategoryPopUpMenu()
        self.delete_category_popup_menu = DeleteCategoryPopUpMenu()
        self.create_or_edit_question_popup_menu = CreateOrEditQuestionPopUpMenu()
        self.confirm_delete_popup_menu = ConfirmDeletePopUpMenu()

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

        self.element_menu_screen.fill_periodic_table()
        for screen in self.screens:
            screen.refresh()


    def login(self, loggedInUserId):
        self.logged_in_user_id = loggedInUserId
        self.state["logged_in_user_id"] = self.logged_in_user_id
        save_state(self.state)
        self.modes_menu_screen.refresh_groups()
        self.element_menu_screen.refresh_buttons()

        self.root.get_screen("modesMenu").ids.account_button.icon = "logout"
        self.root.get_screen("modesMenu").ids.account_button.on_release = self.logout


    def logout(self):
        self.logged_in_user_id = None
        self.state["logged_in_user_id"] = self.logged_in_user_id
        save_state(self.state)
        self.modes_menu_screen.refresh_groups()
        self.element_menu_screen.refresh_buttons()

        self.root.get_screen("modesMenu").ids.account_button.icon = "account"
        self.root.get_screen("modesMenu").ids.account_button.on_release = self.register_or_login_account_popup_menu.open


    def change_screen(self, name):
        self.root.current = name


    def general_menu_open(self):
        general_menu_items = [
            {
                "leading_icon": self.theme_icon,
                "text": self.language_manager.translate("theme"),
                "on_release": lambda: self.change_theme(),
            },
            {
                "leading_icon": "translate",
                "text": self.language_manager.translate("language"),
                "on_release": lambda: self.language_menu_open(),
            },
        ]

        if self.logged_in_user_id:
            general_menu_items = general_menu_items + [
                {
                    "leading_icon": "plus-circle",
                    "text": self.language_manager.translate("create"),
                    "on_release": lambda: self.root.get_screen(self.root.current).create(),
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
                    "on_release": lambda: self.add_group_popup_menu.open(),
                },
                {
                    "leading_icon": "exit-to-app",
                    "text": self.language_manager.translate("leave"),
                    "on_release": lambda: self.root.get_screen(self.root.current).remove(self.logged_in_group),
                }
            ]

        self.general_dropdown_menu = MDDropdownMenu(
            caller=self.root.get_screen(self.root.current).ids.general_menu_button,
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
        self.theme_cls.primary_palette = (
            "Darkblue" if self.dark_mode else "Lightblue"
        )
        self.theme_cls.theme_style = (
            "Dark" if self.dark_mode else "Light"
        )
        self.theme_icon = (
            "weather-sunny" if self.dark_mode else "weather-night"
        )


    def language_menu_open(self):
        select_language_button = MDIconButton(
            opacity=0,
            size_hint=(None, None),
            size=("1dp", "1dp"),
        )

        screen = self.root.get_screen(self.root.current)
        screen.add_widget(select_language_button)

        mouse_x, mouse_y = Window.mouse_pos
        select_language_button.pos = (mouse_x, mouse_y - 40)

        language_menu_items = []
        for language in self.language_manager.get_available_languages():
            language_menu_items.append({"text": language,
                                     "on_release": lambda x=language: self.set_language(x)})
        self.language_dropdown_menu = MDDropdownMenu(
            caller=select_language_button,
            items=language_menu_items
        )
        self.language_dropdown_menu.open()


    def set_language(self, language):
        self.language = language
        self.state["language"] = self.language
        save_state(self.state)
        self.language_manager.set_language(self.language)
        for screen in self.screens:
            screen.refresh()
        self.language_dropdown_menu.dismiss()
        self.general_dropdown_menu.dismiss()


#app.theme_cls.backgroundColor
MainApp().run()
