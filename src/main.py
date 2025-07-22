from popups.createCompoundPopUpMenu import CreateCompoundPopUpMenu
from popups.createCategoryPopUpMenu import CreateCategoryPopUpMenu
from popups.createQuestionPopUpMenu import CreateQuestionPopUpMenu
from popups.loginAccountPopUpMenu import LoginAccountPopUpMenu
from popups.createGroupPopupMenu import CreateGroupPopUpMenu
from popups.addGroupPopupMenu import AddGroupPopUpMenu
from screens.modesMenu import ModesMenuScreen
from screens.questionLearning import QuestionLearningScreen
from screens.compoundMenu import CompoundMenuScreen
from screens.compoundLearning import CompoundLearningScreen
from screens.elementMenu import ElementMenuScreen
from database.database import Database
from utils.json_parser import load_state, save_state

from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from kivy.lang import Builder


class MainApp(MDApp):
    def __init__(self):
        super().__init__()

        # Instantiate variables
        self.darkMode = True
        self.loggedInUserId = None
        self.loggedInGroup = None
        self.groups = {}

        # Instantiate state
        self.state = None

        # Instantiate database
        self.db = Database()

        # Instantiate screens
        self.questionLearningScreen = QuestionLearningScreen(name="questionLearning")
        self.compoundMenuScreen = CompoundMenuScreen(name="compoundMenu")
        self.compoundLearningScreen = CompoundLearningScreen(name="compoundLearning")
        self.elementMenuScreen = ElementMenuScreen(name="elementMenu")
        self.modesMenuScreen = ModesMenuScreen(name="modesMenu")

        # Instantiate popup menus
        self.login_account_popup_menu = LoginAccountPopUpMenu()
        self.create_group_popup_menu = CreateGroupPopUpMenu()
        self.add_group_popup_menu = AddGroupPopUpMenu()
        self.create_compound_popup_menu = CreateCompoundPopUpMenu()
        self.create_category_popup_menu = CreateCategoryPopUpMenu()
        self.create_question_popup_menu = CreateQuestionPopUpMenu()


    def build(self):
        kv_files = [
            "src/main.kv",
            "src/screens/modesMenu.kv",
            "src/screens/questionLearning.kv",
            "src/screens/compoundMenu.kv",
            "src/screens/compoundLearning.kv",
            "src/screens/elementMenu.kv",
        ]
        for file in kv_files:
            Builder.load_file(file)

        sm = ScreenManager()
        sm.add_widget(ModesMenuScreen(name="modesMenu"))#self.modesMenuScreen)
        sm.add_widget(ElementMenuScreen(name="elementMenu"))#self.elementMenuScreen)
        sm.add_widget(CompoundLearningScreen(name="compoundLearning"))#self.compoundMenuScreen)
        sm.add_widget(CompoundMenuScreen(name="compoundMenu"))#self.compoundLearningScreen)
        sm.add_widget(QuestionLearningScreen(name="questionLearning") )#self.questionLearningScreen)
        self.root = sm
        return sm


    def on_start(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = 'Darkblue'

        self.modesMenuScreen.fill_modes_list()
        self.compoundMenuScreen.fill_category_list()

        self.state = load_state()
        if self.state.get("loggedInUserId"):
            self.login(self.state["loggedInUserId"])
        else:
            self.logout()
        if self.state.get("loggedInGroup"):
            self.modesMenuScreen.set_group(self.state["loggedInGroup"])
        self.groups = self.state["groups"]
        self.darkMode = self.state["darkMode"]
        self.set_theme()


    def login(self, loggedInUserId):
        self.loggedInUserId = loggedInUserId
        self.state["loggedInUserId"] = self.loggedInUserId
        save_state(self.state)
        self.root.get_screen("modesMenu").ids.account_button.icon = "logout"
        self.root.get_screen("modesMenu").ids.account_button.on_release = self.logout

        self.root.get_screen("modesMenu").ids.create_group_button.opacity = 1
        self.root.get_screen("modesMenu").ids.create_group_button.disabled = False
        self.root.get_screen("compoundMenu").ids.create_compound_button.opacity = 1
        self.root.get_screen("compoundMenu").ids.create_compound_button.disabled = False
        self.root.get_screen("elementMenu").ids.create_element_button.opacity = 1
        self.root.get_screen("elementMenu").ids.create_element_button.disabled = False
        self.root.get_screen("questionLearning").ids.create_question_button.opacity = 1
        self.root.get_screen("questionLearning").ids.create_question_button.disabled = False


    def logout(self):
        self.loggedInUserId = None
        self.state["loggedInUserId"] = self.loggedInUserId
        save_state(self.state)
        self.root.get_screen("modesMenu").ids.account_button.icon = "account"
        self.root.get_screen("modesMenu").ids.account_button.on_release = self.login_account_popup_menu.open

        self.root.get_screen("modesMenu").ids.create_group_button.opacity = 0
        self.root.get_screen("modesMenu").ids.create_group_button.disabled = True
        self.root.get_screen("compoundMenu").ids.create_compound_button.opacity = 0
        self.root.get_screen("compoundMenu").ids.create_compound_button.disabled = True
        self.root.get_screen("elementMenu").ids.create_element_button.opacity = 0
        self.root.get_screen("elementMenu").ids.create_element_button.disabled = True
        self.root.get_screen("questionLearning").ids.create_question_button.opacity = 0
        self.root.get_screen("questionLearning").ids.create_question_button.disabled = True


    def change_screen(self, name):
        self.root.current = name


    def change_theme(self):
        self.darkMode = False if self.darkMode else True
        self.state["darkMode"] = self.darkMode
        save_state(self.state)
        self.set_theme()


    def set_theme(self):
        self.theme_cls.primary_palette = (
            "Darkblue" if self.darkMode else "Lightblue"
        )
        self.theme_cls.theme_style = (
            "Dark" if self.darkMode else "Light"
        )
        self.root.get_screen(self.root.current).ids.theme_mode.icon = (
            "weather-sunny" if self.darkMode else "weather-night"
        )

#app.theme_cls.backgroundColor
MainApp().run()
