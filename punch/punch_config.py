import collections

from punch.helpers import import_file
from punch import version as ver
from punch import file_configuration as fc


class PunchConfig(object):
    def __init__(self, config_filepath, version_filepath):

        configuration_module, version_module = import_file(config_filepath, version_filepath)

        try:
            self.__config_version__ = configuration_module.__config_version__
        except AttributeError:
            raise ValueError("Given config file is invalid: missing '__config_version__' variable")

        if configuration_module.__config_version__ > 1:
            raise ValueError(
                "Unsupported configuration file version {}".format(configuration_module.__config_version__))

        try:
            files = configuration_module.FILES
        except AttributeError:
            raise ValueError("Given config file is invalid: missing 'FILES' attribute")

        try:
            self.globals = configuration_module.GLOBALS
        except AttributeError:
            self.globals = {}

        self.files = []
        for file_configuration in files:
            if isinstance(file_configuration, collections.Mapping):
                self.files.append(fc.FileConfiguration.from_dict(file_configuration, self.globals))
            else:
                self.files.append(fc.FileConfiguration(file_configuration, {}, self.globals))

        try:
            version = configuration_module.VERSION
        except AttributeError:
            raise ValueError("Given config file is invalid: missing 'VERSION' attribute")

        self.version = ver.Version()

        for version_part in version:
            try:
                value = getattr(version_module, version_part['name'])
                version_part['value'] = value
            except AttributeError:
                raise ValueError("Given version file is invalid: missing '{}' variable".format(version_part['name']))

            self.version.add_part_from_dict(version_part)
