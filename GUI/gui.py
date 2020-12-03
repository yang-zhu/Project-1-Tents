import argparse
import sys
import os

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd() , os.pardir)))
from tents_formula_v2 import solveGrid, Grid


class PuzzleBolck(QLabel):
    clicked = pyqtSignal(int, int)
    rightClicked = pyqtSignal(int, int)

    def __init__(self, i, j):
        super().__init__()
        self.i = i
        self.j = j
        self.initUI()

    def initUI(self):
        self.setStyleSheet("border: 0.5px solid black")
        self.setPixmap(QPixmap("assets/bg.png"))
        self.setScaledContents(True)
        self.fixSize = 35
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.setMinimumSize(self.fixSize, self.fixSize)

    def mousePressEvent(self, ev):
        if ev.button() == Qt.RightButton:
            self.rightClicked.emit(self.i, self.j)
        else:
            self.clicked.emit(self.i, self.j)


class NumberBlock(QLineEdit):
    def __init__(self, i, j, max:int, minSize):
        super().__init__()
        self.x = i
        self.y = j
        self.setObjectName("number_block")
        self.setText("0")
        self.vlidator = QIntValidator(0, max, self)  #  TODO: not work
        self.setValidator(self.vlidator)
        self.initUI(minSize)

    def initUI(self, minSize):
        self.setFixedSize(minSize, minSize)
    
    def getValue(self):
        return int(self.text())


class Board(QWidget):
    def __init__(self):
        super().__init__()
        self.puzzles = {}
        self.trees = set()
        self.adjustSize()
        self.setObjectName('board')
        self.row_size = 0
        self.column_size = 0

    def puzzleMaker(self, size):
        self.row_size = int(size["rowSize"])
        self.column_size = int(size["columnSize"])
        self.sizeChecker = 500
        self.fixSize = 35
        self.maxSize = 50
        layout = QGridLayout()
        layout.setVerticalSpacing(1)
        layout.setHorizontalSpacing(1)
        maxSize = self.row_size if (self.row_size > self.column_size) else self.column_size
        if (self.sizeChecker / maxSize) < self.maxSize:
            minSize = self.fixSize
        else:
            minSize = self.maxSize
        for i in range(self.row_size):  #  counter blocks on left
            counterBlock = QLabel(str(i + 1))
            counterBlock.setAlignment(Qt.AlignCenter)
            counterBlock.setFixedSize(minSize - 2, minSize - 2)
            counterBlock.setObjectName("counter_block")
            self.puzzles[str((i + 1, 0))] = counterBlock
            layout.addWidget(counterBlock, i + 1, 0)
        for j in range(self.column_size):  #  counter blocks on top
            counterBlock = QLabel(str(j + 1))
            counterBlock.setAlignment(Qt.AlignCenter)
            counterBlock.setFixedSize(minSize - 2, minSize - 2)
            counterBlock.setObjectName("counter_block")
            self.puzzles[str((0, j + 1))] = counterBlock
            layout.addWidget(counterBlock, 0, j + 1)
        for i in range(self.row_size):  #  puzzles
            for j in range(self.column_size):
                pb = PuzzleBolck(i + 1, j + 1)
                pb.clicked.connect(self.plantTree)
                pb.rightClicked.connect(self.cutTree)
                self.puzzles[str((i + 1, j + 1))] = pb
                layout.addWidget(pb, i +1 , j + 1)
        for i in range(self.row_size):  #  number blocks on the right
            nb = NumberBlock(i + 1, self.column_size + 1, self.column_size, minSize)
            self.puzzles[str((i + 1, self.column_size + 1))] = nb
            layout.addWidget(nb, i + 1, self.column_size + 1)
        for j in range(self.column_size):  #  number blocks on the left
            nb = NumberBlock(self.row_size + 1, j + 1, self.row_size, minSize)
            self.puzzles[str((self.row_size + 1, j + 1))] = nb
            layout.addWidget(nb, self.row_size + 1, j + 1)

        self.setLayout(layout)

    def plantTree(self, i, j):
        self.puzzles[str((i, j))].setPixmap(QPixmap("assets/tree.png"))
        self.trees.add((i, j))

    def cutTree(self, i, j):
        self.puzzles[str((i, j))].setPixmap(QPixmap("assets/bg.png"))
        if (i, j) in self.trees:
            self.trees.remove((i, j))

    def getTrees(self):
        return self.trees
    
    def getInputValues(self):
        return [self.puzzles[str((i + 1, self.column_size + 1))].getValue() for i in range(self.row_size)], [self.puzzles[str((self.row_size + 1, i + 1))].getValue() for i in range(self.column_size)]
    
    def clearBoard(self):
        print(self.layout.count())
        return self.layout.count()

class InputDialog(QDialog):
    
    accepted = pyqtSignal(dict)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #  maximal 100 * 100
        self.max = 100
        self.setWindowTitle("Row * Column")

        self.rowSize = QLineEdit(self)
        self.columnSize = QLineEdit(self)

        self.rowSize.setValidator(QIntValidator(1, self.max, self))  # not work
        self.columnSize.setValidator(QIntValidator(1, self.max, self))  # not work

        self.rowSize.textEdited[str].connect(self.enable)
        self.columnSize.textEdited[str].connect(self.enable)

        self.button = QPushButton("OK")
        self.button.setDisabled(True)
        self.button.clicked.connect(self.create)

        form = QFormLayout(self)
        form.addRow("row: ", self.rowSize)
        form.addRow("column: ", self.columnSize)
        form.addRow(self.button)

    def enable(self):
        if self.rowSize.text() and self.columnSize.text():
            self.button.setEnabled(True)
        else:
            self.button.setDisabled(True)

    def create(self):
        size = {"rowSize": self.rowSize.text(), "columnSize": self.columnSize.text()}
        self.accepted.emit(size)
        self.accept()


class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.inputDialog = InputDialog()
        self.board = Board()
        self.scrollArea = None
        self.initGUI()

    def initGUI(self):
        self.setWindowTitle("Puzzle")
        self.setWindowIcon(QIcon("assets/icon.jpg"))
        self.fixSize = 600
        self.setMinimumSize(self.fixSize, self.fixSize)
        self.inputDialog.accepted.connect(self.newBoard)

        #  set up menu bar
        menubar = self.menuBar()
        file = menubar.addMenu("File")
        newAction = QAction("New", self)
        newAction.setIcon(QIcon("assets/icon_new.png"))
        newAction.setShortcut("Ctrl+N")
        newAction.setStatusTip("New puzzle")
        newAction.triggered.connect(self.newAction)
        submitAction = QAction("Test&Save", self)
        submitAction.setIcon(QIcon("assets/icon_save.png"))
        submitAction.setShortcut("Ctrl+S")
        submitAction.setStatusTip("Test&Save")
        submitAction.triggered.connect(self.testAndSave)
        quit = menubar.addMenu("Quit")
        quitAction = QAction("Quit", self)
        quitAction.setIcon(QIcon("assets/icon_quit.png"))
        quitAction.setShortcut("Ctrl+Q")
        quitAction.setStatusTip("Quit puzzle")
        quitAction.triggered.connect(self.close)
        about = menubar.addMenu("About")
        aboutAction = QAction("About", self)
        aboutAction.setIcon(QIcon("assets/icon_new.png"))
        aboutAction.setShortcut("Ctrl+B")
        aboutAction.setStatusTip("About")
        aboutAction.triggered.connect(self.showAbout)

        file.addAction(newAction)
        file.addAction(submitAction)
        quit.addAction(quitAction)
        about.addAction(aboutAction)
    
    def newBoard(self, size):
        #  Add a scroll area in main Window
        if self.scrollArea is not None:  #  there is a board already
                self.clearBoard()  #  clear scroll area
        self.board = Board()
        self.centralWidget = QWidget()
        layout = QVBoxLayout(self.centralWidget)
        self.scrollArea = QScrollArea(self.centralWidget)
        self.scrollArea.setObjectName("board_scroll")
        self.scrollArea.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.scrollArea)
        self.board.puzzleMaker(size)
        self.scrollArea.setWidget(self.board)
        self.setCentralWidget(self.centralWidget)

    def clearBoard(self):
        self.scrollArea.deleteLater()

    def showAbout(self):
        with open("information.txt", "r") as f:
            inf = f.readlines()
        self.showInformation("About", (" ").join(inf))

    def newAction(self):
        self.inputDialog.show()

    def testAndSave(self):
        trees = self.board.getTrees()
        tents_in_row, tents_in_col = self.board.getInputValues()

        if sum(tents_in_col + tents_in_row) != len(trees):
            self.showInformation("Error", "The number of tents should be equal to the number of trees, please consider to fix it.")
            return
        grid = Grid(self.board.row_size, self.board.column_size, trees, tents_in_row, tents_in_col)
        if not self.save(grid):
            self.showInformation("Warning", "There is no solution for this map!")
        else:
            self.showInformation("Message", "The puzzles has been saved:D")

    def showInformation(self,typ, text):
        QMessageBox.information(self, typ, text, QMessageBox.Yes)
    
    #  @ref Liu Shaoyin
    def save(self, grid):
        parser = argparse.ArgumentParser(description="GUI Solve & Save puzzles.")
        args = parser.parse_args()
        # TODO: set cadical path
        args.cadical='/Users/macair/Downloads/cadical-sc2020-45029f8/build/cadical'

        solution = solveGrid(args.cadical, grid)

        # Prints the solution
        if solution == None:
            return False
        else:
            # TODO: set save path
            path = '/Users/macair/Documents/GitHub/Project-1-Tents/save.txt'
            f = open(path, 'a+')   
            for r in range(grid.height):
                for c in range(grid.width):
                    if (r, c) in solution:
                        f.write('Δ')
                    elif (r, c) in grid.trees:
                        f.write('T')
                    else:
                        f.write('.')
                f.write(str(grid.tents_in_row[r])+"\n")
            for num in grid.tents_in_col:
                f.write(str(num))
            return True


if __name__ == '__main__':
    app = QApplication([])

    #  @ref Chen Xiao, Yang Zhu  
    app.setStyleSheet("""
        QLabel#counter_block { 
            /* background-color: #d1e7ff; */
            background-color: #d4e8ff;
            border-radius: 10px; 
        border-radius: 10px; 
            border-radius: 10px; 
            font-size: 16px; 
        font-size: 16px; 
            font-size: 16px; 
            font-weight: 500
        }
        QScrollArea#board_scroll {
            background-image: url(""" + 'assets/background1.jpg' + """);
        }
        QLineEdit#number_block{
            background-color: #d4e8ff;
            border-radius: 10px; 
        border-radius: 10px; 
            border-radius: 10px; 
            font-size: 16px;
            border: 1px solid black;
            font-weight: 500
        }
        QWidget#board {
            /* background-color: #7ca6d7; */
            background-color: #13394c;
            border-radius: 10px; 
        border-radius: 10px; 
            border-radius: 10px; 
        }
        """)

    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
