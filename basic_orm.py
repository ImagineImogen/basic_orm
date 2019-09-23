import sqlite3


DATABASE_CONNECTION = sqlite3.connect('temporary.db')
CURSOR = DATABASE_CONNECTION.cursor()

COLUMN_PARAMS = {
    "primary_key": "PRIMARY KEY",
    "foreign_key": "FOREIGN KEY",
    "string": "VARCHAR",
    "integer": "INTEGER",
    "required": "NOT NULL",
    "auto_add": "AUTOINCREMENT"
}


class Table:
    @classmethod
    def get_table_name(cls):
        try:
            return cls.__tablename__
        except AttributeError:
            table_name = cls.__name__ + "s"
            return table_name.lower()

    @classmethod
    def transform_column_parameters_to_sql(cls):
        columns = cls.get_column_names_and_values()
        sql_table_details = []
        for column, value in columns:
            sql_attrs = []

            if value.get('type'):
                sql_attrs.append(COLUMN_PARAMS[value['type']])

            if value.get('length'):
                if value.get('auto_add'):
                    continue
                length_with_brackets = "(%s)" % str(value['length'])
                sql_attrs.append(length_with_brackets)

            if value.get('required'):
                sql_attrs.append(COLUMN_PARAMS['required'])

            if value.get('primary_key'):
                sql_attrs.append(COLUMN_PARAMS['primary_key'])

            if value.get('auto_add'):
                if value.get('type') == "integer":
                    sql_attrs.append(COLUMN_PARAMS['auto_add'])

            if value.get('foreign_key'):
                name = cls.get_table_name()
                reference_table_name = [cls.__name__ for cls in Table.__subclasses__() if cls.__name__ != name]
                foreign_key_sql = ", FOREIGN KEY(%s) REFERENCES %s(%s)" % \
                                  (column, reference_table_name[0].lower(), value['foreign_key'])
                sql_attrs.append(foreign_key_sql)

            sql_column_details = '%s %s' % (column, " ".join(sql_attrs))
            sql_table_details.append(sql_column_details)

        return ", ".join(sql_table_details)

    @classmethod
    def get_column_names_and_values(cls):
        column_parameters = [(k, v) for k, v in cls.__dict__.items() if not k.startswith("__")]

        return column_parameters

    @classmethod
    def create_table(cls):
        create = 'CREATE TABLE IF NOT EXISTS %s (%s)' % (
            cls.get_table_name(),
            cls.transform_column_parameters_to_sql()
        )
        DATABASE_CONNECTION.execute("PRAGMA foreign_keys = ON")
        DATABASE_CONNECTION.execute(create)
        print("A new table was created")

    @classmethod
    def delete_table(cls):
        delete_tab = 'DROP TABLE IF EXISTS %s' % (cls.get_table_name())
        DATABASE_CONNECTION.execute(delete_tab)
        print("A table was deleted")

    @classmethod
    def add(cls, *args): #corresponds to INSERT in raw SQL
        column_names = [column_name for column_name in cls.__dict__.keys() if not column_name.startswith("__")]
        columns_to_insert_to = [i for i in args[0].keys() if i in column_names]

        query = 'INSERT INTO %s %s VALUES (%s)' % \
                (cls.get_table_name(), tuple(columns_to_insert_to), " ,".join(['?'] * len(args[0].values())))
        values = []

        for i in range(len(args[0].items())):
            values.append((args[0][tuple(columns_to_insert_to)[i]]))
        CURSOR.execute(query, tuple(values))
        DATABASE_CONNECTION.commit()

    @classmethod
    def update_all (cls, *args):
        if args:
            column_names_to_update = [column for column in args[0].keys()]
            columns_to_update = [column for column in cls.__dict__.keys() if not column.startswith("__")]
            columns = [col for col in column_names_to_update if col in columns_to_update]
            real_values = []
            for i in columns:

                real_values.append(args[0].get(i))
            if len(args) == 1:
                query = 'UPDATE %s SET %s=?' % (
                    cls.get_table_name(),
                    "=?, ".join(columns)
                )
                CURSOR.execute(query, tuple(real_values))
                DATABASE_CONNECTION.commit()

            return "Please use 'update_one' method for updating a specific row value"
        return "Please add parameters"

    @classmethod
    def update_one(cls, *args):
        if len(args) >= 2:
            columns_to_update = [column for column in cls.__dict__.keys() if not column.startswith("__")]
            columns = [column for column in args[0].keys() if column in columns_to_update]
            values = []
            for i in columns:
                values.append(args[0].get(i))
            condition_columns = [condition_column for condition_column in args[1].keys()
                                 if condition_column in columns_to_update]

            if len(condition_columns) != 0:
                condition_values = [condition_value for condition_value in args[1].values()]
                parameters = values + condition_values

                query = "UPDATE %s SET %s=? WHERE %s=?" % (
                    cls.get_table_name(),
                    "=?, ".join(columns),"=?, ".join(condition_columns) )

                CURSOR.execute(query, tuple(parameters))
                DATABASE_CONNECTION.commit()

            return "Your condition column is not valid, please check"

        return "Please give the conditions or use update_all method"


    @classmethod
    def select(cls, *args):
        columns_to_select = [column for column in cls.__dict__.keys() if not column.startswith("__")]
        val_all = [v for v in cls.__dict__.values()]
        dict1 = {}
        fields = cls.get_column_names_and_values()
        for _ in range(2, len(val_all)-1):
            dict1.update(val_all[_])
        if not args: #SELECT *
            if 'foreign_key' in dict1: #Autojoin
                name = cls.get_table_name()
                print(name)
                another_table_name = [cls.__name__ for cls in Table.__subclasses__() if cls.__name__.lower() != name]

                for k, v in fields:
                    if 'foreign_key' in v:
                        select_all = 'SELECT * FROM %s INNER JOIN %s ON %s.%s=%s.%s' % \
                                 ((name, another_table_name[0].lower(), name, k,  another_table_name[0].lower(),  dict1['foreign_key']))
                        cls.sql_execute(select_all)
            else:
                select_all = 'SELECT * FROM %s' % (cls.get_table_name())
                cls.sql_execute(select_all)


        elif type(args[-1]) is str:
            select_by_columns='SELECT %s FROM %s' % (', '.join(args),cls.get_table_name())
            CURSOR.execute(select_by_columns)
            rows = CURSOR.fetchall()
            for row in rows:
                print(row)
        else:

            columns = [column for column in args[-1].keys() if column in columns_to_select]

            values = []
            for i in columns:
                values.append(args[-1].get(i))

            if type(args[0]) == dict:
                query = 'SELECT * FROM %s WHERE %s=?' % (cls.get_table_name(), "=? AND ".join(tuple(columns)))
                CURSOR.execute(query, values)
                rows = CURSOR.fetchall()
                for row in rows:
                    print(row)

            else:
                columns = [column for column in args[-1].keys() if column in columns_to_select]

                values = []
                for i in columns:
                    values.append(args[-1].get(i))
                if args[0] in columns_to_select:
                    print(args[0])
                    query = "SELECT %s FROM %s WHERE %s=?" % (
                        args[0], cls.get_table_name(), '=? AND '.join(tuple(columns)))
                    CURSOR.execute(query, values)
                    rows = CURSOR.fetchall()
                    for row in rows:
                        print(row)


                return "Such column doesn't exist, please check"

    @classmethod
    def sql_execute(self, select_all):
        CURSOR.execute(select_all)
        rows = CURSOR.fetchall()
        for row in rows:
            print(row)

    @staticmethod
    def close():
        CURSOR.close()
        DATABASE_CONNECTION.close()
