class Module1Model:
    def __init__(self, name, description):
        self.name = name 
        self.description = description

    @staticmethod 
    def get_items():
        return [
            Module1Model("Item 1", "Description for item 1"),
            Module1Model("Item 2", "Description for item 2")
        ]
