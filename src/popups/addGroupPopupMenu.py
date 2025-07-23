from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivy.app import App
from kivy.uix.widget import Widget
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText, MDTextFieldHelperText
from kivymd.uix.boxlayout import MDBoxLayout

from src.utils.json_parser import save_state


class AddGroupPopUpMenu(MDDialog):
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
            MDDialogHeadlineText(text="Add Group", halign="center"),
            MDDialogContentContainer(content_box),
            MDDialogButtonContainer(
                Widget(),
                MDButton(MDButtonText(text="Cancel"), style="text", on_release=self.dismiss),
                MDButton(MDButtonText(text="Add"), style="text", on_release=self.add_group),
                spacing="8dp",
            ),
        )


    def add_group(self, *args, **kwargs):
        app = App.get_running_app()
        name = self.name_field.text.strip()

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
                if result[0] not in app.groups:
                    group = {"id": result[0], "name": result[1]}
                    app.groups.append(group)
                    app.state["groups"] = app.groups
                    save_state(self.state)
                app.modesMenuScreen.refresh_groups()
                app.db.connection.commit()
                self.dismiss()
            else:
                self.name_helper_text.text = "Group does not exist"
                self.name_field.error = False
                self.name_field.error = True


    def dismiss(self, *args, **kwargs):
        self.name_field.text = ""
        self.name_field.error = False
        super().dismiss()
