class HomeconomyModel:
    def __init__(self, name, description):
        self.name = name
        self.description = description

    @staticmethod
    def get_items():
        return [
            HomeconomyModel("Budget Planning", "Track and plan your monthly budget"),
            HomeconomyModel("Expense Tracking", "Monitor your daily expenses")
        ]
