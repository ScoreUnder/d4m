#!/usr/bin/env python
import enum
from PySide6.QtGui import QColor
import PySide6.QtWidgets as qwidgets
import traceback
import PySide6.QtCore 
import sys

from django.forms import modelform_factory

import d4m.common
import d4m.manage
from d4m.manage import ModManager
import d4m.api
from d4m.divamod import DivaSimpleMod


def log_msg(content: str):
    pass

def show_exc_dialog(what_failed: str, exception: Exception, fatal = True):
    pass

def on_unhandled_exception(*args):
    pass

def create_mod_elem(mod: DivaSimpleMod, root):
    return
    root.insert('', 'end', iid=mod.name, text=str(mod))

def on_dml_toggle_click(status_label, mod_manager: ModManager):
    try:
        if mod_manager.enabled:
            mod_manager.disable_dml()
            status_label.setText("DISABLED")
        else:
            mod_manager.enable_dml()
            status_label.setText("ENABLED")
    except Exception as e:
        show_exc_dialog("Toggling DML", e, fatal = False)

def on_install_mod():
    pass #TODO: score lol

def on_toggle_mod(selections, mod_manager: ModManager, tree):
    return
    for selection in selections:
        mod = next(filter(lambda mod: mod.name == selection, mod_manager.mods))
        if mod_manager.is_enabled(mod):
            mod_manager.disable(mod)
            log_msg(f"Disabled {mod}")
        else:
            mod_manager.enable(mod)
            log_msg(f"Enabled {mod}")

def on_update_mod(selections, mod_manager: ModManager, tree):
    return
    log_msg(f"Attempting to update {len(selections)} mods")
    for selection in selections:
        mod = next(filter(lambda mod: mod.name == selection, mod_manager.mods))
        if mod.is_simple():
            log_msg(f"{str(mod)} has an unknown origin and cannot be updated.")
        else:
            if mod.is_out_of_date():
                log_msg(f"Updating {mod}...")
                mod_manager.update(mod)
                log_msg(f"{mod} updated successfully.")
            else:
                log_msg(f"{mod} is already up to date.")

def on_delete_mod(selections, mod_manager: ModManager, tree):
    return
    content = f"Are you sure you want to delete {len(selections)} mods?\n"+", ".join(selections)
    if tkinter.messagebox.askyesno(title = f"Delete {len(selections)} mods?", message=content):
        for selection in selections:
            mod = next(filter(lambda mod: mod.name == selection, mod_manager.mods))
            mod_manager.delete_mod(mod)
            log_msg(f"Deleted {mod}")


class D4mGUI():
    def __init__(self, qapp: qwidgets.QApplication, mod_manager: ModManager):
        # mod_manager.check_for_updates()
        #TODO: re-enable update checking
        window = qwidgets.QWidget()
        main_widget = qwidgets.QVBoxLayout(window)
        top_row = qwidgets.QHBoxLayout()
        mod_table = qwidgets.QTableWidget()
        mod_buttons = qwidgets.QHBoxLayout()
        statusbar = qwidgets.QStatusBar()
        statusbar.showMessage(f"d4m v{d4m.common.VERSION}")

        # Propogate top row
        dml_status_label = qwidgets.QLabel("DivaModLoader (version here)")
        dml_enable_label = qwidgets.QLabel("ENABLED" if mod_manager.enabled else "DISABLED")
        dml_toggle_button = qwidgets.QPushButton("Toggle DivaModLoader")
        dml_toggle_button.clicked.connect(lambda *_: on_dml_toggle_click(dml_enable_label, mod_manager))
        mod_count_label = qwidgets.QLabel("-- mods / -- enabled")
        
        top_row.addWidget(dml_status_label)
        top_row.addWidget(dml_enable_label)
        top_row.addWidget(dml_toggle_button)
        top_row.addWidget(mod_count_label)

        # Propogate mod list
        mod_table.setColumnCount(5) #image, name, creator, version
        mod_table.setHorizontalHeaderLabels(["Thumbnail", "Mod Name", "Mod Author(s)", "Mod Version", "Gamebanana ID"])
        def populate_modlist():
            mod_table.clear()
            mod_table.setRowCount(len(mod_manager.mods))
            for (index, mod) in enumerate(mod_manager.mods):
                mod_image = qwidgets.QTableWidgetItem("image here")
                mod_name = qwidgets.QTableWidgetItem(mod.name)
                mod_author = qwidgets.QTableWidgetItem(mod.author)
                mod_version = qwidgets.QTableWidgetItem(str(mod.version))
                if not mod.is_simple():
                    #TODO: re-enable this
                    # if mod.is_out_of_date():
                    #     mod_version.setBackground(QColor.fromRgb(255, 255, 0))
                    url = f"https://gamebanana.com/mods/{mod.id}"
                    mod_id = qwidgets.QTableWidgetItem(f"<a href=\"{url}\">{mod.id}</a>")
                    mod_table.setItem(index, 4, mod_id)
                mod_table.setItem(index, 0, mod_image)
                mod_table.setItem(index, 1, mod_name)
                mod_table.setItem(index, 2, mod_author)
                mod_table.setItem(index, 3, mod_version)
                enabled_mod_count = sum(1 for m in mod_manager.mods if m.enabled)
                mod_count_label.setText(f"{len(mod_manager.mods)} mods / {enabled_mod_count} enabled")

        populate_modlist()

        def autoupdate(func, *args):
            func(*args)
            populate_modlist()
            mod_count_label.text

        # Propogate action buttons
        install_mod_button = qwidgets.QPushButton("Install Mods...")
        install_mod_button.clicked.connect(lambda *_: autoupdate(on_install_mod))

        toggle_mod_button = qwidgets.QPushButton("Toggle Selected")
        toggle_mod_button.clicked.connect(lambda *_: autoupdate(on_toggle_mod, None, mod_manager, None))

        update_mod_button = qwidgets.QPushButton("Update Selected")
        update_mod_button.clicked.connect(lambda *_: autoupdate(on_update_mod, None, mod_manager, None))

        delete_mod_button = qwidgets.QPushButton("Delete Selected")
        delete_mod_button.clicked.connect(lambda *_: autoupdate(on_delete_mod, None, mod_manager, None))

        refresh_mod_button = qwidgets.QPushButton("Refresh")
        refresh_mod_button.clicked.connect(lambda *_: autoupdate(mod_manager.reload))

        mod_buttons.addWidget(install_mod_button)
        mod_buttons.addWidget(toggle_mod_button)
        mod_buttons.addWidget(update_mod_button)
        mod_buttons.addWidget(delete_mod_button) 
        mod_buttons.addWidget(refresh_mod_button)

        # # Populate main GUI
        main_widget.addLayout(top_row)
        main_widget.addWidget(mod_table)
        main_widget.addLayout(mod_buttons)
        main_widget.addWidget(statusbar)
        window.show()
        sys.exit(qapp.exec())

def main():
    megamix_path = d4m.common.get_megamix_path()
    if not d4m.common.modloader_is_installed(megamix_path):
        #TODO: show annoying popup box :)
        pass
    
    dml_version, dml_enabled, dml_mods_dir = d4m.common.get_modloader_info(megamix_path)
    try:
        dml_latest, dml_download = d4m.manage.check_modloader_version()
        if dml_version < dml_latest:
            if d4m.common.can_autoupdate_dml():
                content = f"A new version of DivaModLoader is available.\nCurrent: {dml_version}\nLatest:{dml_latest}\nDo you want to update?"
                #TODO: yes/no message box here
            else:
                pass
                #TODO: dml autoupdate not supported
    except Exception as e:
        show_exc_dialog("Fetching latest DML version", e, fatal=False)

    mod_manager = ModManager(megamix_path, mods_path=dml_mods_dir)
    app = qwidgets.QApplication([])
    D4mGUI(app, mod_manager)

if __name__ == "__main__":
    main()