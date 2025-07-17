from kivy.clock import Clock
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivymd.uix.list import MDListItem, MDListItemHeadlineText

class CompoundLearningScreen(Screen):
    app = None
    compounds_to_learn = None
    current_index = None

    def start_learning(self, category):
        self.app = App.get_running_app()
        self.app.change_screen("compoundLearning")

        self.compounds_to_learn = [
            compound for compound in self.app.get_all_compounds().values()
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

        current_compound = self.compounds_to_learn[self.current_index]

        def on_clicked(list_item, correct):
            if correct:
                list_item.theme_bg_color = "Custom"
                list_item.md_bg_color = [0, 1, 0, 0.3]
                Clock.schedule_once(lambda dt: self.next_compound(), 1)
            else:
                list_item.theme_bg_color = "Custom"
                list_item.md_bg_color = [1, 0, 0, 0.3]

        def add_option(text, correct):
            item = MDListItem(
                MDListItemHeadlineText(text=text),
                on_release=lambda list_item: on_clicked(item, correct)
            )
            self.app.root.get_screen("compoundLearning").ids.compound_learning_list.add_widget(item)

        item = MDListItem(
            MDListItemHeadlineText(text=f"Which is the correct formula for {current_compound['correct_name']}"))
        item.ripple_effect = False
        item.focus_behavior = False
        self.app.root.get_screen("compoundLearning").ids.compound_learning_list.add_widget(item)

        add_option(current_compound["correct_formula"], True)
        add_option(current_compound["wrong_formula1"], False)
        add_option(current_compound["wrong_formula2"], False)

    def next_compound(self):
        self.current_index += 1
        self.show_next_compound()
