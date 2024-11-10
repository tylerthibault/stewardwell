class ExampleModel:
    def __init__(self, title, content):
        self.title = title 
        self.content = content

    @staticmethod
    def get_all():
        # Simulate database query
        return [
            ExampleModel("First Post", "This is the first post content"),
            ExampleModel("Second Post", "This is the second post content") 
        ]
