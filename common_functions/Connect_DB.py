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
        try:
            sql_st = 'SELECT MAX(Device_ID) AS max_device FROM hospital.DEVICE;'
            self.cursor.execute(sql_st)
            row = self.cursor.fetchone()
            if row.max_device == None:
                return 1
            else:
                return int(row[-1]) + 1
        except Exception as ex:
            print("\tUnexpected error {0} while get available device_ID".format(ex))
            return None

# MODULE FOR CREATE_NEW_DEVICE
    # return: 0: exist, -1 not exist hospital_id
    def Check_Valid_Hospital(self, hospital_ID):
        try:
            sql_st = '''SELECT 1
                        FROM hospital.HOSPITAL AS H
                        WHERE H.Hospital_ID = {};'''.format(hospital_ID)
            self.cursor.execute(sql_st)
            row = self.cursor.fetchone()

            if row != None:
                return 0
            else:
                return -1
        except Exception as ex:
            print ( "\tUnexpected error {0} while check valid hospital".format(ex))

    # return: 0: exist, -1 not exist hospital_id
    def Check_Valid_Buidling(self, hospital_ID, building_code):
        try:
            sql_st = '''SELECT 1
                        FROM hospital.BUILDING AS B
                        WHERE   B.Hospital_ID = {}
                            AND B.Building_Code = '{}';'''.format(hospital_ID, building_code)
            self.cursor.execute(sql_st)
            row = self.cursor.fetchone()

            if row != None:
                return 0
            else:
                return -1
        except Exception as ex:
            print ( "\tUnexpected error {0} while check valid bulding".format(ex))

    # return: 0: exist, -1 not exist hospital_id
    def Check_Valid_Device(self, device_code):
        try:
            sql_st = '''SELECT 1
                        FROM hospital.DEVICE AS D
                        WHERE D.Device_Code = '{}';'''.format(device_code)
            self.cursor.execute(sql_st)
            row = self.cursor.fetchone()

            if row == None:
                return 0
            else:
                return -1
        except Exception as ex:
            print ( "\tUnexpected error {0} while check valid new device".format(ex))
    
    def Insert_New_Device(self, device_ID, device_code, hospital_ID, building_code):
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
        """.format(device_ID, device_code, hospital_ID, building_code)
        try:
            self.cursor.execute(sql_st)
            row = self.cursor.fetchone()
            ret = row.ret
            self.cursor.commit()
        except Exception as ex:
            print ( "\tHas error when insert device information: {}".format(msg))
            return None

        return ret, ""

    def Delete_All_Device(self):
        ret = -1
        sql_st = """\
            DELETE from hospital.device;
        """
        try:
            self.cursor.execute(sql_st)
            self.cursor.commit()
            return 0
        except Exception as ex:
            print ( "\tUnexpected error {0} while create new device".format(ex))

        return ret

    def Get_Patient_Information(self, user_ID):
        # Get Name, birthday, Phone, Address
        sql_st = '''
            SELECT CONCAT(Last_Name, ' ', First_Name) AS Name, Date_Of_Birth, Phone_Number, Address
            FROM hospital.PATIENT
            WHERE Patient_ID = {};
        '''.format(user_ID)
        try:
            self.cursor.execute(sql_st)
            row = self.cursor.fetchone()
            return 0, row[0], row[1], row[2], row[3]
        except Exception as e:
            print("Has error when getting patient information: {}".format(e))
            return -1, 0, 0, 0, 0
    
    def Insert_New_Patient(self, first_name, last_name, date_of_birth, gender, address, phone_number, ssn, user_name, password, e_mail):
        patient_ID = None
        sql_st = """\
        DECLARE @ret_patient_ID INT;
        DECLARE @Patient_ID INT;
            EXEC hospital.Add_Patient \
            @First_Name = '{}', \
            @Last_Name = '{}', \
            @Date_Of_Birth = '{}', \
            @Gender = '{}', \
            @Address = '{}', \
            @Phone_Number = '{}', \
            @SSN = '{}', \
            @User_Name = '{}', \
            @Password = '{}', \
            @E_Mail = '{}', \
            @ret_patient_ID = @ret_patient_ID OUTPUT;
        SELECT @ret_patient_ID as ret_patient_ID;
        """.format(first_name, last_name, date_of_birth, gender, address, phone_number, ssn, user_name, password, e_mail)
        try:
            self.cursor.execute(sql_st)
            row = self.cursor.fetchone()
            patient_ID = row.ret_patient_ID
            self.cursor.commit()
        except Exception as ex:
            print ( "\tHas error at module: Insert_New_Patient in Connect_DB. {} ".format(ex))

        return patient_ID
    
    def Insert_Patient_Img(self, patient_ID, image):
        ret = -1
        sql_st = """\
        DECLARE @return_status INT;
        EXEC hospital.Insert_Img
            @Patient_ID = {},
            @Img = '{}',
            @para_out = @return_status OUTPUT;
        SELECT @return_status as ret;
        """.format(patient_ID, image)
        try:
            self.cursor.execute(sql_st)
            row = self.cursor.fetchone()
            ret = row.ret
            self.cursor.commit()
        except Exception as ex:
            print ( "\tUnexpected error {0} while insert image patient".format(ex))

        return ret
    
    def Delete_Patient(self, patient_ID):
        ret = -1
        sql_st = """\
            DELETE hospital.Patient
            WHERE Patient_ID = {};
        """.format(patient_ID)
        try:
            self.cursor.execute(sql_st)
            self.cursor.commit()
            return 0
        except Exception as ex:
            print ( "\tUnexpected error {0} while delete new patient".format(ex))
        return ret
    
    def Delete_Patien_Img(self, patient_ID):
        ret = -1
        sql_st = """\
            DELETE hospital.PATIENT_IMG
            WHERE Patient_ID = {};
        """.format(patient_ID)
        try:
            self.cursor.execute(sql_st)
            self.cursor.commit()
            return 0
        except Exception as ex:
            print ( "\tUnexpected error {0} while delete new patient".format(ex))
        return ret

# db = DB()
# print(db.Get_Available_Device_ID())
# id = db.Check_Valid_Hospital(2)
# print(id)
# id = db.Check_Valid_Buidling(1, 'A1')
# print(id)
# id = db.Check_Valid_Device('XB00000000')
# print(id)
# db.Close_Connection()

# print(db.Insert_New_Device(1, 'XB00000000', 1, 'A1'))

# print(db.Delete_Device(1))

# print(db.Insert_New_Patient('Hao', 'Dang Hoan', '2000-10-01', 'm', '123 Ly Thuong Kiet', '0990123432', '024582293', 'hao.dang123', 'hoas1234', 'hao@hotmail.com'))

# print(db.Insert_Patient_Img(4, '-0.14538502693176269531/0.07711523771286010742/-0.02651930972933769226/-0.07749503850936889648/-0.09596652537584304810/0.02902343124151229858/-0.04959616065025329590/-0.13908588886260986328/0.15207332372665405273/-0.10876959562301635742/0.30567070841789245605/-0.07628138363361358643/-0.21351784467697143555/-0.10681584477424621582/-0.04293793439865112305/0.19230733811855316162/-0.18567499518394470215/-0.17979717254638671875/-0.02217222377657890320/-0.05868885666131973267/0.05365453660488128662/-0.00161781976930797100/-0.01889562979340553284/0.09524535387754440308/-0.11470939964056015015/-0.35909205675125122070/-0.06547828018665313721/-0.18791122734546661377/0.01396851614117622375/-0.12531945109367370605/-0.01996726356446743011/0.01166521012783050537/-0.15482190251350402832/-0.06691932678222656250/0.06035837531089782715/0.10904476046562194824/-0.05442344397306442261/-0.03158504515886306763/0.22477501630783081055/0.02332936227321624756/-0.15120297670364379883/0.05060161650180816650/0.01816993951797485352/0.27390280365943908691/0.16293142735958099365/0.09317749738693237305/0.00859366171061992645/-0.15666612982749938965/0.15373530983924865723/-0.21228690445423126221/0.07227448374032974243/0.11011874675750732422/0.13214278221130371094/0.06566468626260757446/0.04283107072114944458/-0.16567899286746978760/-0.03069698810577392578/0.09851173311471939087/-0.27845495939254760742/0.03724094480276107788/-0.00745152682065963745/-0.04722602665424346924/-0.01951341703534126282/-0.12375152111053466797/0.28438881039619445801/0.16033190488815307617/-0.12406383454799652100/-0.16358031332492828369/0.20827393233776092529/-0.11226706206798553467/-0.12238579988479614258/0.07001034915447235107/-0.13863092660903930664/-0.19995433092117309570/-0.26975896954536437988/0.06661811470985412598/0.38881748914718627930/0.12092635780572891235/-0.17975217103958129883/0.00248981267213821411/-0.00866327062249183655/-0.06912569701671600342/0.02051286399364471436/0.09633430838584899902/-0.02242402732372283936/-0.03515596687793731689/-0.01284310594201087952/-0.00761520862579345703/0.17306259274482727051/-0.04353122413158416748/-0.07538084685802459717/0.16950911283493041992/-0.08106084167957305908/0.09210093319416046143/0.05193337798118591309/0.05436597019433975220/-0.12191647291183471680/0.04238216206431388855/-0.13258443772792816162/-0.08583633601665496826/-0.01639436930418014526/0.00801460444927215576/0.05152839422225952148/0.09766463935375213623/-0.13022944331169128418/0.14843305945396423340/-0.07015743106603622437/-0.04516962915658950806/-0.08858592063188552856/0.01447004079818725586/-0.08154375106096267700/0.01339198648929595947/0.16201543807983398438/-0.28261867165565490723/0.29800316691398620605/0.16216221451759338379/0.08981692045927047729/0.15687899291515350342/0.08177769184112548828/-0.00267638266086578369/0.00843499600887298584/-0.01441448926925659180/-0.24331226944923400879/-0.06137196719646453857/0.10807615518569946289/-0.01118402183055877686/0.10690347850322723389/0.01473689824342727661/'))