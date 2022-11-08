import openpyxl
from bubble_tracker import Bubble


class DataTable:
    def __init__(self, filename):
        self.filename = filename
        self.wb = openpyxl.load_workbook(filename)
        self.ws = self.wb.active
        self.row = 2

    def set(self, row, col, value):
        self.ws.cell(row=row, column=col).value = value

    def push(self, time: float, bubbles: list[Bubble]):
        for bubble in bubbles:
            self.set(self.row, 1, time)
            self.set(self.row, 2, bubble.id)
            self.set(self.row, 3, bubble.is_big)
            self.set(self.row, 4, bubble.height)
            self.set(self.row, 5, bubble.width)
            self.set(self.row, 6, bubble.center[1])
            self.row += 1

    def save(self):
        self.wb.save(self.filename)
