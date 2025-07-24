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
from screens.question_learning import QuestionLearningScreen
from screens.compound_learning import CompoundLearningScreen

from database.database import Database
from utils.json_parser import load_state, save_state

from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager


class MainApp(MDApp):
    def __init__(self):
        super().__init__()

        # Instantiate variables
        self.dark_mode = True
        self.logged_in_user_id = None
        self.logged_in_group = None
        self.groups = {}

        # Instantiate state
        self.state = None

        # Instantiate database
        self.db = Database()

        # Instantiate screens
        self.question_learning_screen = QuestionLearningScreen(name="questionLearning")
        self.compound_menu_screen = CompoundMenuScreen(name="compoundMenu")
        self.compound_learning_screen = CompoundLearningScreen(name="compoundLearning")
        self.element_menu_screen = ElementMenuScreen(name="elementMenu")
        self.modes_menu_screen = ModesMenuScreen(name="modesMenu")

        # Instantiate popup menus
        self.register_or_login_account_popup_menu = RegisterOrLoginAccountPopUpMenu()
        self.create_or_edit_group_popup_menu = CreateOrEditGroupPopUpMenu()
        self.add_group_popup_menu = AddGroupPopUpMenu()
        self.create_or_edit_compound_popup_menu = CreateOrEditCompoundPopUpMenu()
        self.create_or_edit_category_popup_menu = CreateOrEditCategoryPopUpMenu()
        self.delete_category_popup_menu = DeleteCategoryPopUpMenu()
        self.create_or_edit_question_popup_menu = CreateOrEditQuestionPopUpMenu()
        self.confirm_delete_popup_menu = ConfirmDeletePopUpMenu()


    def build(self):
        kv_files = [
            "src/main.kv",
            "src/screens/modes_menu.kv",
            "src/screens/question_learning.kv",
            "src/screens/compound_menu.kv",
            "src/screens/compound_learning.kv",
            "src/screens/element_menu.kv",
        ]
        for file in kv_files:
            Builder.load_file(file)

        sm = ScreenManager()
        sm.add_widget(ModesMenuScreen(name="modesMenu"))
        sm.add_widget(ElementMenuScreen(name="elementMenu"))
        sm.add_widget(CompoundLearningScreen(name="compoundLearning"))
        sm.add_widget(CompoundMenuScreen(name="compoundMenu"))
        sm.add_widget(QuestionLearningScreen(name="questionLearning"))
        self.root = sm
        return sm


    def on_start(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = 'Darkblue'

        self.modes_menu_screen.fill_modes_list()


        self.state = load_state()
        if self.state.get("logged_in_user_id"):
            self.login(self.state["logged_in_user_id"])
        else:
            self.logout()
        if self.state.get("logged_in_group"):
            self.modes_menu_screen.set_group(self.state["logged_in_group"])
        self.dark_mode = self.state["dark_mode"]
        self.set_theme()


    def login(self, loggedInUserId):
        self.logged_in_user_id = loggedInUserId
        self.state["logged_in_user_id"] = self.logged_in_user_id
        save_state(self.state)
        self.modes_menu_screen.refresh_groups()

        self.root.get_screen("modesMenu").ids.account_button.icon = "logout"
        self.root.get_screen("modesMenu").ids.account_button.on_release = self.logout
        self.root.get_screen("modesMenu").ids.create_or_add_group_button.icon = "plus-circle"
        self.root.get_screen("modesMenu").ids.create_or_add_group_button.on_release = self.create_or_edit_group_popup_menu.open
        self.root.get_screen("modesMenu").ids.delete_or_remove_group_button.icon = "delete"
        self.root.get_screen("modesMenu").ids.delete_or_remove_group_button.on_release = self.modes_menu_screen.delete_group
        self.root.get_screen("modesMenu").ids.edit_group_button.opacity = 1
        self.root.get_screen("modesMenu").ids.edit_group_button.disabled = False
        self.root.get_screen("compoundMenu").ids.create_category_or_compound_button.opacity = 1
        self.root.get_screen("compoundMenu").ids.create_category_or_compound_button.disabled = False
        self.root.get_screen("compoundMenu").ids.edit_category_button.opacity = 1
        self.root.get_screen("compoundMenu").ids.edit_category_button.disabled = False
        self.root.get_screen("compoundMenu").ids.delete_category_button.opacity = 1
        self.root.get_screen("compoundMenu").ids.delete_category_button.disabled = False
        self.root.get_screen("compoundLearning").ids.create_compound_button.opacity = 1
        self.root.get_screen("compoundLearning").ids.create_compound_button.disabled = False
        self.root.get_screen("compoundLearning").ids.edit_compound_button.opacity = 1
        self.root.get_screen("compoundLearning").ids.edit_compound_button.disabled = False
        self.root.get_screen("compoundLearning").ids.delete_compound_button.opacity = 1
        self.root.get_screen("compoundLearning").ids.delete_compound_button.disabled = False
        self.root.get_screen("elementMenu").ids.create_element_button.opacity = 1
        self.root.get_screen("elementMenu").ids.create_element_button.disabled = False
        self.root.get_screen("questionLearning").ids.create_question_button.opacity = 1
        self.root.get_screen("questionLearning").ids.create_question_button.disabled = False
        self.root.get_screen("questionLearning").ids.edit_question_button.opacity = 1
        self.root.get_screen("questionLearning").ids.edit_question_button.disabled = False
        self.root.get_screen("questionLearning").ids.delete_question_button.opacity = 1
        self.root.get_screen("questionLearning").ids.delete_question_button.disabled = False


    def logout(self):
        self.logged_in_user_id = None
        self.state["logged_in_user_id"] = self.logged_in_user_id
        save_state(self.state)
        self.modes_menu_screen.refresh_groups()

        self.root.get_screen("modesMenu").ids.account_button.icon = "account"
        self.root.get_screen("modesMenu").ids.account_button.on_release = self.register_or_login_account_popup_menu.open
        self.root.get_screen("modesMenu").ids.create_or_add_group_button.icon = "plus"
        self.root.get_screen("modesMenu").ids.create_or_add_group_button.on_release = self.add_group_popup_menu.open
        self.root.get_screen("modesMenu").ids.delete_or_remove_group_button.icon = "exit-to-app"
        self.root.get_screen("modesMenu").ids.delete_or_remove_group_button.on_release = lambda: self.modes_menu_screen.remove_group(self.logged_in_group)
        self.root.get_screen("modesMenu").ids.edit_group_button.opacity = 0
        self.root.get_screen("modesMenu").ids.edit_group_button.disabled = True
        self.root.get_screen("compoundMenu").ids.create_category_or_compound_button.opacity = 0
        self.root.get_screen("compoundMenu").ids.create_category_or_compound_button.disabled = True
        self.root.get_screen("compoundMenu").ids.edit_category_button.opacity = 0
        self.root.get_screen("compoundMenu").ids.edit_category_button.disabled = True
        self.root.get_screen("compoundMenu").ids.delete_category_button.opacity = 0
        self.root.get_screen("compoundMenu").ids.delete_category_button.disabled = True
        self.root.get_screen("compoundLearning").ids.create_compound_button.opacity = 0
        self.root.get_screen("compoundLearning").ids.create_compound_button.disabled = True
        self.root.get_screen("compoundLearning").ids.edit_compound_button.opacity = 0
        self.root.get_screen("compoundLearning").ids.edit_compound_button.disabled = True
        self.root.get_screen("compoundLearning").ids.delete_compound_button.opacity = 0
        self.root.get_screen("compoundLearning").ids.delete_compound_button.disabled = True
        self.root.get_screen("elementMenu").ids.create_element_button.opacity = 0
        self.root.get_screen("elementMenu").ids.create_element_button.disabled = True
        self.root.get_screen("questionLearning").ids.create_question_button.opacity = 0
        self.root.get_screen("questionLearning").ids.create_question_button.disabled = True
        self.root.get_screen("questionLearning").ids.edit_question_button.opacity = 0
        self.root.get_screen("questionLearning").ids.edit_question_button.disabled = True
        self.root.get_screen("questionLearning").ids.delete_question_button.opacity = 0
        self.root.get_screen("questionLearning").ids.delete_question_button.disabled = True


    def change_screen(self, name):
        self.root.current = name


    def change_theme(self):
        self.dark_mode = False if self.dark_mode else True
        self.state["dark_mode"] = self.dark_mode
        save_state(self.state)
        self.set_theme()


    def set_theme(self):
        self.theme_cls.primary_palette = (
            "Darkblue" if self.dark_mode else "Lightblue"
        )
        self.theme_cls.theme_style = (
            "Dark" if self.dark_mode else "Light"
        )
        self.root.get_screen(self.root.current).ids.theme_mode.icon = (
            "weather-sunny" if self.dark_mode else "weather-night"
        )

#app.theme_cls.backgroundColor
MainApp().run()
