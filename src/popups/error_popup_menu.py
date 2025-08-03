from kivy.app import App
from kivy.uix.widget import Widget
from ext.kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer


class ErrorPopupMenu(MDDialog):
    def __init__(self):
        self.app = App.get_running_app()
        self.action_function = None

        self.error_label = MDLabel(text="")

        self.headline_text = MDDialogHeadlineText(text=self.app.language_manager.translate("sorry"))
        self.okay_button_text = MDButtonText(text=self.app.language_manager.translate("okay"))

        super().__init__(
            self.headline_text,
            MDDialogContentContainer(self.error_label),
            MDDialogButtonContainer(
                Widget(),
                MDButton(self.okay_button_text, style="text", on_release=self.dismiss),
                spacing="8dp",
            ),
        )


    def open(self, error_label_text=None, action_function=None):
        self.action_function = action_function
        self.error_label.text = error_label_text
        super().open()


    def dismiss(self, *args, **kwargs):
        if self.action_function:
            self.action_function()
        super().dismiss()
