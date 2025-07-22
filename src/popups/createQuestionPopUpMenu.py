from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText, MDTextFieldHelperText
from kivymd.uix.boxlayout import MDBoxLayout
import datetime


class CreateQuestionPopUpMenu(MDDialog):
    def __init__(self):
        self.selected_category = None

        self.question_field = MDTextField(
            MDTextFieldHintText(text="Question"),
            MDTextFieldHelperText(text="Question can't be empty", mode="on_error"),
            mode="outlined",
            size_hint_x=1,
            pos_hint={"center_x": 0.5},
        )

        self.correct_answer_field = MDTextField(
            MDTextFieldHintText(text="Correct Answer"),
            MDTextFieldHelperText(text="Answer can't be empty", mode="on_error"),
            mode="outlined",
            size_hint_x=1,
            pos_hint={"center_x": 0.5},
        )

        self.wrong_answer_field1 = MDTextField(
            MDTextFieldHintText(text="First wrong Answer"),
            MDTextFieldHelperText(text="Answer can't be empty", mode="on_error"),
            mode="outlined",
            size_hint_x=1,
            pos_hint={"center_x": 0.5},
        )

        self.wrong_answer_field2 = MDTextField(
            MDTextFieldHintText(text="Second wrong Answer"),
            MDTextFieldHelperText(text="Answer can't be empty", mode="on_error"),
            mode="outlined",
            multiline=True,
            size_hint_x=1,
            pos_hint={"center_x": 0.5},
        )

        self.wrong_answer_field3 = MDTextField(
            MDTextFieldHintText(text="Third wrong Answer"),
            MDTextFieldHelperText(text="Answer can't be empty", mode="on_error"),
            mode="outlined",
            multiline=True,
            size_hint_x=1,
            pos_hint={"center_x": 0.5},
        )

        self.wrong_answer_field4 = MDTextField(
            MDTextFieldHintText(text="Fourth wrong Answer"),
            MDTextFieldHelperText(text="Answer can't be empty", mode="on_error"),
            mode="outlined",
            multiline=True,
            size_hint_x=1,
            pos_hint={"center_x": 0.5},
        )

        content_box = MDBoxLayout(
            self.question_field,
            self.correct_answer_field,
            self.wrong_answer_field1,
            self.wrong_answer_field2,
            self.wrong_answer_field3,
            self.wrong_answer_field4,
            orientation="vertical",
            spacing="30dp",
            adaptive_height=True,
            size_hint_y=None,
        )

        scroll_view = ScrollView(
            size_hint=(1, None),
            height="400dp",  # You can adjust this height as needed
            do_scroll_x=False,
        )
        scroll_view.add_widget(content_box)

        super().__init__(
            MDDialogHeadlineText(text="Create Formula", halign="center"),
            MDDialogContentContainer(scroll_view),
            MDDialogButtonContainer(
                Widget(),
                MDButton(MDButtonText(text="Cancel"), style="text", on_release=self.dismiss),
                MDButton(MDButtonText(text="Submit"), style="text", on_release=self.add_question),
                spacing="8dp",
            ),
        )


    def add_question(self, *args, **kwargs):
        app = App.get_running_app()
        question = self.question_field.text.strip()
        correct_answer = self.correct_answer_field.text.strip()
        wrong_answer1 = self.wrong_answer_field1.text.strip()
        wrong_answer2 = self.wrong_answer_field2.text.strip()
        wrong_answer3 = self.wrong_answer_field3.text.strip()
        wrong_answer4 = self.wrong_answer_field4.text.strip()
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        valid = True
        if not correct_answer:
            self.correct_answer_field.error = True
            valid = False
        if not wrong_answer1:
            self.wrong_answer_field1.error = True
            valid = False
        if not wrong_answer2:
            self.wrong_answer_field2.error = True
            valid = False
        if not wrong_answer3:
            self.wrong_answer_field3.error = True
            valid = False
        if not wrong_answer4:
            self.wrong_answer_field4.error = True
            valid = False

        if valid:
            app.db.cursor.execute(
                "INSERT INTO questions (question, correct_answer, wrong_answer1, wrong_answer2, wrong_answer3, wrong_answer4, date) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (question, correct_answer, wrong_answer1, wrong_answer2, wrong_answer3, wrong_answer4, date)
            )
            app.db.connection.commit()
            self.dismiss()


    def dismiss(self, *args, **kwargs):
        self.question_field.text = ""
        self.correct_answer_field.text = ""
        self.wrong_answer_field1.text = ""
        self.wrong_answer_field2.text = ""
        self.wrong_answer_field3.text = ""
        self.wrong_answer_field4.text = ""
        self.question_field.error = False
        self.correct_answer_field.error = False
        self.wrong_answer_field1.error = False
        self.wrong_answer_field2.error = False
        self.wrong_answer_field3.error = False
        self.wrong_answer_field4.error = False
        super().dismiss()
