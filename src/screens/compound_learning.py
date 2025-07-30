from kivy.app import App
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivymd.uix.list import MDListItem, MDListItemHeadlineText


class CompoundLearningScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.compounds_to_learn = []
        self.current_index = 0
        self.current_compound = None


    def refresh(self):
        self.show_next_compound()


    def start_learning(self, category=None):
        self.app.change_screen("compoundLearning")
        self.current_index = 0
        if category:
            self.compounds_to_learn = [
                compound for compound in self.app.db.get_all_compounds_by_group(self.app.logged_in_group).values()
                if compound["category"] == category
            ]
        else:
            self.compounds_to_learn = [
                compound for compound in self.app.db.get_all_compounds_by_group(self.app.logged_in_group).values()
            ]
        self.refresh()


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
            headline = MDListItemHeadlineText(text=text)
            headline.font_name = "RobotoDownloaded"
            list_item = MDListItem(
                headline,
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


    def create(self):
        self.app.create_or_edit_compound_popup_menu.open()


    def edit(self):
        self.app.create_or_edit_compound_popup_menu.open(self.current_compound, self.next_compound)


    def delete(self):
        self.app.confirm_delete_popup_menu.open(self.app.language_manager.translate("compound"), self.current_compound["correct_name"], lambda: self.app.db.delete_compound(self.current_compound), self.next_compound)
