from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):

    def _create_user(self, email, name, picture, is_staff, is_superuser, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        now = timezone.now()
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            name=name,
            picture=picture,
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            last_login=now,
            date_joined=now,
            **extra_fields
        )
        if is_superuser:
            user.set_password(name)
        user.save(using=self._db)
        return user

    def create_user(self, email, name, picture, **extra_fields):
        return self._create_user(email, name, picture, False, False, **extra_fields)

    def create_superuser(self, email, password, picture, **extra_fields):
        user = self._create_user(email, password, picture, True, True, **extra_fields)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=254, unique=True)
    name = models.CharField(max_length=500, blank=True)
    contact_no = models.CharField(max_length=20,blank=True,default=False)
    picture = models.CharField(max_length=200, blank=True)
    is_staff = models.BooleanField(default=False)
    is_mentee = models.BooleanField(default=False, blank=True)
    is_mentor = models.BooleanField(default=False, blank=True)
    is_client = models.BooleanField(default=False, blank=True)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    mobile_token = models.CharField(max_length=500, null=True)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __int__(self):
        return self.id

    def get_absolute_url(self):
        return "/users/%i/" % (self.pk)


class MenteeDetails(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile = models.CharField(max_length=15, blank=True)
    education_level = models.CharField(max_length=45, blank=True)
    college = models.CharField(null=True, max_length=300, blank=True)
    degree = models.CharField(null=True, max_length=300, blank=True)
    school_name=models.CharField(null=True, max_length=300, blank=True)
    course = models.CharField(null=True, max_length=300, blank=True)
    designation = models.CharField(null=True, max_length=300, blank=True)
    company = models.CharField(null=True, max_length=300, blank=True)
    industry_exp = models.SmallIntegerField(blank=True, null=True)
    skills = models.TextField(default='[]', blank=True)
    goal_defined = models.BooleanField(null=True, blank=True)
    same_profession = models.BooleanField(null=True, blank=True)
    career1 = models.CharField(null=True, max_length=300, blank=True)
    career2 = models.CharField(null=True, max_length=300, blank=True)
    career_list = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __int__(self):
        return self.user_id

    def get_user_detail_id(self):
        return self.id


class MentorFlow(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    linkedin_url = models.TextField(null=True, max_length=400)
    skills = models.TextField(default='[]', null=True)
    session_121 = models.BooleanField(null=True, default=0)
    webinar = models.BooleanField(null=True, default=0)
    webinar_topics = models.TextField(default='[]', null=True)
    # webinar_min = models.SmallIntegerField(null=True)
    webinar_charge = models.SmallIntegerField(null=True)
    contact_no = models.CharField(max_length=20,null=True)
    details_filled = models.BooleanField(null=True, default=0)
    invalid_url = models.BooleanField(null=True, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __int__(self):
        return self.user_id


class mentor_profile(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    avatar = models.URLField(null=True)
    languages = models.TextField(null=True)
    about = models.TextField(null=True)
    email = models.EmailField(null=True)
    location = models.TextField(null=True)
    professional_details = models.TextField(null=True, max_length=15)
    educational_details = models.TextField(null=True, max_length=15)
    industry_exp = models.FloatField(null=True)
    skills = models.TextField(default='[]')
    contact_no = models.BigIntegerField(null=True)
    country_code = models.CharField(null=True, max_length=7)
    rating = models.FloatField(null=True)
    status = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __int__(self):
        return self.user_id


def img_url(path):
    host="http://ec2-65-0-73-184.ap-south-1.compute.amazonaws.com:8000/"
    return host+str(path)


class MentorImage(models.Model):
    mentor_id = models.IntegerField(null=True)
    mentor_name = models.CharField(max_length=50, null=True)
    image = models.ImageField(upload_to='media/', max_length=2000)
    image_link = models.URLField(null=True)

    def __str__(self):
        return self.mentor_name

    def save(self):
        # if not self.pk:
        self.image_link = img_url(self.image)
        super(MentorImage, self).save()

# def return_datetime():
#    now = timezone.now()
#    return now + timedelta(days=14)


class mentor_schedule(models.Model):
    id = models.AutoField(primary_key=True)
    Mentor_id = models.IntegerField()
    Start_datetime = models.DateTimeField()
    End_datetime = models.DateTimeField()
    Status = models.SmallIntegerField(default=1)  
    Is_scheduled = models.SmallIntegerField(default=0)  
    Created_at = models.DateTimeField(auto_now_add=True)
    Updated_at = models.DateTimeField(auto_now=True)
    Session_name = models.CharField(max_length=100, null=False)
    mentor_charge = models.IntegerField(default=0)
    session_charge = models.IntegerField()
    order_id = models.IntegerField(default=None, null=True)
    mentee_id = models.IntegerField(default=None, null=True)

    def __str__(self):
        a = str(self.Mentor_id)
        return a

    # **** status field info ****
    #  1 = active
    #  0 = deactivate(delete) - if mentor clicks on remove on slot then it will be deleted 



    # **** is_scheduled field info ****

    # 0 = available for booking(free slot, mentee can book this) 
    # 1 = booked slot(mentee done payment and payment is successful) 
    # 2 = under booking slot(
    #     - if mentee stop payment process in middle, then this value will be
    #       there upto 10 mins until script detects this. 
    #     - if payment status is other than "captured"(like authorized, created),
    #       this value will be there.


class mentor_topics(models.Model):
    id = models.AutoField(primary_key=True)
    Mentor_id = models.IntegerField()
    Linked_url = models.URLField()
    Skills = models.TextField()
    Session_121 = models.IntegerField(default=1)
    Webinar = models.IntegerField(default=1)
    Webinar_topics = models.CharField(max_length=1000)
    Webinar_charge = models.CharField(max_length=1000)
    Status = models.IntegerField(default=1, blank=False)
    Created_at = models.DateTimeField(auto_now_add=True)
    Updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.Mentor_id)


class sales_order(models.Model):
    id = models.AutoField(primary_key=True)

    Schedule_id=models.IntegerField()
    Mentor_id = models.IntegerField()
    Mentee_id = models.IntegerField()
    Created_at = models.DateTimeField(auto_now_add=True)
    Payment_id = models.CharField(max_length=100,null=True)
    Is_active = models.SmallIntegerField(default=1)
    Session_name = models.CharField(max_length=30)
    Status = models.SmallIntegerField(default=0)   #
    Status_updated_at=models.DateTimeField(auto_now=True)
    mentee_feedback_id = models.IntegerField(null=True)

    Mentor_feedback_id = models.IntegerField(null=True)
    Video_link = models.URLField(default="https://meet.google.com")
    Parent_id = models.IntegerField(null=True)
    User_order_id = models.CharField(max_length=100,null=True)
    Mentee_name = models.CharField(max_length=100, null=True, blank=True)
    Mentee_phonenumber = models.CharField(max_length=15)
    Mentee_email = models.EmailField(null=True, blank=True)

    session_charge = models.PositiveIntegerField(null=True)
    coupon_amount = models.PositiveIntegerField(null=True)
    coupon_id = models.CharField(max_length=30, null=True)
    final_price = models.PositiveIntegerField(null=True)
    wallet_used = models.BooleanField(default=False)
    wallet_amount = models.IntegerField(null=True)


    def __str__(self):
        return self.User_order_id


    # **** status field info ****

    # 0 = payment process not started (this value will be there by default when mentee fills
    #     name, phone_number, email details in order summary page. But payment process is not initiated.
    #     Here only to whom this session wants to book is submiitted.)
    # 1 = slot booked successfully (when mentee successfully paid amount to this session
    #      then this value will be there)
    # 2=  in the middle of payment process (when only order_id is generated succesfully from razorpay
    #     then this value will be there. if mentee continue the process then it will change to 1, else
    #     if mentee stops the process then it will make is_active field to 0 after a script run on this but status remains unchanged(2))


    # **** is_active field info ****

    # 0 = not active (value will be zero for two scenario
    #     - when to razorpay signature verification fails, making is_active to 0
    #     - if status_updated_at is passed 10 mins, then a running script will change it to zero

    # 1 = active (if mentee successfully paid amount to this slot)


class course_list(models.Model):
    id = models.AutoField(primary_key=True)
    College_Name = models.CharField(max_length=200)
    Level_of_Course = models.CharField(max_length=200)
    Degree = models.CharField(max_length=100)

    def __str__(self):
        return self.College_Name + self.Level_of_Course


class payment_details(models.Model):
    id = models.AutoField(primary_key=True)
    #Sales_Order = models.OneToOneField(sales_order, on_delete=models.CASCADE, null=True)
    razorpay_order_id = models.CharField(max_length=100)
    razorpay_payment_id = models.CharField(max_length=100)
    razorpay_signature = models.CharField(max_length=100,null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.razorpay_payment_id


class skills_list(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class companies_list(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return self.name


class degree_list(models.Model):
    id = models.AutoField(primary_key=True)
    degree_name = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return self.degree_name


class coupon(models.Model):
    coupon_name = models.CharField(max_length=20)
    coupon_code = models.CharField(max_length=30)
    coupon_amount = models.PositiveIntegerField(null=True)
    coupon_percentage = models.SmallIntegerField(null=True)
    active_status = models.SmallIntegerField()
    coupon_minimum_cart_price = models.PositiveIntegerField(null=True)
    coupon_type = models.CharField(max_length=20)
    new_user_coupon = models.SmallIntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.coupon_name


class mentee_feedback(models.Model):
    Sales_Order=models.OneToOneField(sales_order, on_delete=models.CASCADE, null=True)
    mentor_id=models.IntegerField()
    star_rating=models.SmallIntegerField(null=True)
    comments=models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.mentor_id


class voice_call(models.Model):
    id = models.AutoField(primary_key=True)
    sales_order_id = models.PositiveIntegerField()
    user_id = models.PositiveIntegerField(null=True)
    token_id  = models.TextField()
    channel_name = models.CharField(max_length=20)
    expiration_time= models.IntegerField(null=True)
    request_type = models.CharField(max_length=15,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return self.sales_order_id


class wallet(models.Model):
    mentee_id=models.IntegerField()
    current_balance=models.FloatField(default=0)
    previous_balance=models.FloatField(default=0)
    amount_changed=models.FloatField(default=0)
    txn_order_id=models.CharField(max_length=100)
    status=models.SmallIntegerField()  # 1 - created, 2 - money added and active row
    voice_id=models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    remarks = models.CharField(max_length=100,null=True)


class favourite_mentors(models.Model):
    mentee_id=models.IntegerField()
    mentor_id=models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)

class request_sessions(models.Model):
    mentee_id=models.IntegerField()
    mentor_id=models.IntegerField()
    session_name=models.CharField(max_length=50)
    mentor_notify=models.BooleanField(default=True)
    mentee_notify=models.BooleanField(default=False,null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)


class CallHistory(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.PositiveIntegerField()
    channel_name = models.CharField(max_length=100)
    status = models.IntegerField()
    is_mentee = models.BooleanField()
    schedule_id = models.IntegerField(null=True)
    reason = models.IntegerField(null=True)
    remarks = models.CharField(max_length=100,null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class mentor_profile_clicks(models.Model):
    mentee_id = models.IntegerField()
    mentor_id = models.IntegerField()
    session_name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)


class skills_career(models.Model):
    id = models.AutoField(primary_key=True)
    name=models.CharField(max_length=100)
    type=models.CharField(max_length=20)


class events(models.Model):
    title=models.CharField(max_length=300, null=False)
    image=models.ImageField(null=False)
    image_link=models.URLField(null=True)
    price=models.PositiveIntegerField(null=False)
    about_the_mentor=models.TextField(null=True, blank=True)
    about_the_event=models.TextField(null=True, blank=True)
    duration=models.CharField(max_length=50, null=True, blank=True)
    start_datetime=models.DateTimeField(null=True)
    key_takeaways=models.TextField(null=True, blank=True)
    status = models.BooleanField(null=True,blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)




class event_sales_order(models.Model):
    event_id=models.IntegerField()
    mentee_id=models.IntegerField()
    payment_id = models.CharField(max_length=100,null=True)
    status = models.SmallIntegerField(default=0)     #0=not booked, 1=booked, 2=under booking, 3=sign verification failed
    user_order_id = models.CharField(max_length=100,null=True)
    mentee_name = models.CharField(max_length=100, null=True, blank=True)
    mentee_phonenumber = models.CharField(max_length=15)
    mentee_email = models.EmailField(null=True, blank=True)
    event_price = models.PositiveIntegerField(null=True)
    coupon_used = models.BooleanField(default=False)
    coupon_amount = models.FloatField(null=True)
    coupon_code = models.CharField(max_length=30, null=True)
    wallet_used = models.BooleanField(default=False)
    wallet_amount = models.IntegerField(null=True)
    final_price = models.FloatField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status_updated_at=models.DateTimeField(auto_now=True)

    # **** status field info ****

    # 0 = payment process not started (this value will be there by default when mentee fills
    #     name, phone_number, email details in order summary page. But payment process is not initiated.
    #     Here only to whom this session wants to book is submiitted.)
    #
    # 1 = event booked successfully (when mentee successfully paid amount to this event
    #      then this value will be there)
    #
    # 2 =  in the middle of payment process (when only order_id is generated succesfully from razorpay
    #     then this value will be there. if mentee continue the process then it will change to 1, else
    #     if mentee stops the process then it will remain 2 only
    #
    # 3 = when signature verification fails this value will be there 

class mentor_bank_details(models.Model):
    mentor_id=models.IntegerField()
    account_name = models.CharField(max_length=100)
    ifsc_code = models.CharField(max_length=15)
    account_number = models.CharField(max_length=50)
    created_at = models.DateTimeField(null=True,auto_now_add=True)


class session_notification(models.Model):
     schedule_id = models.IntegerField()
     created_at = models.DateTimeField(auto_now_add=True)


class profile_picture(models.Model):
    user_id = models.IntegerField(null=True)
    image = models.ImageField(upload_to='profile_picture/', max_length=200)
    image_link = models.URLField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

class event_feedback(models.Model):
    event_order=models.OneToOneField(event_sales_order, on_delete=models.CASCADE, null=True)
    event_id=models.IntegerField()
    star_rating=models.SmallIntegerField(null=True)
    comments=models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
