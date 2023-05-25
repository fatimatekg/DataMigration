#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import cx_Oracle
from flask import Flask, jsonify, request

# Set the connection parameters
dsn = cx_Oracle.makedsn(host='202.66.172.124', port=1521, sid='C2M2800')
user = 'CISADM'
password = 'CISADM'

# Establish the connection
connection = cx_Oracle.connect(user=user, password=password, dsn=dsn)

# Read select queries from file
with open(os.path.expanduser("~/Desktop/demosa.sql"), 'r') as file:
    select_queries = file.readlines()

# Get account ids from user input
account_ids_str = input("Enter the account IDs separated by comma: ")
account_ids = [acc.strip() for acc in account_ids_str.split(",")]

# Get user_id from user input
user_id = input("Enter the value for USER_ID column: ")

# Build insert queries for each select query and write them to file for each account id
for acc_id in account_ids:
    with open(f'D:/Insert_queries_for {acc_id}.txt', 'w') as file:
        for query in select_queries:
            # Replace account_id placeholder with actual account_id value
            query = query.replace(":account_id", acc_id)

            cursor = connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            column_names = [column[0] for column in cursor.description]

            table_name = query.split()[3]  # Get table name from select query

            for row in rows:
                insert_query = f"INSERT INTO {table_name} ({', '.join(column_names)}) VALUES "

                values = []
                for idx, value in enumerate(row):
                    if value is None:
                        values.append('Null')
                    elif isinstance(value, str):
                        value = value.replace("'", "''")
                        values.append(f"'{value}'")
                    elif isinstance(value, cx_Oracle.Date):
                        value_str = value.strftime("to_date('%d-%b-%y %H:%M:%S','DD-MON-RR HH24:MI:SS')")
                        values.append(value_str)
                    elif isinstance(value, cx_Oracle.LOB):
                        values.append(f"'{value.read()}'")
                    elif isinstance(value, cx_Oracle.Object) and value.type.schema == "MDSYS" and value.type.name == "SDO_GEOMETRY":
                        sdo_geometry_str = "MDSYS.SDO_GEOMETRY("
                        sdo_geometry_str += f"{value.SDO_GTYPE if value.SDO_GTYPE is not None else 'Null'},"
                        sdo_geometry_str += f"{value.SDO_SRID if value.SDO_SRID is not None else 'Null'},"
                        sdo_geometry_str += f"MDSYS.SDO_POINT_TYPE({value.SDO_POINT.X if value.SDO_POINT.X is not None else 'Null'}, {value.SDO_POINT.Y if value.SDO_POINT.Y is not None else 'Null'}, {value.SDO_POINT.Z if value.SDO_POINT.Z is not None else 'Null'}),"
                        sdo_geometry_str += f"{value.SDO_ELEM_INFO if value.SDO_ELEM_INFO is not None else 'Null'},"
                        sdo_geometry_str += f"{value.SDO_ORDINATES if value.SDO_ORDINATES is not None else 'Null'}"
                        sdo_geometry_str += ")"
                        values.append(sdo_geometry_str)
                    else:
                        values.append(str(value))

                    # Check if column name is USER_ID or FREEZE_USER_ID and insert user_id value
                    if column_names[idx] in ['USER_ID', 'FREEZE_USER_ID']:
                        values[-1] = f"'{user_id}'"

                insert_query += f"({', '.join(values)})"
                insert_query += ";\n"
                insert_query += "\n"
                file.write(insert_query)

print("Insert queries generated successfully.")

# Close the connection
connection.close()


# In[1]:


import os
import cx_Oracle
from flask import Flask, jsonify, request
from flask_cors import cross_origin

app = Flask(__name__)
#cors = CORS(app, resources={r"/generate_insert_queries": {"origins": "*"}})
# Set the connection parameters
dsn = cx_Oracle.makedsn(host='202.66.172.124', port=1521, sid='C2M2800')
user = 'CISADM'
password = 'CISADM'

# Read select queries from file
with open(os.path.expanduser("~/Desktop/demosa.sql"), 'r') as file:
    select_queries = file.readlines()



# API endpoint to generate insert queries for given account IDs and user ID
@app.route('/generate_insert_queries', methods=['POST'])
@cross_origin()
def generate_insert_queries():
    try:
        # Get account ids and user id from request data
        account_ids = request.json['account_ids']
        user_id = request.json['user_id']

        # Establish the connection
        connection = cx_Oracle.connect(user=user, password=password, dsn=dsn)

        # Build insert queries for each select query and write them to file for each account id
        for acc_id in account_ids:
            with open(f'D:/Insert_queries_for {acc_id}.txt', 'w') as file:
                for query in select_queries:
                    # Replace account_id placeholder with actual account_id value
                    query = query.replace(":account_id", acc_id)

                    cursor = connection.cursor()
                    cursor.execute(query)
                    rows = cursor.fetchall()
                    column_names = [column[0] for column in cursor.description]

                    table_name = query.split()[3]  # Get table name from select query

                    for row in rows:
                        insert_query = f"INSERT INTO {table_name} ({', '.join(column_names)}) VALUES "

                        values = []
                        for idx, value in enumerate(row):
                            if value is None:
                                values.append('Null')
                            elif isinstance(value, str):
                                value = value.replace("'", "''")
                                values.append(f"'{value}'")
                            elif isinstance(value, cx_Oracle.Date):
                                value_str = value.strftime("to_date('%d-%b-%y %H:%M:%S','DD-MON-RR HH24:MI:SS')")
                                values.append(value_str)
                            elif isinstance(value, cx_Oracle.LOB):
                                values.append(f"'{value.read()}'")
                            elif isinstance(value, cx_Oracle.Object) and value.type.schema == "MDSYS" and value.type.name == "SDO_GEOMETRY":
                                sdo_geometry_str = "MDSYS.SDO_GEOMETRY("
                                sdo_geometry_str += f"{value.SDO_GTYPE if value.SDO_GTYPE is not None else 'Null'},"
                                sdo_geometry_str += f"{value.SDO_SRID if value.SDO_SRID is not None else 'Null'},"
                                sdo_geometry_str += f"MDSYS.SDO_POINT_TYPE({value.SDO_POINT.X if value.SDO_POINT.X is not None else 'Null'}, {value.SDO_POINT.Y if value.SDO_POINT.Y is not None else 'Null'}, {value.SDO_POINT.Z if value.SDO_POINT.Z is not None else 'Null'}),"
                                sdo_geometry_str += f"{value.SDO_ELEM_INFO if value.SDO_ELEM_INFO is not None else 'Null'},"
                                sdo_geometry_str += f"{value.SDO_ORDINATES if value.SDO_ORDINATES is not None else 'Null'}"
                                sdo_geometry_str += ")"
                                values.append(sdo_geometry_str)
                            else:
                                values.append(str(value))

                            # Check if column name is USER_ID or FREEZE_USER_ID and insert user_id value
                            if column_names[idx] in ['USER_ID', 'FREEZE_USER_ID']:
                                values[-1] = f"'{user_id}'"

                        insert_query += f"({', '.join(values)})"
                        insert_query += ";\n"
                        insert_query += "\n"
                        file.write(insert_query)

        # Close the connection
        connection.close()

        # Return success response
        return jsonify({'message': 'Insert queries generated successfully.'}), 200

    except Exception as e:
        # Handle exceptions and return error response
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7000)
    app.run(debug=True)

