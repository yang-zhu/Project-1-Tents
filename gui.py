import argparse
import sys
import os

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))
from encoding import solveGrid, Grid, assetsPath


class PuzzleBolck(QLabel):
    """Puzzle area, which can be selceted to set tree or tent on it"""
    clicked = pyqtSignal(int, int)
    rightClicked = pyqtSignal(int, int)

    def __init__(self, i, j):
        super().__init__()
        self.i = i
        self.j = j
        self.initUI()

    def initUI(self):
        self.setStyleSheet("border: 0.5px solid black")
        self.setPixmap(QPixmap(assetsPath("bg.png")))
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
    """Number area to set number of tents on columns or rows"""
    def __init__(self, i, j, max: int, minSize):
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
    """Board, which have all puzzle, number, counter blocks"""
    def __init__(self):
        super().__init__()
        self.puzzles = {}
        self.trees = set()
        self.adjustSize()
        self.setObjectName("board")
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
        maxSize = (
            self.row_size if (self.row_size > self.column_size) else self.column_size
        )
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
                layout.addWidget(pb, i + 1, j + 1)
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
        self.puzzles[str((i, j))].setPixmap(QPixmap(assetsPath("tree.png")))
        self.trees.add((i - 1, j - 1))

    def cutTree(self, i, j):
        self.puzzles[str((i, j))].setPixmap(QPixmap(assetsPath("bg.png")))
        if (i - 1, j - 1) in self.trees:
            self.trees.remove((i - 1, j - 1))

    def getTrees(self):
        return self.trees

    def getInputValues(self):
        return [
            self.puzzles[str((i + 1, self.column_size + 1))].getValue()
            for i in range(self.row_size)
        ], [
            self.puzzles[str((self.row_size + 1, i + 1))].getValue()
            for i in range(self.column_size)
        ]

    def clearBoard(self):
        return self.layout.count()


class InputDialog(QDialog):
    """Input dialog to set the board size"""

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
        size = {
            "rowSize": self.rowSize.text(),
            "columnSize": self.columnSize.text(),
        }
        self.accepted.emit(size)
        self.accept()


class MainWindow(QMainWindow):
    """The main window of gui, which include board"""
    def __init__(self, solver_path, styleFactory):
        super().__init__()
        self.inputDialog = InputDialog()
        self.board = Board()
        self.scrollArea = None
        self.hasPuzzle = False
        self.initGUI()
        self.solver_path = solver_path
        self.styleFactory = styleFactory

    def initGUI(self):
        self.setWindowTitle("Tents")
        self.setWindowIcon(QIcon(assetsPath("icon.jpg")))
        self.fixSize = 600
        self.setMinimumSize(self.fixSize, self.fixSize)
        self.inputDialog.accepted.connect(self.newBoard)

        #  set up menu bar
        menubar = self.menuBar()
        file = menubar.addMenu("File")
        view = menubar.addMenu("View")
        newAction = QAction("New", self)
        newAction.setIcon(QIcon(assetsPath("icon_new.png")))
        newAction.setShortcut("Ctrl+N")
        newAction.setStatusTip("New puzzle")
        newAction.triggered.connect(self.newAction)
        submitAction = QAction("Save", self)
        submitAction.setIcon(QIcon(assetsPath("icon_save.png")))
        submitAction.setShortcut("Ctrl+S")
        submitAction.setStatusTip("Save")
        submitAction.triggered.connect(self.testAndSave)
        submitAction.setEnabled(False)
        self.submitAction = submitAction
        quit = menubar.addMenu("Quit")
        quitAction = QAction("Quit", self)
        quitAction.setIcon(QIcon(assetsPath("icon_quit.png")))
        quitAction.setShortcut("Ctrl+Q")
        quitAction.setStatusTip("Quit puzzle")
        quitAction.triggered.connect(self.close)
        about = menubar.addMenu("About")
        aboutAction = QAction("About", self)
        aboutAction.setIcon(QIcon(assetsPath("icon.jpg")))
        aboutAction.setShortcut("Ctrl+B")
        aboutAction.setStatusTip("About")
        aboutAction.triggered.connect(self.showAbout)
        defaultView = QAction("Default", self)
        defaultView.setIcon(QIcon(assetsPath("background.jpg")))
        defaultView.setStatusTip("Default view")
        defaultView.triggered.connect(self.setDefaultView)
        christmasView = QAction("Christmas", self)
        christmasView.setIcon(QIcon(assetsPath("christmas.jpg")))
        christmasView.setStatusTip("Christmas view")
        christmasView.triggered.connect(self.setChrismasView)
        galaxyView = QAction("Galaxy", self)
        galaxyView.setIcon(QIcon(assetsPath("galaxy.jpg")))
        galaxyView.setStatusTip("Galaxy view")
        galaxyView.triggered.connect(self.setGalaxyView)

        file.addAction(newAction)
        file.addAction(submitAction)
        view.addAction(defaultView)
        view.addAction(christmasView)
        view.addAction(galaxyView)
        quit.addAction(quitAction)
        about.addAction(aboutAction)

        # set up toolbar
        solveAction = QAction("Solve", self)
        solveAction.setIcon(QIcon.fromTheme("media-playback-start"))
        solveAction.setStatusTip("Solve Puzzle")
        solveAction.triggered.connect(self.solve)
        solveAction.setEnabled(False)
        self.solveAction = solveAction
        tbNewAction = QAction("New", self)
        tbNewAction.setIcon(QIcon.fromTheme("document-new"))
        tbNewAction.setStatusTip("New puzzle")
        tbNewAction.triggered.connect(self.newAction)
        tbSubmitAction = QAction("Save", self)
        tbSubmitAction.setIcon(QIcon.fromTheme("document-save"))
        tbSubmitAction.setStatusTip("Save")
        tbSubmitAction.triggered.connect(self.testAndSave)
        tbSubmitAction.setEnabled(False)
        self.tbSubmitAction = tbSubmitAction

        toolbar = self.addToolBar("Actions")
        toolbar.addAction(tbNewAction)
        toolbar.addAction(solveAction)
        toolbar.addAction(tbSubmitAction)

    def newBoard(self, size):
        #  Add a scroll area in main Window
        if self.hasPuzzle:  #  there is a board already
            self.clearBoard()  #  clear scroll area
        self.hasPuzzle = True
        self.solveAction.setEnabled(True)
        self.submitAction.setEnabled(True)
        self.tbSubmitAction.setEnabled(True)

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
        with open(assetsPath("information.txt"), "r") as f:
            inf = f.read()
        self.showInformation("About", inf)

    def newAction(self):
        self.inputDialog.show()

    def testAndSave(self):
        if not self.hasPuzzle:
            return
        trees = self.board.getTrees()
        tents_in_row, tents_in_col = self.board.getInputValues()
        grid = Grid(
            self.board.row_size,
            self.board.column_size,
            trees,
            tents_in_row,
            tents_in_col,
        )

        if self.solve():
            self.save(grid)
    
    def setDefaultView(self):
        self.styleFactory.setbg("Default", assetsPath("background.jpg"))

    def setChrismasView(self):
        self.styleFactory.setbg("Christmas", assetsPath("christmas.jpg"))

    def setGalaxyView(self):
        self.styleFactory.setbg("Galaxy", assetsPath("galaxy.jpg"))

    def showInformation(self, typ, text):
        msgBox = QMessageBox()
        pixmap = QPixmap(assetsPath("icon_information.jpg"))
        if typ == "Success":
            pixmap = QPixmap(assetsPath("icon_success.png"))
        elif typ == "Remind":
            pixmap = QPixmap(assetsPath("icon_remind.png"))
        elif typ == "About":
            pixmap = QPixmap(assetsPath("icon_About.jpg"))
        elif typ == "Message":
            pixmap = QPixmap(assetsPath("icon_information.jpg"))

        msgBox.setIconPixmap(pixmap)
        msgBox.setText(text)
        msgBox.setWindowTitle(typ)
        msgBox.setWindowIcon(QIcon(assetsPath("icon.jpg")))
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec()

    def clearTents(self):
        for r in range(self.board.row_size):
            for c in range(self.board.column_size):
                if (r, c) not in self.board.trees:
                    self.board.puzzles[str((r + 1, c + 1))].setPixmap(
                        QPixmap(assetsPath("bg.png"))
                    )

    def solve(self):
        if not self.hasPuzzle:
            return

        self.clearTents()

        trees = self.board.getTrees()
        tents_in_row, tents_in_col = self.board.getInputValues()
        grid = Grid(
            self.board.row_size,
            self.board.column_size,
            trees,
            tents_in_row,
            tents_in_col,
        )

        if sum(tents_in_row) != len(trees) or sum(tents_in_col) != len(trees):
            self.showInformation(
                "Remind",
                "The given number of tents does not match the number of trees.",
            )
            return False

        solution = solveGrid(self.solver_path, grid)
        if solution == None:
            self.showInformation("Remind", "There is no solution for this puzzle!")
            return False

        for (r, c) in solution:
            self.board.puzzles[str((r + 1, c + 1))].setPixmap(
                QPixmap(assetsPath("tent.png"))
            )
        return True

    def save(self, grid):
        path = QFileDialog.getSaveFileName()[0]
        if not path:
            return
        with open(path, "w") as f:
            grid.printPuzzle(f)
        self.showInformation("Success", "The puzzle has been saved :D")


class StyleFactory:
    """Style factory to make new background of board"""
    def __init__(self, app):
        self.app = app
        self.stylesheets = dict()
        self.initStyle()

    def initStyle(self):
        bg_img = assetsPath("background.jpg")
        self.stylesheets["Default"] = self.styleMaker(bg_img)
        self.app.setStyleSheet(self.getStyleSheet("Default"))

    def getStyleSheet(self, subject: str):
        return self.stylesheets[subject]

    def styleMaker(self, bg_img):
        #  stylesheet @ref Chen Xiao, Yang Zhu
        stylesheet = (
            """
        QLabel#counter_block { 
            /* background-color: #d1e7ff; */
            background-color: #dddddd;
            border-radius: 10px; 
        border-radius: 10px; 
            border-radius: 10px; 
            font-size: 16px; 
        font-size: 16px; 
            font-size: 16px; 
            /*font-weight: 500*/
        }
        QScrollArea#board_scroll {
            background-image: url("""
            + bg_img
            + """);
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
        """
        )
        return stylesheet

    def setbg(self, subject: str, path: str):
        bg_img = path
        self.stylesheets[subject] = self.styleMaker(bg_img)
        self.app.setStyleSheet(self.getStyleSheet(subject))


def getArgs():
    """Load args by starting"""
    parser = argparse.ArgumentParser(description="Solve 'Tents' puzzles.")
    parser.add_argument("cadical", help="path to CaDiCal")
    return parser.parse_args()

def getCadical():
    """Get argument cadical as cadical path"""
    return getArgs().cadical


if __name__ == "__main__":
    app = QApplication([])
    styleFactory = StyleFactory(app)
    mw = MainWindow(solver_path=getCadical(), styleFactory=styleFactory)
    mw.show()
    sys.exit(app.exec_())
