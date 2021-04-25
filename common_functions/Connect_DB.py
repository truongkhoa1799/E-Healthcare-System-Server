import sys
sys.path.append('/Users/khoa1799/GitHub/E-Healthcare-System-Server')

import pyodbc
from common_functions.utils import LogMesssage
from threading import Timer

class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, ** self.kwargs)

class DB:
    def __init__(self):
        self.__server = "hospitaldb.database.windows.net"
        self.__username = "PYTHON_SERVER"
        self.__password = "Database_Hospital@123"
        self.__database = "HospitalDB"

        # self.conn = pymssql.connect(server, user, password, database)
        self.connect = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+self.__server+';DATABASE='+self.__database+';UID='+self.__username+';PWD='+ self.__password)
        self.cursor = self.connect.cursor()

        self.__reconnect=RepeatTimer(120, self.__ReInitConnection)
        self.__reconnect.daemon = True
        self.__reconnect.start()
        # print(self.cursor.getinfo())

    def __ReInitConnection(self):
        LogMesssage('Reconnect to DB server')
        self.connect = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+self.__server+';DATABASE='+self.__database+';UID='+self.__username+';PWD='+ self.__password)
        self.cursor = self.connect.cursor()

    def Close_Connection(self):
        self.cursor.close()
        self.connect.close()

########################################################################
# Patient Information                                                  #
########################################################################
    ####################################################################
    # INSERT                                                           #
    ####################################################################
    def Insert_New_Patient(self, first_name, last_name, date_of_birth, gender, address, phone_number, ssn, user_name, password, e_mail, flag_valid):
        patient_ID = -1
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
            @flag_valid = '{}', \
            @ret_patient_ID = @ret_patient_ID OUTPUT;
        SELECT @ret_patient_ID as ret_patient_ID;
        """.format(first_name, last_name, date_of_birth, gender, address, phone_number, ssn, user_name, password, e_mail, flag_valid)
        try:
            self.cursor.execute(sql_st)
            row = self.cursor.fetchone()
            patient_ID = row.ret_patient_ID
            self.cursor.commit()
        except Exception as e:
            LogMesssage('\tHas error at module: Insert_New_Patient in Connect_DB. {error}'.format(error=e), opt=2)

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
        except Exception as e:
            LogMesssage('\tHas error at module: Insert_Patient_Img in Connect_DB. {error}'.format(error=e), opt=2)

        return ret

    ####################################################################
    # GET                                                              #
    ####################################################################
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
            LogMesssage('\tHas error at module: Get_Patient_Information in Connect_DB. {error}'.format(error=e), opt=2)
            return -1, 0, 0, 0, 0

    def Get_Patient_Img(self, user_id):
        ret = []
        sql_st = '''SELECT Img FROM hospital.PATIENT_IMG
                    WHERE patient_id = {};'''.format(user_id)
        try:
            self.cursor.execute(sql_st)
            row = self.cursor.fetchone()
            while row:
                # print(type(row[0]))
                ret.append(row[0])
                row = self.cursor.fetchone()
            return 0, ret

        except Exception as e:
            LogMesssage('\tHas error at module: Get_Patient_Img in Connect_DB. {error}'.format(error=e), opt=2)
            return -1, None
    
    ####################################################################
    # DELETE                                                           #
    ####################################################################
    def Delete_Patient(self, patient_ID):
        ret = -1
        sql_st = """\
            DELETE FROM hospital.QUEUE_EXAMINATION
            WHERE Patient_ID = {patient_id};

            DELETE FROM hospital.MEDICATION
            WHERE Patient_ID = {patient_id};

            DELETE FROM hospital.EXAMINATION
            WHERE Patient_ID = {patient_id};

            DELETE FROM hospital.PATIENT_IMG
            WHERE Patient_ID = {patient_id};

            DELETE FROM hospital.PATIENT
            WHERE Patient_ID = {patient_id};
        """.format(patient_id = patient_ID)
        try:
            self.cursor.execute(sql_st)
            self.cursor.commit()
            return 0
        except Exception as e:
            LogMesssage('\tHas error at module: Delete_Patient in Connect_DB. {error}'.format(error=e), opt=2)
        return ret

########################################################################
# DEVICE                                                               #
########################################################################
    ####################################################################
    # INSERT                                                           #
    ####################################################################
    def Insert_New_Device(self, device_code, hospital_ID, building_code):
        ret = -1
        sql_st = """\
        DECLARE @return_status INT;
        EXEC hospital.Add_Device
            @Device_Code = '{}',
            @Hospital_ID = {},
            @Building_Code = '{}',
            @para_out = @return_status OUTPUT;
        SELECT @return_status as ret;
        """.format(device_code, hospital_ID, building_code)
        try:
            self.cursor.execute(sql_st)
            row = self.cursor.fetchone()
            ret = row.ret
            self.cursor.commit()
        except Exception as e:
            LogMesssage('\tHas error at module: Insert_New_Device in Connect_DB. {error}'.format(error=e), opt=2)
            return -1

        return ret
    
    def getListDeviceID(self, hospital_ID):
        list_device_id = []
        sql_st = '''SELECT Device_ID
                    FROM hospital.DEVICE
                    WHERE Hospital_ID = {};'''.format(hospital_ID)
        try:
            self.cursor.execute(sql_st)
            row = self.cursor.fetchone()
            while row:
                list_device_id.append(row[0])
                row = self.cursor.fetchone()
            return 0, list_device_id

        except Exception as e:
            LogMesssage('\tHas error at module: getListDeviceID in Connect_DB. {error}'.format(error=e), opt=2)
            return -1, []


    ####################################################################
    # GET                                                              #
    ####################################################################
    # def Get_Available_Device_ID(self):
    #     try:
    #         sql_st = 'SELECT MAX(Device_ID) AS max_device FROM hospital.DEVICE;'
    #         self.cursor.execute(sql_st)
    #         row = self.cursor.fetchone()
    #         if row.max_device == None:
    #             return 1
    #         else:
    #             return int(row[-1]) + 1
    #     except Exception as e:
    #         LogMesssage('\tHas error at module: Get_Available_Device_ID in Connect_DB. {error}'.format(error=e), opt=2)
    #         return None

    # ####################################################################
    # # CHECK and DELETE                                                 #
    # ####################################################################
    # def Check_Valid_Device(self, device_code):
    #     try:
    #         sql_st = '''SELECT 1
    #                     FROM hospital.DEVICE AS D
    #                     WHERE D.Device_Code = '{}';'''.format(device_code)
    #         self.cursor.execute(sql_st)
    #         row = self.cursor.fetchone()

    #         if row == None:
    #             return 0
    #         else:
    #             return -1
    #     except Exception as e:
    #         LogMesssage('\tHas error at module: Check_Valid_Device in Connect_DB. {error}'.format(error=e), opt=2)
    #         return -1
    
    # def Delete_All_Device(self):
    #     ret = -1
    #     sql_st = """\
    #         DELETE from hospital.device;
    #     """
    #     try:
    #         self.cursor.execute(sql_st)
    #         self.cursor.commit()
    #         return 0
    #     except Exception as e:
    #         LogMesssage('\tHas error at module: Delete_All_Device in Connect_DB. {error}'.format(error=e), opt=2)

    #     return ret
    
    def Delete_Device(self, device_ID):
        ret = -1
        sql_st = """\
            DELETE from hospital.device
            WHERE device_ID = {};
        """.format(device_ID)
        try:
            self.cursor.execute(sql_st)
            self.cursor.commit()
            return 0
        except Exception as e:
            LogMesssage('\tHas error at module: Delete_Device in Connect_DB. {error}'.format(error=e), opt=2)
        return ret

########################################################################
# HOSPITALS                                                            #
########################################################################
    # return: 0: exist, -1 not exist hospital_id
    # def Check_Valid_Hospital(self, hospital_ID):
    #     try:
    #         sql_st = '''SELECT 1
    #                     FROM hospital.HOSPITAL AS H
    #                     WHERE H.Hospital_ID = {};'''.format(hospital_ID)
    #         self.cursor.execute(sql_st)
    #         row = self.cursor.fetchone()

    #         if row != None:
    #             return 0
    #         else:
    #             return -1
    #     except Exception as e:
    #         LogMesssage('\tHas error at module: Check_Valid_Hospital in Connect_DB. {error}'.format(error=e), opt=2)
    #         return -1

    # return: 0: exist, -1 not exist hospital_id
    # def Check_Valid_Buidling(self, hospital_ID, building_code):
    #     try:
    #         sql_st = '''SELECT 1
    #                     FROM hospital.BUILDING AS B
    #                     WHERE   B.Hospital_ID = {}
    #                         AND B.Building_Code = '{}';'''.format(hospital_ID, building_code)
    #         self.cursor.execute(sql_st)
    #         row = self.cursor.fetchone()

    #         if row != None:
    #             return 0
    #         else:
    #             return -1
    #     except Exception as e:
    #         LogMesssage('\tHas error at module: Check_Valid_Buidling in Connect_DB. {error}'.format(error=e), opt=2)
    #         return -1
    
    def GetHospitalIdOfDevice(self, device_ID):
        # Get Name, birthday, Phone, Address
        sql_st = '''SELECT Hospital_ID
                    FROM hospital.DEVICE
                    WHERE Device_ID = {};'''.format(device_ID)
        try:
            self.cursor.execute(sql_st)
            row = self.cursor.fetchone()
            if row is not None:
                return 0, row[0]
            else:
                LogMesssage('\tThere is no Device wit id: {id} in database.'.format(id=device_ID), opt=2)
                return -1, None

        except Exception as e:
            LogMesssage('\tHas error at module: GetHospitalIdOfDevice in Connect_DB. {error}'.format(error=e), opt=2)
            return -1, None


    # return: 0: exist, -1 not exist hospital_id
    
########################################################################
# SENSOR INFORMATION                                                   #
########################################################################
    def Insert_Sensor_Information(self, bmi, pulse, spo2, thermal, height, weight):
        # Get Sensor_information_id
        sql_st = '''DECLARE @return_status INT;
                    EXEC hospital.Add_Sensor_Infor
                        @Weight = {},
                        @Height = {},
                        @Temperature = {},
                        @Heart_Pulse = {},
                        @BMI = {},
                        @SPO2 = {},
                        @para_out = @return_status OUTPUT;
                    SELECT @return_status as ret;'''.format(weight, height, thermal, pulse, bmi, spo2)
        try:
            self.cursor.execute(sql_st)
            row = self.cursor.fetchone()
            # DONT FORGET TO COMMIT
            self.cursor.commit()
            return 0, row[0]
        except Exception as e:
            LogMesssage('\tHas error at module: Insert_Sensor_Information in Connect_DB. {error}'.format(error=e), opt=2)
            return -1, None
    
    def Delete_Sensor_Information(self, sensor_ID):
        ret = -1
        sql_st = """\
            DELETE hospital.SENSOR_INFORMATION
            WHERE ID = {};""".format(sensor_ID)
        try:
            self.cursor.execute(sql_st)
            self.cursor.commit()
            return 0
        except Exception as e:
            LogMesssage('\tHas error at module: Delete_Sensor_Information in Connect_DB. {error}'.format(error=e), opt=2)
        return ret

########################################################################
# QUEUE EXAMINATION                                                    #
########################################################################
    def Insert_Queue_Examination(self, hospital_ID, building_code, room_code, patient_ID, sensor_id):
        # Get Sensor_information_id
        sql_st = '''DECLARE @return_status INT;
                    EXEC hospital.Add_Queue_Examination
                        @H_ID = {},
                        @Building_Code = '{}',
                        @Exam_Room_Code = '{}',
                        @Patient_ID = {},
                        @Sensor_ID = {},
                        @para_out = @return_status OUTPUT;
                    SELECT @return_status as ret;'''.format(hospital_ID, building_code, room_code, patient_ID, sensor_id)
        try:
            self.cursor.execute(sql_st)
            row = self.cursor.fetchone()
            # DONT FORGET TO COMMIT
            self.cursor.commit()
            return 0, row[0]
        except Exception as e:
            LogMesssage('\tHas error at module: Insert_Queue_Examination in Connect_DB. {error}'.format(error=e), opt=2)
            return -1, None

    def Delete_Queue_Examination(self, H_ID, Building_code, Exam_Room_Code, STT):
        ret = -1
        sql_st = """\
            DELETE hospital.QUEUE_EXAMINATION
            WHERE   H_ID = {}
                AND Building_code = '{}' 
                AND Exam_Room_Code = '{}' 
                AND STT = {};""".format(H_ID, Building_code, Exam_Room_Code, STT)
        try:
            self.cursor.execute(sql_st)
            self.cursor.commit()
            return 0
        except Exception as e:
            LogMesssage('\tHas error at module: Delete_Queue_Examination in Connect_DB. {error}'.format(error=e), opt=2)
        return ret
    
########################################################################
# GET EXAMINATION ROOM                                                 #
########################################################################
    def Get_Exam_Room(self, hospital_ID):
        # Get Name, birthday, Phone, Address
        ret = []
        sql_st = '''SELECT D.Dep_id, D.Dep_name, ER.Building_Code, ER.Exam_Room_Code, ER.Number_Patients
                    FROM hospital.EXAM_ROOM as ER
                    JOIN hospital.DEPARTMENT as D
                        ON D.Hospital_ID = {h_id}
                        AND D.Dep_id = ER.Dep_id
                    WHERE ER.Hospital_ID = {h_id}'''.format(h_id=hospital_ID)
        try:
            self.cursor.execute(sql_st)
            row = self.cursor.fetchone()
            while row:
                ret.append({'dep_ID': row[0], 'dep_name': row[1], 'building_code': row[2], 'room_code': row[3], 'num_patients': row[4]})
                row = self.cursor.fetchone()
            return 0, ret

        except Exception as e:
            LogMesssage('\tHas error at module: Get_Exam_Room in Connect_DB. {error}'.format(error=e), opt=2)
            return -1, None

    def test(self):
        sql_st = '''update hospital.department
                    set dep_name = 'Khoa Thần Kinh'
                    where hospital_id = 1 and dep_id = 1;'''
        try:
            self.cursor.execute(sql_st)
            self.cursor.commit()
            return 0
        except Exception as e:
            LogMesssage('\tHas error at module: Delete_Queue_Examination in Connect_DB. {error}'.format(error=e), opt=2)
        return -1


# db = DB()
# print(db.getListDeviceID(1))
# print(db.GetHospitalIdOfDevice('1'))
# db.test()

# ret, list_img = db.Get_Patient_Img(9)
# for i in list_img:
#     img = i.split('/')
#     print(len(img))
#     print(img[0])
#     print(img[-2])
#     print(img[-1])

# print(list_image)

# db.test()
# print(db.Get_Available_Device_ID())
# id = db.Check_Valid_Hospital(2)
# print(id)
# id = db.Check_Valid_Buidling(1, 'A1')
# print(id)
# id = db.Check_Valid_Device('XB00000000')
# print(id)
# db.Close_Connection()

# print(db.Insert_New_Device('D21-000001', 1, 'A1'))

# print(db.Delete_Device(1))

# print(db.Insert_New_Patient('Hao', 'Dang Hoan', '2000-10-01', 'm', '123 Ly Thuong Kiet', '0990123432', '024582293', 'hao.dang123', 'hoas1234', 'hao@hotmail.com'))

# print(db.Insert_Patient_Img(4, '-0.14538502693176269531/0.07711523771286010742/-0.02651930972933769226/-0.07749503850936889648/-0.09596652537584304810/0.02902343124151229858/-0.04959616065025329590/-0.13908588886260986328/0.15207332372665405273/-0.10876959562301635742/0.30567070841789245605/-0.07628138363361358643/-0.21351784467697143555/-0.10681584477424621582/-0.04293793439865112305/0.19230733811855316162/-0.18567499518394470215/-0.17979717254638671875/-0.02217222377657890320/-0.05868885666131973267/0.05365453660488128662/-0.00161781976930797100/-0.01889562979340553284/0.09524535387754440308/-0.11470939964056015015/-0.35909205675125122070/-0.06547828018665313721/-0.18791122734546661377/0.01396851614117622375/-0.12531945109367370605/-0.01996726356446743011/0.01166521012783050537/-0.15482190251350402832/-0.06691932678222656250/0.06035837531089782715/0.10904476046562194824/-0.05442344397306442261/-0.03158504515886306763/0.22477501630783081055/0.02332936227321624756/-0.15120297670364379883/0.05060161650180816650/0.01816993951797485352/0.27390280365943908691/0.16293142735958099365/0.09317749738693237305/0.00859366171061992645/-0.15666612982749938965/0.15373530983924865723/-0.21228690445423126221/0.07227448374032974243/0.11011874675750732422/0.13214278221130371094/0.06566468626260757446/0.04283107072114944458/-0.16567899286746978760/-0.03069698810577392578/0.09851173311471939087/-0.27845495939254760742/0.03724094480276107788/-0.00745152682065963745/-0.04722602665424346924/-0.01951341703534126282/-0.12375152111053466797/0.28438881039619445801/0.16033190488815307617/-0.12406383454799652100/-0.16358031332492828369/0.20827393233776092529/-0.11226706206798553467/-0.12238579988479614258/0.07001034915447235107/-0.13863092660903930664/-0.19995433092117309570/-0.26975896954536437988/0.06661811470985412598/0.38881748914718627930/0.12092635780572891235/-0.17975217103958129883/0.00248981267213821411/-0.00866327062249183655/-0.06912569701671600342/0.02051286399364471436/0.09633430838584899902/-0.02242402732372283936/-0.03515596687793731689/-0.01284310594201087952/-0.00761520862579345703/0.17306259274482727051/-0.04353122413158416748/-0.07538084685802459717/0.16950911283493041992/-0.08106084167957305908/0.09210093319416046143/0.05193337798118591309/0.05436597019433975220/-0.12191647291183471680/0.04238216206431388855/-0.13258443772792816162/-0.08583633601665496826/-0.01639436930418014526/0.00801460444927215576/0.05152839422225952148/0.09766463935375213623/-0.13022944331169128418/0.14843305945396423340/-0.07015743106603622437/-0.04516962915658950806/-0.08858592063188552856/0.01447004079818725586/-0.08154375106096267700/0.01339198648929595947/0.16201543807983398438/-0.28261867165565490723/0.29800316691398620605/0.16216221451759338379/0.08981692045927047729/0.15687899291515350342/0.08177769184112548828/-0.00267638266086578369/0.00843499600887298584/-0.01441448926925659180/-0.24331226944923400879/-0.06137196719646453857/0.10807615518569946289/-0.01118402183055877686/0.10690347850322723389/0.01473689824342727661/'))

# print(db.Delete_Sensor_Information(1))
# print(db.Delete_Queue_Examination(1, 'A1', '101',3))