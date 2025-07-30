import os
import gettext


class LanguageManager:
    def __init__(self, default_language="en"):
        self.assets_path = "assets"
        self.current_language = default_language
        self.translation = None
        self._ = lambda x: x
        self.set_language(default_language)


    def set_language(self, lang_code):
        try:
            self.translation = gettext.translation(
                "texts", localedir=self.assets_path, languages=[lang_code]
            )
            self.translation.install()
            self._ = self.translation.gettext
        except FileNotFoundError:
            print(f"[i18n] Translation for '{lang_code}' not found. Falling back to default.")
            self._ = lambda x: x


    def translate(self, msgid):
        return self._(msgid)


    def get_available_languages(self):
        assets_path = "assets"
        return [name for name in os.listdir(assets_path)
                if os.path.isdir(os.path.join(assets_path, name))]
