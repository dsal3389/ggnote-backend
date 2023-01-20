class NoteNotFound(Exception):
    def __init__(self, id):
        super().__init__(f"note with the id of ({id}) could not be found")
