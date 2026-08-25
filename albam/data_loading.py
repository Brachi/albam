import configparser
from pathlib import Path
import os

import bpy
from bpy.app.handlers import persistent


APPS_USERDATA_FILENAME = "apps-userdata.ini"


class AppsUserDataConfigManager:
    _instance = None
    _config = None
    _filepath = None

    def __new__(cls):
        if cls._instance is None:
            ALBAM_EXTENSION_PATH = bpy.utils.extension_path_user(__package__, create=True)

            cls._instance = super(AppsUserDataConfigManager, cls).__new__(cls)
            cls._filepath = Path(ALBAM_EXTENSION_PATH) / APPS_USERDATA_FILENAME
            cls._config = configparser.ConfigParser()

            # Read file if it exists, otherwise initialize an empty config
            if os.path.exists(str(cls._filepath)):
                cls._config.read(str(cls._filepath))

        return cls._instance

    @property
    def config(self):
        """Exposes the internal ConfigParser instance."""
        return self._config

    def save(self):
        """Saves current memory state back to the original file path."""
        with open(self._filepath, 'w') as configfile:
            self._config.write(configfile)

    def get_app_section(self, app_id):
        app_section = None
        for section in self.config.sections():
            if section == app_id:
                app_section = self.config[section]
        return app_section


@persistent
def populate_albam_data(dummy):

    _populate_apps_userdata()

    # Add here future presets shipped with Albam


def _populate_apps_userdata():
    """
    Populate the initial app_dir attribute, removing a
    value if there's nothing in the config file.
    This avoids revealing the path when a Blend file is shared
    """
    apps_userdata_config = AppsUserDataConfigManager().config
    current_app = bpy.context.scene.albam.apps.app_selected

    for section in apps_userdata_config.sections():
        if section == current_app:
            app_dir = apps_userdata_config[section].get("app_dir")
            if app_dir:  # TODO: check validity, convert to system path
                bpy.context.scene.albam.apps.app_dir = app_dir
                break
    else:
        # Delete potential existing app_dir saved in blend-file if not backed
        # by a ini file
        bpy.context.scene.albam.apps.app_dir = ""
