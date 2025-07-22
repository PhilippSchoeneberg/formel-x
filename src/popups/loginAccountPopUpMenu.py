import datetime
import bcrypt
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivy.app import App
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText, MDTextFieldHelperText
from kivymd.uix.boxlayout import MDBoxLayout


class LoginAccountPopUpMenu(MDDialog):
    def __init__(self):
        self.register_mode = False

        self.email_helper_text = MDTextFieldHelperText(text="E-Mail Address can't be empty", mode="on_error")

        self.email_field = MDTextField(
            MDTextFieldHintText(text="E-Mail Address"),
            self.email_helper_text,
            mode="outlined",
            size_hint_x=1,
            pos_hint={"center_x": 0.5},
        )

        self.password_helper_text = MDTextFieldHelperText(text="Password can't be empty", mode="on_error")

        self.password_field = MDTextField(
            MDTextFieldHintText(text="Password"),
            self.password_helper_text,
            mode="outlined",
            size_hint_x=1,
            pos_hint={"center_x": 0.5},
            password=True,
        )

        self.password_repetition_helper_text = MDTextFieldHelperText(text="Password repetition can't be empty", mode="on_error")

        self.password_repetition_field = MDTextField(
            MDTextFieldHintText(text="Password repetition"),
            self.password_repetition_helper_text,
            mode="outlined",
            size_hint_x=1,
            pos_hint={"center_x": 0.5},
            password=True,
        )

        self.toggle_button = MDButton(
            MDButtonText(text="Go to Registration"),
            style="text",
            on_release=self.toggle_mode,
        )

        self.submit_button = MDButton(MDButtonText(text="Login"),
            style="text",
            on_release=self.login,
        )

        self.headline = MDDialogHeadlineText(text="Login", halign="center")

        self.content_box = MDBoxLayout(
            self.email_field,
            self.password_field,
            orientation="vertical",
            spacing="30dp",
            adaptive_height=True,
            size_hint_y=None,
        )

        super().__init__(
            self.headline,
            MDDialogContentContainer(self.content_box),
            MDDialogButtonContainer(
                MDButton(MDButtonText(text="Cancel"), style="text", on_release=self.dismiss),
                self.submit_button,
                self.toggle_button,
                spacing="8dp",
            ),
        )


    def toggle_mode(self, *args, **kwargs):
        if self.password_repetition_field.parent is None:
            self.register_mode = True
            self.content_box.add_widget(self.password_repetition_field)
            self.headline.text = "Register"
            self.submit_button.children[0].text = "Register"
            self.toggle_button.children[0].text = "Go to Login"
        else:
            self.register_mode = False
            self.content_box.remove_widget(self.password_repetition_field)
            self.headline.text = "Login"
            self.submit_button.children[0].text = "Login"
            self.toggle_button.children[0].text = "Go to Registration"


    def login(self, *args, **kwargs):
        app = App.get_running_app()
        email = self.email_field.text.strip()
        password = self.password_field.text.strip()

        valid = True
        if not email:
            self.email_helper_text.text = "E-Mail Address can't be empty"
            self.email_field.error = False
            self.email_field.error = True
            valid = False
        else:
            self.email_field.error = False
        if not password:
            self.password_helper_text.text = "Password can't be empty"
            self.password_field.error = False
            self.password_field.error = True
            valid = False
        else:
            self.password_field.error = False

        if not self.register_mode:
            if valid:
                app.db.cursor.execute("SELECT id, password FROM accounts WHERE email = ?", (email,))
                result = app.db.cursor.fetchone()
                if result and bcrypt.checkpw(password.encode("utf-8"), result[1].encode("utf-8")):
                    app.db.connection.commit()
                    app.login(result[0])
                    self.dismiss()
                else:
                    self.email_helper_text.text = "E-Mail Address or password is incorrect"
                    self.email_field.error = False
                    self.email_field.error = True
                    self.password_helper_text.text = "E-Mail Address or password is incorrect"
                    self.password_field.error = False
                    self.password_field.error = True
        else:
            password_repetition = self.password_repetition_field.text.strip()
            date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if not password_repetition:
                self.password_repetition_helper_text.text = "Password repetition can't be empty"
                self.password_repetition_field.error = False
                self.password_repetition_field.error = True
                valid = False
            elif password != password_repetition:
                self.password_helper_text.text = "Passwords do not match"
                self.password_field.error = False
                self.password_field.error = True
                self.password_repetition_helper_text.text = "Passwords do not match"
                self.password_repetition_helper_text.error = False
                self.password_repetition_helper_text.error = True
                valid = False
            else:
                self.password_repetition_field.error = False
            if valid:
                app.db.cursor.execute("SELECT * FROM accounts WHERE email = ?", (email,))
                result = app.db.cursor.fetchone()
                if result:
                    self.email_helper_text.text = "Account with this email already exists"
                    self.email_field.error = False
                    self.email_field.error = True
                else:
                    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
                    app.db.cursor.execute(
                        "INSERT INTO accounts (email, password, date) VALUES (?, ?, ?)",
                        (email, hashed_password, date)
                    )
                    self.toggle_mode()


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
