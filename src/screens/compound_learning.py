from src.popups.create_or_edit_compound_popup_menu import CreateOrEditCompoundPopupMenu
from src.popups.confirm_delete_popup_menu import ConfirmDeletePopupMenu
from src.popups.error_popup_menu import ErrorPopupMenu

from kivy.app import App
from kivy.clock import Clock
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import MDListItem, MDListItemHeadlineText


class CompoundLearningScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.compounds_to_learn = []
        self.current_index = 0
        self.current_compound = None


    def refresh(self):
        if self.app.root.current == self.name:
            self.show_next_compound()


    def start_learning(self, category=None, difficulty=None):
        self.current_index = 0
        self.compounds_to_learn = self.app.db.get_all_compounds_by_group(self.app.logged_in_group)
        if category:
            self.compounds_to_learn = [
                compound for compound in self.compounds_to_learn
                if compound["category_id"] == category
            ]
        if difficulty:
            self.compounds_to_learn = [
                compound for compound in self.compounds_to_learn
                if compound["difficulty"] == difficulty.value
            ]
        if not self.compounds_to_learn:
            ErrorPopupMenu().open(self.app.language_manager.translate("no_entries_yet_error"), lambda: self.app.change_screen("compoundMenu"))
        else:
            self.app.change_screen("compoundLearning")
            self.show_next_compound()


    def show_next_compound(self):
        self.ids.compound_learning_list.clear_widgets()

        if self.current_index >= len(self.compounds_to_learn):
            self.app.change_screen("compoundMenu")
            return

        self.current_compound = self.compounds_to_learn[self.current_index]

        def on_clicked(item, correct):
            if correct:
                item.theme_bg_color = "Custom"
                item.md_bg_color = [0, 1, 0, 0.3]
                Clock.schedule_once(lambda dt: self.next_compound(), 1)
            else:
                item.theme_bg_color = "Custom"
                item.md_bg_color = [1, 0, 0, 0.3]

        def add_option(text, correct):
            list_item = MDListItem(
                MDListItemHeadlineText(text=text),
                on_release=lambda item: on_clicked(list_item, correct)
            )
            self.ids.compound_learning_list.add_widget(list_item)

        if self.app.formula_to_name_query_mode:
            headline = MDListItemHeadlineText(text=self.app.language_manager.translate("compound_learning_mode_list_formula_text") + self.current_compound['correct_name'])
            headline.font_name = "RobotoDownloaded"
            title_item = MDListItem(headline)
            title_item.ripple_effect = False
            title_item.focus_behavior = False
            self.ids.compound_learning_list.add_widget(title_item)

            add_option(self.current_compound["correct_formula"], True)
            add_option(self.current_compound["wrong_formula1"], False)
            add_option(self.current_compound["wrong_formula2"], False)
            if self.current_compound["wrong_formula3"]:
                add_option(self.current_compound["wrong_formula3"], False)
            if self.current_compound["wrong_formula4"]:
                add_option(self.current_compound["wrong_formula4"], False)
        else:
            headline = MDListItemHeadlineText(text=self.app.language_manager.translate("compound_learning_mode_list_name_text") + self.current_compound['correct_formula'])
            headline.font_name = "RobotoDownloaded"
            title_item = MDListItem(headline)
            title_item.ripple_effect = False
            title_item.focus_behavior = False
            self.ids.compound_learning_list.add_widget(title_item)

            add_option(self.current_compound["correct_name"], True)
            add_option(self.current_compound["wrong_name1"], False)
            add_option(self.current_compound["wrong_name2"], False)
            if self.current_compound["wrong_name3"]:
                add_option(self.current_compound["wrong_name3"], False)
            if self.current_compound["wrong_name4"]:
                add_option(self.current_compound["wrong_name4"], False)


    def next_compound(self):
        self.current_index += 1
        self.show_next_compound()


    def create(self, *args):
        if self.app.root.get_screen("compoundMenu").create_dropdown_menu:
            self.app.root.get_screen("compoundMenu").create_dropdown_menu.dismiss()
        CreateOrEditCompoundPopupMenu().open()


    def edit(self):
        CreateOrEditCompoundPopupMenu().open(self.current_compound, self.next_compound)


    def delete(self):
        ConfirmDeletePopupMenu().open(self.app.language_manager.translate("compound"), self.current_compound["correct_name"], lambda: self.app.db.delete_compound(self.current_compound), self.next_compound)
