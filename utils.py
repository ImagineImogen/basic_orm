

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
        from basic_orm import Session
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
                reference_table_name = [cls.__name__ for cls in Session.__subclasses__() if cls.__name__ != name]
                foreign_key_sql = ", FOREIGN KEY(%s) REFERENCES %s(%s)" % \
                                  (column, reference_table_name[0], value['foreign_key'])
                sql_attrs.append(foreign_key_sql)

            sql_column_details = '%s %s' % (column, " ".join(sql_attrs))
            sql_table_details.append(sql_column_details)

        return ", ".join(sql_table_details)

    @classmethod
    def get_column_names_and_values(cls):
        column_parameters = [(k, v) for k, v in cls.__dict__.items() if not k.startswith("__")]

        return column_parameters
