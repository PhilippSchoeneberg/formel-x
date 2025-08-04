from src.utils.enums import CategoryTypes, DifficultyTypes

import datetime
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText, MDTextFieldHelperText
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer


class CreateOrEditQuestionPopupMenu(MDDialog):
    def __init__(self):
        self.app = App.get_running_app()
        self.question = None
        self.action_function = None
        self.selected_category = None
        self.selected_difficulty = None

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

        self.categories_button_text = MDButtonText(
            text=self.app.language_manager.translate("select") + self.app.language_manager.translate("category"))

        self.categories_button = MDButton(
            self.categories_button_text,
            style="outlined",
            on_release=self.open_categories_dropdown,
        )

        self.difficulty_button_text = MDButtonText(
            text=self.app.language_manager.translate("select") + self.app.language_manager.translate("difficulty"))

        self.difficulties_button = MDButton(
            self.difficulty_button_text,
            style="outlined",
            on_release=self.open_difficulties_dropdown,
        )

        button_box = MDBoxLayout(
            self.categories_button,
            self.difficulties_button,
            orientation="horizontal",
            spacing="30dp",
            adaptive_height=True,
            size_hint_y=None,
        )

        content_box = MDBoxLayout(
            self.question_field,
            self.correct_answer_field,
            self.wrong_answer_field1,
            self.wrong_answer_field2,
            self.wrong_answer_field3,
            self.wrong_answer_field4,
            button_box,
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

        self.categories_dropdown_menu = MDDropdownMenu(
            caller=self.categories_button,
            items=[],
            width_mult=4,
        )

        self.difficulties_dropdown_menu = MDDropdownMenu(
            caller=self.difficulties_button,
            items=[],
            width_mult=4,
        )


    def open(self, question = None, action_function = None):
        self.app.general_dropdown_menu.dismiss()
        self.question = question
        self.action_function = action_function

        if self.question:
            self.headline_text.text = self.app.language_manager.translate("edit") + self.app.language_manager.translate("question")
            self.question_field.text = self.question["question"]
            self.correct_answer_field.text = self.question["correct_answer"]
            self.wrong_answer_field1.text = self.question["wrong_answer1"]
            self.wrong_answer_field2.text = self.question["wrong_answer2"]
            self.wrong_answer_field3.text = self.question["wrong_answer3"]
            self.wrong_answer_field4.text = self.question["wrong_answer4"]
            self.set_difficulty(DifficultyTypes(self.question["difficulty"]))
            self.set_category(self.app.db.get_category_by_id(self.question["category_id"]))
        else:
            self.headline_text.text = self.app.language_manager.translate("create") + self.app.language_manager.translate("question")

        self.categories_dropdown_menu.items = self.get_category_items()
        self.difficulties_dropdown_menu.items = self.get_difficulty_items()
        super().open()


    def open_categories_dropdown(self, *args, **kwargs):
        self.categories_dropdown_menu.open()


    def get_category_items(self):
        raw_categories = self.app.db.get_all_categories_by_type_and_group(CategoryTypes.question,
                                                                          self.app.logged_in_group)
        categories = [
            {
                "text": category["name"],
                "on_release": lambda x=category: self.set_category(x),
            }
            for category in raw_categories
        ]
        return sorted(categories, key=lambda x: x["text"])


    def set_category(self, category):
        self.selected_category = category
        self.categories_button_text.text = category["name"]
        self.categories_dropdown_menu.dismiss()


    def open_difficulties_dropdown(self, *args, **kwargs):
        self.difficulties_dropdown_menu.open()


    def get_difficulty_items(self):
        return [
            {
                "text": self.app.language_manager.translate(difficulty.value),
                "on_release": lambda x=difficulty: self.set_difficulty(x),
            }
            for difficulty in DifficultyTypes
        ]


    def set_difficulty(self, difficulty):
        self.selected_difficulty = difficulty
        self.difficulty_button_text.text = self.app.language_manager.translate(difficulty.value)
        self.difficulties_dropdown_menu.dismiss()


    def add_question(self, *args, **kwargs):
        question = self.question_field.text.strip()
        correct_answer = self.correct_answer_field.text.strip()
        wrong_answer1 = self.wrong_answer_field1.text.strip()
        wrong_answer2 = self.wrong_answer_field2.text.strip()
        wrong_answer3 = self.wrong_answer_field3.text.strip()
        wrong_answer4 = self.wrong_answer_field4.text.strip()
        category = self.selected_category
        difficulty = self.selected_difficulty
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        valid = True
        if not correct_answer:
            self.correct_answer_field.error = True
            valid = False
        else:
            self.correct_answer_field.error = False

        if not wrong_answer1:
            self.wrong_answer_field1.error = True
            valid = False
        else:
            self.wrong_answer_field1.error = False

        if not wrong_answer2:
            self.wrong_answer_field2.error = True
            valid = False
        else:
            self.wrong_answer_field2.error = False

        if not category:
            valid = False

        if not difficulty:
            valid = False

        if valid:
            if not self.question:
                self.app.db.cursor.execute(
                    "INSERT INTO questions (question, correct_answer, wrong_answer1, wrong_answer2, wrong_answer3, wrong_answer4, difficulty, category_id, group_id, date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (question, correct_answer, wrong_answer1, wrong_answer2, wrong_answer3, wrong_answer4, difficulty.value, category["id"], self.app.logged_in_group["id"], date)
                )
            else:
                self.app.db.cursor.execute(
                    "UPDATE questions SET question = ?, correct_answer = ?, wrong_answer1 = ?, wrong_answer2 = ?, wrong_answer3 = ?, wrong_answer4 = ?, difficulty = ?, category_id = ?, group_id = ?, date = ? WHERE id = ?",
                    (question, correct_answer, wrong_answer1, wrong_answer2, wrong_answer3, wrong_answer4, difficulty.value, category["id"], self.app.logged_in_group["id"], date, self.question["id"])
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
        self.selected_category = None
        self.selected_difficulty = None
        super().dismiss()
