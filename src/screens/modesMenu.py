from src.utils.json_parser import save_state
from src.popups.confirmDeletePopUpMenu import ConfirmDeletePopUpMenu

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

        if self.app.loggedInGroup:
            title_item = MDListItem(
                MDListItemHeadlineText(text="Select Mode"))
            title_item.ripple_effect = False
            title_item.focus_behavior = False
            self.app.root.get_screen("modesMenu").ids.mode_list.add_widget(title_item)
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
        self.refresh_groups()


    def remove_group(self, group):
        if group:
            self.app.groups.remove(group)
            self.app.state["groups"] = self.app.groups
            save_state(self.app.state)
            self.refresh_groups()


    def edit_group(self):
        if self.app.loggedInGroup:
            self.app.create_or_edit_group_popup_menu.open(self.app.loggedInGroup)


    def delete_group(self):
        if self.app.loggedInGroup:
            confirm_delete_popup = ConfirmDeletePopUpMenu("Group", self.app.loggedInGroup["name"], lambda: self.app.db.delete_group(self.app.loggedInGroup), self.refresh_groups)
            confirm_delete_popup.open()


    def refresh_groups(self):
        if self.app.loggedInUserId:
            self.app.groups = self.app.db.get_all_groups_by_owner_id(self.app.loggedInUserId)
        else:
            self.app.groups = self.app.state["groups"]
            for group in self.app.groups:
                self.app.db.cursor.execute("SELECT * FROM groups WHERE id = ?", (group["id"],))
                result = self.app.db.cursor.fetchone()
                if not result:
                    self.remove_group(group)
        if self.app.loggedInGroup not in self.app.groups:
            self.app.loggedInGroup = None
            self.app.root.get_screen("modesMenu").ids.group_name.text = "Select Group"
        self.app.groups = sorted(self.app.groups, key=lambda x: x["name"])
        self.fill_modes_list()
