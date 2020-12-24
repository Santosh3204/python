
import math,re
from .mentor import *
from mentee.agora.call import *
from django.db import connection
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.generics import RetrieveAPIView
from django.views.generic.detail import DetailView

from django.http.response import Http404,HttpResponse
from .forms import SignUpForm
from django.views.decorators.csrf import csrf_exempt
import json
from django.core.exceptions import ObjectDoesNotExist
from .models import User

from django.shortcuts import render
import uuid
# Create your views here.
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from google.oauth2 import id_token

import jwt,json

#from django.shortcuts import redirect, render , render_to_response         #server
from django.shortcuts import redirect, render                               #local

import requests
from google.auth.transport import requests
from django.contrib.auth import login, authenticate
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from mentee.serializers import UserRegistrationSerializer, UserLoginSerializer

from rest_framework.generics import RetrieveAPIView
from rest_framework_jwt.settings import api_settings
from django.contrib.auth.models import update_last_login
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from django.shortcuts import get_object_or_404

from .models import MentorImage, mentor_schedule, mentor_topics, sales_order, mentor_profile, MentorFlow
from .serializers import MentorImageSerializer, mentor_schedule_serializer, mentor_topics_serializer, \
    sales_order_serializer

from rest_framework import status

from mentee.elastic_db import ElasticDB

import time
# from sqlalchemy import create_engine                    #local
# import sqlalchemy                                       #local

import razorpay                                         #local

es_ob = ElasticDB()

JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER

def index(request):
    return render(request, 'login.html')


class UserLoginView(RetrieveAPIView):
    permission_classes = (AllowAny,)

    # serializer_class = UserLoginSerializer

    def post(self, request):
        print(request.data)
        gmail_token = request.data['g_token']
        mobile_token = request.data['m_token']


        idinfo = id_token.verify_oauth2_token(gmail_token, requests.Request(), '191322235073-vgj1avkfgsgmke4gqmlaj0rqr77u3ha1.apps.googleusercontent.com')
        # idinfo = id_token.verify_oauth2_token(gmail_token, requests.Request(),
        #                                      '651163372936-adto0ri3mraijr8umjt9dh8c3l5tufc4.apps.googleusercontent.com')
        # print(idinfo, "id info")
        message = 'User already registered'
        status_code = status.HTTP_200_OK
        user_in_db = None
        response = {
            'success': True,

        }
        mentors = []
        try:
            user_in_db = User.objects.get(email=idinfo['email'])
            print(user_in_db, "1")
            print(user_in_db.pk, "2")
            is_mentee = user_in_db.is_mentee
            is_mentor = user_in_db.is_mentor

            if not is_mentee and not is_mentor:
                message = "User registered  successfully"
                status_code = status.HTTP_201_CREATED
            elif is_mentee or is_mentor:
                pass

        except ObjectDoesNotExist:
            user_in_db = User.objects.create_user(idinfo['email'], idinfo['name'], idinfo["picture"])
            print(user_in_db, "3")
            print(user_in_db.pk, "4")

            message = "User registered  successfully"
            status_code = status.HTTP_201_CREATED

        # saving mobile token
        user_in_db.mobile_token = mobile_token
        user_in_db.save()


        payload = JWT_PAYLOAD_HANDLER(user_in_db)
        jwt_token = JWT_ENCODE_HANDLER(payload)
        update_last_login(None, user_in_db)
        #jwt_token = jwt.encode(payload, "SECRET_KEY").decode('utf-8')
        response["message"] = message
        response["status_code"] = status_code
        response['token'] = jwt_token

        print(response, "response")
        return HttpResponse(json.dumps(response), status=status_code)


class DashboardView(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    def get(self, request):
        # print(request.user, "requestrequest")
        user_in_db = User.objects.get(email=request.user)
        print(user_in_db.id, "user det", user_in_db.email)
        is_mentee = user_in_db.is_mentee
        is_mentor = user_in_db.is_mentor

        response = {
            'success': True,
            "status_code":200,
            "is_mentee":True

        }

        message = 'User already registered'
        status_code = status.HTTP_200_OK

        if is_mentee:

            user_detail = MenteeDetails.objects.get(user_id=user_in_db.pk)
            # print(user_detail.career_list, "user_details", type(user_detail.career_list))
            if user_detail.profile == "student":

                user_detail_dict = {
                    # "College": user_detail.college,
                    #                 "Course": user_detail.course,
                                    "Degree": user_detail.degree,
                                    "fields": json.loads(user_detail.career_list),
                                    "Skills": json.loads(user_detail.skills)}
                mentors = es_ob.search_mentor_for_student(user_detail_dict)
            else:
                user_detail_dict = {
                    # "College": user_detail.college,
                                    "Degree": user_detail.degree, "fields": json.loads(user_detail.career_list),
                                    "Skills": json.loads(user_detail.skills),
                                    "CurrentDesignation": user_detail.designation,
                                    # "CurrentCompany": user_detail.company
                }
                mentors = es_ob.search_mentors_for_prof(user_detail_dict)


            so_rows = sales_order.objects.filter(Mentee_id=user_in_db.pk,Is_active=1,Status=1)

            upcoming_sessions = []
            for row in so_rows:
                schedule_id = row.Schedule_id
                mentor_id = row.Mentor_id
                men_prof = mentor_profile.objects.get(user_id=row.Mentor_id)
                avatar = user_in_db.picture
                name = user_in_db.name
                industry_exp = men_prof.industry_exp
                position = json.loads(men_prof.professional_details)[0]['position']
                session_name = row.Session_name
                schedule_tab = mentor_schedule.objects.get(id=schedule_id)
                start_time = schedule_tab.Start_datetime
                upcoming_sessions.append({"schedule_id":schedule_id,"id_":mentor_id,"name":name,"industry_exp":industry_exp,"avatar":avatar,
                 "position":position,"session_at":str(start_time),"session_name":session_name})

            upcoming_sessions.sort(key=lambda x: x['session_at'],reverse=True)

            response["data"] = {'recommended_mentors': mentors,"upcoming_sessions":upcoming_sessions}
            #print(user_in_db.pk,user_in_db.id,"-------------------------")
            req_sessions = mentee_notifications_func(user_in_db.id)
            print(req_sessions,"req_sessions")
            response["data"].update({"requested_sessions":req_sessions})
            # print(user_detail_dict)

        elif is_mentor:
            mentor_dict = {"mentor_id":user_in_db.pk,"is_scheduled":1}
            upcoming_sessions =fetch_booked_sessions(mentor_dict)
            response["is_mentee"] = False
            response["data"] = {"upcoming_sessions": upcoming_sessions}
            message = "success"
            request_sessions = mentor_notifications_func(user_in_db.id)
            response["data"].update({"requested_sessions":request_sessions})
        else:
            status_code = status.HTTP_201_CREATED
            message = "User has to fill registraion info"

        response["message"] = message
        response["user_email"] = user_in_db.email
        response["user_name"] = user_in_db.name

        return HttpResponse(json.dumps(response), status=status_code)


class UserProfileView(RetrieveAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    # def get(self, request):
    #     try:
    #         print(request.user, "requestrequest")
    #         user_det = User.objects.get(email=request.user)
    #         print(user_det.id, "user det", user_det.email)
    #
    #         # user_profile = MenteeDetails.objects.get(user_id=user_det.pk)
    #         # print(user_profile,"user_profile")
    #         status_code = status.HTTP_200_OK
    #         response = {
    #             'success': 'true',
    #             'message': 'User profile fetched successfully'
    #             # 'data': [{
    #             #     'first_name': user_profile.first_name,
    #             #     'last_name': user_profile.last_name,
    #             #     'phone_number': user_profile.phone_number,
    #             #     'age': user_profile.age,
    #             #     'gender': user_profile.gender,
    #             #     }]
    #         }
    #
    #     except Exception as e:
    #         status_code = status.HTTP_400_BAD_REQUEST
    #         response = {
    #             'success': 'false',
    #             'message': 'User does not exists',
    #             'error': str(e)
    #         }
    #     return Response(response, status=status_code)

    def post(self, request):
        # try:

        data = json.loads(request.body.decode("utf-8"))

        status_code = status.HTTP_200_OK
        mentors = []
        user = User.objects.get(email=request.user)
        if data["profile"] == "mentee":

            try:
                career1 = data["fields"][0]
            except:
                career1 = None
            try:
                career2 = data["fields"][1]
            except:
                career2 = None

            if data["subProfile"] == "student":

                user_details = MenteeDetails(user, profile=data["subProfile"],
                                             # college=data["College"],
                                             degree=data["Degree"],
                                             # course=data["Course"],
                                             goal_defined=data['careerGoals'],
                                             skills=json.dumps(data["Skills"]), career1=career1, career2=career2,
                                             career_list=json.dumps(data["fields"]),
                                             user_id=user.pk)

                user_details.save()

                user.is_mentee = 1
                user.save()

                mentors = es_ob.search_mentor_for_student(data)

            elif data["subProfile"] == 'professional':
                print("-------------------------")
                user_details = MenteeDetails(user, profile=data["subProfile"],
                                             # college=data["College"],
                                             degree=data["Degree"],
                                             # industry_exp=data["IndustryExperience"],
                                             skills=json.dumps(data["Skills"]),
                                             # company=data["CurrentCompany"],
                                             designation=data["CurrentDesignation"],
                                             same_profession=data["stayInField"],
                                             career1=career1, career2=career2, career_list=json.dumps(data["fields"]),
                                             user_id=user.pk)
                user_details.save()
                user.is_mentee = 1
                user.save()
                mentors = es_ob.search_mentors_for_prof(data)
                print("Trueeeeee")

            response = {
                'success': 'true',
                'recommended_mentors': mentors,
                'message': 'User data saved successfully'

            }

        else:
            mentor_flow = MentorFlow(user, linkedin_url=data["linkedin_url"], skills=json.dumps(data["skills"]),
                                     session_121=data["session_121"],
                                     webinar=data["webinar"], webinar_topics=json.dumps(data["webinar_topics"]),
                                     webinar_min=data["webinar_min"],
                                     webinar_max=data["webinar_max"], user_id=user.pk)

            mentor_flow.save()
            user.is_mentor = True
            user.save()

            response = {
                'success': 'true',
                'dashboard': "dashboard mentor",
                'message': 'User data saved successfully'

            }
        # except Exception as e:
        #     print(e,"=======")
        #     status_code = status.HTTP_400_BAD_REQUEST
        #     response = {
        #         'success': 'true',
        #         'status_code': status.HTTP_400_BAD_REQUEST,
        #         'message': 'User does not exists',
        #         'error': str(e)
        #         }
        return Response(response, status=status_code)


class AddMentorData(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

@csrf_exempt
def insert_mentor_data(request):
    mentor_data = json.loads(request.body.decode("utf-8"))

    request_keys = set(mentor_data.keys())

    required_keys = {"mentor_id", "professional_details", "educational_details"
                     ,"location","skills","name", "avatar", "email", "languages","about"}

    keys_diff = required_keys.difference(request_keys)

    status_code = status.HTTP_201_CREATED
    success = True
    message = "User created"
    response = {
        'success': success,
        'message': message

    }

    if len(keys_diff) > 0:
        status_code = status.HTTP_400_BAD_REQUEST
        response["success"] = False
        response["message"] = "required keys doesn't exist :- " + str(keys_diff)
        return JsonResponse(response, status=status_code)

    user_row = User.objects.get(pk=int(mentor_data["mentor_id"]))

    mentor_flow = MentorFlow.objects.get(user_id=user_row.pk)

    skills = json.loads(mentor_flow.skills)

    mentor_data["skills"] = list(set(mentor_data["skills"] + skills))

    industry_exp = es_ob.add_mentor_data(mentor_data)

    men_pro = mentor_profile(user_row, name=mentor_data["name"], avatar=mentor_data["avatar"],
                             languages=json.dumps(mentor_data["languages"]),industry_exp=industry_exp,
                             about=mentor_data["about"], email=mentor_data["email"], location=mentor_data["location"],
                             professional_details=json.dumps(mentor_data["professional_details"]), status=1,
                             educational_details=json.dumps(mentor_data["educational_details"]),
                             skills=json.dumps(mentor_data["skills"]), user_id=user_row.pk)

    men_pro.save()
    mentor_flow.details_filled = 1
    mentor_flow.save()

    return JsonResponse(response, status=status_code)


class UserView(DetailView):
    template_name = 'profile.html'

    def get_object(self):
        return self.request.user


# @csrf_exempt
# @login_required(login_url='/mentee/login/')
# def check_session(request):
#     if request.method == 'GET':
#         print(request.session.keys(), "request.user.is_authenticated", request.user.is_authenticated)
#         if request.session.has_key('member_id'):
#             print(request.session['member_id'], "------")
#             user = User.objects.get(id=request.session['member_id'])
#             username = request.session['member_id']
#             return HttpResponse("user logged in " + str(user.email))
#         else:
#             return HttpResponse("user not loggied in")
#
#     else:
#         return HttpResponse("only get")


# starting mentor_santosh code.

# Create your views here.


# Api for getting image path and name of that person by passing id.

def index_image(request):
    return render(request, "home.html")


class MentorView(APIView):

    # renderer_classes = [TemplateHTMLRenderer]
    # template_name = 'home.html'

    def get(self, request, id):
        mentor = MentorImage.objects.get(image_id=id)
        serializer = MentorImageSerializer(mentor)
        return Response(serializer.data)

        # mentor = get_object_or_404(MentorImage, image_id= id)

        # return Response({'mentor': mentor})


# API for to create schedule for mentor.


class Mentor_Topics_API(APIView):                                           # Adding topics of webinar for a mentor in DB.


    permission_classes = (AllowAny,)

    def post(self, request):
        if type(request.data) != dict:
            return Response("Request body not in Dictionary format", status=400)

        elif len(request.data) != 7:
            return Response("No. of keys is mis-matched, it should be 7", status=400)

        actual_dict = {
            "Mentor_id": int,
            "Linked_url": str,
            "Skills": str,
            "Session_121": int,
            "Webinar": int,
            "Webinar_Topics": list,
            "Webinar_charge": str
        }

        for i in actual_dict:
            if i not in request.data:
                return Response("Keys in Request body mis-matched", status=400)

            if type(request.data[i]) != actual_dict[i]:
                return Response("Values datatype in Request body is mis-matched", status=400)

        text = Mentor_Topics_API_func(request)
        return Response(text, status=200)


class FetchMentorProfile(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication
    # permission_classes = (AllowAny,)

    def get(self, request):

        return Response("get method called successfully")

    def post(self, request):
        """

        :param request:
        :return:
        """
        request_data = request.data

        mentor_id = request_data["mentor_id"]
        one2one_topics = request_data["session_names"]

        data = mentor_profile.objects.get(user_id=mentor_id)

        prof_details = json.loads(data.professional_details)
        edu_details = json.loads(data.educational_details)
        name = data.name
        avatar = data.avatar
        industry_exp = data.industry_exp
        skills = json.loads(data.skills)
        about = data.about

        languages = json.loads(data.languages)

        user_in_db = User.objects.get(email=request.user)
        mentee_id = user_in_db.id

        fav_ment_ob = favourite_mentors.objects.filter(mentee_id=mentee_id,mentor_id=mentor_id)

        fav = 0
        if len(fav_ment_ob)>0:
            fav=1

        current_company = None
        current_designation = None

        for prof in prof_details:
            current_company = prof["company_name"]
            current_designation = prof["position"]
            break

        schedule = fetch_mentors_schedule(mentor_id,0,one2one_topics[0])

        resp = {"mentor_id": mentor_id,
                "mentor_name": name,
                "designation": current_designation,
                "company": current_company,
                "about_me": about,
                "avatar": avatar,
                "industry_exp": industry_exp,
                "skills": skills,
                "languages": languages,
                "professional_details": prof_details,
                "educational_details": edu_details,
                "schedule":schedule,
                "fav":fav}

        return JsonResponse(resp, status=200)


class Fetch_Mentor_Schedule_Api(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):

        return Response("get method called successfully")

    def post(self, request):

        if type(request.data) != dict:
            return Response("Request body not in Dictionary format", status=400)

        elif len(request.data) != 3:
            return Response("No. of keys is mis-matched, it should be 3", status=400)

        actual_dict = {
            "mentor_id": int,
            "is_scheduled": int,
            "session_name": str
        }

        for i in actual_dict:
            if i not in request.data:
                return Response("Keys in Request body mis-matched", status=400)

            if type(request.data[i]) != actual_dict[i]:
                return Response("Values datatype in Request body is mis-matched", status=400)

        mentor_id = request.data["mentor_id"]
        is_scheduled = request.data["is_scheduled"]

        session_name = None
        if 'session_name' in request.data:
            session_name = request.data["session_name"]

        response_dict = {
            "Mentor_id": request.data["mentor_id"]
        }

        schedule = fetch_mentors_schedule(mentor_id, is_scheduled, session_name)

        response_dict.update({"schedule": schedule})

        return Response(response_dict)


class Mentor_Calender_API(APIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    def get(self, request):

        resp_list = Mentor_Calender_API_func(request)
        resp_dict = {
            "status": status.HTTP_200_OK,
            "message": "success",
            "data": resp_list
        }
        return Response(resp_dict)


class Row_Deactivate_API(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    def post(self, request):
        if type(request.data) != dict:
            return Response("Request body not in Dictionary format", status=400)

        elif len(request.data) != 1:
            return Response("No. of keys is mis-matched, it should be 1", status=400)

        actual_dict = {
            "Schedule_id": int
        }

        for i in actual_dict:
            if i not in request.data:
                return Response("Keys in Request body mis-matched", status=400)

            if type(request.data[i]) != actual_dict[i]:
                return Response("Values datatype in Request body is mis-matched", status=400)

        data = Row_Deactivate_API_func(request)
        return Response(data=data, status=status.HTTP_200_OK)


class Booking_121(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    def post(self, request):

        if type(request.data) != dict:
            return Response("Request body not in Dictionary format", status=400)

        elif len(request.data) != 2:
            return Response("No. of keys is mis-matched, it should be 2", status=400)

        actual_dict = {
            "Schedule_id": int,
            "mentee_id": int
        }

        for i in actual_dict:
            if i not in request.data:
                return Response("Keys in Request body mis-matched", status=400)

            if type(request.data[i]) != actual_dict[i]:
                return Response("Values datatype in Request body is mis-matched", status=400)

        data_dict = Booking_121_func(request)

        resp_dict = {
            "status": status.HTTP_200_OK,
            "message": "success",

        }
        resp_dict.update(data_dict)

        return Response(resp_dict)


class Mentor_Profile_API(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    def post(self, request):
        if type(request.data) != dict:
            return Response("Request body not in Dictionary format", status=400)

        elif len(request.data) != 1:
            return Response("No. of keys is mis-matched, it should be 1", status=400)

        actual_dict = {
            "Mentor_id": int
        }

        for i in actual_dict:
            if i not in request.data:
                return Response("Keys in Request body mis-matched", status=400)

            if type(request.data[i]) != actual_dict[i]:
                return Response("Values datatype in Request body is mis-matched", status=400)

        data_dict = Mentor_Profile_API_func(request)
        resp_dict = {
            "status": status.HTTP_200_OK,
        }
        resp_dict.update(data_dict)

        return Response(resp_dict)

class Mentor_Schedule_API(APIView):  # API to schedule for mentor.

    permission_classes = (IsAuthenticated,)                             #server
    authentication_class = JSONWebTokenAuthentication
    

    #permission_classes = [AllowAny,]                                    #local

    # def get(self, request):

    # schedule = get_object_or_404(mentor_schedule, Mentor_id= id)
    # schedule = mentor_schedule.objects.filter(Mentor_id= request.data['Mentor_id'])
    # serializer = mentor_schedule_serializer(schedule, many= True)
    # return Response(serializer.data)

    # def post(self, request):
    #
    #     user_in_db = User.objects.get(email=request.user)
    #     mentor_id = user_in_db.id
    #
    #     text = None
    #     try:
    #         if type(request.data) == dict:
    #             if len(request.data) == 6:
    #                 if type(request.data.get('session_names')) == list and type(
    #                         request.data.get('Days')) == list and type(request.data.get('Start_date')) == str and type(
    #                         request.data.get('end_date')) == str and type(request.data.get('st_time')) == str and type(
    #                         request.data.get('charge')) == int:
    #                             print("777777777777777777")
    #                             text = Mentor_Schedule_API_func(request,mentor_id)
    #                 else:
    #                     raise Exception()
    #             else:
    #                 raise Exception()
    #
    #     except:
    #         return Response("Invalid Request")
    #
    #     cursor= connection.cursor()
    #     query = "SELECT distinct(Session_name) FROM mbox.mentee_mentor_schedule where mentor_id="+str(mentor_id)+" and status=1 and Is_scheduled=0;"
    #     cursor.execute(query)
    #     o2o_topics= []
    #     for topic in cursor.fetchall():
    #         o2o_topics.append(topic[0])
    #     cursor.close()
    #
    #     # increase charge by 100% for mentorbox
    #     mb_charge = 2*request.data["charge"]
    #
    #     es_ob.update_mentor_topics_in_es(o2o_topics, mentor_id, mb_charge)
    #
    #     return Response(text)

    def post(self, request):

        
        user_in_db = User.objects.get(email=request.user)                   #server
        mentor_id = user_in_db.id
        
        if type(request.data) != dict:
            return Response("Request body not in Dictionary format", status=400)

        
        elif len(request.data) != 6:                                                        #server
            return Response("No. of keys is mis-matched, it should be 6", status=400)
        
        #elif len(request.data) != 7:                                                        #local
        #    return Response("No. of keys is mis-matched, it should be 7", status=400)
        
        actual_dict = {
            "session_names": list,
            "Days": list,
            "Start_date": str,
            "end_date": str,
            "st_time": str,
            "charge": int
        }

        for i in actual_dict:
            if i not in request.data:
                return Response("Keys in Request body mis-matched", status=400)

            if type(request.data[i]) != actual_dict[i]:
                return Response("Values datatype in Request body is mis-matched", status=400)

        #mentor_id = 2                                 #local
        text = Mentor_Schedule_API_func(request,mentor_id)

        cursor = connection.cursor()
        query = "SELECT distinct(Session_name) FROM mbox.mentee_mentor_schedule where mentor_id=" + str(
            mentor_id) + " and status=1 and Is_scheduled=0;"
        cursor.execute(query)

        o2o_topics = []
        for topic in cursor.fetchall():
            o2o_topics.append(topic[0])
        cursor.close()

        # increase charge by 100% for mentorbox
        mb_charge = 2 * request.data["charge"]
        es_ob.update_mentor_topics_in_es(o2o_topics, mentor_id, mb_charge)

        return Response(text)


#class excel_to_table(APIView):
#    
#    permission_classes = [AllowAny, ]
#
#    def post(self, request):
#        #df = pd.read_excel(r'C:\Users\S.Santosh Kumar\Desktop\Mentorbox App\data.xlsx', sheet_name='Courses List', usecols=['College_Name', 'Level_of_Course', 'Degree'])
#        df = pd.read_excel(r'C:\Users\S.Santosh Kumar\Desktop\skills_excel.xlsx', sheet_name='skills_excel', usecols=["name"])
#        #df = pd.read_excel(r'C:\Users\S.Santosh Kumar\Desktop\companies.xlsx', sheet_name='companies_sorted',usecols=["name"])
#        #df = pd.read_excel(r'C:\Users\S.Santosh Kumar\Desktop\\Mentorbox App\degree.xlsx', sheet_name='Sheet2', usecols=["degree_name"])
#        print(df)
#        print("data")
#        db_username = "root"
#        db_password = "Santosh@2k"
#        db_ip = "localhost"
#        db_name = "mbox"
#        # db_port = 3306
#
#        conn = sqlalchemy.create_engine('mysql+mysqlconnector://{0}:{1}@{2}/{3}'.
#                                    format(db_username, db_password,
#                                            db_ip, db_name)
#
#                                        )
#
#        print(conn)
#
#        #df.to_sql(con= conn, name= "mentee_course_list", if_exists= "append", index= True, index_label= "id")
#        df.to_sql(con= conn, name= "mentee_skills_list", if_exists= "append", index= True, index_label= "id")
#        #df.to_sql(con=conn, name="mentee_companies_list", if_exists="append", index=True, index_label="id")
#        #df.to_sql(con=conn, name="mentee_degree_list", if_exists="append", index=False)
#        return Response("Done see results")
    

class Create_Order_API(APIView):

    permission_classes = (IsAuthenticated,)                                 #server
    authentication_class = JSONWebTokenAuthentication

    #permission_classes=(AllowAny,)                                           #local



    def post(self, request):

        if type(request.data) != dict:
            return Response("Request body not in Dictionary format", status=400)

        elif len(request.data) != 3:
            return Response("No. of keys is mis-matched, it should be 5", status=400)

        actual_dict = {
            "Schedule_id": int,
            "amount_to_add":int,
            "use_wallet":bool
        }

        for i in actual_dict:
            if i not in request.data:
                return Response("Keys in Request body mis-matched", status=400)

            # if type(request.data[i]) != actual_dict[i]:                       ######################################## bug
            #     return Response("Values datatype in Request body is mis-matched", status=400)

        order_id,order_amount = Create_Order_API_func(request)

        
        resp_dict = {
        "status": status.HTTP_200_OK,
        "order_amount": order_amount,
        "order_id":order_id

        }


        return Response(resp_dict)


class RP_Sign_Verification(APIView):

    permission_classes = (IsAuthenticated,)                                #server
    authentication_class = JSONWebTokenAuthentication

    #permission_classes=(AllowAny,)                                          #local


    def post(self, request):
        if type(request.data) != dict:
            return Response("Request body not in Dictionary format", status=400)

        elif len(request.data) != 3:
            return Response("No. of keys is mis-matched, it should be 3", status=400)

        actual_dict = {
            "razorpay_order_id": str,
            "razorpay_payment_id": str,
            "razorpay_signature": str
        }

        for i in actual_dict:
            if i not in request.data:
                return Response("Keys in Request body mis-matched", status=400)

            if type(request.data[i]) != actual_dict[i]:
                return Response("Values datatype in Request body is mis-matched", status=400)

        resp_note = RP_Sign_Verification_func(request)
        print(resp_note)
        resp_dict = {
            "status": status.HTTP_200_OK,
            "note": resp_note
        }

        return Response(resp_dict)


class Booked_Sessions(APIView):

    permission_classes = [AllowAny, ]

    def post(self, request):
        if type(request.data) != dict:
            return Response("Request body not in Dictionary format", status=400)

        elif len(request.data) != 1:
            return Response("No. of keys is mis-matched, it should be 1", status=400)

        actual_dict = {"Is_scheduled": int
                       }

        for i in actual_dict:
            if i not in request.data:
                return Response("Keys in Request body mis-matched", status=400)

            if type(request.data[i]) != actual_dict[i]:
                return Response("Values datatype in Request body is mis-matched", status=400)

        resp_list = Booked_Sessions_func(request)
        resp_dict = {
            "status": status.HTTP_200_OK,
            "message": "success",
            "data": resp_list
        }

        return Response(resp_dict)


class Search_API(APIView):
    permission_classes = [AllowAny, ]

    def post(self, request):

        if type(request.data) != dict:
            return Response("Request body not in Dictionary format", status=400)

        elif len(request.data) != 2:
            return Response("No. of keys is mis-matched, it should be 2", status=400)

        actual_dict = {"name": str,
                       "type": str
                       }

        for i in actual_dict:
            if i not in request.data:
                return Response("Keys in Request body mis-matched", status=400)

            if type(request.data[i]) != actual_dict[i]:
                return Response("Values datatype in Request body is mis-matched", status=400)

            resp_list = Search_API_func(request)
            resp_dict = {
                "status": status.HTTP_200_OK,
                "data": resp_list
            }

            return Response(resp_dict)


class Fetch_Session_Names_API(APIView):
    permission_classes = [AllowAny, ]

    def post(self, request):
        if type(request.data) != dict:
            return Response("Request body not in Dictionary format", status=400)

        elif len(request.data) != 1:
            return Response("No. of keys is mis-matched, it should be 1", status=400)

        actual_dict = {"name": str
                       }

        for i in actual_dict:
            if i not in request.data:
                return Response("Keys in Request body mis-matched", status=400)

            if type(request.data[i]) != actual_dict[i]:
                return Response("Values datatype in Request body is mis-matched", status=400)

            resp_list = Fetch_Session_Names_API_func(request)  # returning list of sessions names
            resp_dict = {
                "status": status.HTTP_200_OK,
                "session_names": resp_list
            }

            return Response(resp_dict)


class Mentor_Details_API(APIView):
    permission_classes = [AllowAny, ]

    def post(self, request):

        if type(request.data) != dict:
            return Response("Request body not in Dictionary format", status=400)

        elif len(request.data) != 1:
            return Response("No. of keys is mis-matched, it should be 1", status=400)

        actual_dict = {"Schedule_id": int
                       }

        for i in actual_dict:
            if i not in request.data:
                return Response("Keys in Request body mis-matched", status=400)

            if type(request.data[i]) != actual_dict[i]:
                return Response("Values datatype in Request body is mis-matched", status=400)

            resp_dict = {
                "status": status.HTTP_200_OK
            }

            data_dict = Mentor_Details_API_func(request)

            resp_dict.update(data_dict)

            return Response(resp_dict)


class Coupon_API(APIView):
    permission_classes = (IsAuthenticated,)                                   #server
    authentication_class = JSONWebTokenAuthentication

    #permission_classes = [AllowAny, ]                                          #local

    def post(self, request):

        if type(request.data) != dict:
            return Response("Request body not in Dictionary format", status=400)

        elif len(request.data) != 2:
            return Response("No. of keys is mis-matched, it should be 2", status=400)

        actual_dict = {"schedule_id": int,
                       "coupon_code": str
                       }

        for i in actual_dict:
            if i not in request.data:
                return Response("Keys in Request body mis-matched", status=400)

            if type(request.data[i]) != actual_dict[i]:
                return Response("Values datatype in Request body is mis-matched", status=400)

        resp_dict = {
            "status": status.HTTP_200_OK
        }

        data_dict = Coupon_API_func(request)

        resp_dict.update(data_dict)

        return Response(resp_dict)


class Mentee_My_Orders_API(APIView):
        
    permission_classes = (IsAuthenticated,)                             #server
    authentication_classes = JSONWebTokenAuthentication

    #permission_classes = (AllowAny,)                               #local

    def get(self, request):
        
        resp_dict = {
            "status": status.HTTP_200_OK
        }

        data_dict = Mentee_My_Order_API_func(request)

        resp_dict.update(data_dict)

        return Response(resp_dict)

class Mentor_My_Orders_API(APIView):
        
    permission_classes = (IsAuthenticated,)                             #server
    authentication_class = JSONWebTokenAuthentication
        
    #permission_classes = (AllowAny,)                               #local

    def get(self, request):
        

        data_lst,mentee_status = Mentor_My_Orders_API_func(request)
        
        resp_dict = {
            "status": status.HTTP_200_OK,
            "is_mentee":mentee_status,
            "data":data_lst
        }
        
        
        return Response(resp_dict)

class Mentor_Payment_History(APIView):

    permission_classes=(IsAuthenticated,)                                   #server
    authentication_classes=JSONWebTokenAuthentication

    #permission_classes=(AllowAny,)                                          #local

    def get(self, request):
        resp_dict={
            "status":status.HTTP_200_OK
        }

        data_list=Mentor_Payment_History_func(request)
        
        resp_dict.update({"data":data_list})
        
        return Response(resp_dict)


class Mentee_Feedback(APIView):

    #permission_classes=(IsAuthenticated,)               #server
    #authentication_classes=JSONWebTokenAuthentication

    permission_classes=(AllowAny,)                      #local
    def post(self, request):
        if type(request.data) != dict:
            return Response("Request body not in Dictionary format", status=400)

        elif len(request.data) != 3:
            return Response("No. of keys is mis-matched, it should be 3", status=400)

        actual_dict = {"schedule_id":int,
                       "star_rating": int,
                       "comments": str
                       }

        for i in actual_dict:
            if i not in request.data:
                return Response("Keys in Request body mis-matched", status=400)

            if type(request.data[i]) != actual_dict[i]:
                return Response("Values datatype in Request body is mis-matched", status=400)

        Mentee_Feedback_func(request)
    
        return Response("Feedback Saved", status=200)


class VoiceCalling(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication
    # permission_classes = [AllowAny, ]

    def post(self,request):

        data = request.data

        if "schedule_id" not in data:
            return Response("schedule_id not present", status=400)

        schedule_id = data["schedule_id"]

        voice_det = generate_voice_token(schedule_id,request)

        return Response(voice_det,status=status.HTTP_200_OK)


class DisconnectCall(APIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    # permission_classes = [AllowAny, ]
    def post(self,request):
        data = request.data

        request_struc = {"schedule_id":int,"channel_name":str,"call_completed":bool}

        for req_key in request_struc:
            if req_key not in data:
                return Response(req_key+" not present", status=400)

        disconnect_call(request,data)

        return Response(status=200)


class ChannelEventListener(APIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    # permission_classes = [AllowAny, ]

    def post(self,request):

        data = request.data

        request_struc = {"schedule_id": int, "channel_name": str, "callback_status": bool}

        for req_key in request_struc:
            if req_key not in data:
                return Response(req_key + " not present", status=400)

        channel_event_listener(request, data)

        return Response(status=200)


class Wallet_API(APIView):

    permission_classes=(IsAuthenticated,)                           #server
    authentication_class=JSONWebTokenAuthentication
    #permission_classes=(AllowAny,)                                  #local

    def post(self, request):
        if type(request.data) != dict:
            return Response("Request body not in Dictionary format", status=400)

        elif len(request.data) != 1:
            return Response("No. of keys is mis-matched, it should be 1", status=400)

        actual_dict = {"amount":int
                       }

        for i in actual_dict:
            if i not in request.data:
                return Response("Keys in Request body mis-matched", status=400)

            if type(request.data[i]) != actual_dict[i]:
                return Response("Values datatype in Request body is mis-matched", status=400)

        order_id=Wallet_API_func(request)

        resp_dict={
            "status":200,
            "message":"success",
            "order_id":order_id
            
        }
        return Response(resp_dict)
    
    
class wallet_verification(APIView):
    
    permission_classes=(IsAuthenticated,)                               #server
    authentication_class=JSONWebTokenAuthentication

    #permission_classes=(AllowAny,)

    def post(self,request):
        if type(request.data) != dict:
            return Response("Request body not in Dictionary format", status=400)

        elif len(request.data) != 3:
            return Response("No. of keys is mis-matched, it should be 3", status=400)

        actual_dict = {"razorpay_order_id":str,
                        "razorpay_payment_id":str,
                        "razorpay_signature":str
                       }

        for i in actual_dict:
            if i not in request.data:
                return Response("Keys in Request body mis-matched", status=400)

            if type(request.data[i]) != actual_dict[i]:
                return Response("Values datatype in Request body is mis-matched", status=400)

        data_dict=wallet_verification_func(request)


        resp_dict={
            "status":200,
        }

        resp_dict.update(data_dict)
        return Response(resp_dict)


class wallet_history(APIView):
    permission_classes=(IsAuthenticated,)                           #server
    authentication_class=JSONWebTokenAuthentication
    
    
    #permission_classes=(AllowAny,)                                  #local

    def get(self, request):

        resp_dict={
            "status":200
        }

        data_dict=wallet_history_func(request)

        resp_dict.update(data_dict)
        return Response(resp_dict)


class make_payment(APIView):
    permission_classes=(IsAuthenticated,)                           #server
    authentication_class=JSONWebTokenAuthentication

    # permission_classes=(AllowAny,)

    def post(self,request):
        if type(request.data) != dict:
            return Response("Request body not in Dictionary format", status=400)

        elif len(request.data) != 6:
            return Response("No. of keys is mis-matched, it should be 7", status=400)

        actual_dict = {"Schedule_id":int,
                        "name":str,
                        "phone_number":str,
                        "email":str,
                        "is_coupon_valid":bool,
                        "Coupon_id":str
                       }

        for i in actual_dict:
            if i not in request.data:
                return Response("Keys in Request body mis-matched", status=400)

            # if type(request.data[i]) != actual_dict[i]: ########################################################### bug ??????
            #     return Response("Values datatype in Request body is mis-matched", status=400)

        data_dict=make_payment_func(request)




        resp_dict={
            "status":200,
        }

        resp_dict.update(data_dict)
        return Response(resp_dict)


class update_favourite_mentors(APIView):
    permission_classes=(IsAuthenticated,)                   #server
    authentication_class=JSONWebTokenAuthentication

    #permission_classes=(AllowAny,)                          #local

    def post(self,request):
        if type(request.data) != dict:
            return Response("Request body not in Dictionary format", status=400)

        elif len(request.data) != 1:
            return Response("No. of keys is mis-matched, it should be 1", status=400)

        actual_dict = {"mentor_id":str,
                       }

        for i in actual_dict:
            if i not in request.data:
                return Response("Keys in Request body mis-matched", status=400)

            if type(request.data[i]) != actual_dict[i]:
                return Response("Values datatype in Request body is mis-matched", status=400)

        added_status=favourite_mentor_functions(request)

        resp_dict={
            "status":200,
            "added":added_status

        }

        return Response(resp_dict)


class profile_page(APIView):
    permission_classes=(IsAuthenticated,)                   #server
    authentication_class=JSONWebTokenAuthentication

    #permission_classes=(AllowAny,)                          #local

    def get(self,request):

        data_dict=profile_page_func(request)

        resp_dict={
            "status":200
        }
        resp_dict.update(data_dict)


        return Response(resp_dict)


class FindMentors(APIView):

    permission_classes=(AllowAny,)

    def post(self,request):

        search_data = request.data

        mandatory_fileds = {"skills","career_profile","languages","exp","min_charge","max_charge"}

        if len(mandatory_fileds.difference(set(search_data.keys())))>0:
            return Response("request fields missing",status=400)

        profiles = es_ob.find_mentor(search_data)

        if profiles is None:
            return Response("Please select profile or skills",status=400)

        resp_dict = {
            "status": 200,
            "data":profiles
        }
        # resp_dict.update(data_dict)

        return Response(resp_dict)


"""
class Razorpay_test(APIView):
    permission_classes=(AllowAny,)
    def post(self, request):
        

        client=razorpay.Client(auth=("rzp_test_A5QQVVWf0eMog1", "mwIcHdj1fIDGVi44N6BoUX0W"))
        #client = razorpay.Client(auth=('rzp_test_JAObx3Y47SmBhB', 'RKxq0NX3rGgEZ3HEKt5cr5BT'))
        #order_id = request.data['order_id']
        payment_id = request.data['payment_id']

        resp = client.payment.fetch(payment_id)
        #resp = client.order.fetch(order_id)
        print(resp)
        return Response(resp, status=200)

class Pay_test(APIView):
    permission_classes=(AllowAny,)

    def post(self, request):
        

        order_amount = 3000
        order_currency = 'INR'
        order_receipt = "MB211"
        notes = {'Shipping address': 'Bommanahalli, Bangalore'}  # OPTIONAL
        # client = razorpay.Client(auth=('rzp_test_JAObx3Y47SmBhB', 'RKxq0NX3rGgEZ3HEKt5cr5BT'))
        client = razorpay.Client(auth=('rzp_test_A5QQVVWf0eMog1', 'mwIcHdj1fIDGVi44N6BoUX0W'))

        response = client.order.create(
            dict(amount=order_amount, currency=order_currency, receipt=order_receipt, notes=notes))
        print("**********************")
        print(response['id'])
        return render(request, 'payment.html', {'order_id':response['id']})


"""


class fetch_favourite_mentors(APIView):
    permission_classes=(IsAuthenticated,)           #server
    authentication_class=JSONWebTokenAuthentication

    def get(self,request):
        data_list=fetch_favourite_mentors_func(request)

        resp_dict={
            "status":200,
             "data": data_list
        }
        print(resp_dict)
        #resp_dict.update(data_dict)

        return Response(resp_dict)

class request_session(APIView):
    
    permission_classes=(IsAuthenticated,)           #server
    authentication_class=JSONWebTokenAuthentication

    #permission_classes=(AllowAny,)                      #local

    def post(self,request):
        if type(request.data) != dict:
            return Response("Request body not in Dictionary format", status=400)

        elif len(request.data) != 2:
            return Response("No. of keys is mis-matched, it should be 1", status=400)

        actual_dict = {"mentor_id":str,
                        "session_name":str
                       }

        for i in actual_dict:
            if i not in request.data:
                return Response("Keys in Request body mis-matched", status=400)

            if type(request.data[i]) != actual_dict[i]:
                return Response("Values datatype in Request body is mis-matched", status=400)

        msg=request_session_func(request)

        resp_dict={
            "status":200,
            "message":msg

        }

        return Response(resp_dict)


class mentor_notifications(APIView):

    permission_classes=(IsAuthenticated,)                   #server
    authentication_class=JSONWebTokenAuthentication

    #permission_classes=(AllowAny,)


    def get(self,request):

        try:  # server
            user_in_db = User.objects.get(email=request.user)

        except Exception as e:
            print(e)
            print("Requested user doesn't exist in db")
            return Response("Requested user doesn't exist in db", status=500)

        data_lst=mentor_notifications_func(user_in_db.id)

        resp_dict={
            "status":200,
            "requested_sessions":data_lst
        }

        return Response(resp_dict)

class notify_mentee(APIView):
    permission_classes=(IsAuthenticated,)                   #server
    authentication_class=JSONWebTokenAuthentication

    #permission_classes=(AllowAny,)

    def post(self,request):
        if type(request.data) != dict:
            return Response("Request body not in Dictionary format", status=400)

        elif len(request.data) != 1:
            return Response("No. of keys is mis-matched, it should be 1", status=400)

        actual_dict = {"req_session_id":int,
                       }

        for i in actual_dict:
            if i not in request.data:
                return Response("Keys in Request body mis-matched", status=400)

            if type(request.data[i]) != actual_dict[i]:
                return Response("Values datatype in Request body is mis-matched", status=400)

        success_msg,reload_status=notify_mentee_func(request)
        resp_dict={
            "status":200,
            "message":success_msg,
            "reload_status":reload_status

        }

        if success_msg is None:
           resp_dict={
            "status":200,
            "message":"Please schedule session first"

           }
        

        return Response(resp_dict)


class CancelSessionRequest(APIView):
    permission_classes = (IsAuthenticated,)  # server
    authentication_class = JSONWebTokenAuthentication

    # permission_classes=(AllowAny,)

    def post(self,request):

        data = request.data

        actual_dict = {"req_session_id": int,
                       }

        if 'req_session_id' not in data:
            return Response("req_session_id not present in request data", status=400)

        remove_session_request(request,data["req_session_id"])

        return Response(status=200)

class mentee_notifications(APIView):
    permission_classes=(IsAuthenticated,)                   #server
    authentication_class=JSONWebTokenAuthentication

    #permission_classes=(AllowAny,)


    def get(self,request):
        try:                                                                    #server
            user_in_db=User.objects.get(email=request.user)
        except Exception as e:
            print(e)
            print("Current user doesn't exist in db")
            return Response("Current user doesn't exist in db",status=500)

        data_lst=mentee_notifications_func(user_in_db.id)

        resp_dict={
            "status":200,
            "mentors":data_lst
        }

        return Response(resp_dict)

