from abc import ABC, abstractmethod


class GUIFactory(ABC):
    @abstractmethod
    def create_label(self, *args):
        pass

    @abstractmethod
    def create_button(self, *args):
        pass

    @abstractmethod
    def create_entry(self, *args):
        pass

    @abstractmethod
    def create_listbox(self, *args):
        pass

    @abstractmethod
    def create_scrollbar(self, *args):
        pass

    @abstractmethod
    def create_canvas(self, *args):
        pass

    @abstractmethod
    def create_checkbutton(self, *args):
        pass

    @abstractmethod
    def create_scale(self, *args):
        pass

    @abstractmethod
    def create_option_menu(self, *args):
        pass
