from rest_framework.response import Response
import time
from mentee.models import *
from mentee.serializers import *
import re
from rest_framework import status
import datetime
import pytz
import json
from mentee.agora.src.RtcTokenBuilder import RtcTokenBuilder # agora
import requests


def generate_voice_token(schedule_id,request):
    """

    :param request:
    :return:
    """

    user = User.objects.get(email=request.user)

    user_id = user.pk
    is_mentee = user.is_mentee

    try:
        sch_obj = mentor_schedule.objects.get(id=schedule_id)
    except:
        print("no such session scheduled by mentor or session expired")
        return None

    st_time = sch_obj.Start_datetime
    ed_time = sch_obj.End_datetime
    session_name = sch_obj.Session_name
    order_id = sch_obj.order_id

    is_call = True
    sec_left = None
    voice_token = None
    message = None
    channel_name = None

    # Check if this session is marked completed by one of the user
    sales_ob = sales_order.objects.get(id=order_id)

    if sales_ob.Status == 2:  # Status field is not boolean

        if is_mentee:
            message = "Mentor has marked this session as completed"
        else:
            message = "Mentee has marked this session as completed"

        is_call = False
        voice_det = {"is_call": is_call, "channel_name": channel_name, "user_id": user_id,
                     "sec_left": sec_left, "voice_token": voice_token, "message": message}
        return voice_det

    # Fetch other schedules as well so to calculate expiry timme of this call
    next_sch_obs = mentor_schedule.objects.filter(Mentor_id=sch_obj.Mentor_id,Created_at__gt=ed_time).order_by("-Created_at")

    # st_time= datetime.datetime(2020, 12, 7, 0, 30, 0)
    # ed_time = datetime.datetime(2020, 12, 7, 0, 40, 0)

    channel_name = str(session_name)+"_"+str(order_id)
    cr_time = datetime.datetime.now()

    voice_obj = voice_call()
    voice_obj.channel_name = channel_name
    voice_obj.sales_order_id = order_id
    voice_obj.user_id = user_id
    # import time
    # aa = int(time.time()+600)
    # sec_left = 600
    # voice_token = get_voice_token(channel_name, user_id,aa)

    if (st_time - cr_time).total_seconds() < 15: # 15 sec limit
        print("true")
        if len(next_sch_obs) > 0:
            next_call_at = next_sch_obs[0].Start_datetime
            sec_left = int((next_call_at - cr_time).total_seconds())
            print(sec_left / 60, "mins left")

            if sec_left<60:  # if next call of a mentor is in next 60 secs then send call expired message
                message = "Session expired"
                is_call = False
                voice_obj.request_type = "expired"
            else:
                voice_token = get_voice_token(channel_name, user_id, 0)

                # save voice details in table
                voice_obj.token_id = voice_token
                voice_obj.expiration_time = sec_left-30
                voice_obj.request_type = "connect"

                call_ob = CallHistory()
                call_ob.channel_name = channel_name
                call_ob.user_id = user_id
                call_ob.is_mentee = is_mentee
                call_ob.status = 1
                call_ob.schedule_id = schedule_id
                call_ob.remarks = "Channel join request"
                call_ob.save()

        else:

            # get voice token for this session
            voice_token = get_voice_token(channel_name,user_id,0)

            # save voice details in table
            voice_obj.token_id = voice_token
            voice_obj.expiration_time = None
            voice_obj.request_type = "connect"

            call_ob = CallHistory()
            call_ob.channel_name = channel_name
            call_ob.user_id = user_id
            call_ob.is_mentee = is_mentee
            call_ob.status = 1
            call_ob.schedule_id = schedule_id
            call_ob.remarks = "Channel join request"
            call_ob.save()

    elif (st_time - cr_time).total_seconds() > 15:
        message = "Call again at " + str(st_time)
        is_call = False
        voice_obj.request_type = "early"

        print(message)
    # elif (cr_time - ed_time).total_seconds() >1800:
    #     message = "Session expired"
    #     is_call = False
    #     voice_obj.request_type = "expired"
    #     print(message)
    else:
        print((ed_time - cr_time).total_seconds() < 0)

    voice_obj.save()

    ed_time_st = int(ed_time.timestamp()*1000)
    voice_det = {"is_call":is_call, "channel_name":channel_name,"user_id":user_id,
    "sec_left":sec_left, "voice_token":voice_token,"message":message,"end_time":ed_time_st}

    print(voice_det)
    return voice_det


def get_voice_token(channel_name,uid,privilegeExpiredTs):
    """

    :param channel_name:
    :param uid:
    :param privilegeExpiredTs:
    :return:
    """
    appID = "840e67b9d38c44ee8c975b9338546e69"
    appCertificate = "8f3fc6f306bd4d53a8063254b1bc5de1"
    # channelName = "11-10-2020 12:12:12 python mentor_id"  # get channel name
    # uid = 2882341273  # sales_order_id
    #
    # expireTimeInSeconds = 60
    #
    # currentTimestamp = int(time.time())
    # privilegeExpiredTs = currentTimestamp + expireTimeInSeconds
    role = 1

    token = RtcTokenBuilder.buildTokenWithUid(appID, appCertificate, channel_name, uid, role,
                                              privilegeExpiredTs)

    return token


def disconnect_call(request,data):
    """

    :param request:
    :param data:
    :return:
    """

    user = User.objects.get(email=request.user)

    user_id = user.pk
    is_mentee = user.is_mentee

    call_ob = CallHistory()

    leave_status = 25
    remarks = "Call disconnected"

    if data["call_completed"]:
        leave_status = 35
        remarks = "Call completed"

        # sch_obj = mentor_schedule.objects.get(id=data["schedule_id"])
        sales_ord_ob = sales_order.objects.get(Schedule_id=data["schedule_id"],Status=1)

        sales_ord_ob.Status=2  # call completed
        sales_ord_ob.save()
        print("sales order status 2")
        ms_ob = mentor_schedule.objects.get(id=data["schedule_id"])
        ms_ob.Is_scheduled = 4 # session completed
        ms_ob.Status=0
        ms_ob.save()
        print("mentor schedule is schedyle = 4 ")
        # sending push notification for call completion

        if is_mentee:
            message = "Mentee has marked the session as completed"
            notify_id = sales_ord_ob.Mentor_id
        else:
            message = "Mentor has marked the session as completed"
            notify_id = sales_ord_ob.Mentee_id

        user_ob = User.objects.get(id=notify_id)

        send_push_notification(user_ob.mobile_token, message, "Session completed")

    call_ob.channel_name = data["channel_name"]
    call_ob.user_id = user_id
    call_ob.is_mentee = is_mentee
    call_ob.status = leave_status
    call_ob.schedule_id = data["schedule_id"]
    call_ob.remarks = remarks

    call_ob.save()


def channel_event_listener(request, data):
    """

    :param request:
    :param data:
    :return:
    """

    user = User.objects.get(email=request.user)

    user_id = user.pk
    is_mentee = user.is_mentee

    call_ob = CallHistory()
    remarks = None
    reason = None

    if data["callback_status"]==5:
        remarks = "Channel joined"
    elif data["callback_status"]==10:
        remarks = "Remote user has joined"
    elif data["callback_status"]==15: # remote audio quality
        remarks = json.dumps(data["quality_count"])
    elif data["callback_status"]==30:
        remarks = "Remote offline"
        reason = data["reason"]

    call_ob.channel_name = data["channel_name"]
    call_ob.user_id = user_id
    call_ob.is_mentee = is_mentee
    call_ob.status = data["callback_status"]
    call_ob.schedule_id = data["schedule_id"]
    call_ob.remarks = remarks
    call_ob.reason = reason
    call_ob.save()


def send_push_notification(mobile_token, message, title):
    """

    :param mobile_token:
    :param message:
    :param title:
    :return:
    """
    # sending push notification for call completion
    fcm_key = "AAAALIuxoME:APA91bEkyslF0vrmIGX14kwS2wAGEvb8PGCdKnvNgC7JUTwrXZkAyZv-0MrPQ0kMHKd6vzceErzHlz76i4MPF8icPtMux1GSckZoFfjDhX9M89rRZiTds0fxm-5lKTy0WqVlHtBP_HiJ"
    headers = {"Content-Type": "application/json",
               "Authorization": "key=" + fcm_key}

    notify_data = {
        "to": mobile_token,
        "notification": {
             "body": message,
             "title": title,
             "content_available": True,
             "priority": "high",
             "icon":"splash_icon"
         },
        "data": {"notification_id": 5, "message": message,"title":title,"priority": "high","body":message}
    }

    requests.post('https://fcm.googleapis.com/fcm/send', data=json.dumps(notify_data), headers=headers)


