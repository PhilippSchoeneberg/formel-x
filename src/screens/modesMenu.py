from src.utils.json_parser import save_state

from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import MDListItem, MDListItemHeadlineText


class ModesMenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.group_dropdown_menu = None


    def fill_modes_list(self):
        self.app = App.get_running_app()
        self.app.root.get_screen("modesMenu").ids.mode_list.clear_widgets()
        self.app.root.get_screen("modesMenu").ids.mode_list.add_widget(
            MDListItem(
                MDListItemHeadlineText(text="Elements"),
                on_release=lambda _: self.app.change_screen("elementMenu")
            )
        )
        self.app.root.get_screen("modesMenu").ids.mode_list.add_widget(
            MDListItem(
                MDListItemHeadlineText(text="Compounds"),
                on_release=lambda _: self.app.change_screen("compoundMenu")
            )
        )
        self.app.root.get_screen("modesMenu").ids.mode_list.add_widget(
            MDListItem(
                MDListItemHeadlineText(text="Questions"),
                on_release=lambda _: self.app.questionLearningScreen.start_learning()
            )
        )


    def group_menu_open(self):
        group_menu_items = []
        for group in self.app.groups:
            group_menu_items.append({"text": group["name"],
                                     "on_release": lambda x=group: self.set_group(x)})
        self.group_dropdown_menu = MDDropdownMenu(
            caller=self.app.root.get_screen(self.app.root.current).ids.choose_group_button,
            items=group_menu_items
        )
        self.group_dropdown_menu.open()


    def set_group(self, group):
        self.app.loggedInGroup = group
        self.app.state["loggedInGroup"] = self.app.loggedInGroup
        save_state(self.app.state)
        self.app.root.get_screen("modesMenu").ids.group_name.text = group["name"]
        if self.group_dropdown_menu:
            self.group_dropdown_menu.dismiss()
