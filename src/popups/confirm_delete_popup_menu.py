from kivy.app import App
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivy.uix.widget import Widget
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.boxlayout import MDBoxLayout
from ext.kivymd.uix.label import MDLabel


class ConfirmDeletePopupMenu(MDDialog):
    def __init__(self):
        self.app = App.get_running_app()
        self.delete_function = None
        self.action_function = None

        self.question_label = MDLabel(text="",)

        content_box = MDBoxLayout(
            self.question_label,
            orientation="vertical",
            spacing="30dp",
            adaptive_height=True,
            size_hint_y=None,
        )

        self.headline_text = MDDialogHeadlineText(text="")
        self.cancel_button_text = MDButtonText(text=self.app.language_manager.translate("cancel"))
        self.submit_button_text = MDButtonText(text=self.app.language_manager.translate("submit"))

        super().__init__(
            self.headline_text,
            MDDialogContentContainer(content_box),
            MDDialogButtonContainer(
                Widget(),
                MDButton(self.cancel_button_text, style="text", on_release=self.dismiss),
                MDButton(self.submit_button_text, style="text", on_release=self.do),
                spacing="8dp",
            ),
        )


    def open(self, type_name=None, item_name=None, delete_function=None, action_function=None):
        self.app.general_dropdown_menu.dismiss()
        self.delete_function = delete_function
        self.action_function = action_function
        self.question_label.text = self.app.language_manager.translate("delete_text") + "\"" + item_name + "\"?"
        self.headline_text.text = self.app.language_manager.translate("delete") + type_name + "?"
        super().open()


    def do(self, *args, **kwargs):
        self.delete_function()
        self.action_function()
        self.dismiss()
