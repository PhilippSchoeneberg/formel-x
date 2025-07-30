from src.utils.enums import CategoryTypes

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.button import MDIconButton
from kivymd.uix.list import MDListItem, MDListItemHeadlineText


class CompoundMenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()


    def refresh(self, *args):
        self.ids.query_mode_title.text = self.app.language_manager.translate("formula_to_name")
        self.fill_category_list()


    def fill_category_list(self):
        self.ids.compound_category_list.clear_widgets()
        compound_categories = self.app.db.get_all_categories_by_type_and_group(CategoryTypes.compound, self.app.logged_in_group)

        title_item = MDListItem(
            MDListItemHeadlineText(text=self.app.language_manager.translate("select") + self.app.language_manager.translate("category")))
        title_item.ripple_effect = False
        title_item.focus_behavior = False
        self.ids.compound_category_list.add_widget(title_item)

        for compound_category_id, compound_category in compound_categories.items():
            self.ids.compound_category_list.add_widget(
                MDListItem(
                    MDListItemHeadlineText(text=compound_category["name"]),
                    on_release=lambda _, cat_id=compound_category_id: self.app.compound_learning_screen.start_learning(cat_id)
                )
            )

        if len(compound_categories) >= 2:
            self.ids.compound_category_list.add_widget(
                MDListItem(
                    MDListItemHeadlineText(text=self.app.language_manager.translate("all")),
                    on_release=lambda _, cat_id=None: self.app.compound_learning_screen.start_learning(cat_id)
                )
            )


    def create(self):
        create_button = MDIconButton(
            opacity=0,
            size_hint=(None, None),
            size=("1dp", "1dp"),
        )

        screen = self.app.root.get_screen(self.app.root.current)
        screen.add_widget(create_button)

        mouse_x, mouse_y = Window.mouse_pos
        create_button.pos = (mouse_x, mouse_y - 40)

        add_menu_items = [
            {
                "text": self.app.language_manager.translate("add_category"),
                "on_release": lambda: self.app.create_or_edit_category_popup_menu.open(CategoryTypes.compound, False),
            },
            {
                "text": self.app.language_manager.translate("add_compound"),
                "on_release": lambda: self.app.root.get_screen("compoundLearning").create(),
            },
        ]
        MDDropdownMenu(
            caller=create_button,
            items=add_menu_items
        ).open()


    def edit(self):
        self.app.create_or_edit_category_popup_menu.open(CategoryTypes.compound, True)


    def delete(self):
        self.app.delete_category_popup_menu.open(CategoryTypes.compound)


    def switch_query_mode(self):
        self.app.formula_to_name_query_mode = not self.app.formula_to_name_query_mode
        self.ids.query_mode_title.text = (
            self.app.language_manager.translate("formula_to_name") if self.app.formula_to_name_query_mode else self.app.language_manager.translate("name_to_formula")
        )
