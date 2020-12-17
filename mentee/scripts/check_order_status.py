import pandas as pd
import schedule
import time
import datetime
import sqlalchemy
from sqlalchemy import create_engine
import requests
import razorpay

from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

def check_sales_order():


    start=time.time()
    print(start)
    print(datetime.datetime.now())

    db_username = "root"
    db_password = "Santosh@2k"
    db_ip = "localhost"
    db_name = "mbox"
    # db_port = 3306

    conn = sqlalchemy.create_engine('mysql+mysqlconnector://{0}:{1}@{2}/{3}'.
                                format(db_username, db_password,
                                        db_ip, db_name),echo=True

                                    )

    
    Base = declarative_base()
    class mentee_sales_order(Base):
        __tablename__ = 'mentee_sales_order'
        id = Column(Integer, primary_key =  True)
        Mentor_id = Column(Integer)
        Mentee_id = Column(Integer)
        Created_at=Column(DateTime)
        Payment_id=Column(String)
        Is_active = Column(Integer)
        Session_name= Column(String)
        Status=Column(String)
        mentee_feedback_id=Column(Integer)
        Mentor_feedback_id=Column(Integer)
        Video_link=Column(Integer)
        Parent_id=Column(Integer)
        User_order_id=Column(String)
        Mentee_name=Column(String)
        Mentee_phonenumber=Column(String)
        Mentee_email=Column(String)
        session_charge=Column(Integer)
        coupon_amount=Column(Integer)
        coupon_id=Column(String)
        final_price=Column(Integer)
        Schedule_id=Column(Integer)
        Status_updated_at=Column(DateTime)
        wallet_used=Column(Integer)
        wallet_amount=Column(Integer)

    class mentee_payment_details(Base):
        __tablename__ = 'mentee_payment_details'
        id = Column(Integer, primary_key =  True)
        razorpay_order_id=Column(String)
        razorpay_payment_id=Column(String)
        razorpay_signature=Column(String)


    class mentee_mentor_schedule(Base):
        __tablename__ = 'mentee_mentor_schedule'
        id = Column(Integer, primary_key =  True)
        Mentor_id=Column(Integer)
        Start_datetime=Column(DateTime)
        End_datetime=Column(DateTime)
        Status=Column(Integer)
        Is_scheduled=Column(Integer)
        Created_at=Column(DateTime)
        Updated_at=Column(DateTime)
        Session_name=Column(String)
        mentor_charge=Column(Integer)
        order_id=Column(Integer)
        session_charge=Column(Integer)



    


    Session = sessionmaker()
    Session.configure(bind=conn)
    session = Session()
    
    check=0
    t10=datetime.timedelta(minutes=10)
    print("ten minutes:",t10)

    row=session.query(mentee_sales_order).filter_by(Is_active=1, Status=0).all()
    print(len(row))
    for i in row:
        print("******************************************************************************************")        
        current_time=datetime.datetime.now()
        
        print(i.Status_updated_at)
        if current_time-i.Status_updated_at>=t10:
            print("condition valid")
            print("row order_id",i.User_order_id)
            print("row id:",i.id)
            if i.User_order_id !=None:
                order_id=i.User_order_id
                print("order_id:",order_id)
                response = requests.get('https://api.razorpay.com/v1/orders/%s/payments'%order_id, auth=("rzp_test_A5QQVVWf0eMog1", "mwIcHdj1fIDGVi44N6BoUX0W"))
                print(response.text)
                d1=response.json()
                pay_id=""

                if d1['count']!=0:
                    for j in range(d1['count']):
                        if d1['items'][j]['status']=="captured":
                            if d1['items'][j]['order_id']==order_id:
                                pay_id=d1['items'][j]['id']

                            i.Payment_id=pay_id
                            i.Status=1
                            session.commit()

                            pay_det=mentee_payment_details(razorpay_order_id=order_id, razorpay_payment_id=pay_id)
                            session.add(pay_det)
                            session.commit()

                            sch_obj=session.query(mentee_mentor_schedule).get(i.Schedule_id)
                            objs=session.query(mentee_mentor_schedule).filter_by(Mentor_id=sch_obj.Mentor_id,Start_datetime=sch_obj.Start_datetime).all()
                            #print(len(objs))
                            for k in objs:
                                k.order_id=None
                                k.Is_scheduled=1
                                k.Status=0
                                
                                session.commit()
                            sch_obj.order_id=i.id
                            sch_obj.Status=1
                            session.commit()

                        else:
                           check=1 
                else:
                    check=1
            else:
                check=1


        if check==1:
            i.Is_active=0
            session.commit()
            
            sch_obj=session.query(mentee_mentor_schedule).get(i.Schedule_id)
            #print("sch_obj",len(sch_obj))
            objs=session.query(mentee_mentor_schedule).filter_by(Mentor_id=sch_obj.Mentor_id,Start_datetime=sch_obj.Start_datetime).all()
            #print("obj",len(objs))
            #print(len(objs))
            for k in objs:
                k.order_id=None
                k.Is_scheduled=0
                
                session.commit()
                    
    print("Execution time",time.time()-start)
    

schedule.every(1).seconds.do(check_sales_order)

while 1:
    schedule.run_pending()