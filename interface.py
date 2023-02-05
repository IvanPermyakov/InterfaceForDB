from PyQt6.QtWidgets import QAbstractItemView, QApplication, QMessageBox, QMainWindow, QLabel, QLineEdit, QTableWidgetItem, QWidget, QTableWidget, QPushButton, QGridLayout, QComboBox
from PyQt6.QtCore import Qt
from InteractionWithDB import InteractWithPGSQL
from sqlalchemy.exc import InternalError
import sys 

class MainWindow(QMainWindow):
    def __init__(self, UserName, Password, Port, Database):
        super().__init__()
        self.resize(700, 700)
        self.setWindowTitle('MainWindow')

        self.DictDataType = {'': 0, 'INTEGER': 1, 'NUMERIC': 2, 'TEXT': 3, 'DATE': 4}
        self.DictPK = {'': 0, 'PK': 1}
        self.fixActualTable = [] #Список для хранения данных о актуальных колонках, для дальнейшего обновления таблицы
        self.actualNameTable = None

        #Центральный виджет
        CentralWidget = QWidget(self) 
        self.setCentralWidget(CentralWidget)

        Grid = QGridLayout()             
        CentralWidget.setLayout(Grid) 
        self.Connect = InteractWithPGSQL(UserName, Password, Port, Database)

        #Drop table
        self.ButtonDropTable = QPushButton('Drop table')
        self.ButtonDropTable.clicked.connect(self.DropTable)
        Grid.addWidget(self.ButtonDropTable, 1, 0)

        #Выборка и добавление всех таблиц на форму
        self.Table = QTableWidget(self) 
        self.Table.setColumnCount(1)  
        self.Table.setHorizontalHeaderLabels(["Tables"])
        self.Table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.Table.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.InsertNameTablesInTable()
        self.Table.resizeColumnsToContents()
        self.Table.doubleClicked.connect(self.SlotDoubleClicked)
        Grid.addWidget(self.Table, 2, 0, 2, 1)
        #Grid.setColumnStretch(0, 1)

        #Наименование таблицы
        self.LineNameTable = QLineEdit()
        Grid.addWidget(self.LineNameTable, 0, 2)

        #Очистка таблицы колонок
        self.ButtonClear = QPushButton('Clear')
        self.ButtonClear.clicked.connect(self.ClearTableCreation)
        Grid.addWidget(self.ButtonClear, 0, 3)

        #Сохранение таблицы и изменений
        self.ButtonSave = QPushButton('Save')
        self.ButtonSave.clicked.connect(self.SaveTable)
        Grid.addWidget(self.ButtonSave, 0, 4)

        #Добавление строки в таблицу колонок
        self.ButtonAddRow = QPushButton('Add attribute')
        self.ButtonAddRow.clicked.connect(self.AddRow)
        Grid.addWidget(self.ButtonAddRow, 1, 3)

        #Удаление строки из таблицы колонок
        self.ButtonAddRow = QPushButton('Del attribute')
        self.ButtonAddRow.clicked.connect(self.DelRow)
        Grid.addWidget(self.ButtonAddRow, 1, 4)

        #Таблица колонок
        self.CreationTable = QTableWidget(self) 
        self.CreationTable.setColumnCount(3) 
        self.CreationTable.setRowCount(1) 
        self.CreationTable.setHorizontalHeaderLabels(["Name column", "Data type", "Primary key"])
        self.CreationTable.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.CreationTable.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        comboDT = self.ComboBox(self.DictDataType)
        comboPK = self.ComboBox(self.DictPK)
        self.CreationTable.setCellWidget(0, 1, comboDT)
        self.CreationTable.setCellWidget(0, 2, comboPK)

        Grid.addWidget(self.CreationTable, 2, 2, 2, 5)
        Grid.setColumnStretch(2, 5)

    #Drop table
    def DropTable(self):
        try:
            nameTable = self.Table.currentItem().text()
            self.Connect.RemoveTable(nameTable)
            row = self.Table.currentRow()
            self.Table.removeRow(row)
        except AttributeError:
            self.MessageBox('Выберите таблицу которую хотите удалить')
        except InternalError:
            self.MessageBox('Таблица имеет ограничение')

    #Выборка и добавление всех таблиц на форму
    def InsertNameTablesInTable(self):
        tables = self.Connect.SelectAllTables()
        self.Table.setRowCount(tables.rowcount)
        for i, cell in enumerate(tables):
            self.Table.setItem(i, 0, QTableWidgetItem(cell[0]))

    #Событие на двойное нажатие мышкой по таблице и загрузка ее колонок в таблицу колонок
    def SlotDoubleClicked(self, mi):
        self.CreationTable.clearContents()
        nameTable = mi.data()
        self.actualNameTable = nameTable
        self.LineNameTable.setText(nameTable)
        self.InsertInfoInTable(nameTable)

    #Заполнение таблицы колонок
    def InsertInfoInTable(self, nameTable):    
        self.fixActualTable = []
        infoColumn = self.Connect.SelectAllColumnsForTable(nameTable)
        self.CreationTable.setRowCount(infoColumn.rowcount)
        for i, column in enumerate(infoColumn):
            rowActualTable = []

            self.CreationTable.setItem(i, 0, QTableWidgetItem(column[0]))
            rowActualTable.append(column[0])

            comboDT = self.ComboBox(self.DictDataType)
            try:
                comboDT.setCurrentIndex(self.DictDataType[column[1].upper()])
            except KeyError:
                comboDT.setCurrentIndex(0)
            self.CreationTable.setCellWidget(i, 1, comboDT)
            rowActualTable.append(comboDT.currentText())

            comboPK = self.ComboBox(self.DictPK)
            if column[2] is not None:
                comboPK.setCurrentIndex(self.DictPK[column[2].upper()])
            else:
                comboPK.setCurrentIndex(0)
            self.CreationTable.setCellWidget(i, 2, comboPK)
            rowActualTable.append(comboPK.currentText())
            self.fixActualTable.append(rowActualTable)

    #Очистка таблицы колонок
    def ClearTableCreation(self):
        self.CreationTable.clearContents()
        self.CreationTable.setRowCount(0)
        self.AddRow()
        self.LineNameTable.clear()

    #Добавление строки в таблицу колонок
    def AddRow(self):
        self.CreationTable.setRowCount(self.CreationTable.rowCount() + 1)
        comboDT = self.ComboBox(self.DictDataType)
        self.CreationTable.setCellWidget(self.CreationTable.rowCount()-1, 1, comboDT)
        comboPK = self.ComboBox(self.DictPK)
        self.CreationTable.setCellWidget(self.CreationTable.rowCount()-1, 2, comboPK)

    #Удаление строки из таблицы колонок
    def DelRow(self):
        row = self.CreationTable.currentRow()
        self.CreationTable.removeRow(row)

    #Сохранение таблицы и изменений
    def SaveTable(self):
        rows = self.CreationTable.rowCount()
        cols = self.CreationTable.columnCount()
        dataTable = []
        for row in range(rows):
            dataRow = []
            for col in range(cols):
                try:
                    if col == 0:
                        dataRow.append(self.CreationTable.item(row,col).text())
                    else:
                        dataRow.append(self.CreationTable.cellWidget(row, col).currentText())
                except:
                    break
            dataTable.append(dataRow)
        if self.LineNameTable.text() == '':
            self.MessageBox('Введите имя таблицы')
        else:
            messageText = self.Connect.SaveTable(self.LineNameTable.text(), dataTable, self.actualNameTable, self.fixActualTable)
            self.MessageBox(messageText)
            #Обновление таблиц в списке таблиц
            self.InsertNameTablesInTable()
            #Обновление колонок в таблице колонок
            self.InsertInfoInTable(self.LineNameTable.text())


    class ComboBox(QComboBox):
        def __init__(self, Dict):
            super().__init__()
            self.addItems(Dict.keys())
            self.currentIndexChanged.connect(self.getComboValue)

        def getComboValue(self):
            return self.currentText()
        
    class MessageBox(QMessageBox):
        def __init__(self, message):
            super().__init__()
            self.setIcon(QMessageBox.Icon.Information)
            self.setText(message)
            self.setWindowTitle(message)
            self.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            self.exec()
            

class FirstWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(300, 100)
        self.setWindowTitle('Подключение к базе данных')

        #Центральный виджет
        CentralWidget = QWidget(self) 
        self.setCentralWidget(CentralWidget)

        Grid = QGridLayout()             
        CentralWidget.setLayout(Grid)  

        self.LabelUser = QLabel('Имя пользователя:')
        self.LineUser = QLineEdit()
        self.LabelPass = QLabel('Пароль:')
        self.LinePass = QLineEdit()
        self.LabelPort = QLabel('Порт:')
        self.LinePort = QLineEdit()
        self.LabelDB = QLabel('База данных:')
        self.LineDB = QLineEdit()
        self.Button = QPushButton('Подключить')

        Grid.addWidget(self.LabelUser, 0, 0)
        Grid.addWidget(self.LineUser, 0, 1)
        Grid.addWidget(self.LabelPass, 1, 0)
        Grid.addWidget(self.LinePass, 1, 1)
        Grid.addWidget(self.LabelPort, 2, 0)
        Grid.addWidget(self.LinePort, 2, 1)
        Grid.addWidget(self.LabelDB, 3, 0)
        Grid.addWidget(self.LineDB, 3, 1)
        Grid.addWidget(self.Button, 4, 0)

class TechWindow(QMainWindow):
    def __init__(self):
        super(TechWindow, self).__init__()
        self.setWindowTitle('MainWindow')

    def ShowFirstWindow(self):
        self.FirstWindow = FirstWindow()
        self.FirstWindow.Button.clicked.connect(self.ShowMainWindow)
        self.FirstWindow.Button.clicked.connect(self.FirstWindow.close)
        self.FirstWindow.show()

    def ShowMainWindow(self):
        self.w2 = MainWindow(self.FirstWindow.LineUser.text(), self.FirstWindow.LinePass.text(), self.FirstWindow.LinePort.text(), self.FirstWindow.LineDB.text())
        self.w2.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = TechWindow()
    w.ShowFirstWindow()
    app.exec()   
