from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QScrollArea
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import sys
from os import path

def assetsPath(filename):
    return path.join(path.dirname(__file__), 'assets', filename)

class ShowGrid(QWidget):
    def __init__(self, g, s):
        super().__init__()
        self.grid = g
        self.solution = s
        cell_size = 35

        self.setFixedWidth(cell_size*(self.grid.width+1))
        self.setFixedHeight(cell_size*(self.grid.height+1))

        tent = QPixmap(assetsPath('tent.png'))
        tree = QPixmap(assetsPath('tree.png'))

        layout = QGridLayout()
        layout.setVerticalSpacing(1)
        layout.setHorizontalSpacing(1)
        for row in range(self.grid.height):
            for col in range(self.grid.width):
                if (row, col) in self.grid.trees:
                    layout.addWidget(self.image_widget(tree), row, col)
                elif (row, col) in self.solution:
                    layout.addWidget(self.image_widget(tent), row, col)
                else:
                    label = QLabel()
                    label.setObjectName("empty")
                    layout.addWidget(label, row, col)
                
        for row in range(self.grid.height):
            layout.addWidget(self.text_widget(str(g.tents_in_row[row]), cell_size), row, g.width)
        for col in range(self.grid.width):
            layout.addWidget(self.text_widget(str(g.tents_in_col[col]), cell_size), g.height, col)

        self.setLayout(layout)
        self.setObjectName("board")

    def image_widget(self, i):
        label = QLabel(self)
        label.setPixmap(i)
        label.setScaledContents(True)
        return label

    @staticmethod
    def text_widget(text, cs):
        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
        label.setFixedSize(cs - 2, cs - 2)
        label.setObjectName("text_widget")
        return label

def display(grid, solution):

    app = QApplication([])

    app.setStyleSheet("""
    QLabel#text_widget { 
        /* background-color: #d1e7ff; */
        background-color: #d4e8ff;
        border-radius: 10px; 
        font-size: 16px; 
        font-weight: 500
    }
    QLabel#empty {
        background-color: rgb(201, 187, 113)
    }
    QScrollArea#container {
        background-image: url(""" + assetsPath('background.jpg') + """);
    }
    QWidget#board {
        /* background-color: #7ca6d7; */
        background-color: #13394c;
        border-radius: 10px; 
    }
    """)
    scrollArea = QScrollArea()
    scrollArea.setObjectName("container")
    gridWidget = ShowGrid(grid, solution)
    scrollArea.setWidget(gridWidget)
    scrollArea.setAlignment(Qt.AlignCenter)
    scrollArea.setWindowTitle('Tents')
    scrollArea.showMaximized()
    scrollArea.show()
    sys.exit(app.exec_())

