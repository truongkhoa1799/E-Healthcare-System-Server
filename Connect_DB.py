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
        row = self.cursor.fetchone()
        temp = ""
        while row:
            temp = row[2]
            row = self.cursor.fetchone()

        temp = temp.split('/')
        print(len(temp))
    
    def Get_Available_Device_ID(self):
        sql_st = 'SELECT MAX(Device_ID) AS max_device FROM hospital.DEVICE;'
        self.cursor.execute(sql_st)
        row = self.cursor.fetchone()
        if row.max_device == None:
            return 1
        else:
            return int(row[-1]) + 1

# MODULE FOR CREATE_NEW_DEVICE
    # return: 0: exist, -1 not exist hospital_id
    def Check_Valid_Hospital(self, hospital_id):
        sql_st = '''SELECT 1
                    FROM hospital.HOSPITAL AS H
                    WHERE H.Hospital_ID = {};'''.format(hospital_id)
        self.cursor.execute(sql_st)
        row = self.cursor.fetchone()

        if row != None:
            return 0
        else:
            return -1

    # return: 0: exist, -1 not exist hospital_id
    def Check_Valid_Buidling(self, hospital_id, building_code):
        sql_st = '''SELECT 1
                    FROM hospital.BUILDING AS B
                    WHERE   B.Hospital_ID = {}
                        AND B.Building_Code = '{}';'''.format(hospital_id, building_code)
        self.cursor.execute(sql_st)
        row = self.cursor.fetchone()

        if row != None:
            return 0
        else:
            return -1

    # return: 0: exist, -1 not exist hospital_id
    def Check_Valid_Device(self, device_code):
        sql_st = '''SELECT 1
                    FROM hospital.DEVICE AS D
                    WHERE D.Device_Code = '{}';'''.format(device_code)
        self.cursor.execute(sql_st)
        row = self.cursor.fetchone()

        if row == None:
            return 0
        else:
            return -1
    
    def Insert_New_Device(self, device_id, device_code, hospital_id, building_code):
        ret = -1
        sql_st = """\
        DECLARE @return_status INT;
            EXEC hospital.Add_Device \
            @Device_ID = {}, \
            @Device_Code = '{}', \
            @Hospital_ID = {}, \
            @Building_Code = '{}', \
            @para_out = @return_status OUTPUT;
        SELECT @return_status as ret;
        """.format(device_id, device_code, hospital_id, building_code)
        try:
            self.cursor.execute(sql_st)
            row = self.cursor.fetchone()
            ret = row.ret
            self.cursor.commit()
        except Exception as ex:
            print ( "\tUnexpected error {0} while create new device".format(ex))

        return ret

db = DB()
# print(db.Get_Available_Device_ID())
# id = db.Check_Valid_Hospital(2)
# print(id)
# id = db.Check_Valid_Buidling(1, 'A1')
# print(id)
# id = db.Check_Valid_Device('XB00000000')
# print(id)
# db.Close_Connection()

# print(db.Insert_New_Device(1, 'XB00000000', 1, 'A1'))