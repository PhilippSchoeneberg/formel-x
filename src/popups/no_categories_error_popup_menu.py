from kivy.app import App
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivy.uix.widget import Widget
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.boxlayout import MDBoxLayout
from ext.kivymd.uix.label import MDLabel


class NoCategoriesErrorPopupMenu(MDDialog):
    def __init__(self):
        self.app = App.get_running_app()
        self.action_function = None

        self.error_label = MDLabel(text=self.app.language_manager.translate("no_categories_error"))

        content_box = MDBoxLayout(
            self.error_label,
            orientation="vertical",
            spacing="30dp",
            adaptive_height=True,
            size_hint_y=None,
        )

        self.headline_text = MDDialogHeadlineText(text=self.app.language_manager.translate("sorry"))
        self.okay_button_text = MDButtonText(text=self.app.language_manager.translate("okay"))

        super().__init__(
            self.headline_text,
            MDDialogContentContainer(content_box),
            MDDialogButtonContainer(
                Widget(),
                MDButton(self.okay_button_text, style="text", on_release=self.dismiss),
                spacing="8dp",
            ),
        )


    def open(self, action_function=None):
        self.action_function = action_function
        super().open()


    def dismiss(self, *args, **kwargs):
        self.action_function()
        super().dismiss()
