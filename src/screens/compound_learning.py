from kivy.app import App
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivymd.uix.list import MDListItem, MDListItemHeadlineText


class CompoundLearningScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.compounds_to_learn = None
        self.current_index = None
        self.current_compound = None


    def start_learning(self, category):
        self.app = App.get_running_app()
        self.app.change_screen("compoundLearning")

        self.compounds_to_learn = [
            compound for compound in self.app.db.get_all_compounds_by_group(self.app.logged_in_group).values()
            if compound["category"] == category
        ]

        self.current_index = 0
        self.show_next_compound()
        self.app.change_screen("compoundLearning")


    def show_next_compound(self):
        self.app.root.get_screen("compoundLearning").ids.compound_learning_list.clear_widgets()

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
            self.app.root.get_screen("compoundLearning").ids.compound_learning_list.add_widget(list_item)

        title_item = MDListItem(
            MDListItemHeadlineText(text=f"Which is the correct formula for {self.current_compound['correct_name']}"))
        title_item.ripple_effect = False
        title_item.focus_behavior = False
        self.app.root.get_screen("compoundLearning").ids.compound_learning_list.add_widget(title_item)

        add_option(self.current_compound["correct_formula"], True)
        add_option(self.current_compound["wrong_formula1"], False)
        add_option(self.current_compound["wrong_formula2"], False)


    def next_compound(self):
        self.current_index += 1
        self.show_next_compound()


    def edit_compound(self):
        self.app.create_or_edit_compound_popup_menu.open(self.current_compound, self.next_compound)


    def delete_compound(self):
        self.app.confirm_delete_popup_menu.open("Compound", self.current_compound["correct_name"], lambda: self.app.db.delete_compound(self.current_compound), self.next_compound)
