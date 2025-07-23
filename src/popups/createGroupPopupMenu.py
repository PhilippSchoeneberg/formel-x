from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivy.app import App
from kivy.uix.widget import Widget
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText, MDTextFieldHelperText
from kivymd.uix.boxlayout import MDBoxLayout
import datetime


class CreateGroupPopUpMenu(MDDialog):
    def __init__(self):
        self.name_helper_text = MDTextFieldHelperText(text="Group name can't be empty", mode="on_error")

        self.name_field = MDTextField(
            MDTextFieldHintText(text="Group name"),
            self.name_helper_text,
            mode="outlined",
            size_hint_x=1,
            pos_hint={"center_x": 0.5},
        )

        content_box = MDBoxLayout(
            self.name_field,
            orientation="vertical",
            spacing="30dp",
            adaptive_height=True,
            size_hint_y=None,
        )

        super().__init__(
            MDDialogHeadlineText(text="Create Group", halign="center"),
            MDDialogContentContainer(content_box),
            MDDialogButtonContainer(
                Widget(),
                MDButton(MDButtonText(text="Cancel"), style="text", on_release=self.dismiss),
                MDButton(MDButtonText(text="Submit"), style="text", on_release=self.create_group),
                spacing="8dp",
            ),
        )


    def create_group(self, *args, **kwargs):
        app = App.get_running_app()
        name = self.name_field.text.strip()
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        valid = True
        if not name:
            self.name_helper_text.text = "Group name can't be empty"
            self.name_field.error = False
            self.name_field.error = True
            valid = False
        else:
            self.name_field.error = False

        if valid:
            app.db.cursor.execute("SELECT * FROM groups WHERE name = ?", (name,))
            result = app.db.cursor.fetchone()
            if result:
                self.name_helper_text.text = "Group name already exists"
                self.name_field.error = False
                self.name_field.error = True
            else:
                app.db.cursor.execute(
                    "INSERT INTO groups (name, owner_id, date) VALUES (?, ?, ?)",
                    (name, app.loggedInUserId, date)
                )
                app.modesMenuScreen.refresh_groups()
                app.db.connection.commit()
                self.dismiss()


    def dismiss(self, *args, **kwargs):
        self.name_field.text = ""
        self.name_field.error = False
        super().dismiss()
