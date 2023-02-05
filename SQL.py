#Строка подключения к СУБД
ConnectionString = 'postgresql://{user}:{password}@localhost:{port}/{database}'

#Для выборки всех таблиц из БД
DMLSelectAllTable = "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"

#Для выборки всех атрибутов таблицы
DMLSelectAllAttr = ("SELECT c.column_name, c.data_type, tc.PK "+ 
        "FROM information_schema.columns c "+
        "LEFT JOIN (SELECT c.column_name, 'PK' as PK "+
                    "FROM information_schema.table_constraints tc "+
                    "JOIN information_schema.constraint_column_usage AS ccu USING (constraint_schema, constraint_name) "+
                    "JOIN information_schema.columns AS c ON c.table_schema = tc.constraint_schema "+
                    "AND tc.table_name = c.table_name AND ccu.column_name = c.column_name "+
                    "WHERE constraint_type = 'PRIMARY KEY' and tc.table_name = '{nameTable}') tc ON tc.column_name = c.column_name "+
        "WHERE c.table_name = '{nameTable}'")

#Получение имени первичного ключа таблицы
DMLSelectNamePK = ("select constraint_name from information_schema.constraint_column_usage " +
                    "where table_name = '{nameTable}' and column_name = '{nameAttr}'")

#Изменение таблицы
DDLAlterTable = 'ALTER TABLE "{nameTable}" '

#Изменение типа данных колонки
DDLChangeDataType = "ALTER COLUMN {nameAttr} TYPE {dataType} USING {nameAttr}::{dataTypeLower}"

#Добавление нового атрибута в таблицу
DDLAddAttr = "ADD {nameAttr} {dataType}"

#Удаление атрибута в таблице
DDLDropAttr = 'DROP COLUMN "{nameAttr}"'

#Добавление первичного ключа в таблицу
DDLAddPK = "ADD PRIMARY KEY ({nameAttr})"

#Удаление первичного ключа в таблице
DDLDropPK = 'DROP CONSTRAINT "{nameConstr}"'
