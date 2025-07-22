from kivy.clock import Clock
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivymd.uix.list import MDListItem, MDListItemHeadlineText


class QuestionLearningScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.questions_to_learn = None
        self.current_index = None


    def start_learning(self):
        self.app = App.get_running_app()
        self.app.change_screen("questionLearning")

        self.questions_to_learn = [
            question for question in self.app.db.get_all_questions().values()
        ]

        self.current_index = 0
        self.show_next_question()
        self.app.change_screen("questionLearning")


    def show_next_question(self):
        self.app.root.get_screen("questionLearning").ids.question_learning_list.clear_widgets()

        if self.current_index >= len(self.questions_to_learn):
            self.app.change_screen("modesMenu")
            return

        current_question = self.questions_to_learn[self.current_index]

        def on_clicked(item, correct):
            if correct:
                item.theme_bg_color = "Custom"
                item.md_bg_color = [0, 1, 0, 0.3]
                Clock.schedule_once(lambda dt: self.next_compound(), 1)
            else:
                item.theme_bg_color = "Custom"
                item.md_bg_color = [1, 0, 0, 0.3]


        def add_option(text, correct):
            list_item = MDListItem(
                MDListItemHeadlineText(text=text),
                on_release=lambda item: on_clicked(item, correct)
            )
            self.app.root.get_screen("questionLearning").ids.question_learning_list.add_widget(list_item)

        title_item = MDListItem(MDListItemHeadlineText(text=current_question["question"]))
        title_item.ripple_effect = False
        title_item.focus_behavior = False
        self.app.root.get_screen("questionLearning").ids.question_learning_list.add_widget(title_item)

        add_option(current_question["correct_answer"], True)
        add_option(current_question["wrong_answer1"], False)
        add_option(current_question["wrong_answer2"], False)
        add_option(current_question["wrong_answer3"], False)
        add_option(current_question["wrong_answer4"], False)


    def next_compound(self):
        self.current_index += 1
        self.show_next_question()
