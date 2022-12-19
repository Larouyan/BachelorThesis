from abc import ABC, abstractmethod


class GUIFactory(ABC):
    @abstractmethod
    def create_label(self, *args):
        """
        Create a label
        """
        pass

    @abstractmethod
    def create_button(self, *args):
        """
        Create a button
        """
        pass

    @abstractmethod
    def create_entry(self, *args):
        """
        Create an entry (or text field)
        """
        pass

    @abstractmethod
    def create_listbox(self, *args):
        """
        Create a list box
        """
        pass

    @abstractmethod
    def create_scrollbar(self, *args):
        """
        Create a scrollbar
        """
        pass

    @abstractmethod
    def create_canvas(self, *args):
        """
        Create a canvas
        """
        pass

    @abstractmethod
    def create_checkbutton(self, *args):
        """
        Create a check button
        """
        pass

    @abstractmethod
    def create_scale(self, *args):
        """
        Create a scale
        """
        pass

    @abstractmethod
    def create_option_menu(self, *args):
        """
        Create an option menu
        """
        pass
