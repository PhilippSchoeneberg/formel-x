from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import MDListItem, MDListItemHeadlineText


class CompoundMenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.group_dropdown_menu = None


    def refresh(self, *args):
        self.app = App.get_running_app()
        self.ids.query_mode_title.text = self.app.language_manager.translate("formula_to_name")
        self.fill_category_list()


    def fill_category_list(self):
        self.app = App.get_running_app()
        self.ids.category_list.clear_widgets()
        categories = self.app.db.get_all_categories_by_group(self.app.logged_in_group)

        title_item = MDListItem(
            MDListItemHeadlineText(text=self.app.language_manager.translate("select") + self.app.language_manager.translate("category")))
        title_item.ripple_effect = False
        title_item.focus_behavior = False
        self.ids.category_list.add_widget(title_item)

        for category_id, category in categories.items():
            self.ids.category_list.add_widget(
                MDListItem(
                    MDListItemHeadlineText(text=category["name"]),
                    on_release=lambda _, cat_id=category_id: self.app.compound_learning_screen.start_learning(cat_id)
                )
            )

        if categories:
            self.ids.category_list.add_widget(
                MDListItem(
                    MDListItemHeadlineText(text=self.app.language_manager.translate("all")),
                    on_release=lambda _, cat_id=None: self.app.compound_learning_screen.start_learning(cat_id)
                )
            )


    def create_or_edit_category_or_compound_menu_open(self):
        self.app = App.get_running_app()
        add_menu_items = [
            {
                "text": self.app.language_manager.translate("add_formula"),
                "on_release": lambda: self.app.create_or_edit_compound_popup_menu.open(),
            },
            {
                "text": self.app.language_manager.translate("add_category"),
                "on_release": lambda: self.app.create_or_edit_category_popup_menu.open(),
            }
        ]
        MDDropdownMenu(
            caller=self.app.root.get_screen(self.app.root.current).ids.create_category_or_compound_button,
            items=add_menu_items
        ).open()


    def create(self):
        self.app.create_or_edit_category_popup_menu.open(False)


    def edit(self):
        self.app.create_or_edit_category_popup_menu.open(True)


    def delete(self):
        self.app.delete_category_popup_menu.open()


    def switch_query_mode(self):
        self.app = App.get_running_app()
        self.app.formula_to_name_query_mode = not self.app.formula_to_name_query_mode
        self.ids.query_mode_title.text = (
            self.app.language_manager.translate("formula_to_name") if self.app.formula_to_name_query_mode else self.app.language_manager.translate("name_to_formula")
        )
