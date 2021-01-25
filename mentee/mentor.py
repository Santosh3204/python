
import jwt, json
from datetime import datetime,timedelta
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.generics import RetrieveAPIView
from django.views.generic.detail import DetailView
from rest_framework.response import Response
import time
from .models import *
from .serializers import *
import re
from rest_framework import status
import datetime
import pytz
import calendar
import pandas as pd
import xlrd
import razorpay
import hmac
import hashlib
import binascii
import uuid
from mentee.agora.src.RtcTokenBuilder import RtcTokenBuilder # agora
from mentee.agora.call import send_push_notification


def fetch_booked_sessions(request):
    objects = mentor_schedule.objects.filter(Mentor_id=request['mentor_id'],
                                             Is_scheduled=request['is_scheduled'],Status=1).order_by('Start_datetime')

    data = []

    for i in range(len(objects)):
        if objects[i].Start_datetime.date() == datetime.date.today():
            date = "Today"

        elif objects[i].Start_datetime.date() == datetime.date.today() + timedelta(days=1):
            date = "Tomorrow"
        else:
            date = objects[i].Start_datetime.date().strftime("%d %b")

        sales_ob = sales_order.objects.get(id=objects[i].order_id)
        mentee_obj = MenteeDetails.objects.get(id=sales_ob.Mentee_id)

        diff_time = datetime.datetime.now() - objects[i].Start_datetime
        minutes_diff = diff_time.total_seconds()/60
        if minutes_diff>=60:
            print("skipped session")
            continue


        # mentee_name = mentee_obj.user.name

        if mentee_obj.profile == "Student":
            mentee_dict = {
                "id_": mentee_obj.id,
                "Mentee_name": sales_ob.Mentee_name,
                "session_name": objects[i].Session_name,
                "session_date": date,
                "Session_time": objects[i].Start_datetime.time().strftime('%I:%M %p'),
                # "College_name": mentee_obj.college,
                "Skills": json.loads(mentee_obj.skills),
                "degree": mentee_obj.degree,
                # "course": mentee_obj.course,
                "Mentee_type": mentee_obj.profile, "avatar": mentee_obj.user.picture,
                "schedule_id":objects[i].id
            }

            data.append(mentee_dict)

        else:
            mentee_dict = {
                "id_": mentee_obj.id,
                "Mentee_name": sales_ob.Mentee_name,
                "session_name": objects[i].Session_name,
                "session_date": date,
                "Session_time": objects[i].Start_datetime.time().strftime('%I:%M %p'),
                # "College_name": mentee_obj.college,
                "Skills": json.loads(mentee_obj.skills),
                "degree": mentee_obj.degree,
                # "company": mentee_obj.company,
                "Designation": mentee_obj.designation,
                "Mentee_type": mentee_obj.profile, "avatar": mentee_obj.user.picture,
                "schedule_id": objects[i].id
            }

            data.append(mentee_dict)

    return data

"""
def fetch_booked_sessions(request):
    objects = mentor_schedule.objects.filter(Mentor_id=request['mentor_id'],
                                             Is_scheduled=request['is_scheduled']).order_by('Start_datetime')

    data = []

    for i in range(len(objects)):
        if objects[i].Start_datetime.date() == datetime.date.today():
            date = "Today"

        elif objects[i].Start_datetime.date() == datetime.date.today() + timedelta(days=1):
            date = "Tomorrow"
        else:
            date = objects[i].Start_datetime.date().strftime("%d %b")

        mentee_obj = MenteeDetails.objects.get(id=objects[i].order_id)
        # mentee_name = mentee_obj.user.name

        if mentee_obj.profile == "Student":
            mentee_dict = {
                "mentee_id": objects[i].order_id,
                "Mentee_name": mentee_obj.user.name,
                "session_name": objects[i].Session_name,
                "session_date": date,
                "Session_time": objects[i].Start_datetime.time().strftime('%I:%M %p'),
                #"College_name": mentee_obj.college,
                "Skills": mentee_obj.skills,
                "degree": mentee_obj.degree,
                #"course": mentee_obj.course,
                "Mentee_type": mentee_obj.profile, "avatar": mentee_obj.user.picture,
                "schedule_id": mentee_obj.id
            }

            data.append(mentee_dict)

        else:
            mentee_dict = {
                "mentee_id": objects[i].order_id,
                "Mentee_name": mentee_obj.user.name,
                "session_name": objects[i].Session_name,
                "session_date": date,
                "Session_time": objects[i].Start_datetime.time().strftime('%I:%M %p'),
                #"College_name": mentee_obj.college,
                "Skills": mentee_obj.skills,
                "degree": mentee_obj.degree,
                #"company": mentee_obj.company,
                "Designation": mentee_obj.designation,
                "Mentee_type": mentee_obj.profile, "avatar": mentee_obj.user.picture,
                "schedule_id": mentee_obj.id
            }

            data.append(mentee_dict)

    return data
"""

def single_list(lst):  # this function is used by Mentor_Profile_API_func
    lst = lst.strip('""')
    lst = eval(lst)

    return lst


def Mentor_Profile_API_func(request):
    try:
        object = mentor_profile.objects.get(user=request.data["Mentor_id"])
    except Exception as e:
        print("Error occured while fetching data from mentor_profile table")
        print(e)
        return Response(json.loads("Error occured while fetching data from mentor_profile table"),
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    try:

        c_name = single_list(object.Company)
        c_logos = single_list(object.Company_Logo)
        c_designation = single_list(object.Designation)
        c_duration = single_list(object.Company_Duration)

        data_dict = {
            "Mentor_Name": object.Name,
            "Designation": c_designation[0],
            "Company": c_name[0],
            "About me": object.About,
        }

        professional_details = []
        educational_details = []
        position = ""

        for i in range(len(c_name)):
            company_name = c_name[i]
            company_logo = c_logos[i]
            company_details = {
                "Company_Name": company_name,
                "Company_Logo": company_logo,
            }

            if type(c_designation[i]) == list:

                additional_info = []
                company_designation = []
                for j in range(len(c_designation[i])):
                    position = c_designation[i][j]

                    additional_info.append(c_duration[i][j])

                    desig_info = {
                        "Position": position,
                        "Additional info": additional_info,
                    }

                    company_designation.append(desig_info)

                    desig_info_key = {
                        "Company Designation": company_designation

                    }

                    company_details.update(desig_info_key)

                professional_dict = {
                    "professional details": company_details
                }

                professional_details.append(company_details)

            else:
                position = c_designation[i]

                additional_info = []
                additional_info.append(c_duration[i])
                company_designation = []
                desig_info = {
                    "Position": position,
                    "Additional info": additional_info,
                }

                company_designation.append(desig_info)
                desig_info_key = {
                    "Company Designation": desig_info

                }
                company_details.update(desig_info_key)

                professional_dict = {
                    "professional details": company_details
                }

                professional_details.append(company_details)

        p_dict = {
            "professional_details": professional_details
        }

        data_dict.update(p_dict)
        college_names = single_list(object.College)
        college_degree = single_list(object.Degree)
        college_course = single_list(object.Course)
        college_logo = single_list(object.Logo)

        for i in range(len(college_names)):
            additional_info = []
            additional_info.append(college_course[i])
            college_dict = {
                "Institute_Name": college_names[i],
                "institute_Logo": college_logo[i],
                "Additional_info": additional_info

            }
            educational_details.append(college_dict)
        edu_dict = {
            "Educational Details": educational_details
        }
        data_dict.update(edu_dict)

        return data_dict

    except Exception as e:
        print("Error occured while arranging data in Reponse structure format")
        print(e)
        return Response(json.loads("Error occured while arranging data in Reponse structure format"),
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def Booking_121_func(request):
    user_in_db = User.objects.get(email=request.user)
    mentee_id = user_in_db.id

    try:
        row = mentor_schedule.objects.get(pk=request.data['Schedule_id'], Status=1, Is_scheduled=0)
    except Exception as e:
        print("Error occured while fetching data from mentor_schedule table")
        print(e)
        return Response(json.loads("Error occured while fetching data from mentor_schedule table"),
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    booking = sales_order()
    booking.Mentor_id = row.Mentor_id
    booking.Mentee_id = mentee_id
    booking.Schedule_id = request.data['Schedule_id']
    booking.Session_name = row.Session_name
    booking.save()

    row.Is_scheduled = 1
    row.order_id = request.data['mentee_id']
    row.save()

    mentor_objs = mentor_schedule.objects.filter(Mentor_id=row.Mentor_id,
                                                 Start_datetime=row.Start_datetime,
                                                 Status=1, Is_scheduled=0)

    for i in range(len(mentor_objs)):
        mentor_objs[i].Status = 0
        mentor_objs[i].save()

        # Required sales_order table "id" to provide order_id
    data_dict = {
        "order_id": "DFS%*#VDJJ^#R#HH",
    }

    return data_dict


def Row_Deactivate_API_func(request):
    try:
        obj = mentor_schedule.objects.get(id=request.data['Schedule_id'], Status=1)
    except Exception as e:
        print("Error occured while fetching data from mentor_schedule table")
        print(e)
        return Response(json.loads("Error occured while fetching data from mentor_schedule table"),
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    check=0
    msg="Can't delete this slot"

    if obj.Is_scheduled==0:
        check=1
        msg="Deactivated Successfully"

    if check:

        obj.Status = 0
        obj.save()
    # serializer = mentor_schedule_serializer(q_obj)
    # return Response(serializer.data, status=status.HTTP_200_OK)
    # return serializer.data
    return msg


def Mentor_Calender_API_func(request):
    user_in_db = User.objects.get(email=request.user)
    mentor_id = user_in_db.id
    now = datetime.datetime.now()
    objects = mentor_schedule.objects.filter(Mentor_id=mentor_id, Status=1,Start_datetime__gt=now).order_by('-Start_datetime')

    if len(objects) != 0:

        data = []
        month = []
        year = []

        for i in range(len(objects)):
            dt = objects[i].Start_datetime.date()

            month.append(calendar.month_name[dt.month])
            year.append(dt.year)

        month = list(dict.fromkeys(month))
        year = list(dict.fromkeys(year))

        for y in range(len(year)):
            for i in range(len(month)):

                schedule = []
                for j in range(len(objects)):
                    if year[y] == objects[j].Start_datetime.year:
                        if month[i] == calendar.month_name[objects[j].Start_datetime.month]:

                            schedule.append({
                                "date": objects[j].Start_datetime.strftime("%d"),
                                "topic": objects[j].Session_name,
                                "time": objects[j].Start_datetime.time().strftime("%I:%M %p"),
                                "schedule_id": objects[j].pk,
                                "is_scheduled": objects[j].Is_scheduled,

                            })
                        else:
                            continue
                    else:
                        continue

                if len(schedule) != 0:
                    title = str(month[i]) + " " + str(year[y])
                    title_dict = {
                        "title": title,
                        "schedule": schedule
                    }
                    # title_dict.update(schedule_dict)
                    data.append(title_dict)
                    # data_dict = {"data": data}
                    # resp_dict.update(data_dict)

        return data
    else:
        #print("No Mentor exists with the provided Mentor_id")
        return []


def Mentor_Topics_API_func(request):
    for i in range(len(request.data["Webinar_Topics"])):
        request.data["Webinar_topics"] = request.data["Webinar_Topics"][i]

        serializer = mentor_topics_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

    return "Topics added successfully"


def Mentor_Schedule_API_func(request, mentor_id):  # API to schedule for mentor.

    av_dates = []  # List to store available dates for mentorship

    tdelta = datetime.timedelta(days=1)

    dd, mm, yyyy = map(int, request.data["Start_date"].split("-"))

    dt = datetime.date(yyyy, mm, dd)

    dd, mm, yyyy = map(int, request.data["end_date"].split("-"))

    end_date = datetime.date(yyyy, mm, dd)

    for topic in request.data["session_names"]:
        name = str(topic).title()
        skills_career.objects.get_or_create(name=name)

    while dt <= end_date:  # Checking dates for given week days

        if dt != end_date:

            for j in range(len(request.data["Days"])):
                if dt.isoweekday() == request.data["Days"][j]:
                    av_dates.append(dt)

        else:

            for j in range(len(request.data["Days"])):
                if dt.isoweekday() == request.data["Days"][j]:
                    av_dates.append(dt)

        dt = dt + tdelta

    av_dates_count = len(av_dates)
    n_sessions = av_dates_count * len(request.data["session_names"])

    if len(av_dates) == 0:
        print("Given weekdays does't matches with given dates.Please check and try again!!!")
        return "Given weekdays does't matches with given dates.Please check and try again!!!"

    request.data["Start_datetime"] = av_dates[0]

    hh, mts = map(int, request.data["st_time"].split(":"))

    time_delta = datetime.timedelta(minutes=30)

    for d in range(len(av_dates)):

        Start_datetime = datetime.datetime(av_dates[d].year, av_dates[d].month, av_dates[d].day, hh, mts)

        if Start_datetime < datetime.datetime.now():  # not allowing past dates and time to schedule
            print("not scheduled because of past date and time given as input")
            continue

        start_time = datetime.time(hh, mts)
        start_date = Start_datetime.date()

        end_datetime = Start_datetime + time_delta  # Adding 20 minutes for the given start date and time.

        request.data["Start_datetime"] = Start_datetime
        request.data["End_datetime"] = end_datetime
        # request.data["session_charge"] = request.data["charge"]*2
        # Start of time parameter checking
        # print(mentor_id, "mentorrrr id")
        time_check = mentor_schedule.objects.filter(Mentor_id=mentor_id, Status=1)  # fetching objects of the mentor
        # whose status is active-"1"

        count = 0
        for t in range(len(time_check)):  # Iterating on objects if input was unable to schedule

            if start_date == time_check[t].Start_datetime.date():  # not considering past sessions
                # print("date matched object date:", time_check[t].Start_datetime.date())
                t_30 = datetime.timedelta(minutes=40)

                consider = 0

                if time_check[t].Start_datetime < datetime.datetime.now():
                    if time_check[t].Is_scheduled == 1 or time_check[t].Is_scheduled == 2:
                        consider = 1

                else:
                    consider = 1

                if consider == 1:
                    obj_start_datetime = time_check[t].Start_datetime - t_30
                    obj_start_datetime_2 = time_check[t].Start_datetime + t_30
                    if obj_start_datetime.time() >= start_time or obj_start_datetime_2.time() <= start_time:  # On matching dates, checking on
                        # print("is start time greater or not(1>2)" ,obj_start_datetime.time(), start_time)           #time duration on that date
                        # print("is end time or not(1>2)" ,time_check[t].End_datetime.time(), end_datetime.time())
                        pass


                    else:
                        count += 1  # Setting count to 1, if given time is unable to schedule
                        break

        # End of time parameter chhecking

        # print("count of object:", count)
        if count == 0:

            for i in range(len(request.data["session_names"])):
                request.data["Session_name"] = request.data["session_names"][i]
                n_sessions -= 1
                request.data["Mentor_id"] = mentor_id
                if request.data['charge'] <= 200:
                    request.data['mentor_charge'] = request.data['charge']
                    request.data['session_charge'] = 400
                else:
                    request.data['mentor_charge'] = request.data['charge']
                    request.data['session_charge'] = request.data['charge'] * 2
                serializer = mentor_schedule_serializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    # print("serializer data :", serializer.data)

    if n_sessions == 0:

        return "All Dates and Time given are SCHEDULED SUCCESSFULLY !!!"
    elif n_sessions < av_dates_count * len(request.data["session_names"]):
        return "Some Sessions are not scheduled due to TIME on particular DATES are either coincide with already SCHEDULED SESSIONS or given past time or sessions are under booking!!!"
    else:
        return "No Schedule had Created because, TIME on all matching DATES are coincide with already SCHEDULED SESSIONS or given past time or sessions are under booking!!!"
    return "Created successfully"


def Create_Order_API_func(request):

    user_in_db = User.objects.get(email=request.user)                       #server
    mentee_id = user_in_db.id
    print(mentee_id,request.data['Schedule_id'],"00000")
    sales_ord = sales_order.objects.filter(Schedule_id=request.data['Schedule_id'],Status=0,
                                           Is_active=1, Mentee_id=mentee_id).order_by('-Status_updated_at')
    print(len(sales_ord),"sales ord 111111111111")
    if len(sales_ord) != 0:
        try:
            print("222222222222222")
            # row = mentor_schedule.objects.get(id=request.data['Schedule_id'], Status=1, Is_scheduled=0)
            row = mentor_schedule.objects.get(id=request.data['Schedule_id'], Status=1, Is_scheduled__in=[0,2])

            if row.Is_scheduled==2 and row.mentee_id != sales_ord[0].Mentee_id:

                print("some one already booking")
                return None,None
        except Exception as e:
            print("Error occured while fetching data from mentor_schedule table")
            print(e)
            return Response("Error occured while fetching data from mentor_schedule table",
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        print("3333333333333")
        mentor_objs = mentor_schedule.objects.filter(Mentor_id=row.Mentor_id,
                                                     Start_datetime=row.Start_datetime,
                                                     Status=1, Is_scheduled__in=[0,2])

        wt = wallet.objects.filter(mentee_id=user_in_db).order_by('-updated_at')

        if len(wt) != 0:

            if request.data["use_wallet"] and wt[0].current_balance >= sales_ord[0].final_price:
                print("went insideeeeeeeeeeeeeeeeeeeeeeeeeee")

                row.Is_scheduled = 1
                row.order_id = sales_ord[0].id
                row.mentee_id = user_in_db.id
                row.save()

                print("row updated in sales order table")
                for i in range(len(mentor_objs)):
                    mentor_objs[i].Is_scheduled = 0
                    mentor_objs[i].Status = 0
                    mentor_objs[i].order_id = None
                    mentor_objs[i].save()

                order_id = str(uuid.uuid1())
                sales_ord[0].User_order_id = order_id
                sales_ord[0].Status = 1  # payment done

                sales_ord[0].wallet_used = request.data["use_wallet"]
                sales_ord[0].wallet_amount = sales_ord[0].final_price

                sales_ord[0].save()

                order_amount = 0

                # deduct money for this session
                wall_obj = wallet()
                wall_obj.mentee_id = user_in_db.id
                wall_obj.txn_order_id = order_id
                wall_obj.amount_changed = -sales_ord[0].final_price
                wall_obj.status = 2  # added money
                wall_obj.remarks = sales_ord[0].Session_name + " session"

                wall_obj.previous_balance = wt[0].current_balance
                wall_obj.current_balance = wt[0].current_balance - sales_ord[0].final_price

                wall_obj.save()
                print(" wallet row deducted")

                print("fetching mentor details for notificaton")

                mentor_user = User.objects.get(pk=sales_ord[0].Mentor_id)
                mobile_token = mentor_user.mobile_token
                message = user_in_db.name+" has booked a session with you"
                title = "Session booked"

                send_push_notification(mobile_token,message,title)

                return order_id, order_amount

            elif wt[0].current_balance + request.data['amount_to_add'] >= sales_ord[0].final_price:
                order_amount = request.data['amount_to_add'] * 100
            else:
                amount = sales_ord[0].final_price - wt[0].current_balance
                order_amount = amount * 100
        else:
            order_amount = sales_ord[0].final_price * 100

        row.Is_scheduled = 2  # booking in progress
        row.order_id = sales_ord[0].id
        row.mentee_id = user_in_db.id
        row.save()

        for i in range(len(mentor_objs)):
            mentor_objs[i].Is_scheduled=2                                     #progress
            mentor_objs[i].save()

        order_currency = 'INR'
        order_receipt = str(sales_ord[0].id)
        notes = {'Shipping address': 'Bommanahalli, Bangalore'}  # OPTIONAL

        try:

            # client = razorpay.Client(auth=('rzp_test_JAObx3Y47SmBhB', 'RKxq0NX3rGgEZ3HEKt5cr5BT'))
            client = razorpay.Client(auth=('rzp_test_A5QQVVWf0eMog1', 'mwIcHdj1fIDGVi44N6BoUX0W'))

            response = client.order.create(
                dict(amount=order_amount, currency=order_currency, receipt=order_receipt, notes=notes))
        except Exception as e:
            print("Error occured in generating order_id from razorpay pay API side")
            print(e)


            sales_ord[0].Is_active = 0
            sales_ord[0].save()
            return Response("Order ID not generated successfully", status=500)

        sales_ord[0].User_order_id = response['id']

        if request.data["use_wallet"]:
            sales_ord[0].wallet_used = request.data["use_wallet"]
        sales_ord[0].wallet_amount = order_amount/100
        sales_ord[0].save()

        return response["id"],order_amount
    # else:
    #
    #     try:
    #         print("else 55555555555555555555555")
    #         row = mentor_schedule.objects.get(pk=request.data['Schedule_id'], Status=1, Is_scheduled=0)
    #     except Exception as e:
    #         print("Error occured while fetching data from mentor_schedule table")
    #         print(e,"-----------66666666")
    #         return Response("Error occured while fetching data from mentor_schedule table",
    #                         status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    #
    #     mentor_objs = mentor_schedule.objects.filter(Mentor_id=row.Mentor_id,
    #                                                  Start_datetime=row.Start_datetime,
    #                                                  Status=1, Is_scheduled=0)
    #
    #     print(len(mentor_objs))
    #
    #     sales_ord=sales_order.objects.filter(Schedule_id=row.id, Is_active=1, Mentee_id=mentee_id).order_by('-Status_updated_at')
    #
    #     if len(sales_ord)==0:
    #         print("sales_order table doesnot contain matching any row")
    #         return Response("sales_order table doesnot contain matching any row",status=500)
    #
    #
    #     wt=wallet.objects.filter(mentee_id=user_in_db).order_by('-updated_at')
    #
    #     if len(wt)!=0:
    #
    #         if request.data["use_wallet"] and wt[0].current_balance>=sales_ord[0].final_price:
    #             print("went insideeeeeeeeeeeeeeeeeeeeeeeeeee")
    #             order_amount = 0
    #             order_id = str(uuid.uuid1())
    #             # deduct money for this session
    #             wall_obj = wallet()
    #             wall_obj.mentee_id = user_in_db.id
    #             wall_obj.txn_order_id = order_id
    #             wall_obj.amount_changed = -sales_ord[0].final_price
    #             wall_obj.status = 2  # added money
    #             wall_obj.remarks = sales_ord[0].Session_name + " session"
    #
    #             wall_obj.previous_balance = wt[0].current_balance
    #             wall_obj.current_balance = wt[0].current_balance - sales_ord[0].final_price
    #
    #             wall_obj.save()
    #             print(" wallet row deducted")
    #             sales_ord[0].User_order_id =order_id
    #             sales_ord[0].Status = 1  # payment done
    #
    #             sales_ord[0].wallet_used = request.data["use_wallet"]
    #             sales_ord[0].wallet_amount = sales_ord[0].final_price
    #
    #             sales_ord[0].save()
    #             print("row updated in sales order table")
    #
    #             for i in range(len(mentor_objs)):
    #                 mentor_objs[i].Is_scheduled = 0
    #                 mentor_objs[i].Status = 0
    #                 mentor_objs[i].order_id = None
    #                 mentor_objs[i].save()
    #
    #             row.Is_scheduled = 1
    #             row.order_id = sales_ord[0].id
    #             row.save()
    #             print("2000000000000000000000000")
    #             return order_id,order_amount
    #
    #         elif wt[0].current_balance+request.data['amount_to_add']>=sales_ord[0].final_price:
    #             order_amount = request.data['amount_to_add']*100
    #         else:
    #             amount = sales_ord[0].final_price - wt[0].current_balance
    #             order_amount = amount*100
    #     else:
    #         order_amount = sales_ord[0].final_price*100
    #
    #     for i in range(len(mentor_objs)):
    #         mentor_objs[i].Is_scheduled=2                                     #progress
    #         mentor_objs[i].save()
    #
    #     print("---------------------------------------------")
    #     order_currency = 'INR'
    #     order_receipt = str(sales_ord[0].id)
    #     notes = {'Shipping address': 'Bommanahalli, Bangalore'}  # OPTIONAL
    #
    #     try:
    #
    #         # client = razorpay.Client(auth=('rzp_test_JAObx3Y47SmBhB', 'RKxq0NX3rGgEZ3HEKt5cr5BT'))
    #         client = razorpay.Client(auth=('rzp_test_A5QQVVWf0eMog1', 'mwIcHdj1fIDGVi44N6BoUX0W'))
    #
    #         response = client.order.create(
    #             dict(amount=order_amount, currency=order_currency, receipt=order_receipt, notes=notes))
    #     except Exception as e:
    #         print("Error occured in generating order_id from razorpay pay API side")
    #         print(e)
    #
    #         print(len(mentor_objs))
    #         for i in range(len(mentor_objs)):
    #             mentor_objs[i].Is_scheduled = 0
    #             mentor_objs[i].order_id = None
    #             mentor_objs[i].save()
    #
    #         sales_ord[0].Is_active = 0
    #
    #         return Response("Order ID not generated successfully", status=500)
    #     print("haan bhai 00000000000")
    #     sales_ord[0].User_order_id = response['id']
    #     sales_ord[0].Status = 0 # payment not done, new row
    #     if request.data["use_wallet"]:
    #         sales_ord[0].wallet_used = request.data["use_wallet"]
    #     sales_ord[0].wallet_amount = order_amount/100
    #     print("haan bhai 11111111111111111")
    #     sales_ord[0].save()
    #
    #     # print(len(mentor_objs))
    #     # for i in range(len(mentor_objs)):
    #     #     mentor_objs[i].Is_scheduled=2  # in process
    #     #     mentor_objs[i].Status=1
    #     #     mentor_objs[i].order_id=None
    #     #     mentor_objs[i].save()
    #
    #
    #     row.Status=1
    #     row.Is_scheduled = 2  # progress
    #     row.order_id = sales_ord[0].Mentee_id
    #     row.save()
    #
    #     return response['id'],order_amount


def RP_Sign_Verification_func(request):

    user_in_db = User.objects.get(email=request.user)  # server
    mentee_id = user_in_db.id
    
    try:
        sales_ord=sales_order.objects.get(User_order_id=request.data['razorpay_order_id'])
    except Exception as e:
        print(e)
        print("Error occured in getting fetching data from sales_order table using order_id")
        return Response("Error occured in getting fetching data from sales_order table using order_id", status=422)

    try:
        sch_id=sales_ord.Schedule_id
        sch_obj=mentor_schedule.objects.get(id=sch_id)
        objects=mentor_schedule.objects.filter(Mentor_id=sales_ord.Mentor_id,Start_datetime=sch_obj.Start_datetime, Status=1)
    except Exception as e:
        print(e)
        print("Error in mentor_schedule table")
        return Response("Error in mentor_schedule table while fetching sessions", status=422)
    
    try:
        # generated_signature = hmac_sha256(request.data['razorpay_order_id'] + "|" + request.data['razorpay_payment_id'], 'RKxq0NX3rGgEZ3HEKt5cr5BT')
        s1 = request.data['razorpay_order_id'] + "|" + request.data['razorpay_payment_id']

        key = 'RKxq0NX3rGgEZ3HEKt5cr5BT'
        key= 'mwIcHdj1fIDGVi44N6BoUX0W'
        hex_str = key.encode()
        message = s1.encode()

        generated_signature = hmac.new(hex_str, message, hashlib.sha256).hexdigest()
        print(generated_signature)
        print(request.data['razorpay_signature'])
        if (generated_signature == request.data['razorpay_signature']):
            print("Payment is successfull, Data came from authenticated source")
        
        else:
            sch_obj.Is_scheduled=0
            sch_obj.order_id=None
            sch_obj.save()
            for i in range(len(objects)):
                objects[i].Is_scheduled=0
                objects[i].order_id=None
                objects[i].save()
            sales_ord.Is_active=0
            print("Data not came from authenticated sources")
            #return Response("Data not came from authenticated sources, Razorpay signature and generated signature mis-matched",status=422)
    except Exception as e:
        print(e)
        sch_obj.Is_scheduled = 0
        sch_obj.order_id = None
        sch_obj.save()
        for i in range(len(objects)):
            objects[i].Is_scheduled=0
            objects[i].order_id=None
            objects[i].save()
        sales_ord.Is_active=0
        print("Data not came from authenticated sources")
        #return Response("Data not came from authenticated sources, Razorpay signature and generated signature mis-matched",status=422)
        
    
    check=0

    try:

        # client = razorpay.Client(auth=('rzp_test_JAObx3Y47SmBhB', 'RKxq0NX3rGgEZ3HEKt5cr5BT'))
        client = razorpay.Client(auth=('rzp_test_A5QQVVWf0eMog1', 'mwIcHdj1fIDGVi44N6BoUX0W'))
        status = client.utility.verify_payment_signature(request.data)
        print(status,"payment statusssss")
        check=1
    
    except Exception as e:
    
        print(e)
    
        
        
        rz_dict = client.payment.fetch(request.data['razorpay_payment_id'])
        if rz_dict['status']=="captured" and rz_dict['captured']==True:
            check=1
        else:
            sch_obj.Is_scheduled = 0
            sch_obj.order_id = None
            sch_obj.save()
            for i in range(len(objects)):
                objects[i].Is_scheduled=0
                objects[i].order_id=None
                objects[i].save()
            sales_ord.Is_active=0
            print("Razorpay Signature verification Failed")
            return Response("Razorpay Signature verification Failed",status=422)

    if check==1:
        
        try:
            sales_ord.Payment_id = request.data['razorpay_payment_id']
            sales_ord.Status = 1  # payment done
            sales_ord.save()
        except Exception as e:
            print(e)
            return Response("Error occured in sales_order table", status=500)

        try:
            rz = payment_details()
            rz.Sales_Order = sales_ord
            rz.razorpay_order_id = request.data['razorpay_order_id']
            rz.razorpay_payment_id = request.data['razorpay_payment_id']
            rz.razorpay_signature = request.data['razorpay_signature']
            rz.save()

        except Exception as e:
            print(e)
            return Response("Error occured in payment_detals table", status=500)


        for i in range(len(objects)):
            objects[i].Is_scheduled = 0
            objects[i].Status = 0
            objects[i].order_id = None
            objects[i].save()

        sch_obj.Is_scheduled = 1
        sch_obj.order_id = sales_ord.id
        sch_obj.save()

        ########## add amount in wallet and deduct money


        mth = wallet.objects.filter(mentee_id=mentee_id, status=2).order_by('-updated_at')

        row = wallet()
        row.mentee_id = user_in_db.id
        row.txn_order_id = request.data['razorpay_order_id']
        row.amount_changed = sales_ord.wallet_amount
        row.status = 2  # added money
        row.remarks = sales_ord.Session_name+ " session"
        curr_bal = 0
        if len(mth) != 0:
            curr_bal = mth[0].current_balance
            row.previous_balance = mth[0].current_balance
            row.current_balance = mth[0].current_balance + sales_ord.wallet_amount

        else:
            row.mentee_id = user_in_db.id
            row.txn_order_id = request.data['razorpay_order_id']
            row.previous_balance = curr_bal
            row.current_balance = sales_ord.wallet_amount
        row.save()

        # deduct money for this session
        row = wallet()
        row.mentee_id = user_in_db.id
        row.txn_order_id = request.data['razorpay_order_id']
        row.amount_changed = -sales_ord.final_price
        row.status = 2  # added money
        row.remarks = sales_ord.Session_name + " session"

        row.previous_balance = curr_bal + sales_ord.wallet_amount
        row.current_balance = curr_bal + sales_ord.wallet_amount - sales_ord.final_price

        row.save()
        print("fetchig mentors detaisl for notification")
        mentor_user = User.objects.get(pk=sales_ord.Mentor_id)
        mobile_token = mentor_user.mobile_token
        message = user_in_db.name + " has booked a session with you"
        title = "Session booked"

        send_push_notification(mobile_token, message, title)

        return "Payment Successfully"
    else:
        # print(status)
        
        sch_obj.Is_scheduled = 0
        sch_obj.order_id = None
        sch_obj.save()
        for i in range(len(objects)):
            objects[i].Is_scheduled=0
            objects[i].order_id=None
            objects[i].save()
        sales_ord.Is_active=0
        print("Payment Failed")
        sales_ord.save()       
        return "Payment Failed"


def Booked_Sessions_func(request):
    try:
        user_det = User.objects.get(email=request.user)
        Mentor_id = user_det.id

    except Exception as e:
        print(e)
        print("User doesn't exist")
        return Response("User doesn't exist", status=500)

    # Mentor_id = 1
    objects = mentor_schedule.objects.filter(Mentor_id=Mentor_id, Is_scheduled=request.data['Is_scheduled']).order_by(
        'Start_datetime')

    data = []

    for i in range(len(objects)):
        if objects[i].Start_datetime.date() == datetime.date.today():
            date = "Today"

        elif objects[i].Start_datetime.date() == datetime.date.today() + timedelta(days=1):
            date = "Tomorrow"
        else:
            date = objects[i].Start_datetime.date().strftime("%d %b")
        try:
            mentee_obj = MenteeDetails.objects.get(id=objects[i].order_id)
            # mentee_name = mentee_obj.user.name
        except Exception as e:
            print(e)
            print("Mentee doesnot exist in Mentee Details table")
            return Response("Mentee doesnot exist in Mentee Details table", status=500)

        if mentee_obj.profile == "Student":
            mentee_dict = {
                "mentee_id": objects[i].order_id,
                "Mentee_name": mentee_obj.user.name,
                "session_name": objects[i].Session_name,
                "session_date": date,
                "Session_time": objects[i].Start_datetime.time().strftime('%I:%M %p'),
                "College_name": mentee_obj.college,
                "Skills": mentee_obj.skills,
                "degree": mentee_obj.degree,
                "course": mentee_obj.course,
                "Mentee_type": mentee_obj.profile
            }

            data.append(mentee_dict)

        else:
            mentee_dict = {
                "mentee_id": objects[i].order_id,
                "Mentee_name": mentee_obj.user.name,
                "session_name": objects[i].Session_name,
                "session_date": date,
                "Session_time": objects[i].Start_datetime.time().strftime('%I:%M %p'),
                "College_name": mentee_obj.college,
                "Skills": mentee_obj.skills,
                "degree": mentee_obj.degree,
                "company": mentee_obj.company,
                "Designation": mentee_obj.designation,
                "Mentee_type": mentee_obj.profile
            }

            data.append(mentee_dict)

    return data


"""    
    text = request.data['name']
    text = re.escape(text) 
    #objects = skills_list.objects.filter(name__contains= request.data['skill'])
    #objects = skills_list.objects.filter(name__icontains= request.data['skill']))
    #objects = skills_list.objects.filter(name__startswith= request.data['skill'])
    #objects = skills_list.objects.filter(name__iregex=r"(^|\s)%s" % text)
    data_lst = []
    try:
        if request.data['type'] == 'skill':
            objects = skills_list.objects.filter(name__iregex=r"(^|\s)%s" % text)
            for i in range(10):
                try:
                    data_lst.append(objects[i].name)
                except:
                    break
        elif request.data['type'] == 'college':
            for i in range(10):
                objects = course_list.objects.filter(College_Name__iregex=r"(^|\s)%s" % text)
                try:
                    data_lst.append(objects[i].College_Name)
                except:
                    break
        elif request.data['type'] == 'course':
            for i in range(10):
                objects = course_list.objects.filter(Level_of_Course__iregex=r"(^|\s)%s" % text)
                try:
                    data_lst.append(objects[i].Level_of_Course)
                except:
                    break
        elif request.data['type'] == 'degree':
            for i in range(10):
                objects = course_list.objects.filter(Degree__iregex=r"(^|\s)%s" % text)
                try:
                    data_lst.append(objects[i].Degree)
                except:
                    break
        else:
            raise Exception()
    except Exception as e:
        print("Error in Value in key('type')")
        print(e)
        return Response(json.loads("Error in Value in key('type')"), status= status.HTTP_500_INTERNAL_SERVER_ERROR)

    data_lst= list(dict.fromkeys(data_lst))

    return data_lst
"""


def fetch_mentor_schedule_func(request):
    try:
        user_det = User.objects.get(email=request.user)
        Mentor_id = user_det.id

    except Exception as e:
        print(e)
        print("User doesn't exist")
        return Response("User doesn't exist", status=500)

        objects = mentor_schedule.objects.filter(Mentor_id=Mentor_id,
                                                 Is_scheduled=request.data["is_scheduled"],
                                                 Session_name=request.data["Session_name"],
                                                 Status=1).order_by('Start_datetime')

        response_dict = {
            "Mentor_id": Mentor_id
        }

        schedule = []
        tdelta = datetime.timedelta(days=1)
        schedule_dates = []

        for i in range(len(objects)):
            dt = objects[i].Start_datetime.date()
            schedule_dates.append(dt)

        schedule_dates = list(dict.fromkeys(schedule_dates))

        schedule_dates.sort()

        for i in range(len(schedule_dates)):
            dt = schedule_dates[i]
            times = []
            Schedule_ids = []

            for j in range(len(objects)):
                dt_obj = objects[j].Start_datetime.date()
                if dt == dt_obj:

                    if objects[j].Start_datetime.date() == datetime.date.today():
                        str1 = "Today"

                    elif objects[j].Start_datetime.date() == datetime.date.today() + tdelta:
                        str1 = "Tomorrow"

                    else:
                        str1 = [[objects[j].Start_datetime.date().strftime("%d-%m-%Y")]]

                    times.append(objects[j].Start_datetime.time().strftime("%I:%M %p"))
                    Schedule_ids.append(objects[j].pk)

            schedule.append(
                {
                    "date": str1,
                    "times": times,
                    "Schedule_ids": Schedule_ids,
                }
            )

        schedule_dict = {"schedule": schedule}
        response_dict.update(schedule_dict)

        return response_dict


def add_session_name_to_mentor_profile(sessions, mentor_id):
    """
    :param sessions:
    :param mentor_id:
    :return:
    """

    pass


def fetch_mentors_schedule(mentor_id, is_scheduled, session_name):
    """
    :param mentor_id:
    :param is_scheduled:
    :param session_name:
    :return:
    """
    if session_name is not None:
        objects = mentor_schedule.objects.filter(Mentor_id=mentor_id,
                                                 Is_scheduled=is_scheduled,
                                                 Session_name=session_name,
                                                 Status=1).order_by('Start_datetime')
    else:
        objects = mentor_schedule.objects.filter(Mentor_id=mentor_id,
                                                 Is_scheduled=is_scheduled,
                                                 Status=1).order_by('Start_datetime')

    date = ""
    schedule = []
    # times = []
    # Schedule_ids = []
    tdelta = datetime.timedelta(days=1)
    schedule_dates = []
    fetch_dates = []
    charges = []

    for i in range(len(objects)):
        if datetime.datetime.now()<objects[i].Start_datetime:
           dt = objects[i].Start_datetime.date()
           print("dt value", dt)
           schedule_dates.append(dt)
    # print(schedule_dates)

    schedule_dates = list(dict.fromkeys(schedule_dates))

    schedule_dates.sort()
    print("---------------------")
    print("Sorted dates of list", schedule_dates)
    print("---------------------")
    print("length of schedule dates", len(schedule_dates))

    for i in range(len(schedule_dates)):
        dt = schedule_dates[i]
        times = []
        Schedule_ids = []
        charges = []
        print("Outer loop date", dt)
        # same_dt_obj = objects.filter(Start_datetime= )
        for j in range(len(objects)):
            if objects[j].Start_datetime > datetime.datetime.now():
                dt_obj = objects[j].Start_datetime.date()
                if dt == dt_obj:

                    if objects[j].Start_datetime.date() == datetime.date.today():
                        str1 = "Today"

                    elif objects[j].Start_datetime.date() == datetime.date.today() + tdelta:
                        str1 = "Tomorrow"

                    else:
                        str1 = objects[j].Start_datetime.date().strftime("%d-%m-%Y")

                    times.append(objects[j].Start_datetime.time().strftime("%I:%M %p"))
                    Schedule_ids.append(objects[j].pk)
                    charges.append(int(objects[j].session_charge))

                    print("Inner loop date", dt_obj)

        schedule.append(
            {
                "date": str1,
                "times": times,
                "Schedule_ids": Schedule_ids,
                "charges": charges
            }
        )
        print(schedule)
    return schedule


def Search_API_func(request):
    text = request.data['name']
    text = re.escape(text)

    # objects = skills_list.objects.filter(name__contains= request.data['skill'])
    # objects = skills_list.objects.filter(name__icontains= request.data['skill']))
    # objects = skills_list.objects.filter(name__startswith= request.data['skill'])
    # objects = skills_list.objects.filter(name__iregex=r"(^|\s)%s" % text)

    data_lst = []
    try:
        if request.data['type'] == 'skill':
            objects = skills_list.objects.filter(name__iregex=r"(^|\s)%s" % text)
            for i in range(10):
                try:
                    data_lst.append(objects[i].name)
                except:
                    break

        elif request.data['type'] == 'college':
            objects = course_list.objects.filter(College_Name__iregex=r"(^|\s)%s" % text)
            for i in range(10):
                try:
                    data_lst.append(objects[i].College_Name)
                except:
                    break

        elif request.data['type'] == 'course':
            objects = course_list.objects.filter(Level_of_Course__iregex=r"(^|\s)%s" % text)
            for i in range(10):
                try:
                    data_lst.append(objects[i].Level_of_Course)
                except:
                    break

        elif request.data['type'] == 'degree':
            objects = degree_list.objects.filter(degree_name__iregex=r"(^|\s)%s" % text)
            for i in range(10):
                try:
                    data_lst.append(objects[i].degree_name)
                except:
                    break
        elif request.data['type'] == 'skills_career':
            objects = skills_career.objects.filter(name__iregex=r"(^|\s)%s" % text)
            for i in range(10):
                try:
                    data_lst.append(objects[i].name)
                except:
                    break
        else:

            raise Exception()

    except Exception as e:
        print("Error in Value in key('type')")
        print(e)
        return Response(json.loads("Error in Value in key('type')"), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    data_lst = list(dict.fromkeys(data_lst))

    return data_lst

def Mentor_Details_API_func(request):
    try:
        objects = mentor_schedule.objects.get(id=request.data['Schedule_id'])
        print(objects.Mentor_id)
    except Exception as e:
        print("Error occured while fetching data in mentor_schedule")
        print(e)
        return Response(json.loads("Error occured while fetching data in mentor_schedule"),
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    try:
        obj_pf = mentor_profile.objects.get(user=objects.Mentor_id)
        print(obj_pf.user)
    except Exception as e:
        print("Error occured while fetching data in mentor_profile table")
        print(e)
        return Response(json.loads("Error occured while fetching data in mentor_profile table"),
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    try:
        obj_us = User.objects.get(id=objects.Mentor_id)
        print(obj_us.name)
    except Exception as e:
        print("Error occured while fetching data in mentor_profile table")
        print(e)
        return Response(json.loads("Error occured while fetching data in mentor_profile table"),
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if objects.Start_datetime.date() == datetime.date.today():
        date = "Today, " + str(objects.Start_datetime.strftime("%I:%M %p"))

    elif objects.Start_datetime.date() == datetime.date.today() + timedelta(days=1):
        date = "Tomorrow, " + str(objects.Start_datetime.strftime("%I:%M %p"))
    else:
        date = objects.Start_datetime.date().strftime("%d %b, %I:%M %p")  # strftime(", %I:%M %p")

    design_lst = eval(obj_pf.professional_details)

    data_dict = {
        "name": obj_us.name,
        "picture": obj_us.picture,
        "designation": design_lst[0],
        "session_name": objects.Session_name,
        "session_datetime": date,
        "charge": objects.charge
    }

    return data_dict


def Fetch_Session_Names_API_func(request):
    text = request.data['name']
    text = re.escape(text)
    try:
        objects = mentor_schedule.objects.filter(Status=1, Session_name__iregex=r"(^|\s)%s" % text)
    except Exception as e:
        print("Error occured in fetching data from mentor_schedule table")
        print(e)
        return Response("No session are there with given name", status=500)

    sessions_list = []
    for i in range(len(objects)):
        sessions_list.append(objects[i].Session_name)
    sessions_list = list(dict.fromkeys(sessions_list))

    return sessions_list


def Coupon_API_func(request):
                                     
    try:                                                             #server
        user_det = User.objects.get(email=request.user)
        mentee_id = user_det.id
    except Exception as e:
        print(e)
        print("User doesn't exist")
        return Response("User doesn't exist", status=500)
    
    try:
        schedule_obj = mentor_schedule.objects.get(id=request.data['schedule_id'], Status=1, Is_scheduled= 0)
    except Exception as e:
        print(e)
        return Response("Error in mentor schedule table", status=500)

    try:
        coupon_obj = coupon.objects.get(coupon_code=request.data['coupon_code'], active_status=1)
    except Exception as e:
        print(e)
        
        data_dict = {
            "valid":False,
            "message":"Coupon can't applied"
        }

        return data_dict

    #mentee_id= 2                                                      #local
    

    if coupon_obj is not None:

        # if len(new_user)<=3:
        if coupon_obj.new_user_coupon == 1:
            new_user = mentor_schedule.objects.filter(order_id=mentee_id)
            if len(new_user) >= 4:
                print("Not a New user")
                data_dict = {
                    "valid": False,
                    "message": "This coupon is for new user only who has booked less than 3 sessions, You already booked more than 3 sessions."
                }
                return data_dict

        if coupon_obj.coupon_type == "flat":
            chargeable_amount = schedule_obj.session_charge - coupon_obj.coupon_amount
            coupon_amount = coupon_obj.coupon_amount

        if coupon_obj.coupon_type == "percentage":
            discount = ((schedule_obj.session_charge * coupon_obj.coupon_percentage) // 100)
            chargeable_amount = schedule_obj.session_charge - discount
            coupon_amount = discount
        data_dict = {
            "valid": True,
            "coupon_amount": coupon_amount,
            "session_price": schedule_obj.session_charge,
            "chargeable_amount": chargeable_amount
        }

        return data_dict

    else:
        data_dict = {
            "valid": False,
            "message": "coupon can't applicable"
        }

        return data_dict


def Mentee_My_Order_API_func(request):

    inner_list = []

    data_dict = {
        "is_mentee": True,
        "inner_data": []
    }

    try:                                                             #server
        user_in_db = User.objects.get(email=request.user)
    except Exception as e:
        print(e)
        print("User doesn't exist")
        return Response("User doesn't exist", status=500)

    if user_in_db.is_mentee:

        sales_ord_objs = sales_order.objects.filter(Mentee_id=user_in_db.id, Status__in=[1,2], Is_active=1).order_by('-Created_at')

        client = razorpay.Client(auth=("rzp_test_A5QQVVWf0eMog1", "mwIcHdj1fIDGVi44N6BoUX0W"))

        for row in sales_ord_objs:
            mentor_in_db = None
            try:
                mentor_in_db = User.objects.get(id=row.Mentor_id)
            except Exception as e:
                print(e)
                print("error occured in for loop in User table")

            payment_id = row.Payment_id
            payment_mode = "Wallet"
            if payment_id is not None:
                resp = client.payment.fetch(payment_id)
                #print(resp,"--------------------------------------------------")
                #payment_mode = resp['method']
                if 'method' in resp:
                    payment_mode = resp['method']
                else:
                    payment_mode = "--"
            is_feedback = False
            try:
                fd = mentee_feedback.objects.get(Sales_Order=row)
                rating = fd.star_rating
                comments = fd.comments
                is_feedback = True
            except Exception as e:
                print("No Feedback given")
                rating = 0
                comments = ""
              
            sch_obj = mentor_schedule.objects.get(id=row.Schedule_id)

            inner_dict = {
                "mentor_name": mentor_in_db.name,
                "order_id": row.User_order_id,
                "star_rating": rating,
                "comments": comments,
                "actual_price": row.session_charge,
                "coupon_id": row.coupon_id,
                "coupon_amount": row.coupon_amount,
                "payment_mode": payment_mode,
                "session_name": row.Session_name,
                "profile_pic": mentor_in_db.picture,
                "date": sch_obj.Start_datetime.strftime("%d %b %Y"),
                "time": sch_obj.Start_datetime.strftime("%I:%M %p"),
                "paid_amount": row.final_price,
                "created_at": row.Created_at,
                "is_feedback":is_feedback,
                "schedule_id":sch_obj.id
            }

            msg = False
            t_30 = datetime.timedelta(minutes=30)

            allowed_time = sch_obj.End_datetime + t_30

            if row.Status == 2:

                msg = True
            elif datetime.datetime.now() >= allowed_time:

                msg = True
            else:

                msg = False

            inner_dict.update({"feedback_status": msg})

            inner_list.append(inner_dict)
        data_dict["inner_data"] = inner_list

    else:
        mentee_status = False

        sales_ord_objs = sales_order.objects.filter(Mentor_id=user_in_db.id, Status__in=[1,2], Is_active=1)

        for row in sales_ord_objs:

            try:
                mentee_in_db = User.objects.get(id=row.Mentee_id)
            except Exception as e:
                print(e)
                print("error occured in for loop in User table")

            sch_obj = mentor_schedule.objects.get(id=row.Schedule_id)

            data_di = {
                "mentee_name": mentee_in_db.name,
                "session_name": row.Session_name,
                "profile_pic": mentee_in_db.picture,
                "date": sch_obj.Start_datetime.strftime("%d %b %Y"),
                "time": sch_obj.Start_datetime.strftime("%I:%M %p"),
                "paid_amount": sch_obj.mentor_charge

            }

            inner_list.append(data_di)
        data_dict["is_mentee"] = mentee_status
        data_dict["data"] = inner_list


    return data_dict

            
def Mentor_My_Orders_API_func(request):

    
    try:                                                             #server
        user_in_db = User.objects.get(email=request.user)
        mentor_id = user_in_db.id
    except Exception as e:
        print(e)
        print("User doesn't exist")
        return Response("User doesn't exist", status=500)
    
    
    #mentor_id=2                                                     #local
    obj=mentor_schedule.objects.filter(Mentor_id=mentor_id, Is_scheduled=1, Status=1).order_by('-Start_datetime')

    lst=[]
    
    for row in obj:
        try:
            sales_ord=sales_order.objects.get(Schedule_id=row.id,Is_active=1,Status=2)
        except:
            continue
        mentee_in_db=User.objects.get(id=sales_ord.Mentee_id)
        
        print(row.id)
        data_dict={
            "mentee_name":mentee_in_db.name,
            "session_name":row.Session_name,
            "profile_pic":mentee_in_db.picture,
            "date":row.Start_datetime.strftime("%d %b %Y"),
            "time":row.Start_datetime.strftime("%I:%M %p"),
            "paid_amount":sales_ord.session_charge
            
        }

        
        lst.append(data_dict)
    

    #user_in_db=User.objects.get(id=2)                           #local
    if user_in_db.is_mentee==True:
        mentee_status=True
    else:
        mentee_status=False

    #data_dict={
    #    "is_mentee":mentee_status,
    #    "outer_data":outer_lst,
    #    "inner_data":inner_lst
    #}

    return lst,mentee_status


    
    
        
def Mentor_Payment_History_func(request):
    
    try:                                                                       #server
        user_in_db=User.objects.get(email=request.user)
        mentor_id=user_in_db.id
    except Exception as e:
        print(e)
        print("Mentor details not found in User table")
        return Response("Mentor details not found in User table", status=500)
    

    #mentor_id=2                                                                 #local
    sales_ord=sales_order.objects.filter(Mentor_id=mentor_id, Status=2)

    month_lst=[]
    
    for row in sales_ord:
        
        month=row.Mentor_Schedule.Start_datetime.strftime("%B %Y")
        month_lst.append(month)
    
    
    
    month_lst=list(dict.fromkeys(month_lst))
    
    month_lst.reverse()
    
    

    month_payment_history=[]
    for m in month_lst:
        aggregated_amount=0
        for row in sales_ord:            
            month=row.Mentor_Schedule.Start_datetime.strftime("%B %Y")
            
            if month==m:
                aggregated_amount+=row.final_price

        pay_dict={
            "month":m,
            "aggregated_amount":aggregated_amount
        }
        month_payment_history.append(pay_dict)

    return month_payment_history



def Mentee_Feedback_func(request):

    try:
        sales_ord=sales_order.objects.filter(Schedule_id=request.data['schedule_id']).order_by("-Status_updated_at")
    except Exception as e:
        print(e)
        print("Order_id doesnot exists in sales_order table")
        return Response("Order_id doesnot exists in sales_order table", status=500)

    obj=mentee_feedback()
    obj.Sales_Order=sales_ord[0]
    obj.mentor_id=sales_ord[0].Mentor_id
    obj.star_rating=request.data['star_rating']
    obj.comments=request.data['comments']

    obj.save()






def Wallet_API_func(request):
    
    
    try:                                                        #server
        user_in_db=User.objects.get(email=request.user)    
        mentee_id=user_in_db.id
    except Exception as e:
        print(e)
        print("Requested user doesn't exist in db")
        return Response("Requested user doesn't exist in db", status=500)

    
    #user_in_db=User.objects.get(id=4)                           #local
    #mentee_id=user_in_db.id
    
    amount=request.data['amount']*100

    order_amount=amount
    order_currency='INR'
    order_receipt=str(mentee_id)
    notes={
        "name":user_in_db.name,
        "id":user_in_db.id
    }

    try:
        client=razorpay.Client(auth=('rzp_test_A5QQVVWf0eMog1', 'mwIcHdj1fIDGVi44N6BoUX0W'))
        response=client.order.create(dict(amount=order_amount, currency=order_currency, receipt=order_receipt, notes=notes))

    except Exception as e:
        print(e)
        print("Order id not generated")
        return Response("Order id not generated", status=500)

    
    
    mth=wallet.objects.filter(mentee_id=mentee_id,status=2).order_by('-updated_at')
    
    row=wallet()

    if len(mth)!=0:

        row.mentee_id=user_in_db.id
        row.txn_order_id=response['id']
        row.previous_balance=mth[0].current_balance
        row.current_balance=mth[0].current_balance
        row.amount_changed=request.data['amount']
        row.status=1                                #created
        row.save()

    else:
        row.mentee_id=user_in_db.id
        row.txn_order_id=response['id']
        row.previous_balance=0
        row.current_balance=0
        row.amount_changed=request.data['amount']
        row.status=1                                #created
        row.save()


    return response['id']



def wallet_verification_func(request):
    
    s1 = request.data['razorpay_order_id'] + "|" + request.data['razorpay_payment_id']

    key = 'RKxq0NX3rGgEZ3HEKt5cr5BT'
    key= 'mwIcHdj1fIDGVi44N6BoUX0W'
    hex_str = key.encode()
    message = s1.encode()

    generated_signature = hmac.new(hex_str, message, hashlib.sha256).hexdigest()
    
    print(request.data['razorpay_signature'])
    if (generated_signature == request.data['razorpay_signature']):
        print("Payment is successfull, Data came from authenticated source")
    else:
        print("Data not came from authenticate sources")
        return Response("Data not came from authenticate sources", status=500)


    try:

        # client = razorpay.Client(auth=('rzp_test_JAObx3Y47SmBhB', 'RKxq0NX3rGgEZ3HEKt5cr5BT'))
        client = razorpay.Client(auth=('rzp_test_A5QQVVWf0eMog1', 'mwIcHdj1fIDGVi44N6BoUX0W'))
        status = client.utility.verify_payment_signature(request.data)
        print(status,"payment statusssss")
    except Exception as e:
        print(e)
        print("signature verification falied at razorpay side")
        return Response("signature verification falied at razorpay side", status=500)

    if status==None:
        try:
            row=wallet.objects.get(txn_order_id=request.data['razorpay_order_id'])
        except Exception as e:
            print(e)
            print("order_id in wallet table doesnot exists")
            return Response("order_id in wallet table doesnot exists", status=500)

    row.status=2
    row.current_balance = row.previous_balance+row.amount_changed
    row.remarks = "Money added"
    row.save()

    data_dict={
        "messsage":"Rs."+str(row.amount_changed)+" added sucessfully",
        "updated_balance":row.current_balance
    }    


    return data_dict



def wallet_history_func(request):
    

    try:                                                                    #server
        user_in_db=User.objects.get(email=request.user)
    except Exception as e:
        print(e)
        print("User doesn't exist in db")
        return Response("User doesn't exist in db", status=500)

    # user_in_db=User.objects.get(id=4)

    obj=wallet.objects.filter(mentee_id=user_in_db.id, status=2).order_by('-updated_at')
    
    data_lst=[]
    if len(obj)==0:
        return {"current_balance":0,"history":data_lst}
    current_balance=obj[0].current_balance

    for row in obj:
        if row.current_balance>row.previous_balance:
            str1="Money Added"
        else:
            str1="Session for ..."
        data_dict={
            "order_id":row.txn_order_id,
            "message":str1,
            "amount_changed":row.amount_changed,
            "remarks":row.remarks,
            "date":row.updated_at.strftime("%Y-%m-%d %I:%M %p")
        }
        data_lst.append(data_dict)

    final_dict={
        "current_balance":current_balance,
        "history":data_lst
    }

    return final_dict


def make_payment_func(request):

    try:                                                                        #server
        user_in_db=User.objects.get(email=request.user)
    except Exception as e:
        print(e)
        print("Current user doesn't exist in db")
        return Response("Current user doesn't exist in db", status=500)


    # user_in_db=User.objects.get(id=4)                                           #local

    try:
        schedule_obj=mentor_schedule.objects.get(id=request.data['Schedule_id'],Status=1)
    except Exception as e:
        print(e)
        print("session doesn't exists in db")
        return Response("session doesn't exists in db",status=500)

    chargeable_amount = schedule_obj.session_charge

    sales_ord = sales_order()
    sales_ord.Schedule_id = schedule_obj.id
    sales_ord.Mentor_id = schedule_obj.Mentor_id
    sales_ord.Mentee_id = user_in_db.id
    sales_ord.Session_name = schedule_obj.Session_name
    sales_ord.Mentee_name = request.data['name']
    sales_ord.Mentee_phonenumber = request.data['phone_number']
    sales_ord.Mentee_email = request.data['email']
    sales_ord.session_charge = schedule_obj.session_charge

    if request.data['is_coupon_valid']==True:
        try:
            coupon_obj=coupon.objects.get(coupon_code=request.data['Coupon_id'])
            print("11111111111111111111111111111")
        except Exception as e:
            print(e)
            print("Coupon doesn't exists in db")
            return Response("Coupon doesn't exists in db", status=500)

        #session_charge=
        
        
        # if len(new_user)<=3:
        #if coupon_obj.new_user_coupon == 1:
        #    new_user = mentor_schedule.objects.filter(order_id=user_in_db.id) ############################################ whats this??
        #    if len(new_user) >= 4:
        #        print("This coupon is for new user who has booked 3 and less than 3 sessions.")
        #        return Response("This coupon is for new user who has booked 3 and less than 3 sessions.",status=500)

        coupon_amount = 0
        if coupon_obj.coupon_type == "flat":
            print("2222222222222222222",coupon_obj.coupon_amount)
            chargeable_amount = schedule_obj.session_charge - coupon_obj.coupon_amount
            coupon_amount = coupon_obj.coupon_amount

        if coupon_obj.coupon_type == "percentage":
            print("33333333333333333")
            discount = ((schedule_obj.session_charge * coupon_obj.coupon_percentage) // 100)
            chargeable_amount = schedule_obj.session_charge - discount
            coupon_amount = discount
        


        sales_ord.coupon_amount=coupon_amount
        sales_ord.coupon_id=request.data['Coupon_id']
    print("4444444444444444444",chargeable_amount)
    sales_ord.final_price = chargeable_amount
    sales_ord.save()

    wt=wallet.objects.filter(mentee_id=user_in_db.id,status=2).order_by('-updated_at')
    
    if len(wt)==0:
        data_dict = {
            "wallet_balance": 0,
            "session_charge": chargeable_amount
        }
    else:

        data_dict={
            "wallet_balance":wt[0].current_balance,
            "session_charge":chargeable_amount
        }
    

    return data_dict



def favourite_mentor_functions(request):
    
        
    try:                                                                            #server
        user_in_db=User.objects.get(email=request.user)
    except Exception as e:
        print(e)
        print("Current user not there in db")
        return Response("Current user not there in db",status=500)
    
    #user_in_db=User.objects.get(id=1)                                              #local

    obj=favourite_mentors.objects.filter(mentor_id=int(request.data['mentor_id']),mentee_id=user_in_db.id)
    
    if len(obj)>0:
        obj[0].delete()
        return 0
    else:
        row=favourite_mentors()
        row.mentor_id=request.data['mentor_id']
        row.mentee_id=user_in_db.id
        row.save()

        return 1


def profile_page_func(request):
    
    
    try:                                                                #server
        user_in_db=User.objects.get(email=request.user)
    except Exception as e:
        print(e)
        print("Current user not exist in db")
        return Response("Current user not exist in db",status=500)
    

    #user_in_db=User.objects.get(id=2)                                   #local

    lst=[]

    obj=mentor_schedule.objects.filter(Mentor_id=user_in_db.id,Is_scheduled=1)

    bank_det= mentor_bank_details.objects.filter(mentor_id=user_in_db.id).order_by('-created_at')


    account_name = ""
    account_number = ""
    ifsc_code = ""
    if len(bank_det)>0:
        account_name = bank_det[0].account_name
        account_number =bank_det[0].account_number
        ifsc_code = bank_det[0].ifsc_code

    if len(obj)==0:
        total_sessions=0
        total_amount=0
        topics=lst

    else:
        total_sessions=len(obj)
        amount=0
        
        for row in obj:
            amount += row.mentor_charge
            lst.append(row.Session_name)

        lst=list(dict.fromkeys(lst))
        lst.sort()

        total_amount=amount
        topics=lst

    data_dict={
            "name":user_in_db.name,
            "joined_on":user_in_db.date_joined.strftime("%d-%m-%Y"),
            "image":user_in_db.picture,
            "total_sessions":total_sessions,
            "total_amount":total_amount,
            "topics":lst,
            "account_name":account_name,
            "account_number":account_number,
            "ifsc_code":ifsc_code
    }

    return data_dict

        

        
    
def fetch_favourite_mentors_func(request):
    
    
    try:                                                            #server
        user_in_db=User.objects.get(email=request.user)
    except Exception as e:
        print(e)
        print("User doesn't exists in db")
        return Response("User doesn't exists in db",status=500)
 
    
 
    #user_in_db=User.objects.get(id=4)                  #local
 
    obj=favourite_mentors.objects.filter(mentee_id=user_in_db.id)
 
    data_lst=[]
 
    for row in obj:
        try:
            mentor=User.objects.get(id=row.mentor_id)
            m_profile=mentor_profile.objects.get(user=mentor)
        except:
            continue
 
        sessions=[]
        sch_obj=mentor_schedule.objects.filter(Mentor_id=mentor.id,Status=1)
 
        for roww in sch_obj:
            sessions.append(roww.Session_name)
 
        sessions=list(dict.fromkeys(sessions))
        sessions.sort()
 
        view_count = mentor_profile_clicks.objects.filter(mentor_id=row.mentor_id).values_list(
            'mentee_id').distinct().count()
 
 
        company_name=json.loads(m_profile.professional_details)[0]["company_name"]
        designation=json.loads(m_profile.professional_details)[0]["position"]
 
        data_dict={
            "avatar":m_profile.avatar,
            "name":m_profile.name,
            "industry_exp":m_profile.industry_exp,
            "id_":mentor.id,
            "company_name":company_name,
            "designation":designation,
            "session_names":sessions,
            "view_count":view_count
        }
 
        data_lst.append(data_dict)
 
    return data_lst


def request_session_func(request):

    
    try:                                                                    #server
        user_in_db=User.objects.get(email=request.user)
    except Exception as e:
        print(e)
        print("Current user doesn't exists in db")
        return Response("Current user doesn't exists in db",status=500)
    
    #user_in_db=User.objects.get(id=1)                                           #local   mentee

    find_row=request_sessions.objects.filter(mentee_id=user_in_db.id, mentor_id=int(request.data['mentor_id']),
                    session_name=request.data['session_name']).order_by('-updated_at')

    check=0
    #print(len(find_row))

    if len(find_row)==0:
        check=1
    
    else:
        t_24=datetime.timedelta(hours=24)
        current_time=datetime.datetime.now()
        if current_time-find_row[0].updated_at>=t_24:
            print("24 condition")
            check=1
        else:
            return "You have already made %s session request with this Mentor, Please wait for 24 hrs to make request again."%request.data['session_name']

    

    if check:
        row=request_sessions()
        row.mentee_id=user_in_db
        row.mentor_id=int(request.data['mentor_id'])
        row.session_name=request.data['session_name']

        row.save()

        mentor_ob = User.objects.get(id=int(request.data['mentor_id']))
        title = "You have received a session request"
        message = "Topic : "+request.data['session_name']
        send_push_notification(mentor_ob.mobile_token,message,title)

        return "Requested Successfully"


def mentor_notifications_func(user_id):

    
    # try:                                                                    #server
    #     user_in_db=User.objects.get(email=request.user)
    # except Exception as e:
    #     print(e)
    #     print("Current user doesn't exists in db")
    #     return Response("Current user doesn't exists in db",status=500)
    #

    #user_in_db=User.objects.get(id=5)                                       #local mentor     

    obj=request_sessions.objects.filter(mentor_id=user_id,mentor_notify=True).order_by('-updated_at')

    data_lst=[]
    for row in obj:
        try:
            mentee=User.objects.get(id=row.mentee_id)
        except Exception as e:
            print(e)
            print("Requested mentee doesn't exist in db")
            continue

        data_dict={
            "mentee_id":mentee.id,
            "mentee_name":mentee.name,
            "mentee_image":mentee.picture,
            "session":row.session_name,
            "req_session_id":row.id,
            "requested_on":str(row.created_at)
        }

        data_lst.append(data_dict)

    return data_lst

        
def notify_mentee_func(request):                                                    #mentor changing request_session table
    #
    # try:                                                                    #server
    #     user_in_db=User.objects.get(email=request.user)
    # except Exception as e:
    #     print(e)
    #     print("Current user doesn't exists in db")
    #     return Response("Current user doesn't exists in db",status=500)
    

    #user_in_db=User.objects.get(id=2)                                       #local mentor

    try:
        row=request_sessions.objects.get(id=request.data["req_session_id"])

        mentor_id = row.mentor_id
        session_name = row.session_name

        try:
            ms_rows = mentor_schedule.objects.filter(Mentor_id=mentor_id,Status=1,
                                     Is_scheduled=0,Session_name=session_name,Start_datetime__gt=datetime.datetime.now())
            print(len(ms_rows),"================")
            if len(ms_rows)>0:

                row.mentor_notify = False
                row.mentee_notify = True

                row.save()

                mentee_ob = User.objects.get(id=row.mentee_id)

                message = "Your requested session is now available to book"
                title = "A session on "+row.session_name+" has been created"
                send_push_notification(mentee_ob.mobile_token,message,title)

                return "Notified Successfully",1
            else:
                return "Please, first create atleast 2-3 sessions on - "+session_name,0
        except Exception as e:
            print(e,"eeeeeeeeeeeeee")
            return None,0

    except Exception as e:
        print(e)
        print("No row exists in request_sessions table ")
        return "NO such session request exists",1


def mentee_notifications_func(mentee_id):

    #
    

    #user_in_db=User.objects.get(id=1)                                      #local mentee
    print(mentee_id,type(mentee_id))
    obj=request_sessions.objects.filter(mentee_id=mentee_id,mentee_notify=1).order_by("-updated_at")

    data_lst=[]
    print(len(obj),"5555555555555555555555555555555555555555555555555555")
    for row in obj:
        try:
            mentor=mentor_profile.objects.get(user_id=row.mentor_id)
            prof_det = json.loads(mentor.professional_details)

            current_designation = prof_det[0]["position"]
            company_name = prof_det[0]["company_name"]
        except Exception as e:
            print(e)
            print("Mentor not exits in db with mentor id:", row.mentor_id)
            continue

        data_dict={
            "name":mentor.name,
            "designation":current_designation,
            "company_name":company_name,
            "avatar":mentor.avatar,
            "id_":mentor.id,
            "session_names":[row.session_name],
            "req_session_id":row.id
        }

        data_lst.append(data_dict)

    return data_lst

def remove_session_request(request,req_session_id):
    """

    :param req_session_id:
    :return:
    """

    try:                                                                    #server
        user_in_db=User.objects.get(email=request.user)
    except Exception as e:
        print(e)
        print("Current user doesn't exists in db")
        return Response("Current user doesn't exists in db",status=500)

    row = request_sessions.objects.get(id=req_session_id)


    if user_in_db.is_mentee:
        row.mentee_notify = False
        row.save()
    else:
        row.mentor_notify = False
        row.save()


def events_details_func(request):
    try:
        row=events.objects.get(id=request.data['event_id'])
    except Exception as e:
        print(e)
        return Response("row not exists", status=500)

    data_dict={
        "title":row.title,
        "image":row.image_link,
        "date_time":row.start_datetime.strftime("%d-%m-%Y %I:%M %p"),
        "duration":row.duration,
        "price":row.price,
        "about_mentor":row.about_the_mentor,
        "about_webinar":row.about_the_event,
        "key_takeaways":row.key_takeaways
    }

    return data_dict


def save_account_details(details,mentor_id):
    """

    :param details:
    :param mentor_id:
    :return:
    """

    mbd = mentor_bank_details()
    mbd.mentor_id = mentor_id
    mbd.account_name = details["account_name"].upper().strip()
    mbd.account_number = details["account_number"].strip()
    mbd.ifsc_code = details["ifsc_code"].strip()
    mbd.save()




