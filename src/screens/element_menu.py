from src.popups.error_popup_menu import ErrorPopupMenu

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivymd.uix.screen import MDScreen
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.list import MDListItem, MDListItemHeadlineText


class ElementMenuScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.buttons = None
        self.headline = None
        self.elements = None
        self.element_symbols = None


    def refresh(self, *args):
        if not self.buttons:
            self.fill_periodic_table()
        self.set_learning_mode(self.app.learning_mode)


    def fill_periodic_table(self, *args):
        self.buttons = []
        self.elements = self.app.db.get_all_elements_by_group(self.app.logged_in_group)
        self.element_symbols = [element["symbol"] for element in self.elements.values()]

        self.ids.element_learning_list.clear_widgets()

        self.headline = MDListItemHeadlineText(text=self.app.language_manager.translate("element_remembering_mode_list_text"),
                                               max_lines=2)
        self.headline.shorten = False
        self.headline.ellipsize = False
        title_item = MDListItem(self.headline)
        title_item.ripple_effect = False
        title_item.focus_behavior = False
        self.ids.element_learning_list.add_widget(title_item)

        self.ids.periodic_table.clear_widgets()

        layout = MDGridLayout(
            cols = 18,
            size_hint = (None, None),
            spacing = 5,
            padding = 10,
        )
        layout.bind(minimum_height=layout.setter("height"))
        layout.bind(minimum_width=layout.setter("width"))

        layout.width = Window.width

        element_grid = [[None for _ in range(18)] for _ in range(10)]

        for element in self.app.db.get_all_elements().values():
            symbol = element["symbol"]
            group = element["system_group"] - 1
            period = element["system_period"] - 1

            btn = MDButton(
                style = "elevated",
                on_release = lambda x, el=element: self.element_clicked(x, el),
            )
            text = MDButtonText(text="")
            btn.add_widget(text)
            text.text = symbol
            text.theme_text_color = "Custom"
            btn.theme_bg_color = "Custom"

            self.buttons.append({"button": btn, "text": text})

            element_grid[period][group] = btn

        for row in element_grid:
            for col in row:
                widget = col if col else Widget(size_hint=(1, None), height="48dp")
                layout.add_widget(widget)

        self.ids.periodic_table.add_widget(layout)


    def element_clicked(self, item, element):
        if self.app.learning_mode:
            if element["symbol"] == self.current_element["symbol"]:
                item.theme_bg_color = "Custom"
                item.md_bg_color = [0, 1, 0, 0.3]
                Clock.schedule_once(lambda dt: self.next_element(), 1)
            else:
                item.theme_bg_color = "Custom"
                item.md_bg_color = [1, 0, 0, 0.3]
        elif self.app.logged_in_user_id:
            if element["symbol"] not in self.element_symbols:
                self.app.db.link_element_to_group(element, self.app.logged_in_group)
                self.element_symbols.append(element["symbol"])
                item.md_bg_color = [0, 1, 0, 0.3]
            else:
                self.app.db.unlink_element_to_group(element, self.app.logged_in_group)
                self.element_symbols.remove(element["symbol"])
                item.md_bg_color = [0.10588235294117647, 0.10588235294117647, 0.12941176470588237, 1.0]


    def refresh_buttons(self):
        self.elements = self.app.db.get_all_elements_by_group(self.app.logged_in_group)
        self.element_symbols = [element["symbol"] for element in self.elements.values()]
        for button in self.buttons:
            if not self.app.learning_mode:
                button["text"].text_color = [0.7490196078431373, 0.7607843137254902, 1.0, 1.0]
                if self.app.logged_in_user_id:
                    button["button"].md_bg_color = (
                        [0.10588235294117647, 0.10588235294117647, 0.12941176470588237, 1.0] if button["text"].text not in self.element_symbols else [0, 1, 0, 0.3]
                    )
                else:
                    button["button"].md_bg_color = [0.10588235294117647, 0.10588235294117647, 0.12941176470588237, 1.0]
            else:
                button["text"].text_color = [0.7490196078431373, 0.7607843137254902, 1.0, 0]
                button["button"].md_bg_color = [0.10588235294117647, 0.10588235294117647, 0.12941176470588237, 1.0]


    def set_learning_mode(self, learning_mode):
        self.app.learning_mode = learning_mode
        if self.app.learning_mode:
            self.ids.learning_mode_title.text = self.app.language_manager.translate("learning_mode")
            self.start_learning()
        else:
            self.ids.learning_mode_title.text = self.app.language_manager.translate("remembering_mode")
            if self.app.logged_in_user_id:
                self.headline.text = self.app.language_manager.translate("add_element_to_learning_mode_hint")
            else:
                self.headline.text = self.app.language_manager.translate("element_remembering_mode_list_text")
            self.refresh_buttons()


    def start_learning(self):
        self.elements_to_learn = [element for element in self.app.db.get_all_elements_by_group(self.app.logged_in_group).values()]
        if self.elements_to_learn:
            self.current_index = 0
            self.show_next_element()
        else:
            ErrorPopupMenu().open(self.app.language_manager.translate("no_elements_yet_error"))


    def show_next_element(self):
        self.refresh_buttons()
        if self.current_index >= len(self.elements_to_learn):
            self.set_learning_mode(not self.app.learning_mode)
            return
        self.current_element = self.elements_to_learn[self.current_index]
        self.headline.text = self.app.language_manager.translate("element_learning_mode_list_text") + self.current_element['name']


    def next_element(self):
        self.current_index += 1
        self.show_next_element()
