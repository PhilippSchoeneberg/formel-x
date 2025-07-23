from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import MDListItem, MDListItemHeadlineText


class CompoundMenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.group_dropdown_menu = None


    def on_pre_enter(self):
        self.fill_category_list()


    def fill_category_list(self):
        self.app = App.get_running_app()
        self.app.root.get_screen("compoundMenu").ids.category_list.clear_widgets()
        categories = self.app.db.get_all_categories_by_group(self.app.loggedInGroup)

        title_item = MDListItem(
            MDListItemHeadlineText(text="Select Category"))
        title_item.ripple_effect = False
        title_item.focus_behavior = False
        self.app.root.get_screen("compoundMenu").ids.category_list.add_widget(title_item)

        for category_id, category in categories.items():
            self.app.root.get_screen("compoundMenu").ids.category_list.add_widget(
                MDListItem(
                    MDListItemHeadlineText(text=category["name"]),
                    on_release=lambda _, cat_id=category_id: self.app.compoundLearningScreen.start_learning(cat_id)
                )
            )


    def create_compound_menu_open(self):
        self.app = App.get_running_app()
        add_menu_items = [
            {
                "text": "Add Formula",
                "on_release": lambda: self.app.create_compound_popup_menu.open(),
            },
            {
                "text": "Add Category",
                "on_release": lambda: self.app.create_category_popup_menu.open(),
            }
        ]
        MDDropdownMenu(
            caller=self.app.root.get_screen(self.app.root.current).ids.create_compound_button,
            items=add_menu_items
        ).open()
