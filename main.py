import pymssql

server = "hospitaldb.database.windows.net"
user = "JETSON_BOARD"
password = "Database_Hospital@123"

conn = pymssql.connect(server, user, password, "HospitalDB")
cursor = conn.cursor()

sql_st = 'SELECT * FROM hospital.PATIENT_IMG'
cursor.execute(sql_st)

cursor.execute(sql_st)
row = cursor.fetchone()
temp = ""
while row:
    temp = row[2]
    row = cursor.fetchone()
conn.close()

temp = temp.split('/')
print(len(temp))