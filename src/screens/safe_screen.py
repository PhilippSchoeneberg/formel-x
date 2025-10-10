from kivy.metrics import dp
from kivy.core.window import Window
from kivy.utils import platform
from kivymd.uix.screen import MDScreen


class SafeScreen(MDScreen):
    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)

        # Ensure keyboard doesn't overlap widgets
        Window.softinput_mode = "below_target"
        Window.borderless = False

        if hasattr(self, "ids") and "main_box" in self.ids:
            # Add extra padding for Android/iOS to avoid status/nav bars
            if platform in ("android", "ios"):
                top_padding = dp(28)   # space for status bar
                bottom_padding = dp(24)  # space for gesture/nav bar
            else:
                top_padding = dp(0)
                bottom_padding = dp(0)

            self.ids.main_box.padding = [0, top_padding, 0, bottom_padding]
