from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys

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
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.setMinimumSize(35, 35)

    def mousePressEvent(self, ev):
        if ev.button() == Qt.RightButton:
            self.rightClicked.emit(self.i, self.j)
        else:
            self.clicked.emit(self.i, self.j)


class NumberBlock(QWidget):
    def __init__(self, i, j, max, minSize):
        super().__init__()
        self.x = i
        self.y = j
        self.inputLine = QLineEdit(self)
        self.inputLine.setObjectName("number_block")
        self.inputLine.setText("0")
        self.vlidator = QIntValidator(0, max, self)
        self.inputLine.setValidator(self.vlidator)
        self.initUI(minSize)

    def initUI(self, minSize):
        self.setFixedSize(minSize, minSize)


class Board(QWidget):
    def __init__(self, size):
        super().__init__()
        self.puzzles = {}
        self.puzzleMaker(size)
        self.adjustSize()
        self.setObjectName('board')
        self.setMinimumSize(35*int(size["rowSize"]), 35*int(size["columnSize"]))

    def puzzleMaker(self, size):
        row_size = int(size["rowSize"])
        column_size = int(size["columnSize"])
        layout = QGridLayout()
        layout.setVerticalSpacing(1)
        layout.setHorizontalSpacing(1)
        maxSize = row_size if (row_size > column_size) else column_size
        if (500 / maxSize) < 50:
            minSize = 35
        else:
            minSize = 50
        for i in range(row_size):
            counterBlock = QLabel(str(i + 1))
            counterBlock.setAlignment(Qt.AlignCenter)
            counterBlock.setFixedSize(minSize - 2, minSize - 2)
            counterBlock.setObjectName("counter_block")
            self.puzzles[str((i + 1, 0))] = counterBlock
            layout.addWidget(counterBlock, i + 1, 0)
        for j in range(column_size):
            counterBlock = QLabel(str(j + 1))
            counterBlock.setAlignment(Qt.AlignCenter)
            counterBlock.setFixedSize(minSize - 2, minSize - 2)
            counterBlock.setObjectName("counter_block")
            self.puzzles[str((0, j + 1))] = counterBlock
            layout.addWidget(counterBlock, 0, j + 1)
        for i in range(row_size):
            for j in range(column_size):
                pb = PuzzleBolck(i + 1, j + 1)
                pb.clicked.connect(self.plantTree)
                pb.rightClicked.connect(self.cutTree)
                self.puzzles[str((i + 1, j + 1))] = pb
                layout.addWidget(pb, i +1 , j + 1)
        for i in range(row_size):
            nb = NumberBlock(i + 1, column_size + 1, row_size, minSize)
            self.puzzles[str((i + 1, column_size + 1))] = nb
            layout.addWidget(nb, i + 1, column_size + 1)
        for j in range(column_size):
            nb = NumberBlock(row_size + 1, j + 1, column_size, minSize)
            self.puzzles[str((row_size + 1, j + 1))] = nb
            layout.addWidget(nb, row_size + 1, j + 1)

        self.setLayout(layout)
        print("created clearlly")

    def plantTree(self, i, j):
        self.puzzles[str((i, j))].setPixmap(QPixmap("assets/tree.png"))

    def cutTree(self, i, j):
        self.puzzles[str((i, j))].setPixmap(QPixmap("assets/bg.png"))


class InputDialog(QDialog):
    
    accepted = pyqtSignal(dict)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #  maximal 10000 * 10000
        self.setWindowTitle("Row * Column")
        self.intValidator = QIntValidator(1, 100, self)

        self.rowSize = QLineEdit(self)
        self.columnSize = QLineEdit(self)

        self.rowSize.setValidator(self.intValidator)
        self.columnSize.setValidator(self.intValidator)

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
        self.initGUI()

    def initGUI(self):
        self.setWindowTitle("Puzzle")
        self.setWindowIcon(QIcon("assets/icon.jpg"))
        self.setMinimumSize(600, 600)
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
        newAction.triggered.connect(self.save)
        quit = menubar.addMenu("Quit")
        quitAction = QAction("Quit", self)
        quitAction.setIcon(QIcon("assets/icon_quit.png"))
        quitAction.setShortcut("Ctrl+Q")
        quitAction.setStatusTip("Quit puzzle")
        quitAction.triggered.connect(self.close)

        file.addAction(newAction)
        file.addAction(submitAction)
        quit.addAction(quitAction)
    
    def newBoard(self, size):
        #  Add a scroll area in main Window
        self.centralWidget = QWidget()
        layout = QVBoxLayout(self.centralWidget)
        self.scrollArea = QScrollArea(self.centralWidget)
        self.scrollArea.setObjectName("board_scroll")
        self.scrollArea.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.scrollArea)
        self.board = Board(size)
        self.scrollArea.setWidget(self.board)
        self.setCentralWidget(self.centralWidget)

    def newAction(self):
        self.inputDialog.show()

    def save(self):
        print("save")

app = QApplication([])

#  @ref Chen Xiao, Yang Zhu  
app.setStyleSheet("""
    QLabel#counter_block { 
        /* background-color: #d1e7ff; */
        background-color: #d4e8ff;
        border-radius: 10px; 
        font-size: 16px; 
        font-weight: 500
    }
    QScrollArea#board_scroll {
        background-image: url(""" + 'assets/background1.jpg' + """);
    }
    QLineEdit#number_block{
        background-color: #d4e8ff;
        border-radius: 10px; 
        font-size: 16px;
        border: 1px solid black;
        font-weight: 500
    }
    QWidget#board {
        /* background-color: #7ca6d7; */
        background-color: #13394c;
        border-radius: 10px; 
    }
    """)

mw = MainWindow()
mw.show()
sys.exit(app.exec_())
