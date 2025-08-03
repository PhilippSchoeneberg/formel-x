from src.utils.json_parser import save_state
from src.popups.add_group_popup_menu import AddGroupPopupMenu
from src.popups.confirm_delete_popup_menu import ConfirmDeletePopupMenu
from src.popups.create_or_edit_group_popup_menu import CreateOrEditGroupPopupMenu

from kivy.app import App
from kivymd.uix.screen import MDScreen
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.list import MDListItem, MDListItemHeadlineText


class ModesMenuScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.group_dropdown_menu = None
        self.help_button = None


    def refresh(self):
        self.refresh_groups()


    def fill_modes_list(self):
        self.ids.mode_list.clear_widgets()
        if self.help_button:
            self.remove_widget(self.help_button)

        if self.app.logged_in_group:
            title_item = MDListItem(
                MDListItemHeadlineText(text=self.app.language_manager.translate("select") + self.app.language_manager.translate("mode") + ":"))
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
                    on_release=lambda _: self.app.change_screen("questionMenu")
                )
            )
        elif not self.app.groups:
            if self.app.logged_in_user_id:
                self.help_button = MDButton(
                    MDButtonText(text=self.app.language_manager.translate("create") + self.app.language_manager.translate("group")),
                    size_hint=(None, None),
                    size=("150dp", "48dp"),
                    pos_hint={"center_x": 0.5, "center_y": 0.5},
                    on_release=lambda _: self.create()
                )
                self.add_widget(self.help_button)
            else:
                self.help_button = MDButton(
                    MDButtonText(text=self.app.language_manager.translate("add") + self.app.language_manager.translate("group")),
                    size_hint=(None, None),
                    size=("150dp", "48dp"),
                    pos_hint={"center_x": 0.5, "center_y": 0.5},
                    on_release=lambda _: AddGroupPopupMenu().open()
                )
                self.add_widget(self.help_button)


    def group_menu_open(self):
        group_menu_items = []
        if self.app.groups:
            for group in self.app.groups:
                group_menu_items.append({"text": group["name"],
                                         "on_release": lambda x=group: self.set_group(x)})
            self.group_dropdown_menu = MDDropdownMenu(
                caller=self.ids.select_group_button,
                items=group_menu_items
            )
            self.group_dropdown_menu.open()
        else:
            if self.app.logged_in_user_id:
                self.create()
            else:
                AddGroupPopupMenu().open()


    def set_group(self, group):
        if self.group_dropdown_menu:
            self.group_dropdown_menu.dismiss()
        self.app.logged_in_group = group
        self.app.state["logged_in_group"] = self.app.logged_in_group
        save_state(self.app.state)
        if self.app.logged_in_group:
            self.ids.group_name.text = group["name"]
        else:
            self.ids.group_name.text = self.app.language_manager.translate("select") + self.app.language_manager.translate("group")
        self.refresh_groups()


    def remove(self, group):
        if group:
            self.app.groups.remove(group)
            self.app.state["groups"] = self.app.groups
            save_state(self.app.state)
            self.refresh_groups()


    def create(self, *args):
        CreateOrEditGroupPopupMenu().open()


    def edit(self):
        if self.app.logged_in_group:
            CreateOrEditGroupPopupMenu().open(self.app.logged_in_group)


    def delete(self):
        if self.app.logged_in_group:
            ConfirmDeletePopupMenu().open(self.app.language_manager.translate("group"), self.app.logged_in_group["name"], lambda: self.app.db.delete_group(self.app.logged_in_group), self.refresh_groups)


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
                    self.remove(group)
        if self.app.logged_in_group not in self.app.groups:
            if self.app.groups:
                self.set_group(self.app.groups[0])
            elif self.app.logged_in_group is not None:
                self.set_group(None)
        self.app.groups = sorted(self.app.groups, key=lambda x: x["name"])
        self.fill_modes_list()
