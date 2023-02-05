from sqlalchemy import MetaData, create_engine, Table, Column, INTEGER, NUMERIC, DATE, TEXT, inspect
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.exc import ProgrammingError
import SQL

class InteractWithPGSQL():
    def __init__(self, user, password, port, database):
        self.user = user
        self.password = password
        self.port = port
        self.database = database
        self.base = declarative_base()
        self.engine = self.__connectToDBSqlAlc()
        self.sessionMake = sessionmaker(bind=self.engine)
        self.sessionConfig = self.sessionMake.configure(bind=self.engine)
        self.session = Session(self.engine, autocommit=True)

    def __connectToDBSqlAlc(self):
        engine = create_engine(SQL.ConnectionString.format(user = self.user, password = self.password, 
                                                           port= self.port, database= self.database))
        return engine.connect()
    
    def SelectAllTables(self):
        return self.session.execute(SQL.DMLSelectAllTable)
    
    def SelectAllColumnsForTable(self, NameTable):
        return self.session.execute(SQL.DMLSelectAllAttr.format(nameTable = NameTable))
    
    def SaveTable(self, NameTable, Columns, OldNameTable, OldColumns):
        insp = inspect(self.engine)

        if insp.has_table(NameTable) and NameTable == OldNameTable:
            textMsg = self.UpdateTable(NameTable, Columns, OldColumns)
            return textMsg
        elif insp.has_table(NameTable) and NameTable != OldNameTable:
            return 'Таблица с таким именем уже существует, если вы хотите изменить таблицу выберите таблицу из списка слева'
        else:
            metadata = MetaData()
            ListColumns = []

            for column in Columns:
                ListColumns.append(self.__SelectTypeColumn(str(column[1]) + str(column[2]), column[0]))

            CUTable = Table(NameTable, metadata, 
            *ListColumns
            )
            CUTable.create(self.engine, checkfirst=True)
            return 'Таблица создана'

    def RemoveTable(self, NameTable):
        metadata = MetaData()
        DTable = Table(NameTable, metadata)
        DTable.drop(self.engine, checkfirst=True)

    def UpdateTable(self, NameTable, Columns, OldColumns):
        ListUpdateCommand = []
        NewAttr = []
        DropAttr = []
        sqlAlterTable = SQL.DDLAlterTable.format(nameTable = NameTable)

        #[0] - NameAttr [1] - DataType [2] - Primary key
        #Сравнение измененных данных таблицы и таблицы которая существует на данный момент в БД
        #Формирования списка DDL команд изменения таблицы 
        for Column in Columns:
            NewAttr.append(Column[0])
            newColumn = True
            for OldColumn in OldColumns:
                if Column[0] == OldColumn[0]:
                    #Если все атрибуты колонки совпадают то переходим к следующей
                    if Column[1] == OldColumn[1] and Column[2] == OldColumn[2]:
                        newColumn = False
                        break
                    #Добавление/Удаление первичного ключа
                    elif Column[1] == OldColumn[1] and Column[2] != OldColumn[2]:
                        textDDL = self.__AddPrimaryKey(Column[0], Column[2], NameTable)
                        ListUpdateCommand.append(sqlAlterTable + textDDL)
                        newColumn = False
                    #Изменение типа данных колонки
                    elif Column[1] != OldColumn[1]:
                        textDDL = sqlAlterTable + SQL.DDLChangeDataType.format(nameAttr = Column[0], dataType = Column[1], 
                                                                               dataTypeLower = Column[1].lower())
                        ListUpdateCommand.append(textDDL)

                        newColumn = False
                        if Column[2] != OldColumn[2]:
                            textDDL = self.__AddPrimaryKey(Column[0], Column[2], NameTable)
                            ListUpdateCommand.append(sqlAlterTable + textDDL)
                else:
                    continue
            #Если колонка не была обновлена, то добавляем её
            if newColumn:
                ListUpdateCommand.append(sqlAlterTable + SQL.DDLAddAttr.format(nameAttr = Column[0], dataType = Column[1]))
                if Column[2] == 'PK':
                    textDDL = self.__AddPrimaryKey(Column[0], Column[2], NameTable)
                    ListUpdateCommand.append(sqlAlterTable + textDDL)
        
        #Удаленные атрибуты
        DropAttr = [x[0] for x in OldColumns if x[0] not in NewAttr]

        for attr in DropAttr:
            ListUpdateCommand.append(sqlAlterTable + SQL.DDLDropAttr.format(nameAttr = attr))
        textMsg = []
        
        for row in ListUpdateCommand:
            try:
                self.session.execute(row)
            except ProgrammingError as e:
                if 'привести тип numeric к date нельзя' in e.args[0]:
                    textMsg.append('Возникла ошибка при обновлении таблицы, привести тип numeric к date нельзя')
                    continue
                elif 'привести тип integer к date нельзя' in e.args[0]:
                    textMsg.append('Возникла ошибка при обновлении таблицы, привести тип integer к date нельзя')
                    continue
                elif 'привести тип date к numeric нельзя' in e.args[0]:
                    textMsg.append('Возникла ошибка при обновлении таблицы, привести тип date к numeric нельзя')
                    continue
                elif 'привести тип date к integer нельзя' in e.args[0]:
                    textMsg.append('Возникла ошибка при обновлении таблицы, привести тип date к integer нельзя')
                    continue
                elif 'не может иметь несколько первичных ключей' in e.args[0]:
                    textMsg.append('Возникла ошибка при обновлении таблицы,таблица не может иметь несколько первичных ключей')
                    continue
                else:
                    textMsg.append('Возникла ошибка при обновлении таблицы, не обработанное исключение')
                    continue
        if textMsg == []:
            textMsg.append('Таблица обновлена')
        return ", ".join(textMsg)
    
    def __AddPrimaryKey(self, ColumnName, ColumnPK, NameTable):
        if ColumnPK == 'PK':
            return SQL.DDLAddPK.format(nameAttr=ColumnName)
        else:
            Constraint = self.session.execute(SQL.DMLSelectNamePK.format(nameTable = NameTable, nameAttr = ColumnName)).one()[0]
            return SQL.DDLDropPK.format(nameConstr = Constraint)

    def __SelectTypeColumn(self, Type, NameColumn):
        DictClassColumns = {
            'INTEGERPK': Column(NameColumn, INTEGER, primary_key=True),
            'INTEGER': Column(NameColumn, INTEGER),
            'NUMERIC': Column(NameColumn, NUMERIC(10,2)),
            'NUMERICPK': Column(NameColumn, NUMERIC(10,2)),
            'DATE': Column(NameColumn, DATE),
            'DATEPK': Column(NameColumn, DATE),
            'TEXT': Column(NameColumn, TEXT),
            'TEXTPK': Column(NameColumn, TEXT),
        }
        return DictClassColumns[Type]
