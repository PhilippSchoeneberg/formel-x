import datetime
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivy.app import App
from kivy.uix.widget import Widget
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText, MDTextFieldHelperText
from kivymd.uix.boxlayout import MDBoxLayout


class CreateOrEditGroupPopUpMenu(MDDialog):
    def __init__(self):
        self.group = None
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

        self.headline = MDDialogHeadlineText(text="Create Group", halign="center")

        super().__init__(
            self.headline,
            MDDialogContentContainer(content_box),
            MDDialogButtonContainer(
                Widget(),
                MDButton(MDButtonText(text="Cancel"), style="text", on_release=self.dismiss),
                MDButton(MDButtonText(text="Submit"), style="text", on_release=self.create_group),
                spacing="8dp",
            ),
        )


    def open(self, group = None):
        self.group = group
        if self.group:
            self.headline = "Edit Group"
            self.name_field.text = self.group["name"]
        super().open()


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
                if not self.group:
                    app.db.cursor.execute(
                        "INSERT INTO groups (name, owner_id, date) VALUES (?, ?, ?)",
                        (name, app.logged_in_user_id, date)
                    )
                else:
                    app.db.cursor.execute(
                        "UPDATE groups SET name = ?, owner_id = ?, date = ? WHERE id = ?",
                        (name, app.logged_in_user_id, date, self.group["id"])
                    )
                app.modes_menu_screen.refresh_groups()
                app.db.connection.commit()
                self.dismiss()


    def dismiss(self, *args, **kwargs):
        self.headline = "Create Group"
        self.name_field.text = ""
        self.name_field.error = False
        super().dismiss()
