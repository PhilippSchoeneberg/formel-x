from src.utils.json_parser import save_state

from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import MDListItem, MDListItemHeadlineText


class ModesMenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.group_dropdown_menu = None


    def refresh(self):
        self.refresh_groups()


    def fill_modes_list(self):
        self.ids.mode_list.clear_widgets()

        if self.app.logged_in_group:
            title_item = MDListItem(
                MDListItemHeadlineText(text=self.app.language_manager.translate("select") + self.app.language_manager.translate("mode")))
            title_item.ripple_effect = False
            title_item.focus_behavior = False
            self.ids.mode_list.add_widget(title_item)
            self.ids.mode_list.add_widget(
                MDListItem(
                    MDListItemHeadlineText(text=self.app.language_manager.translate("elements")),
                    on_release=lambda _: self.app.change_screen("elementMenu")
                )
            )
            self.ids.mode_list.add_widget(
                MDListItem(
                    MDListItemHeadlineText(text=self.app.language_manager.translate("compounds")),
                    on_release=lambda _: self.app.change_screen("compoundMenu")
                )
            )
            self.ids.mode_list.add_widget(
                MDListItem(
                    MDListItemHeadlineText(text=self.app.language_manager.translate("questions")),
                    on_release=lambda _: self.app.change_screen("questionLearning")
                )
            )


    def group_menu_open(self):
        group_menu_items = []
        for group in self.app.groups:
            group_menu_items.append({"text": group["name"],
                                     "on_release": lambda x=group: self.set_group(x)})
        self.group_dropdown_menu = MDDropdownMenu(
            caller=self.ids.select_group_button,
            items=group_menu_items
        )
        self.group_dropdown_menu.open()


    def set_group(self, group):
        self.app.logged_in_group = group
        self.app.state["logged_in_group"] = self.app.logged_in_group
        save_state(self.app.state)
        self.ids.group_name.text = group["name"]
        if self.group_dropdown_menu:
            self.group_dropdown_menu.dismiss()
        self.refresh_groups()


    def remove(self, group):
        if group:
            self.app.groups.remove(group)
            self.app.state["groups"] = self.app.groups
            save_state(self.app.state)
            self.refresh_groups()


    def create(self):
        self.app.create_or_edit_group_popup_menu.open()


    def edit(self):
        if self.app.logged_in_group:
            self.app.create_or_edit_group_popup_menu.open(self.app.logged_in_group)


    def delete(self):
        if self.app.logged_in_group:
            self.app.confirm_delete_popup_menu.open("Group", self.app.logged_in_group["name"], lambda: self.app.db.delete_group(self.app.logged_in_group), self.refresh_groups)


    def refresh_groups(self):
        self.app = App.get_running_app()
        if self.app.logged_in_user_id:
            self.app.groups = self.app.db.get_all_groups_by_owner_id(self.app.logged_in_user_id)
        else:
            self.app.groups = self.app.state["groups"]
            for group in self.app.groups:
                self.app.db.cursor.execute("SELECT * FROM groups WHERE id = ?", (group["id"],))
                result = self.app.db.cursor.fetchone()
                if not result:
                    self.remove_group(group)
        if self.app.logged_in_group not in self.app.groups:
            self.app.logged_in_group = None
            self.ids.group_name.text = self.app.language_manager.translate("select") + self.app.language_manager.translate("group")
        self.app.groups = sorted(self.app.groups, key=lambda x: x["name"])
        self.fill_modes_list()
