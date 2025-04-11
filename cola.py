class ColaMisiones:
    def __init__(self):
        self.items = []

    def enqueue(self, mision):
        self.items.append(mision)

    def dequeue(self):
        if self.is_empty():
            return None
        return self.items.pop(0)

    def first(self):
        if self.is_empty():
            return None
        return self.items[0]

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)
