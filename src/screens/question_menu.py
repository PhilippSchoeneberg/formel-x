from src.popups.create_or_edit_category_popup_menu import CreateOrEditCategoryPopupMenu
from src.popups.delete_category_popup_menu import DeleteCategoryPopupMenu
from src.utils.enums import CategoryTypes, DifficultyTypes

from kivy.app import App
from kivy.core.window import Window
from kivymd.uix.screen import MDScreen
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.button import MDIconButton, MDButton, MDButtonText
from kivymd.uix.list import MDListItem, MDListItemHeadlineText


class QuestionMenuScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.difficulty_dropdown_menu = None
        self.select_difficulty = None


    def on_pre_enter(self, *args):
        self.refresh()


    def refresh(self, *args):
        self.fill_category_list()


    def fill_category_list(self):
        self.ids.question_category_list.clear_widgets()
        question_categories = self.app.db.get_all_categories_by_type_and_group(CategoryTypes.question, self.app.logged_in_group)

        title_item = MDListItem(
            MDListItemHeadlineText(text=self.app.language_manager.translate("select") + self.app.language_manager.translate("category") + ":"))
        title_item.ripple_effect = False
        title_item.focus_behavior = False
        self.ids.question_category_list.add_widget(title_item)

        if question_categories:
            for question_category_id, question_category in question_categories.items():
                button_text = MDButtonText(
                    text=self.app.language_manager.translate("select") + self.app.language_manager.translate(
                        "difficulty"))
                button = MDButton(
                    button_text,
                    on_release=lambda x, btn_txt=button_text: self.difficulty_menu_open(x, btn_txt)
                )
                list_item = MDListItem(
                    MDListItemHeadlineText(text=question_category["name"]),
                    on_release=lambda _, cat_id=question_category_id: self.select_category(cat_id)
                )
                list_item.add_widget(button)
                self.ids.question_category_list.add_widget(list_item)

            if len(question_categories) >= 2:
                button_text = MDButtonText(
                    text=self.app.language_manager.translate("select") + self.app.language_manager.translate(
                        "difficulty"))
                button = MDButton(
                    button_text,
                    on_release=lambda x, btn_txt=button_text: self.difficulty_menu_open(x, btn_txt)
                )
                list_item = MDListItem(
                    MDListItemHeadlineText(text=self.app.language_manager.translate("all")),
                    on_release=lambda _, cat_id=None: self.select_category(cat_id)
                )
                list_item.add_widget(button)
                self.ids.question_category_list.add_widget(list_item)
        else:
            error_item = MDListItem(
                MDListItemHeadlineText(text=self.app.language_manager.translate("no_categories_yet_error")))
            error_item.ripple_effect = False
            error_item.focus_behavior = False
            self.ids.question_category_list.add_widget(error_item)
            if self.app.logged_in_user_id:
                self.ids.question_category_list.add_widget(
                    MDListItem(
                        MDListItemHeadlineText(text=self.app.language_manager.translate("create") + self.app.language_manager.translate("category")),
                        on_release=lambda _, cat_id=None: CreateOrEditCategoryPopupMenu().open(CategoryTypes.question, False)
                    )
                )


    def difficulty_menu_open(self, button, button_text):
        difficulty_menu_items = []
        for difficulty in DifficultyTypes:
            difficulty_menu_items.append({"text": self.app.language_manager.translate(difficulty.value),
                                          "on_release": lambda x=difficulty: self.set_difficulty(button_text, x)})
        self.difficulty_dropdown_menu = MDDropdownMenu(
            caller=button,
            items=difficulty_menu_items
        )
        self.difficulty_dropdown_menu.open()


    def set_difficulty(self, button_text, difficulty):
        self.select_difficulty = difficulty
        button_text.text = self.select_difficulty.value


    def select_category(self, category_id):
        self.app.question_learning_screen.start_learning(category_id, self.select_difficulty)


    def create(self):
        create_button = MDIconButton(
            opacity=0,
            size_hint=(None, None),
            size=("1dp", "1dp"),
        )

        screen = self.app.root.get_screen(self.app.root.current)
        screen.add_widget(create_button)

        mouse_x, mouse_y = Window.mouse_pos
        create_button.pos = (mouse_x, mouse_y - 40)

        add_menu_items = [
            {
                "text": self.app.language_manager.translate("add_category"),
                "on_release": lambda: CreateOrEditCategoryPopupMenu().open(CategoryTypes.question, False),
            },
            {
                "text": self.app.language_manager.translate("add_question"),
                "on_release": lambda: self.app.root.get_screen("questionLearning").create(),
            },
        ]
        MDDropdownMenu(
            caller=create_button,
            items=add_menu_items
        ).open()


    def edit(self):
        CreateOrEditCategoryPopupMenu().open(CategoryTypes.question, True)


    def delete(self):
        DeleteCategoryPopupMenu().open(CategoryTypes.question)
