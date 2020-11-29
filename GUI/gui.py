import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class mainGUI(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.inputDialog = InputDialog(self)
        self.mainvbox = QVBoxLayout()
        self.puzzles = dict()
        self.inputDialog.accepted.connect(self.createPuzzleMap)
        self.initUI()
        
    def initUI(self):
        #  set up icon
        self.setWindowTitle('Icon')
        self.setWindowIcon(QIcon('bild/icon.jpg'))

        #  set up menu bar
        menubar = self.menuBar()
        file = menubar.addMenu("File")
        newAction = QAction('New', self)
        newAction.setIcon(QIcon('bild/icon_new.png'))
        newAction.setShortcut('Ctrl+N')
        newAction.setStatusTip('New puzzle')
        newAction.triggered.connect(self.newAction)
        submitAction = QAction('Test&Save', self)
        submitAction.setIcon(QIcon('bild/icon_save.png'))
        submitAction.setShortcut('Ctrl+S')
        submitAction.setStatusTip('Test&Save')
        newAction.triggered.connect(self.save)
        quit = menubar.addMenu("Quit")
        quitAction = QAction('Quit', self)
        quitAction.setIcon(QIcon('bild/icon_quit.png'))
        quitAction.setShortcut('Ctrl+Q')
        quitAction.setStatusTip('Quit puzzle')
        quitAction.triggered.connect(self.close)

        file.addAction(newAction)
        file.addAction(submitAction)
        quit.addAction(quitAction)

        #  set up new puzzle
        mainWid = QWidget()
        mainWid.setStyleSheet("background-color: rgb(209, 186, 116)")
        mainWid.setLayout(self.mainvbox)
        self.setCentralWidget(mainWid)

        #  set up window
        self.setGeometry(400, 100, 350, 350)

    #  TODO: save tree and number
    def save(self):
        print("saved")

    def newAction(self):
        self.inputDialog.show()
    #  TODO: clearMap
    def clearMap(self, map):
        pass

    def plantTree(self, i,j):
        self.puzzles[str((i, j))].setPixmap(QPixmap('bild/tree.png'))
    
    def cutTree(self, i,j):
        self.puzzles[str((i, j))].setPixmap(QPixmap('bild/bg.png'))
        
    def createPuzzleMap(self, size):
        #  TODO:self.clearMap()
        map = QVBoxLayout()
        map.setContentsMargins(0, 0, 0, 0)
        map.setSpacing(0)
        self.puzzles.clear()
        columnSize = int(size['columnSize'])
        rowSize = int(size['rowSize'])
        for i in range(rowSize):
            hbox = QHBoxLayout()
            hbox.setContentsMargins(0, 0, 0, 0)
            hbox.setSpacing(0)
            for j in range(columnSize):
                pb = PuzzleBolck(i, j)
                hbox.addWidget(pb)
                self.puzzles[str((i, j))]=pb
                self.puzzles[str((i, j))].clicked.connect(self.plantTree)
                self.puzzles[str((i, j))].rightClicked.connect(self.cutTree)
                if j == columnSize - 1:
                    pb = PaddingBlock(i, j + 1)
                    nb = NumberBlock(i, j + 2, columnSize)
                    hbox.addWidget(pb)
                    hbox.addWidget(nb)
                    map.addLayout(hbox)
                    self.puzzles[str((i, j + 1))] = pb
                    self.puzzles[str((i, j + 2))] = nb
                    if i == rowSize - 1:
                        phbox = QHBoxLayout()
                        phbox.setContentsMargins(0,0,0,0)
                        phbox.setSpacing(0)
                        nhbox = QHBoxLayout()
                        nhbox.setContentsMargins(0,0,0,0)
                        nhbox.setSpacing(0)
                        for m in range(columnSize+2):
                            pb = PaddingBlock(i + 1, m)
                            phbox.addWidget(pb)
                            self.puzzles[str((i + 1, m))] = pb
                        map.addLayout(phbox)

                        for m in range(columnSize + 2):
                            if m < columnSize:
                                nb = NumberBlock(i + 2, m, columnSize)
                                nhbox.addWidget(nb)
                                self.puzzles[str((i + 2, m))] = nb
                            else:
                                pb = PaddingBlock(i + 2, m)
                                nhbox.addWidget(pb)
                                self.puzzles[str((i + 2, m))] = pb
                        map.addLayout(nhbox)
        self.mainvbox.addLayout(map)
        self.sumbit = QPushButton('OK')


class InputDialog(QDialog):
    
    accepted = pyqtSignal(dict)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #  maximal 80 * 80
        self.int = QIntValidator(1, 80, self)

        self.rowSize = QLineEdit(self)
        self.columnSize = QLineEdit(self)

        self.rowSize.setValidator(self.int)
        self.columnSize.setValidator(self.int)

        self.rowSize.textEdited[str].connect(self.enable)
        self.columnSize.textEdited[str].connect(self.enable)

        self.button = QPushButton('OK')
        self.button.setDisabled(True)
        self.button.clicked.connect(self.create)

        form = QFormLayout(self)
        form.addRow('row: ', self.rowSize)
        form.addRow('column: ', self.columnSize)
        form.addRow(self.button)

    def enable(self):
        if self.rowSize.text() and self.columnSize.text():
            self.button.setEnabled(True)
        else:
            self.button.setDisabled(True)

    def create(self):
        values = {'rowSize': self.rowSize.text(),
                  'columnSize': self.columnSize.text()}
        self.accepted.emit(values)
        self.accept()


class PuzzleBolck(QLabel):
    clicked = pyqtSignal(int,int)
    rightClicked = pyqtSignal(int,int)
    
    def __init__(self, i, j):
        super().__init__()
        self.x = i * 2
        self.y = j * 2
        self.initUI()

    def initUI(self):
        self.setStyleSheet("border: 0.5px solid black")
        self.setPixmap(QPixmap("bild/bg.png"))
        self.adjustSize()
        self.setScaledContents(True)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.setMinimumSize(5, 5)
        self.setGeometry(400 + self.x, 100 + self.y, 10, 10)

    def mousePressEvent(self, ev):
        i, j  = int(self.x/2), int(self.y/2)

        if ev.button()==Qt.RightButton:
            self.rightClicked.emit(i, j)
        else:
            self.clicked.emit(i, j)


class PaddingBlock(QLabel):
    
    def __init__(self, i, j):
        super().__init__()
        self.x = i * 2
        self.y = j * 2
        self.initUI()

    def initUI(self):
        self.setStyleSheet("border: 0.1px solid black")
        #self.setPixmap(QPixmap("bild/bg.png"))
        self.adjustSize()
        self.setScaledContents(True)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.setMinimumSize(5, 5)
        self.setGeometry(400 + self.x, 100 + self.y, 10, 10)


class NumberBlock(QWidget):

    def __init__(self, i, j, max):
        super().__init__()
        self.x = i * 2
        self.y = j * 2
        self.inputLine = QLineEdit(self)
        self.inputLine.setText("0")
        self.vlidator = QIntValidator(0, max, self)
        self.inputLine.setValidator(self.vlidator)
        self.initUI()

    def initUI(self):
        self.setStyleSheet("border: 1px solid black")
        self.setMinimumSize(5, 5)
        self.setGeometry(400 + self.x, 100 + self.y, 10, 10)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = mainGUI()
    gui.show()
    sys.exit(app.exec_()) 

