from collections import namedtuple

import yaml


class YAMLConfigParser:

    def __init__(self, config_class: namedtuple, validate_function):
        self.config_class = config_class
        self.validate_function = validate_function

    def parse(self, document):
        """
        Parse a yaml config document.

        :param document: An open file or a string
        :return: An instance of config_class
        """
        data = yaml.load(document)
        return self.create_config_instance(data)

    def create_config_instance(self, data):
        validated_data = self.validate_function(data)
        return self.config_class(**validated_data)


class YAMLListConfigParser(YAMLConfigParser):

    def __init__(self, config_class: namedtuple, validate_function):
        super().__init__(config_class, validate_function)

    def parse(self, document):
        """
        Parse multiple yaml documents.

        :param document: An open file or a string
        :return: A list of instantiated config_classes
        """
        config_objects = []
        for data in filter(None, yaml.load_all(document)):
            config_objects.append(super().create_config_instance(data))
        return config_objects
