import pyodbc

class DB:
    def __init__(self):
        server = "hospitaldb.database.windows.net"
        username = "JETSON_BOARD"
        password = "Database_Hospital@123"
        database = "HospitalDB"

        # self.conn = pymssql.connect(server, user, password, database)
        self.connect = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
        self.cursor = self.connect.cursor()
    
    def Close_Connection(self):
        self.cursor.close()
        self.connect.close()
    
    def Get_Information(self):

        sql_st = 'SELECT * FROM hospital.PATIENT_IMG'
        self.cursor.execute(sql_st)

        self.cursor.execute(sql_st)
        row = self.cursor.fetchone()
        temp = ""
        while row:
            temp = row[2]
            row = self.cursor.fetchone()

        temp = temp.split('/')
        print(len(temp))

db = DB()
db.Get_Information()
db.Close_Connection()