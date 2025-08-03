from src.popups.create_or_edit_question_popup_menu import CreateOrEditQuestionPopupMenu
from src.popups.confirm_delete_popup_menu import ConfirmDeletePopupMenu
from src.popups.error_popup_menu import ErrorPopupMenu

from kivy.app import App
from kivy.clock import Clock
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import MDListItem, MDListItemHeadlineText


class QuestionLearningScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.questions_to_learn = []
        self.current_index = 0
        self.current_question = None


    def refresh(self):
        if self.app.root.current == self.name:
            self.show_next_question()


    def start_learning(self, category=None, difficulty=None):
        self.current_index = 0
        self.questions_to_learn = self.app.db.get_all_questions_by_group(self.app.logged_in_group)
        if category:
            self.questions_to_learn = [
                question for question in self.questions_to_learn
                if question["category_id"] == category
            ]
        if difficulty:
            self.questions_to_learn = [
                question for question in self.questions_to_learn
                if question["difficulty"] == difficulty.value
            ]
        if not self.questions_to_learn:
            ErrorPopupMenu().open(self.app.language_manager.translate("no_entries_yet_error"), lambda: self.app.change_screen("questionMenu"))
        else:
            self.app.change_screen("questionLearning")
            self.show_next_question()


    def show_next_question(self):
        self.ids.question_learning_list.clear_widgets()

        if self.current_index >= len(self.questions_to_learn):
            self.app.change_screen("questionMenu")
            return

        self.current_question = self.questions_to_learn[self.current_index]

        def on_clicked(item, correct):
            if correct:
                item.theme_bg_color = "Custom"
                item.md_bg_color = [0, 1, 0, 0.3]
                Clock.schedule_once(lambda dt: self.next_question(), 1)
            else:
                item.theme_bg_color = "Custom"
                item.md_bg_color = [1, 0, 0, 0.3]

        def add_option(text, correct):
            list_item = MDListItem(
                MDListItemHeadlineText(text=text),
                on_release=lambda item: on_clicked(item, correct)
            )
            self.ids.question_learning_list.add_widget(list_item)

        title_item = MDListItem(MDListItemHeadlineText(text=self.current_question["question"]))
        title_item.ripple_effect = False
        title_item.focus_behavior = False
        self.ids.question_learning_list.add_widget(title_item)

        add_option(self.current_question["correct_answer"], True)
        add_option(self.current_question["wrong_answer1"], False)
        add_option(self.current_question["wrong_answer2"], False)
        if self.current_question["wrong_answer3"]:
            add_option(self.current_question["wrong_answer3"], False)
        if self.current_question["wrong_answer4"]:
            add_option(self.current_question["wrong_answer4"], False)


    def next_question(self):
        self.current_index += 1
        self.show_next_question()


    def create(self, *args):
        if self.app.root.get_screen("questionMenu").create_dropdown_menu:
            self.app.root.get_screen("questionMenu").create_dropdown_menu.dismiss()
        CreateOrEditQuestionPopupMenu().open()


    def edit(self):
        CreateOrEditQuestionPopupMenu().open(self.current_question, self.next_question)


    def delete(self):
        ConfirmDeletePopupMenu().open(self.app.language_manager.translate("question"), self.current_question["question"], lambda: self.app.db.delete_question(self.current_question), self.next_question)
