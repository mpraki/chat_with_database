SCHEMA_DESCRIPTION = """Parse the data structure and For each item in the data structure,
    add a "description" field with a concise explanation of the column's purpose (15-50 words)
    and return the updated list of items. Do not add any additional text. Return only the list of items in python dict type.
    Do not include any code block delimiters like ```python or ``` in your response.
     e.g.: [{{'TableName': 'employees', 'ColumnName': 'employee_id', 'DataType':
    'bigint', 'MaxLength': 8, 'IsNullable': False, 'CONSTRAINT_TYPE': 'PRIMARY_KEY_CONSTRAINT', 'ConstraintName':
    'employees_pk', 'ReferencedTable': None, 'ReferencedColumn': None, 'description': 'Unique identifier for each employee record.
    Serves as the primary key and is used to reference employees throughout the system.'}},
    {{'TableName': 'employees', 'ColumnName': 'department_id', 'DataType': 'bigint', 'MaxLength': 8, 'IsNullable': False,
    'CONSTRAINT_TYPE': 'FOREIGN KEY', 'ConstraintName': 'employees_department_id_fk', 'ReferencedTable': 'departments',
    'ReferencedColumn': 'department_id', 'description': 'References the department the employee belongs to.
    Ensures that each employee is linked to a valid department in the departments table.'}}] data_structure: {data_structure}"""
