import datetime
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText, MDTextFieldHelperText
from kivymd.uix.boxlayout import MDBoxLayout


class CreateOrEditQuestionPopUpMenu(MDDialog):
    def __init__(self):
        self.app = App.get_running_app()
        self.question = None
        self.action_function = None

        self.question_hint_text = MDTextFieldHintText(text=self.app.language_manager.translate("question"))
        self.question_helper_text = MDTextFieldHelperText(text=self.app.language_manager.translate("question") + self.app.language_manager.translate("empty_error"), mode="on_error")

        self.question_field = MDTextField(
            self.question_hint_text,
            self.question_helper_text,
            mode="outlined",
            size_hint_x=1,
            pos_hint={"center_x": 0.5},
        )

        self.correct_answer_hint_text = MDTextFieldHintText(text=self.app.language_manager.translate("correct_answer"))
        self.correct_answer_helper_text = MDTextFieldHelperText(
            text=self.app.language_manager.translate("correct_answer") + self.app.language_manager.translate("empty_error"),
            mode="on_error")

        self.correct_answer_field = MDTextField(
            self.correct_answer_hint_text,
            self.correct_answer_helper_text,
            mode="outlined",
            size_hint_x=1,
            pos_hint={"center_x": 0.5},
        )

        self.wrong_answer1_hint_text = MDTextFieldHintText(text=self.app.language_manager.translate("first_wrong_answer"))
        self.wrong_answer1_helper_text = MDTextFieldHelperText(
            text=self.app.language_manager.translate("first_wrong_answer") + self.app.language_manager.translate(
                "empty_error"),
            mode="on_error")

        self.wrong_answer_field1 = MDTextField(
            self.wrong_answer1_hint_text,
            self.wrong_answer1_helper_text,
            mode="outlined",
            size_hint_x=1,
            pos_hint={"center_x": 0.5},
        )

        self.wrong_answer2_hint_text = MDTextFieldHintText(
            text=self.app.language_manager.translate("second_wrong_answer"))
        self.wrong_answer2_helper_text = MDTextFieldHelperText(
            text=self.app.language_manager.translate("second_wrong_answer") + self.app.language_manager.translate(
                "empty_error"),
            mode="on_error")

        self.wrong_answer_field2 = MDTextField(
            self.wrong_answer2_hint_text,
            self.wrong_answer2_helper_text,
            mode="outlined",
            multiline=True,
            size_hint_x=1,
            pos_hint={"center_x": 0.5},
        )

        self.wrong_answer3_hint_text = MDTextFieldHintText(
            text=self.app.language_manager.translate("third_wrong_answer"))
        self.wrong_answer3_helper_text = MDTextFieldHelperText(
            text=self.app.language_manager.translate("third_wrong_answer") + self.app.language_manager.translate(
                "empty_error"),
            mode="on_error")

        self.wrong_answer_field3 = MDTextField(
            self.wrong_answer3_hint_text,
            self.wrong_answer3_helper_text,
            mode="outlined",
            multiline=True,
            size_hint_x=1,
            pos_hint={"center_x": 0.5},
        )

        self.wrong_answer4_hint_text = MDTextFieldHintText(
            text=self.app.language_manager.translate("fourth_wrong_answer"))
        self.wrong_answer4_helper_text = MDTextFieldHelperText(
            text=self.app.language_manager.translate("fourth_wrong_answer") + self.app.language_manager.translate(
                "empty_error"),
            mode="on_error")

        self.wrong_answer_field4 = MDTextField(
            self.wrong_answer4_hint_text,
            self.wrong_answer4_helper_text,
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

        self.headline_text = MDDialogHeadlineText(text=self.app.language_manager.translate("create") + self.app.language_manager.translate("question"), halign="center")
        self.cancel_button_text = MDButtonText(text=self.app.language_manager.translate("cancel"))
        self.submit_button_text = MDButtonText(text=self.app.language_manager.translate("submit"))

        super().__init__(
            self.headline_text,
            MDDialogContentContainer(scroll_view),
            MDDialogButtonContainer(
                Widget(),
                MDButton(self.cancel_button_text, style="text", on_release=self.dismiss),
                MDButton(self.submit_button_text, style="text", on_release=self.add_question),
                spacing="8dp",
            ),
        )


    def open(self, question = None, action_function = None):
        self.app.general_dropdown_menu.dismiss()
        self.question = question
        self.action_function = action_function

        self.question_hint_text.text = self.app.language_manager.translate("question")
        self.question_helper_text.text = self.app.language_manager.translate("question") + self.app.language_manager.translate("empty_error")
        self.correct_answer_hint_text.text = self.app.language_manager.translate("correct_answer")
        self.correct_answer_helper_text.text = self.app.language_manager.translate("correct_answer") + self.app.language_manager.translate("empty_error")
        self.wrong_answer1_hint_text.text = self.app.language_manager.translate("first_wrong_answer")
        self.wrong_answer1_helper_text.text = self.app.language_manager.translate("first_wrong_answer") + self.app.language_manager.translate("empty_error")
        self.wrong_answer2_hint_text.text = self.app.language_manager.translate("second_wrong_answer")
        self.wrong_answer2_helper_text.text = self.app.language_manager.translate("second_wrong_answer") + self.app.language_manager.translate("empty_error")
        self.wrong_answer3_hint_text.text = self.app.language_manager.translate("third_wrong_answer")
        self.wrong_answer3_helper_text.text = self.app.language_manager.translate("third_wrong_answer") + self.app.language_manager.translate("empty_error")
        self.wrong_answer4_hint_text.text = self.app.language_manager.translate("fourth_wrong_answer")
        self.wrong_answer4_helper_text.text = self.app.language_manager.translate("fourth_wrong_answer") + self.app.language_manager.translate("empty_error")

        self.question_hint_text.canvas.ask_update()
        self.question_helper_text.canvas.ask_update()
        self.correct_answer_hint_text.canvas.ask_update()
        self.correct_answer_helper_text.canvas.ask_update()
        self.wrong_answer1_hint_text.canvas.ask_update()
        self.wrong_answer1_helper_text.canvas.ask_update()
        self.wrong_answer2_hint_text.canvas.ask_update()
        self.wrong_answer2_helper_text.canvas.ask_update()
        self.wrong_answer3_hint_text.canvas.ask_update()
        self.wrong_answer3_helper_text.canvas.ask_update()
        self.wrong_answer4_hint_text.canvas.ask_update()
        self.wrong_answer4_helper_text.canvas.ask_update()

        if self.question:
            self.headline_text.text = self.app.language_manager.translate("edit") + self.app.language_manager.translate("question")
            self.question_field.text = self.question["question"]
            self.correct_answer_field.text = self.question["correct_answer"]
            self.wrong_answer_field1.text = self.question["wrong_answer1"]
            self.wrong_answer_field2.text = self.question["wrong_answer2"]
            self.wrong_answer_field3.text = self.question["wrong_answer3"]
            self.wrong_answer_field4.text = self.question["wrong_answer4"]
        else:
            self.headline_text.text = self.app.language_manager.translate("create") + self.app.language_manager.translate("question")
        self.cancel_button_text.text = self.app.language_manager.translate("cancel")
        self.submit_button_text.text = self.app.language_manager.translate("submit")
        super().open()


    def add_question(self, *args, **kwargs):
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

        if valid:
            if not self.question:
                self.app.db.cursor.execute(
                    "INSERT INTO questions (question, correct_answer, wrong_answer1, wrong_answer2, wrong_answer3, wrong_answer4, group_id, date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (question, correct_answer, wrong_answer1, wrong_answer2, wrong_answer3, wrong_answer4, self.app.logged_in_group["id"], date)
                )
            else:
                self.app.db.cursor.execute(
                    "UPDATE questions SET question = ?, correct_answer = ?, wrong_answer1 = ?, wrong_answer2 = ?, wrong_answer3 = ?, wrong_answer4 = ?, group_id = ?, date = ? WHERE id = ?",
                    (question, correct_answer, wrong_answer1, wrong_answer2, wrong_answer3, wrong_answer4, self.app.logged_in_group["id"], date, self.question["id"])
                )
                self.action_function()
            self.app.db.connection.commit()
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
