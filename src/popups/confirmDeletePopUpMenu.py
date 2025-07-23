from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogContentContainer, MDDialogButtonContainer
from kivy.uix.widget import Widget
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.boxlayout import MDBoxLayout
from ext.kivymd.uix.label import MDLabel


class ConfirmDeletePopUpMenu(MDDialog):
    def __init__(self, type_name, item_name, delete_function, action_function):
        self.delete_function = delete_function
        self.action_function = action_function
        self.question_label = MDLabel(
            text=f"Are you sure you want to delete \"" + item_name + "\"?",
        )
        content_box = MDBoxLayout(
            self.question_label,
            orientation="vertical",
            spacing="30dp",
            adaptive_height=True,
            size_hint_y=None,
        )

        super().__init__(
            MDDialogHeadlineText(text="Delete " + type_name + "?", halign="center"),
            MDDialogContentContainer(content_box),
            MDDialogButtonContainer(
                Widget(),
                MDButton(MDButtonText(text="Cancel"), style="text", on_release=self.dismiss),
                MDButton(MDButtonText(text="Delete"), style="text", on_release=self.do),
                spacing="8dp",
            ),
        )


    def do(self, *args, **kwargs):
        self.delete_function()
        self.action_function()
        self.dismiss()
