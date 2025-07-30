from kivy.app import App
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivymd.uix.list import MDListItem, MDListItemHeadlineText


class QuestionLearningScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.questions_to_learn = []
        self.current_index = 0
        self.current_question = None


    def refresh(self):
        if self.app.root.current == self.name:
            self.show_next_question()


    def start_learning(self, category=None):
        self.app.change_screen("questionLearning")
        self.current_index = 0
        if category:
            self.questions_to_learn = [
                question for question in self.app.db.get_all_questions_by_group(self.app.logged_in_group).values()
                if question["category"] == category
            ]
        else:
            self.questions_to_learn = [
                question for question in self.app.db.get_all_questions_by_group(self.app.logged_in_group).values()
            ]
        self.refresh()


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


    def create(self):
        self.app.create_or_edit_question_popup_menu.open()


    def edit(self):
        self.app.create_or_edit_question_popup_menu.open(self.current_question, self.next_question)


    def delete(self):
        self.app.confirm_delete_popup_menu.open(self.app.language_manager.translate("question"), self.current_question["question"], lambda: self.app.db.delete_question(self.current_question), self.next_question)
