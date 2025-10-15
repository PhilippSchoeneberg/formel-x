from src.screens.safe_screen import SafeScreen
from src.utils.enums import CategoryTypes, DifficultyTypes
from src.popups.delete_category_popup_menu import DeleteCategoryPopupMenu
from src.popups.create_or_edit_category_popup_menu import CreateOrEditCategoryPopupMenu

from kivy.app import App
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.list import MDListItem, MDListItemHeadlineText


class CompoundMenuScreen(SafeScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.difficulty_dropdown_menu = None
        self.create_dropdown_menu = None
        self.select_difficulty = None
        self.helper_ui = None


    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.refresh()


    def refresh(self, *args):
        self.ids.query_mode_title.text = self.app.language_manager.translate("formula_to_name")
        self.fill_category_list()


    def fill_category_list(self):
        self.ids.compound_category_list.clear_widgets()
        if self.helper_ui:
            self.remove_widget(self.helper_ui)

        compound_categories = self.app.db.get_all_categories_by_type_and_group(CategoryTypes.compound, self.app.logged_in_group)
        compound_categories = sorted(compound_categories, key=lambda x: x["name"])

        if compound_categories:
            title_item = MDListItem(
                MDListItemHeadlineText(text=self.app.language_manager.translate("select") + self.app.language_manager.translate("category") + ":"))
            title_item.ripple_effect = False
            title_item.focus_behavior = False
            self.ids.compound_category_list.add_widget(title_item)

            if len(compound_categories) >= 2:
                button_text = MDButtonText(
                    text=self.app.language_manager.translate("select") + self.app.language_manager.translate(
                        "difficulty"))
                button = MDButton(
                    button_text,
                    on_release=lambda x, btn_txt=button_text: self.difficulty_menu_open(x, btn_txt)
                )
                list_item = MDListItem(
                        MDListItemHeadlineText(text=self.app.language_manager.translate("all")),
                        on_release=lambda _, cat_id=None: self.select_category(cat_id)
                    )
                list_item.add_widget(button)
                self.ids.compound_category_list.add_widget(list_item)

            for compound_category in compound_categories:
                button_text = MDButtonText(text=self.app.language_manager.translate("select") + self.app.language_manager.translate("difficulty"))
                button = MDButton(
                    button_text,
                    on_release=lambda x, btn_txt=button_text: self.difficulty_menu_open(x, btn_txt)
                )
                list_item = MDListItem(
                    MDListItemHeadlineText(text=compound_category["name"]),
                    on_release=lambda _, cat_id=compound_category["id"]: self.select_category(cat_id)
                )
                list_item.add_widget(button)
                self.ids.compound_category_list.add_widget(list_item)
        else:
            if self.app.logged_in_user_id:
                self.helper_ui = MDButton(
                    MDButtonText(text=self.app.language_manager.translate("create") + self.app.language_manager.translate("category")),
                    size_hint=(None, None),
                    size=("150dp", "48dp"),
                    pos_hint={"center_x": 0.5, "center_y": 0.5},
                    on_release=lambda _, cat_id=None: CreateOrEditCategoryPopupMenu().open(CategoryTypes.compound, False)
                )
                self.add_widget(self.helper_ui)
            else:
                self.helper_ui = MDLabel(
                    text=self.app.language_manager.translate("no_categories_yet_error"),
                    size_hint=(None, None),
                    size=("250", "48"),
                    pos_hint={"center_x": 0.5, "center_y": 0.5},
                    halign="center",
                    valign="middle"
                )
                self.add_widget(self.helper_ui)


    def difficulty_menu_open(self, button, button_text):
        difficulty_menu_items = []
        for difficulty in DifficultyTypes:
            difficulty_menu_items.append({"text": self.app.language_manager.translate(difficulty.value),
                                          "on_release": lambda x=difficulty: self.set_difficulty(button_text, x)})
        self.difficulty_dropdown_menu = MDDropdownMenu(
            caller=button,
            items=difficulty_menu_items
        )
        self.difficulty_dropdown_menu.open()


    def set_difficulty(self, button_text, difficulty):
        self.select_difficulty = difficulty
        button_text.text = self.app.language_manager.translate(self.select_difficulty.value)


    def select_category(self, category_id):
        self.app.compound_learning_screen.start_learning(category_id, self.select_difficulty)


    def create(self, original_caller):
        add_menu_items = [
            {
                "text": self.app.language_manager.translate("add_category"),
                "on_release": lambda: CreateOrEditCategoryPopupMenu().open(CategoryTypes.compound, False),
            },
            {
                "text": self.app.language_manager.translate("add_compound"),
                "on_release": lambda: self.app.root.get_screen("compoundLearning").create(),
            },
        ]
        self.create_dropdown_menu = MDDropdownMenu(
            caller=original_caller,
            items=add_menu_items
        )
        if self.app.general_dropdown_menu:
            self.app.general_dropdown_menu.dismiss()
        self.create_dropdown_menu.open()


    def edit(self):
        CreateOrEditCategoryPopupMenu().open(CategoryTypes.compound, True)


    def delete(self):
        DeleteCategoryPopupMenu().open(CategoryTypes.compound)


    def switch_query_mode(self):
        self.app.formula_to_name_query_mode = not self.app.formula_to_name_query_mode
        self.ids.query_mode_title.text = (
            self.app.language_manager.translate("formula_to_name") if self.app.formula_to_name_query_mode else self.app.language_manager.translate("name_to_formula")
        )
