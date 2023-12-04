
import mysql.connector

import pymysql


db = pymysql.connect(host ='teamivy2.cf2oulnhlquf.us-east-2.rds.amazonaws.com', port = 3306, user = 'admin', password = 'password', db = 'TEAMIVY')



cursor = db.cursor()
cursor.execute('SELECT * FROM Officers')
officer_raw = cursor.fetchall()

print(officer_raw)




config = {
  'user': 'root',
  'password': 'root',
  'host': 'localhost',
  'unix_socket': '/Applications/MAMP/tmp/mysql/mysql.sock',
  'database': 'proj', #final_project_testing_1
  'raise_on_warnings': True
}

db2 = mysql.connector.connect(**config)

cursor = db2.cursor()
cursor.execute('SELECT * FROM Users')
officer_raw = cursor.fetchall()

print(cursor.column_names)