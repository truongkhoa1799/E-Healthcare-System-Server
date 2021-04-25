# from parameters import *
# from common_functions.manage_device import *
# from common_functions.utils import LogMesssage

# def Get_Examination_Room(device_ID):
#     error_msg = 'Fail to get examination room'
#     try:
#         # CHANGE 6-4: do not use gGet_Twin_Information. Instead, use db for getting hospital_ID
#         # location = Get_Twin_Information(device_ID)
#         # hospital_ID = int(location['hospital_ID'])

#         # device_ID stored in DB is Int
#         # test
#         # device_ID = '2'
#         device_ID = int(device_ID)
#         ret, hospital_ID = para.db.GetHospitalIdOfDevice(device_ID)
#         if ret == -1:
#             return {'return': -1, 'msg': error_msg}

#         ret, exam_room = para.db.Get_Exam_Room(hospital_ID)
#         if ret == 0:
#             return {'return': 0, 'msg': exam_room, 'hospital_ID': hospital_ID}
#         else:
#             return {'return': -1, 'msg': error_msg}

#     except Exception as e:
#         LogMesssage('Has error at moudle Get_Examination_Room in file get_examination_room.py: {error}'.format(error=e), opt=2)
#         return {'return': -1, 'msg': error_msg}
    