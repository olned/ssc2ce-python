class BookEventHandlerHolder:
    """

    """

    def __init__(self):
        self.on_book_update = None
        self.on_book_setup = None

    def set_on_book_setup(self, handler) -> None:
        self.on_book_setup = handler

    def set_on_book_update(self, handler) -> None:
        self.on_book_update = handler
