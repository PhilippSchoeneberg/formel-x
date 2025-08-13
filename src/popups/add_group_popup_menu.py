from src.utils.json_parser import save_state

from kivy.app import App
from kivy.uix.widget import Widget
from ext.kivymd.uix.boxlayout import MDBoxLayout
from ext.kivymd.uix.button import MDButton, MDButtonText
from ext.kivymd.uix.textfield import MDTextField, MDTextFieldHintText, MDTextFieldHelperText
from ext.kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer


class AddGroupPopupMenu(MDDialog):
    def __init__(self):
        self.app = App.get_running_app()

        self.name_helper_text = MDTextFieldHelperText(text=self.app.language_manager.translate("group_name") + self.app.language_manager.translate("empty_error"), mode="on_error")
        self.name_hint_text = MDTextFieldHintText(text=self.app.language_manager.translate("group_name"))

        self.name_field = MDTextField(
            self.name_hint_text,
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

        self.headline_text = MDDialogHeadlineText(text=self.app.language_manager.translate("add_group"), halign="center")
        self.cancel_button_text = MDButtonText(text=self.app.language_manager.translate("cancel"))
        self.submit_button_text = MDButtonText(text=self.app.language_manager.translate("submit"))

        super().__init__(
            self.headline_text,
            MDDialogContentContainer(content_box),
            MDDialogButtonContainer(
                Widget(),
                MDButton(self.cancel_button_text, style="text", on_release=self.dismiss),
                MDButton(self.submit_button_text, style="text", on_release=self.add_group),
                spacing="8dp",
            ),
        )

    def on_open(self):
        if self.app.general_dropdown_menu:
            self.app.general_dropdown_menu.dismiss()
        super().open()


    def add_group(self, *args, **kwargs):
        name = self.name_field.text.strip()

        valid = True
        if not name:
            self.name_helper_text.text = self.app.language_manager.translate("group_name") + self.app.language_manager.translate("empty_error")
            self.name_field.error = False
            self.name_field.error = True
            valid = False
        else:
            self.name_field.error = False

        if valid:
            group = self.app.db.get_group_by_name(name)
            if group:
                if group not in self.app.groups:
                    self.app.groups.append(group)
                    self.app.state["groups"] = self.app.groups
                    save_state(self.state)
                    self.app.modes_menu_screen.refresh_groups()
                    self.dismiss()
                else:
                    self.name_helper_text.text = self.app.language_manager.translate("group") + self.app.language_manager.translate("already_added_error")
                    self.name_field.error = False
                    self.name_field.error = True
            else:
                self.name_helper_text.text = self.app.language_manager.translate("group") + self.app.language_manager.translate("does_not_exist_error")
                self.name_field.error = False
                self.name_field.error = True


    def dismiss(self, *args, **kwargs):
        self.name_field.text = ""
        self.name_field.error = False
        super().dismiss()
