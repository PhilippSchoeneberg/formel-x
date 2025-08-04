from kivy.app import App
from kivy.uix.widget import Widget
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText, MDTextFieldHelperText
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer


class CreateOrEditGroupPopupMenu(MDDialog):
    def __init__(self):
        self.app = App.get_running_app()
        self.group = None

        self.name_hint_text = MDTextFieldHintText(text= self.app.language_manager.translate("group_name"))
        self.name_helper_text = MDTextFieldHelperText(text= self.app.language_manager.translate("group_name") +  self.app.language_manager.translate("empty_error"), mode="on_error")

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

        self.headline_text = MDDialogHeadlineText(text= self.app.language_manager.translate("create") + self.app.language_manager.translate("group"), halign="center")
        self.cancel_button_text = MDButtonText(text=self.app.language_manager.translate("cancel"))
        self.submit_button_text = MDButtonText(text=self.app.language_manager.translate("submit"))

        super().__init__(
            self.headline_text,
            MDDialogContentContainer(content_box),
            MDDialogButtonContainer(
                Widget(),
                MDButton(self.cancel_button_text, style="text", on_release=self.dismiss),
                MDButton(self.submit_button_text, style="text", on_release=self.create_group),
                spacing="8dp",
            ),
        )


    def open(self, group = None):
        if self.app.general_dropdown_menu:
            self.app.general_dropdown_menu.dismiss()

        self.group = group
        if self.group:
            self.headline_text = self.app.language_manager.translate("edit") + self.app.language_manager.translate("group")
            self.name_field.text = self.group["name"]
        else:
            self.headline_text.text = self.app.language_manager.translate("create") + self.app.language_manager.translate("group")

        super().open()


    def create_group(self, *args, **kwargs):
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
                self.name_helper_text.text = self.app.language_manager.translate("group_name") + self.app.language_manager.translate("already_exists_error")
                self.name_field.error = False
                self.name_field.error = True
            else:
                if not self.group:
                    self.app.db.create_group(name, self.app.logged_in_user_id)
                else:
                    self.app.db.update_group(self.group["id"], name, self.app.logged_in_user_id)
                self.app.modes_menu_screen.refresh_groups()
                self.dismiss()


    def dismiss(self, *args, **kwargs):
        self.name_field.text = ""
        self.name_field.error = False
        super().dismiss()
