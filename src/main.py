from kivymd.app import MDApp
import sqlite3


class MainApp(MDApp):
    connection = None
    cursor = None

    def on_start(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = 'Darkblue'

        # Connect to database
        self.connection = sqlite3.connect("formulaX.db")
        self.cursor = self.connection.cursor()

    def change_theme(self):
        self.theme_cls.primary_palette = (
            "Lightblue" if self.theme_cls.primary_palette == "Darkblue" else "Darkblue"
        )
        self.theme_cls.theme_style = (
            "Light" if self.theme_cls.theme_style == "Dark" else "Dark"
        )
        self.root.ids.theme_mode.icon = (
            "weather-night" if self.root.ids.theme_mode.icon == "weather-sunny" else "weather-sunny"
        )

MainApp().run()
