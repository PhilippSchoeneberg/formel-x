from src.utils.enums import CategoryTypes

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.button import MDIconButton
from kivymd.uix.list import MDListItem, MDListItemHeadlineText


class QuestionMenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()


    def refresh(self, *args):
        self.fill_category_list()


    def fill_category_list(self):
        self.ids.question_category_list.clear_widgets()
        question_categories = self.app.db.get_all_categories_by_type_and_group(CategoryTypes.question, self.app.logged_in_group)

        title_item = MDListItem(
            MDListItemHeadlineText(text=self.app.language_manager.translate("select") + self.app.language_manager.translate("category")))
        title_item.ripple_effect = False
        title_item.focus_behavior = False
        self.ids.question_category_list.add_widget(title_item)

        for question_category_id, question_category in question_categories.items():
            self.ids.question_category_list.add_widget(
                MDListItem(
                    MDListItemHeadlineText(text=question_category["name"]),
                    on_release=lambda _, cat_id=question_category_id: self.app.question_learning_screen.start_learning(cat_id)
                )
            )

        if len(question_categories) >= 2:
            self.ids.question_category_list.add_widget(
                MDListItem(
                    MDListItemHeadlineText(text=self.app.language_manager.translate("all")),
                    on_release=lambda _, cat_id=None: self.app.question_learning_screen.start_learning(cat_id)
                )
            )


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
                "on_release": lambda: self.app.create_or_edit_category_popup_menu.open(CategoryTypes.question, False),
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
        self.app.create_or_edit_category_popup_menu.open(CategoryTypes.question, True)


    def delete(self):
        self.app.delete_category_popup_menu.open(CategoryTypes.question)
