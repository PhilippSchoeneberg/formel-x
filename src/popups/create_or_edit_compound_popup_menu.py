from src.utils.transform_to_unicode import transform_to_unicode

from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText, MDTextFieldHelperText
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.menu import MDDropdownMenu
import datetime


class CreateOrEditCompoundPopUpMenu(MDDialog):
    def __init__(self):
        self.app = App.get_running_app()
        self.compound = None
        self.action_function = None
        self.selected_category = None

        self.correct_name_hint_text = MDTextFieldHintText(text=self.app.language_manager.translate("correct_formula_name"))
        self.correct_name_helper_text = MDTextFieldHelperText(text=self.app.language_manager.translate("correct_formula_name") + self.app.language_manager.translate("empty_error"), mode="on_error")

        self.correct_name_field = MDTextField(
            self.correct_name_hint_text,
            self.correct_name_helper_text,
            mode="outlined",
            size_hint_x=1,
            pos_hint={"center_x": 0.5},
        )

        self.wrong_name1_hint_text = MDTextFieldHintText(text=self.app.language_manager.translate("first_wrong_formula_name"))
        self.wrong_name1_helper_text = MDTextFieldHelperText(text=self.app.language_manager.translate("first_wrong_formula_name") + self.app.language_manager.translate("empty_error"), mode="on_error")

        self.wrong_name_field1 = MDTextField(
            self.wrong_name1_hint_text,
            self.wrong_name1_helper_text,
            mode="outlined",
            size_hint_x=1,
            pos_hint={"center_x": 0.5},
        )

        self.wrong_name2_hint_text = MDTextFieldHintText(
            text=self.app.language_manager.translate("second_wrong_formula_name"))
        self.wrong_name2_helper_text = MDTextFieldHelperText(
            text=self.app.language_manager.translate("second_wrong_formula_name") + self.app.language_manager.translate(
                "empty_error"), mode="on_error")

        self.wrong_name_field2 = MDTextField(
            self.wrong_name2_hint_text,
            self.wrong_name2_helper_text,
            mode="outlined",
            size_hint_x=1,
            pos_hint={"center_x": 0.5},
        )

        self.wrong_name3_hint_text = MDTextFieldHintText(
            text=self.app.language_manager.translate("third_wrong_formula_name"))
        self.wrong_name3_helper_text = MDTextFieldHelperText(
            text=self.app.language_manager.translate("third_wrong_formula_name") + self.app.language_manager.translate(
                "empty_error"), mode="on_error")

        self.wrong_name_field3 = MDTextField(
            self.wrong_name3_hint_text,
            self.wrong_name3_helper_text,
            mode="outlined",
            size_hint_x=1,
            pos_hint={"center_x": 0.5},
        )

        self.wrong_name4_hint_text = MDTextFieldHintText(
            text=self.app.language_manager.translate("fourth_wrong_formula_name"))
        self.wrong_name4_helper_text = MDTextFieldHelperText(
            text=self.app.language_manager.translate("fourth_wrong_formula_name") + self.app.language_manager.translate(
                "empty_error"), mode="on_error")

        self.wrong_name_field4 = MDTextField(
            self.wrong_name4_hint_text,
            self.wrong_name4_helper_text,
            mode="outlined",
            size_hint_x=1,
            pos_hint={"center_x": 0.5},
        )

        self.correct_formula_hint_text = MDTextFieldHintText(
            text=self.app.language_manager.translate("correct_formula"))
        self.correct_formula_helper_text = MDTextFieldHelperText(
            text=self.app.language_manager.translate("correct_formula") + self.app.language_manager.translate(
                "empty_error"), mode="on_error")

        self.correct_formula_field = MDTextField(
            self.correct_formula_hint_text,
            self.correct_formula_helper_text,
            mode="outlined",
            multiline=True,
            size_hint_x=1,
            pos_hint={"center_x": 0.5},
        )

        self.wrong_formula1_hint_text = MDTextFieldHintText(
            text=self.app.language_manager.translate("first_wrong_formula"))
        self.wrong_formula1_helper_text = MDTextFieldHelperText(
            text=self.app.language_manager.translate("first_wrong_formula") + self.app.language_manager.translate(
                "empty_error"), mode="on_error")

        self.wrong_formula_field1 = MDTextField(
            self.wrong_formula1_hint_text,
            self.wrong_formula1_helper_text,
            mode="outlined",
            multiline=True,
            size_hint_x=1,
            pos_hint={"center_x": 0.5},
        )

        self.wrong_formula2_hint_text = MDTextFieldHintText(
            text=self.app.language_manager.translate("first_wrong_formula"))
        self.wrong_formula2_helper_text = MDTextFieldHelperText(
            text=self.app.language_manager.translate("first_wrong_formula") + self.app.language_manager.translate(
                "empty_error"), mode="on_error")

        self.wrong_formula_field2 = MDTextField(
            self.wrong_formula2_hint_text,
            self.wrong_formula2_helper_text,
            mode="outlined",
            multiline=True,
            size_hint_x=1,
            pos_hint={"center_x": 0.5},
        )

        self.wrong_formula3_hint_text = MDTextFieldHintText(
            text=self.app.language_manager.translate("first_wrong_formula"))
        self.wrong_formula3_helper_text = MDTextFieldHelperText(
            text=self.app.language_manager.translate("first_wrong_formula") + self.app.language_manager.translate(
                "empty_error"), mode="on_error")

        self.wrong_formula_field3 = MDTextField(
            self.wrong_formula3_hint_text,
            self.wrong_formula3_helper_text,
            mode="outlined",
            multiline=True,
            size_hint_x=1,
            pos_hint={"center_x": 0.5},
        )

        self.wrong_formula4_hint_text = MDTextFieldHintText(
            text=self.app.language_manager.translate("first_wrong_formula"))
        self.wrong_formula4_helper_text = MDTextFieldHelperText(
            text=self.app.language_manager.translate("first_wrong_formula") + self.app.language_manager.translate(
                "empty_error"), mode="on_error")

        self.wrong_formula_field4 = MDTextField(
            self.wrong_formula4_hint_text,
            self.wrong_formula4_helper_text,
            mode="outlined",
            multiline=True,
            size_hint_x=1,
            pos_hint={"center_x": 0.5},
        )

        self.categories_button_text = MDButtonText(text=self.app.language_manager.translate("select") + self.app.language_manager.translate("category"))

        self.categories_button = MDButton(
            self.categories_button_text,
            style="outlined",
            on_release=self.open_categories_dropdown,
        )

        content_box = MDBoxLayout(
            self.correct_name_field,
            self.wrong_name_field1,
            self.wrong_name_field2,
            self.wrong_name_field3,
            self.wrong_name_field4,
            self.correct_formula_field,
            self.wrong_formula_field1,
            self.wrong_formula_field2,
            self.wrong_formula_field3,
            self.wrong_formula_field4,
            self.categories_button,
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

        self.headline_text = MDDialogHeadlineText(text=self.app.language_manager.translate("create") + self.app.language_manager.translate("compound"), halign="center")
        self.cancel_button_text = MDButtonText(text=self.app.language_manager.translate("cancel"))
        self.submit_button_text = MDButtonText(text=self.app.language_manager.translate("submit"))

        super().__init__(
            self.headline_text,
            MDDialogContentContainer(scroll_view),
            MDDialogButtonContainer(
                Widget(),
                MDButton(self.cancel_button_text, style="text", on_release=self.dismiss),
                MDButton(self.submit_button_text, style="text", on_release=self.add_compound),
                spacing="8dp",
            ),
        )

        self.categories_dropdown_menu = MDDropdownMenu(
            caller=self.categories_button,
            items=[],
            width_mult=4,
        )


    def open(self, compound = None, action_function = None):
        self.app.general_dropdown_menu.dismiss()
        self.compound = compound
        self.action_function = action_function

        self.correct_name_hint_text.text = self.app.language_manager.translate("correct_formula_name")
        self.correct_name_helper_text.text = self.app.language_manager.translate("correct_formula_name") + self.app.language_manager.translate("empty_error")
        self.wrong_name1_hint_text.text = self.app.language_manager.translate("first_wrong_formula_name")
        self.wrong_name1_helper_text.text = self.app.language_manager.translate("first_wrong_formula_name") + self.app.language_manager.translate("empty_error")
        self.wrong_name2_hint_text.text = self.app.language_manager.translate("second_wrong_formula_name")
        self.wrong_name2_helper_text.text = self.app.language_manager.translate("second_wrong_formula_name") + self.app.language_manager.translate("empty_error")
        self.wrong_name3_hint_text.text = self.app.language_manager.translate("third_wrong_formula_name")
        self.wrong_name3_helper_text.text = self.app.language_manager.translate("third_wrong_formula_name") + self.app.language_manager.translate("empty_error")
        self.wrong_name4_hint_text.text = self.app.language_manager.translate("fourth_wrong_formula_name")
        self.wrong_name4_helper_text.text = self.app.language_manager.translate("fourth_wrong_formula_name") + self.app.language_manager.translate("empty_error")
        self.correct_formula_hint_text.text = self.app.language_manager.translate("correct_formula")
        self.correct_formula_helper_text.text = self.app.language_manager.translate("correct_formula") + self.app.language_manager.translate("empty_error")
        self.wrong_formula1_hint_text.text = self.app.language_manager.translate("first_wrong_formula")
        self.wrong_formula1_helper_text.text = self.app.language_manager.translate("first_wrong_formula") + self.app.language_manager.translate("empty_error")
        self.wrong_formula2_hint_text.text = self.app.language_manager.translate("first_wrong_formula")
        self.wrong_formula2_helper_text.text = self.app.language_manager.translate("first_wrong_formula") + self.app.language_manager.translate("empty_error")
        self.wrong_formula3_hint_text.text = self.app.language_manager.translate("first_wrong_formula")
        self.wrong_formula3_helper_text.text = self.app.language_manager.translate("first_wrong_formula") + self.app.language_manager.translate("empty_error")
        self.wrong_formula4_hint_text.text = self.app.language_manager.translate("first_wrong_formula")
        self.wrong_formula4_helper_text.text = self.app.language_manager.translate("first_wrong_formula") + self.app.language_manager.translate("empty_error")
        self.categories_button_text.text = self.app.language_manager.translate("select") + self.app.language_manager.translate("category")
        self.headline_text.text = self.app.language_manager.translate("create") + self.app.language_manager.translate("compound")
        self.cancel_button_text.text = self.app.language_manager.translate("cancel")
        self.submit_button_text.text = self.app.language_manager.translate("submit")

        if self.compound:
            self.headline_text = self.app.language_manager.translate("edit") + self.app.language_manager.translate("compound")
            self.correct_name_field.text = self.compound["correct_name"]
            self.wrong_name_field1.text = self.compound["wrong_name1"]
            self.wrong_name_field2.text = self.compound["wrong_name2"]
            self.wrong_name_field3.text = self.compound["wrong_name3"]
            self.wrong_name_field4.text = self.compound["wrong_name4"]
            self.correct_formula_field.text = self.compound["correct_formula"]
            self.wrong_formula_field1.text = self.compound["wrong_formula1"]
            self.wrong_formula_field2.text = self.compound["wrong_formula2"]
            self.wrong_formula_field3.text = self.compound["wrong_formula3"]
            self.wrong_formula_field4.text = self.compound["wrong_formula4"]
            self.selected_category = self.app.db.get_category_by_id(self.compound["category"])
            self.categories_button_text.text = self.selected_category["name"]
        self.categories_dropdown_menu.items = self.get_category_items()
        super().open()


    def open_categories_dropdown(self, *args, **kwargs):
        self.categories_dropdown_menu.open()


    def get_category_items(self):
        categories = self.app.db.get_all_categories_by_group(self.app.logged_in_group)
        return [
            {
                "text": category["name"],
                "on_release": lambda x=category: self.set_category(x),
            }
            for category in categories.values()
        ]


    def set_category(self, category):
        self.selected_category = category
        self.categories_button_text.text = category["name"]
        self.categories_dropdown_menu.dismiss()


    def add_compound(self, *args, **kwargs):
        correct_name = self.correct_name_field.text.strip()
        wrong_name1 = self.wrong_name_field1.text.strip()
        wrong_name2 = self.wrong_name_field2.text.strip()
        wrong_name3 = self.wrong_name_field3.text.strip()
        wrong_name4 = self.wrong_name_field4.text.strip()
        correct_formula = transform_to_unicode(self.correct_formula_field.text.strip())
        wrong_formula1 = transform_to_unicode(self.wrong_formula_field1.text.strip())
        wrong_formula2 = transform_to_unicode(self.wrong_formula_field2.text.strip())
        wrong_formula3 = transform_to_unicode(self.wrong_formula_field3.text.strip())
        wrong_formula4 = transform_to_unicode(self.wrong_formula_field4.text.strip())
        category = self.selected_category
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        valid = True
        if not correct_name:
            self.correct_name_field.error = True
            valid = False
        else:
            self.correct_name_field.error = False

        if not wrong_name1:
            self.wrong_name_field1.error = True
            valid = False
        else:
            self.wrong_name_field1.error = False

        if not wrong_name2:
            self.wrong_name_field2.error = True
            valid = False
        else:
            self.wrong_name_field2.error = False

        if not correct_formula:
            self.correct_formula_field.error = True
            valid = False
        else:
            self.correct_formula_field.error = False

        if not wrong_formula1:
            self.wrong_formula_field1.error = True
            valid = False
        else:
            self.wrong_formula_field1.error = False

        if not wrong_formula2:
            self.wrong_formula_field2.error = True
            valid = False
        else:
            self.wrong_formula_field2.error = False

        if not category:
            valid = False

        if valid:
            if not self.compound:
                self.app.db.cursor.execute(
                    "INSERT INTO compounds (correct_name, wrong_name1, wrong_name2, wrong_name3, wrong_name4, correct_formula, wrong_formula1, wrong_formula2, wrong_formula3, wrong_formula4, category_id, group_id, date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (correct_name, wrong_name1, wrong_name2, wrong_name3, wrong_name4, correct_formula, wrong_formula1, wrong_formula2, wrong_formula3, wrong_formula4, category["id"], self.app.logged_in_group["id"], date)
                )
            else:
                self.app.db.cursor.execute("UPDATE compounds SET correct_name = ?, wrong_name1 = ?, wrong_name2 = ?,  wrong_name3 = ?, wrong_name4 = ?, correct_formula = ?, wrong_formula1 = ?, wrong_formula2 = ?, wrong_formula3 = ?, wrong_formula4 = ?, category_id = ?, group_id = ?, date = ? WHERE id = ?",
                    (correct_name, wrong_name1, wrong_name2, wrong_name3, wrong_name4, correct_formula, wrong_formula1, wrong_formula2, wrong_formula3, wrong_formula4, category["id"], self.app.logged_in_group["id"], date, self.compound["id"])
                )
                self.action_function()
            self.app.db.connection.commit()
            self.dismiss()


    def dismiss(self, *args, **kwargs):
        self.correct_name_field.text = ""
        self.wrong_name_field1.text = ""
        self.wrong_name_field2.text = ""
        self.wrong_name_field3.text = ""
        self.wrong_name_field4.text = ""
        self.correct_formula_field.text = ""
        self.wrong_formula_field1.text = ""
        self.wrong_formula_field2.text = ""
        self.wrong_formula_field3.text = ""
        self.wrong_formula_field4.text = ""
        self.correct_name_field.error = False
        self.wrong_name_field1.error = False
        self.wrong_name_field2.error = False
        self.wrong_name_field3.error = False
        self.wrong_name_field4.error = False
        self.correct_formula_field.error = False
        self.wrong_formula_field1.error = False
        self.wrong_formula_field2.error = False
        self.wrong_formula_field3.error = False
        self.wrong_formula_field4.error = False
        self.selected_category = None
        super().dismiss()
