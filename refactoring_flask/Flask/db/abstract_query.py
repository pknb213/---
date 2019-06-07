from Flask.py.utils import *
from abc import *


class DatabaseApis(metaclass=ABCMeta):
    @abstractmethod
    def get_history_from_show_field(self, a):
        pass

    @abstractmethod
    def add_info_from_history(self, a):
        pass

    @abstractmethod
    def add_model_from_modelId(self, a):
        pass


