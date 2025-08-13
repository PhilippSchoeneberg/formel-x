import bcrypt
from kivy.app import App
from ext.kivymd.uix.boxlayout import MDBoxLayout
from ext.kivymd.uix.button import MDButton, MDButtonText
from ext.kivymd.uix.textfield import MDTextField, MDTextFieldHintText, MDTextFieldHelperText
from ext.kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer


class RegisterOrLoginAccountPopupMenu(MDDialog):
    def __init__(self):
        self.app = App.get_running_app()
        self.register_mode = False

        self.email_hint_text = MDTextFieldHintText(text=self.app.language_manager.translate("email_address"))
        self.email_helper_text = MDTextFieldHelperText(text=self.app.language_manager.translate("email_address") + self.app.language_manager.translate("empty_error"), mode="on_error")

        self.email_field = MDTextField(
            self.email_hint_text,
            self.email_helper_text,
            mode="outlined",
            size_hint_x=1,
            pos_hint={"center_x": 0.5},
        )

        self.password_hint_text = MDTextFieldHintText(text=self.app.language_manager.translate("password"))
        self.password_helper_text = MDTextFieldHelperText(text=self.app.language_manager.translate("password") + self.app.language_manager.translate("empty_error"), mode="on_error")

        self.password_field = MDTextField(
            self.password_hint_text,
            self.password_helper_text,
            mode="outlined",
            size_hint_x=1,
            pos_hint={"center_x": 0.5},
            password=True,
        )

        self.password_repetition_hint_text = MDTextFieldHintText(text=self.app.language_manager.translate("password_repetition"))
        self.password_repetition_helper_text = MDTextFieldHelperText(text=self.app.language_manager.translate("password_repetition") + self.app.language_manager.translate("empty_error"), mode="on_error")

        self.password_repetition_field = MDTextField(
            self.password_repetition_hint_text,
            self.password_repetition_helper_text,
            mode="outlined",
            size_hint_x=1,
            pos_hint={"center_x": 0.5},
            password=True,
        )

        self.content_box = MDBoxLayout(
            self.email_field,
            self.password_field,
            orientation="vertical",
            spacing="30dp",
            adaptive_height=True,
            size_hint_y=None,
        )

        self.headline = MDDialogHeadlineText(text=self.app.language_manager.translate("login"), halign="center")
        self.cancel_button_text = MDButtonText(text=self.app.language_manager.translate("cancel"))
        self.submit_button_text = MDButtonText(text=self.app.language_manager.translate("login"))
        self.toggle_button_text = MDButtonText(text=self.app.language_manager.translate("go_to_registration"))

        super().__init__(
            self.headline,
            MDDialogContentContainer(self.content_box),
            MDDialogButtonContainer(
                MDButton(self.cancel_button_text, style="text", on_release=self.dismiss),
                MDButton(self.submit_button_text, style="text", on_release=self.login),
                MDButton(self.toggle_button_text, style="text", on_release=self.toggle_mode),
                spacing="8dp",
            ),
        )


    def toggle_mode(self, *args, **kwargs):
        if self.password_repetition_field.parent is None:
            self.register_mode = True
            self.content_box.add_widget(self.password_repetition_field)
            self.headline.text = self.app.language_manager.translate("register")
            self.submit_button_text.text = self.app.language_manager.translate("register")
            self.toggle_button_text.text = self.app.language_manager.translate("go_to_login")
        else:
            self.register_mode = False
            self.content_box.remove_widget(self.password_repetition_field)
            self.headline.text = self.app.language_manager.translate("login")
            self.submit_button_text.text = self.app.language_manager.translate("login")
            self.toggle_button_text.text = self.app.language_manager.translate("go_to_registration")


    def login(self, *args, **kwargs):
        email = self.email_field.text.strip()
        password = self.password_field.text.strip()

        valid = True
        if not email:
            self.email_helper_text.text = self.app.language_manager.translate("email_address") + self.app.language_manager.translate("empty_error")
            self.email_field.error = False
            self.email_field.error = True
            valid = False
        else:
            self.email_field.error = False
        if not password:
            self.password_helper_text.text = self.app.language_manager.translate("password") + self.app.language_manager.translate("empty_error")
            self.password_field.error = False
            self.password_field.error = True
            valid = False
        else:
            self.password_field.error = False

        if not self.register_mode:
            if valid:
                account = self.app.db.get_account_by_email(email)
                if account and bcrypt.checkpw(password.encode("utf-8"), account["password"].encode("utf-8")):
                    self.app.login(account["id"])
                    self.dismiss()
                else:
                    self.email_helper_text.text = self.app.language_manager.translate("email_address") + self.app.language_manager.translate("or") + self.app.language_manager.translate("password") + self.app.language_manager.translate("incorrect_error")
                    self.email_field.error = False
                    self.email_field.error = True
                    self.password_helper_text.text = self.app.language_manager.translate("email_address") + self.app.language_manager.translate("or") + self.app.language_manager.translate("password") + self.app.language_manager.translate("incorrect_error")
                    self.password_field.error = False
                    self.password_field.error = True
        else:
            password_repetition = self.password_repetition_field.text.strip()
            if not password_repetition:
                self.password_repetition_helper_text.text = self.app.language_manager.translate("password_repetition") + self.app.language_manager.translate("empty_error")
                self.password_repetition_field.error = False
                self.password_repetition_field.error = True
                valid = False
            elif password != password_repetition:
                self.password_helper_text.text = self.app.language_manager.translate("password") + self.app.language_manager.translate("and") + self.app.language_manager.translate("password_repetition") + self.app.language_manager.translate("do_not_match_error")
                self.password_field.error = False
                self.password_field.error = True
                self.password_repetition_helper_text.text = self.app.language_manager.translate("password") + self.app.language_manager.translate("and") + self.app.language_manager.translate("password_repetition") + self.app.language_manager.translate("do_not_match_error")
                self.password_repetition_helper_text.error = False
                self.password_repetition_helper_text.error = True
                valid = False
            else:
                self.password_repetition_field.error = False
            if valid:
                account = self.app.db.get_account_by_email(email)
                if account:
                    self.email_helper_text.text =  self.app.language_manager.translate("account") +  self.app.language_manager.translate("already_exists_error")
                    self.email_field.error = False
                    self.email_field.error = True
                else:
                    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
                    self.app.db.create_account(email, hashed_password)
                    account = self.app.db.get_account_by_email(email)
                    self.app.login(account["id"])
                    self.dismiss()


    def dismiss(self, *args, **kwargs):
        if self.register_mode:
            self.toggle_mode()
        self.email_field.text = ""
        self.password_field.text = ""
        self.password_repetition_field.text = ""
        self.email_field.error = False
        self.password_field.error = False
        self.password_repetition_field.error = False
        super().dismiss()
