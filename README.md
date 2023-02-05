### Десктоп приложение для взаимодействия с СУБД PostgreSQL. ###
Для подключения к другой СУБД, нужно изменить строку подключения и запросы в файле SQL.py.

По умолчанию строка подключения имеет тип postgresql://user:password@localhost:port/database.

Данное приложение позволяет добавлять таблицы, удалять таблицы, изменять таблицы, а точнее добавлять/удалять атрибуты в таблицах, изменять тип данных атрибутов, присваивать первичные ключи.

Приложение поддерживает работу с типами данных(INTEGER, TEXT, DATE, NUMERIC(10,2))

При запуске приложение запрашивает данные для подключения
![FirstWindow](https://github.com/IvanPermyakov/InterfaceForDB/blob/main/Picture/FirstWindow.JPG)

После подключения открывается основное окно приложения
![MainWindow](https://github.com/IvanPermyakov/InterfaceForDB/blob/main/Picture/MainWindow.JPG)

1) Таблица со списком таблиц хранящихся в БД, при двойном щелчке по наименованию таблицы  все её атрибуты открываются в правой таблице 
2) Таблица со списком всех атрибутов таблицы, в ней содержатся наименования атрибутов, тип данных атрибута и является ли атрибут первичным ключом
3) Кнопка "Drop table" при выделении ячейки в левой таблице и нажатии на кнопку происходит удаление таблицы из БД
4) TextBox содержит наименование таблицы
5) Кнопка "Clear" очищает правую таблицу и TextBox
6) Кнопка "Save" сохраняет изменения хранящиеся в правой таблице
7) Кнопка "Add attribute" добавляет строку в правую таблицу
8) Кнопка "Del attribute" удаляет выделенную строку в правой таблице

Для изменения уже созданной таблицы нужно:
1) Выбрать её из списка в левой таблице
2) Провести каки-либо изменения
3) Нажать на кнопку "Save"

Для создания новой таблицы
1) Задать уникальное наименование таблицы в TextBox'e
2) Добавить необходимое количество атрибутов
3) Нажать на кнопку "Save"