from kivy.metrics import dp
from kivy.core.window import Window
from kivy.utils import platform
from kivymd.uix.screen import MDScreen

if platform == "android":
    from jnius import autoclass

class SafeScreen(MDScreen):
    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        Window.softinput_mode = "resize"
        Window.borderless = False
        Window.bind(on_resize=self.update_safe_padding)
        self.update_safe_padding()

    def update_safe_padding(self, *args):
        top_padding = dp(0)
        bottom_padding = dp(0)

        if hasattr(self, "ids") and "main_box" in self.ids:
            if platform == "android":
                PythonActivity = autoclass("org.kivy.android.PythonActivity")
                activity = PythonActivity.mActivity
                res = activity.getResources()

                status_bar_id = res.getIdentifier("status_bar_height", "dimen", "android")
                if status_bar_id > 0:
                    top_padding = res.getDimensionPixelSize(status_bar_id) / Window._density

                nav_bar_id = res.getIdentifier("navigation_bar_height", "dimen", "android")
                if nav_bar_id > 0:
                    bottom_padding = res.getDimensionPixelSize(nav_bar_id) / Window._density

                # Keyboard adjustment
                if Window.height < Window.system_size[1]:
                    bottom_padding = dp(0)

            elif platform == "ios":
                top_padding = dp(44)
                bottom_padding = dp(34)
                if Window.height < Window.system_size[1]:
                    bottom_padding = dp(0)

            self.ids.main_box.padding = [0, top_padding, 0, bottom_padding]
