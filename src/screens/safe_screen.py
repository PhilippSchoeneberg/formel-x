from kivy.metrics import dp
from kivy.core.window import Window
from kivymd.uix.screen import MDScreen

class SafeScreen(MDScreen):
    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)

        Window.softinput_mode = "below_target"
        Window.borderless = False

        if hasattr(self, "ids") and "main_box" in self.ids:
            self.ids.main_box.padding = [
                0,
                dp(Window.top),
                0,
                dp(Window.bottom),
            ]
