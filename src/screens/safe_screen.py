from kivy.metrics import dp
from kivy.utils import platform
from kivymd.uix.screen import MDScreen

# Only import plyer on mobile
if platform == "android":
    from jnius import autoclass


class SafeScreen(MDScreen):
    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)

        # Default desktop padding
        top_padding = dp(0)
        bottom_padding = dp(0)

        if platform == "android":
            # Get Android activity and window
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity
            window = activity.getWindow()

            # Get root view
            decorView = window.getDecorView()

            # Insets for status bar / nav bar
            insets = decorView.getRootWindowInsets()
            if insets:
                top_padding = dp(insets.getSystemWindowInsetTop())
                bottom_padding = dp(insets.getSystemWindowInsetBottom())

        # Apply padding if main_box exists
        if hasattr(self, "ids") and "main_box" in self.ids:
            self.ids.main_box.padding = [0, top_padding, 0, bottom_padding]
