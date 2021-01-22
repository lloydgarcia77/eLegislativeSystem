  
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.exceptions import ValidationError

# for encryption
from django.conf import settings
from cryptography.fernet import Fernet
import base64
import logging
import traceback 

import os

from django.conf import settings

def encrypt_key(txt):

    """Encrypt objects"""
    try:
        # convert integer etc to string first
        txt = str(txt)
        # get key from settings
        cipher_suite = Fernet(settings.ENCRYPT_KEY)  # key should be byte
        # #input should be byte, so convert the text to byte
        encrypted_text = cipher_suite.encrypt(txt.encode('ascii'))
        # encode to urlsafe base64 format
        encrypted_text = base64.urlsafe_b64encode(
            encrypted_text).decode("ascii")

        return encrypted_text

    except Exception as e:
        # log if an error
        logging.getLogger("error_logger").error(traceback.format_exc())
        return None

def file_validator_image(value):
    """To validate uploading of image"""
    file_size = value.size
    valid_file_extension = ['.jpg', '.png', '.jpeg','.JPG','.PNG','.JPEG',]

    file_extension = os.path.splitext(value.name)[1] 

    file_size_kb = file_size * 0.001
    file_size_mb = file_size_kb * 0.0001 

    if not file_extension in valid_file_extension: 
        raise ValidationError("Invalid file! Valid files only: ('.jpg', '.png', '.jpeg', 'pdf', 'doc', 'docx')")

    else:
        if file_size_mb > 5: # 5MB 
            raise ValidationError("The maximum file size can be upload is 5 MB")
        else: 
            return value

def file_validator_pdf(value):
    """To validate uploading of image"""
    file_size = value.size
    valid_file_extension = ['.pdf',]

    file_extension = os.path.splitext(value.name)[1] 

    file_size_kb = file_size * 0.001
    file_size_mb = file_size_kb * 0.0001 

    if not file_extension in valid_file_extension: 
        raise ValidationError("Invalid file! Valid files only: ('.pdf')")

    else:
        if file_size_mb > 5: # 5MB 
            raise ValidationError("The maximum file size can be upload is 5 MB")
        else: 
            return value

# https://www.codingforentrepreneurs.com/blog/how-to-create-a-custom-django-user-model?fbclid=IwAR3uqTca3xfqHKhSEez8KRIFgbt3s0odNHiM-gRMfK_HYxBjvPyEbZJ9DUM
class UserManager(BaseUserManager):
    """Maanger for user profiles"""

    def create_user(self, email, f_name, m_name, l_name, gender, dob, age, address, password=None):
        """Create a new user profile"""

        if not email:
            raise ValueError('User must have email address')

        email = self.normalize_email(email)
        user = self.model(email=email, f_name=f_name, m_name=m_name, l_name=l_name, gender=gender, dob=dob, age=age, address=address, password=password)
        user.key_id =  encrypt_key(user.id)
        user.set_password(password)
        user.save(using=self._db)

        return user
    def create_staffuser(self, email, f_name, m_name, l_name, gender, dob, age, address, password):
        """
        Creates and saves a staff user with the given email and password.
        """
        user = self.create_user(email, f_name, m_name, l_name, gender, dob, age, address, password)
        user.key_id =  encrypt_key(user.id)
        user.staff = True
        user.save(using=self._db)

        return user
    def create_superuser(self, email, f_name, m_name, l_name, gender, dob, age, address, password):
        """Create and save a new superuser with the given details"""
        user = self.create_user(email, f_name, m_name, l_name, gender, dob, age, address, password)
        user.key_id =  encrypt_key(user.id)
        user.is_superuser = True
        user.is_staff = True 
        user.save(using=self._db)

        return user

class User(AbstractBaseUser, PermissionsMixin):
    """Customized model for user in django"""
    GENDER_LIST = (
        ('Male', 'Male'),
        ('Female', 'Female')
    )
    TITLE = (
        ('None','None'),
        ('Secretary to the city council','Secretary to the city council'),
        ('Asst. Secretary to the city council','Asst. Secretary to the city council'),
        ('Administrative Division','Administrative Division'),
        ('Agenda & Briefinf Division','Agenda & Briefinf Division'),
        ('Journal & Briefing Division','Journal & Briefing Division'),
        ('Legal Division','Legal Division'),
        ('Majority Floor Leader','Majority Floor Leader'),
        ('Asst. Majority Floor Leader','Asst. Majority Floor Leader'),
        ('Standing Committees','Standing Committees'),
        ('City Councilors','City Councilors'),
        ('Office of the city council of manila','Office of the city council of manila'),
        ('Vice-Mayor & Presiding Officer','Vice-Mayor & Presiding Officer'),
        ('City Mayor','City Mayor'),
        ('Adminisrator','Adminisrator'),
    ) 
    key_id =  models.CharField(max_length=255,unique=True)
    email = models.EmailField(max_length=255, unique=True)
    image = models.ImageField(upload_to='images/', blank=True, validators=[file_validator_image])
    f_name = models.CharField(max_length=50, verbose_name="First Name")
    m_name = models.CharField(max_length=50, verbose_name="Middle Name")
    l_name = models.CharField(max_length=50, verbose_name="Last Name")
    gender = models.CharField(max_length=50, choices=GENDER_LIST, default='Male')
    dob = models.DateField(null=True, blank=True)
    age = models.IntegerField()
    address = models.CharField(max_length=255)
    title = models.CharField(max_length=100, choices=TITLE, default=TITLE[0][0])
    date_added = models.DateTimeField(auto_now=True)    

    # active = models.BooleanField(default=True)
    # staff = models.BooleanField(default=False) # a admin user; non super-user
    # admin = models.BooleanField(default=False) # a superuser
    # notice the absence of a "Password field", that is built in.
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['f_name','m_name','l_name','age','gender', 'dob', 'address',] # Email & Password are required by default.

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):              # __unicode__ on Python 2
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True
 
STATUS_LIST = (
    ('None','None'),
    ('Pending','Pending'),
    ('Approved','Approved'),
    ('Denied','Denied'),
)
class AgendaModel(models.Model):
    no = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=255)
    version = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    status = models.CharField(max_length=100, choices=STATUS_LIST, default=STATUS_LIST[0][0])
    is_signed = models.BooleanField(default=False)
    hard_copy = models.FileField(upload_to='documents/%Y/%m/%d', verbose_name="hard copy", blank=True, null=True, validators=[file_validator_pdf])
    content = models.TextField()
    date_filed = models.DateTimeField(auto_now=True)

    # https://stackoverflow.com/questions/16041232/django-delete-filefield#:~:text=Try%20django%2Dcleanup%2C%20it%20automatically,FileField%20when%20you%20remove%20model.&text=You%20can%20also%20simply%20overwrite,before%20calling%20the%20super%20function.
    # pip install django-cleanup
    # Delete file when clear
    """
    INSTALLED_APPS = (
     ...
    'django_cleanup', # should go after your apps
    )   
    """
    # def delete(self,*args,**kwargs):
    #     if os.path.isfile(self.hard_copy.path):
    #         os.remove(self.hard_copy.path) 
    #     super(AgendaModel, self).delete(*args,**kwargs)

    def __str__(self):
        return str(self.title)

class ResolutionModel(models.Model):
    agenda_fk = models.ForeignKey(AgendaModel, on_delete=models.CASCADE, related_name="resolution_fk")
    no = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=255)
    version = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    status = models.CharField(max_length=100, choices=STATUS_LIST, default=STATUS_LIST[0][0])
    is_signed = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)
    hard_copy = models.FileField(upload_to='documents/%Y/%m/%d', verbose_name="hard copy", blank=True, null=True, validators=[file_validator_pdf])
    content = models.TextField()
    date_filed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.title)

class CommitteeReportResolutionModel(models.Model):
    resolution_committee_report_fk = models.ForeignKey(ResolutionModel, on_delete=models.CASCADE, related_name="resolution_committee_report_fk")
    no = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=255)
    version = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    status = models.CharField(max_length=100, choices=STATUS_LIST, default=STATUS_LIST[0][0])
    is_signed = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)
    hard_copy = models.FileField(upload_to='documents/%Y/%m/%d', verbose_name="hard copy", blank=True, null=True, validators=[file_validator_pdf])
    content = models.TextField()
    date_filed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.title)

class CommentsRecomendationResolutionModel(models.Model):
    resolution_comments_recommendation_fk = models.ForeignKey(ResolutionModel, on_delete=models.CASCADE, related_name="resolution_comments_recommendation_fk")
    commentor_resolution = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="commentor_resolution_fk")
    message = models.CharField(max_length=255)
    date_filed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.message
     
class OrdinanceModel(models.Model):
    agenda_fk = models.ForeignKey(AgendaModel, on_delete=models.CASCADE, related_name="ordinance_fk")
    no = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=255)
    version = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    status = models.CharField(max_length=100, choices=STATUS_LIST, default=STATUS_LIST[0][0])
    is_signed = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)
    hard_copy = models.FileField(upload_to='documents/%Y/%m/%d', verbose_name="hard copy", blank=True, null=True, validators=[file_validator_pdf])
    content = models.TextField()
    veto_message = models.CharField(max_length=255, blank=True, null=True, default="None")
    date_filed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.title)

class CommitteeReportOrdinanceModel(models.Model):
    ordinance_committee_report_fk = models.ForeignKey(OrdinanceModel, on_delete=models.CASCADE, related_name="ordinance_committee_report_fk")
    no = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=255)
    version = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    status = models.CharField(max_length=100, choices=STATUS_LIST, default=STATUS_LIST[0][0])
    is_signed = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)
    hard_copy = models.FileField(upload_to='documents/%Y/%m/%d', verbose_name="hard copy", blank=True, null=True, validators=[file_validator_pdf])
    content = models.TextField()
    date_filed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.title)

class CommentsRecomendationOrdinanceModel(models.Model):
    ordinance_comments_recomendation_fk = models.ForeignKey(OrdinanceModel, on_delete=models.CASCADE, related_name="ordinance_comments_recomendation_fk")
    commentor_ordiance = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="commentor_ordiance_fk")
    message = models.CharField(max_length=255)
    date_filed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.message

class MOMModel(models.Model):
    no = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=255)
    version = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    status = models.CharField(max_length=100, choices=STATUS_LIST, default=STATUS_LIST[0][0])
    is_signed = models.BooleanField(default=False) 
    hard_copy = models.FileField(upload_to='documents/%Y/%m/%d', verbose_name="hard copy", blank=True, null=True, validators=[file_validator_pdf])
    content = models.TextField()
    date_filed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.title)
 
class AnnouncementModel(models.Model):
    title = models.CharField(max_length=250)
    subject = models.CharField(max_length=250)
    content = models.CharField(max_length=250)
    visible = models.BooleanField(default=False)
    date_filed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.title)

class NotificationsModel(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sender_fk")
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="receiver_fk")
    message = models.CharField(max_length=200)
    tags = models.CharField(max_length=250, choices=settings.NOTIFICATION_TAGS, default=settings.NOTIFICATION_TAGS[0][0])
    url = models.URLField(max_length=250, default="")
    is_read = models.BooleanField(default=False)
    date_filed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.message)
