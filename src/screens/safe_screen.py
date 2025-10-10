from kivy.metrics import dp
from kivy.core.window import Window
from kivy.utils import platform
from kivymd.uix.screen import MDScreen

if platform == "android":
    from jnius import autoclass


class SafeScreen(MDScreen):
    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        Window.softinput_mode = "below_target"
        Window.borderless = False

        top_padding = dp(0)
        bottom_padding = dp(0)

        if hasattr(self, "ids") and "main_box" in self.ids:
            if platform == "android":
                # Get status bar height
                PythonActivity = autoclass("org.kivy.android.PythonActivity")
                Context = autoclass("android.content.Context")
                activity = PythonActivity.mActivity
                res_id = activity.getResources().getIdentifier("status_bar_height", "dimen", "android")
                if res_id > 0:
                    top_padding = activity.getResources().getDimensionPixelSize(res_id) / Window.density

                # Get navigation bar height
                res_id = activity.getResources().getIdentifier("navigation_bar_height", "dimen", "android")
                if res_id > 0:
                    bottom_padding = activity.getResources().getDimensionPixelSize(res_id) / Window.density

            elif platform == "ios":
                # iOS typical safe area offsets (approx)
                top_padding = dp(44)  # status bar + notch
                bottom_padding = dp(34)  # home indicator

            self.ids.main_box.padding = [0, top_padding, 0, bottom_padding]
