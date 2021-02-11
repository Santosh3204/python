#!/usr/bin/env python
# coding: utf-8

import mysql.connector
import time
import datetime
import json
import requests


class SendPushNotification:

    def __int__(self):
        self.conn = mysql.connector.connect(host='65.1.116.219',user='santosh',passwd='Only@123',database='mbox')

    @staticmethod
    def send_push_notification(mobile_token, message,title):
        """

        :param mobile_token:
        :param message:
        :param title:
        :return:
        """
        # sending push notification for call completion
        fcm_key = "AAAAOFlketw:APA91bF7JEPkPpBQ6QKqbKEQ4hBSBGSk1V2qpS5sgcn-FKe0TrTO-PcIjndN3SOBkyXksPXojzHJDoVGayfFcD4yt0TtdocPx0xVUUa62KwwBCAvkIoXjAJcn1OCMqozdPyiwijTgpNy"
        headers = {"Content-Type": "application/json",
                   "Authorization": "key=" + fcm_key}

        notify_data = {
            "to": mobile_token,
            "priority":10,
            "notification": {
                 "body": message,
                 "title": title,
                 "content_available": True,
                 "priority": "high",
                 "color":"#36A4AA"
             },
            "data": {"notification_id": 5, "message": message,"title":title,"priority": "high","body":message}
        }

        resp = requests.post('https://fcm.googleapis.com/fcm/send', data=json.dumps(notify_data), headers=headers)
        return json.loads(resp.text)

    def fetch_upcoming_sessions(self):

        curtime = datetime.datetime.now()
        query = """select Mentor_id,mentee_id,Session_name,Start_datetime,id from mbox.mentee_mentor_schedule 
                    where Is_scheduled=1 and Status=1 and id not in (select schedule_id from mbox.mentee_session_notification) and
                    Start_datetime>'"""+str(curtime)+"""' and '"""+str(curtime)+"""'>=DATE_SUB(Start_datetime, INTERVAL 30 minute);"""

        cursor = self.conn.cursor()
        cursor.execute(query)
        all_sessions = cursor.fetchall()
        cursor.close()

        for sess in all_sessions:
            cursor = self.conn.cursor()
            mentor_query = """select mu.mobile_token,mp.name from mbox.mentee_user as mu join 
            mbox.mentee_mentor_profile as mp on mu.id=mp.id where mu.id="""+str(sess[0])+";"

            cursor.execute(mentor_query)
            mentor_details = cursor.fetchone()
            cursor.close()
            mentor_mtoken = mentor_details[0]
            mentor_name = mentor_details[1]
            session_name= sess[2]
            session_time = sess[3].strftime("%R")+" "+sess[3].strftime("%p")

            cursor = self.conn.cursor()
            mentee_query = """select mu.name,mu.mobile_token from mbox.mentee_user as mu where mu.id="""+str(sess[1])+";"

            cursor.execute(mentee_query)
            mentee_details = cursor.fetchone()

            cursor.close()
            mentee_name = mentee_details[0]
            mentee_mtoken = mentee_details[1]

            # send notification to mentee

            title = "You have an upcoming session with "+mentor_name.title()
            message = "Topic: "+session_name+"\nTime: "+session_time

            mentee_status = SendPushNotification.send_push_notification(mentee_mtoken, message,title)

            title = "You have an upcoming session with "+mentee_name.title()

            mentor_status = SendPushNotification.send_push_notification(mentor_mtoken, message,title)

            if mentee_status:
                schedule_id= sess[4]
                formatted_date = curtime.strftime('%Y-%m-%d %H:%M:%S')
                insert_query = "insert into mbox.mentee_session_notification (schedule_id,created_at) values ("+str(schedule_id)+",'"+str(formatted_date)+"');"
                print(insert_query)
                cursor = self.conn.cursor()
                cursor.execute(insert_query)
                cursor.close()
                self.conn.commit()


if __name__ == "__main__":

    push_noti_ob = SendPushNotification()

    while True:
        try:
            push_noti_ob.fetch_upcoming_sessions()
        except Exception as e:
            push_noti_ob = SendPushNotification()
            push_noti_ob.fetch_upcoming_sessions()

        time.sleep(600)

