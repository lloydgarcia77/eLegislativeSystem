from django.http import JsonResponse, Http404, HttpResponseRedirect, HttpResponse
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.conf import settings
from elegislative_app import forms

from django.contrib.auth.decorators import login_required

# Models
from elegislative_app import models

# for encrypting of primary keys
from cryptography.fernet import Fernet
import base64
import logging
import traceback  

import json
from functools import wraps
from itertools import chain
# Create your views here.

# key id encryption
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

def decrypt_key(txt):

    """Decrypt objects"""
    try:
        # base64 decode
        txt = base64.urlsafe_b64decode(txt)
        cipher_suite = Fernet(settings.ENCRYPT_KEY)
        decoded_text = cipher_suite.decrypt(txt).decode("ascii")
        return decoded_text
    except Exception as e:
        # log the error
        logging.getLogger("error_logger").error(traceback.format_exc())
        return None

# Handles the error pages

def error_404(request, exception):
    template_name = "error/error_404.html"
    context = {

    }
    return render(request, template_name, context)

def error_500(request):
    template_name = "error/error_500.html"
    context = {

    }
    return render(request, template_name, context)


def login_page(request):
    """Login Page"""
    template_name = "registration/login.html"
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        # if is active
        if user:
            if user.is_active and user.is_staff and user.is_superuser: 
                login(request, user)
                return HttpResponseRedirect(reverse("elegislative:dashboard_page"))
            else:
                messages.error(request, "Your account is INVALID! please try again.")
        else:
            print("Invalid Password")
 
    
    return render(request, template_name)
    
def register_page(request):
    """Registration Page"""
    template_name = "registration/register.html"
    if request.method == 'GET':
        form = forms.RegisterForm(request.GET or None)
    elif request.method == 'POST':
        form = forms.RegisterForm(request.POST or None, request.FILES)
        if form.is_valid():
            regForm = form.save(commit=False)
            regForm.key_id =  encrypt_key(regForm.id)
            regForm.is_active = False
            regForm.is_staff = False
            regForm.is_superuser = False
            regForm.save()
            messages.success(
                request, "You have successfully registered, please try to login.")
            return HttpResponseRedirect(reverse("login"))

        else:
            print("Form Error!")
    
    context = {
        'form': form,
    }
    return render(request, template_name, context)

def elegislative_index_page(request):
    template_name = "elegislative/elegislative_index_page.html"

    context = {
        'Hello': 'Hello',
    }
    return render(request, template_name, context)

"""
[--------------------MAIN FUNCTIONALITY--------------------]
"""
# https://stackoverflow.com/questions/5469159/how-to-write-a-custom-decorator-in-django
def authorize(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        user = get_object_or_404(models.User, email=request.user.email) 
        if  user.is_superuser:
            return function(request, *args, **kwargs)
        else:
            raise Http404
            # return HttpResponseRedirect('/')
    return wrap

@login_required
def dashboard_page(request):
    template_name = "elegislative/dashboard.html"
    user = get_object_or_404(models.User, email=request.user.email)
 
    context = {
        'user': user,
    }
    return render(request, template_name, context)


"""
[START] -> CRUD, Manage Agenda Features
"""

# Agenda Feature 
@authorize
@login_required
def agenda_page(request):
    template_name = "elegislative/agenda/agenda.html" 
    user = get_object_or_404(models.User, email=request.user.email) 
    agenda = models.AgendaModel.objects.all()
    context = {
        'user': user,
        'agenda': agenda,
    }
    return render(request, template_name, context)

@authorize
@login_required
def create_agenda_page(request):
    template_name = "elegislative/agenda/create_new_agenda.html"
    user = get_object_or_404(models.User, email=request.user.email)  

    if request.method == 'GET':
        form = forms.AgendaForm(request.GET or None)
    elif request.method == 'POST':
        form = forms.AgendaForm(request.POST or None) 
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse_lazy("elegislative:agenda_page"))
        else:
            print("Agenda page error")
    context = {
        'user': user,
        'form':form,
    }
    return render(request, template_name, context)

@authorize
@login_required
def edit_agenda_page(request, id): 
    template_name = "elegislative/agenda/edit_agenda.html"    
    user = get_object_or_404(models.User, email=request.user.email)
    agenda = get_object_or_404(models.AgendaModel, id=id)

    if request.method == 'GET':
        form = forms.EditAgendaForm(request.GET or None, instance=agenda)
    elif request.method == 'POST':
        form = forms.EditAgendaForm(request.POST or None, request.FILES, instance=agenda)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse_lazy("elegislative:agenda_page"))
    context = {
        'user': user,
        'form':form,
    }
    return render(request, template_name, context)

@authorize
@login_required
def delete_agenda_page(request, id):
    data = dict()
    template_name = "elegislative/agenda/delete_agenda.html"    
    user = get_object_or_404(models.User, email=request.user.email)
    agenda = get_object_or_404(models.AgendaModel, id=id)

    if request.is_ajax():
        if request.method == 'GET':
            context = {
                'agenda': agenda,
            }
            data['html_form'] = render_to_string(template_name, context, request)
        elif request.method == 'POST':            
            data['form_is_valid'] = True
            agenda.delete() 
        return JsonResponse(data)
    else:
        raise Http404()

@authorize
@login_required
def print_agenda_page(request, id):
    template_name = "elegislative/agenda/print_agenda.html"  
    user = get_object_or_404(models.User, email=request.user.email)
    agenda = get_object_or_404(models.AgendaModel, id=id)
    context = {
        'user': user,
        'agenda':agenda,
    }
    return render(request, template_name, context)



"""
[END] -> CRUD, Manage Agenda Features
"""

"""
[START] -> CRUD, Manage Comments & Recommendation Features
"""
# Proposed Ordinance & Resolution Feature

# For Resolution
@authorize
@login_required
def comments_and_recommendation(request): 
    template_name = "elegislative/comments_recommendation/comments_recommendation.html"
    user = get_object_or_404(models.User, email=request.user.email) 
    resolutions = models.ResolutionModel.objects.all().filter(Q(is_public=True)) 
    ordinances = models.OrdinanceModel.objects.all().filter(Q(is_public=True)) 

    # combine = list(resolutions) + list(ordinances)

    # # get modelname based on query
    # # for c in combine:
    # #     print(combine.model.__name__)

    context = {
        'user': user,
        'resolutions': resolutions,
        'ordinances': ordinances, 
    }    
    return render(request, template_name, context)

@authorize
@login_required
def posting_resolution(request, id):
    template_name = "elegislative/comments_recommendation/posting_resolution.html"
    user = get_object_or_404(models.User, email=request.user.email) 
    resolution = get_object_or_404(models.ResolutionModel, id=id)
    com_rec = models.CommentsRecomendationResolutionModel.objects.all().filter(resolution_comments_recommendation_fk=resolution)
    context = {
        'user': user, 
        'resolution': resolution,
        'com_rec': com_rec,
    }   
    return render(request, template_name, context)

@authorize
@login_required
def posting_resolution_post_comment(request, id):
    data = dict() 
    if request.is_ajax():
        user = get_object_or_404(models.User, email=request.user.email) 
        resolution = get_object_or_404(models.ResolutionModel, id=id)
        com_rec = models.CommentsRecomendationResolutionModel.objects.all().filter(resolution_comments_recommendation_fk=resolution)
        if resolution.is_public: 
            if request.method == 'POST': 
                json_obj = json.loads(request.body)
                comment = json_obj['data'] 
                create = models.CommentsRecomendationResolutionModel(resolution_comments_recommendation_fk=resolution, commentor_resolution=user, message=comment)
                create.save()  

                url = reverse_lazy('elegislative:posting_resolution_delete_comment', kwargs={'id':create.id, 'rid':resolution.id}) 
                data = {
                    'image': create.commentor_resolution.image.url,
                    'name': f"{create.commentor_resolution.f_name} {create.commentor_resolution.l_name}",
                    'date_filed': create.date_filed.strftime("%b. %d, %Y, %I:%M %p"),
                    'message': create.message,
                    'url': url,
                    'total': com_rec.count(),
                } 

            context = {
                'user': user, 
                'resolution': resolution,
            }    
            return JsonResponse(data)
        else:

            raise Http404()
    else:
        raise Http404()
 
@authorize
@login_required
def posting_resolution_delete_comment(request, id, rid):
    data = dict() 
    if request.is_ajax():
        user = get_object_or_404(models.User, email=request.user.email) 
        comment = get_object_or_404(models.CommentsRecomendationResolutionModel, id=id)
        resolution = get_object_or_404(models.ResolutionModel, id=rid)
        com_rec = models.CommentsRecomendationResolutionModel.objects.all().filter(resolution_comments_recommendation_fk=resolution)
        if request.method == 'POST':
            comment.delete()
            data ={
                'form_is_valid': True,
                'total': com_rec.count(),
            } 
            return JsonResponse(data) 
    else:
        raise Http404()

# For Ordinance
@authorize
@login_required
def posting_ordinance(request, id):
    template_name = "elegislative/comments_recommendation/posting_ordinance.html"
    user = get_object_or_404(models.User, email=request.user.email) 
    ordinance = get_object_or_404(models.OrdinanceModel, id=id)
    com_rec = models.CommentsRecomendationOrdinanceModel.objects.all().filter(ordinance_comments_recomendation_fk=ordinance)
    context = {
        'user': user, 
        'ordinance': ordinance,
        'com_rec': com_rec,
    }   
    return render(request, template_name, context)


@authorize
@login_required
def posting_ordinance_post_comment(request, id):
    data = dict() 
    if request.is_ajax():
        user = get_object_or_404(models.User, email=request.user.email) 
        ordinance = get_object_or_404(models.OrdinanceModel, id=id)
        com_rec = models.CommentsRecomendationOrdinanceModel.objects.all().filter(ordinance_comments_recomendation_fk=ordinance)
        if ordinance.is_public: 
            if request.method == 'POST': 
                json_obj = json.loads(request.body)
                comment = json_obj['data'] 
                create = models.CommentsRecomendationOrdinanceModel(ordinance_comments_recomendation_fk=ordinance, commentor_ordiance=user, message=comment)
                create.save()  

                url = reverse_lazy('elegislative:posting_ordinance_delete_comment', kwargs={'id':create.id, 'oid':ordinance.id}) 
                data = {
                    'image': create.commentor_ordiance.image.url,
                    'name': f"{create.commentor_ordiance.f_name} {create.commentor_ordiance.l_name}",
                    'date_filed': create.date_filed.strftime("%b. %d, %Y, %I:%M %p"),
                    'message': create.message,
                    'url': url,
                    'total': com_rec.count(),
                } 

            context = {
                'user': user, 
                'ordinance': ordinance,
            }    
            return JsonResponse(data)
        else:

            raise Http404()
    else:
        raise Http404()
 
@authorize
@login_required
def posting_ordinance_delete_comment(request, id, oid):
    data = dict() 
    if request.is_ajax():
        user = get_object_or_404(models.User, email=request.user.email) 
        comment = get_object_or_404(models.CommentsRecomendationOrdinanceModel, id=id)
        ordinance = get_object_or_404(models.OrdinanceModel, id=oid)
        com_rec = models.CommentsRecomendationOrdinanceModel.objects.all().filter(ordinance_comments_recomendation_fk=ordinance)
        if request.method == 'POST':
            comment.delete()
            data ={
                'form_is_valid': True,
                'total': com_rec.count(),
            } 
            return JsonResponse(data) 
    else:
        raise Http404()


"""
[END] -> CRUD, Manage Comments & Recommendation  Features
"""
 
"""
[START] -> Manage Committee Reports Features
"""
@authorize
@login_required
def committee_reports(request):
    template_name = "elegislative/committee_reports/committee_reports.html"
    user = get_object_or_404(models.User, email=request.user.email) 
    c_resolutions = models.CommitteeReportResolutionModel.objects.all()
    c_ordinances = models.CommitteeReportOrdinanceModel.objects.all()
    # result_list = list(chain(c_resolutions, c_ordinances)) 
    resolution = models.CommitteeReportResolutionModel.objects.all()
    ordinance = models.CommitteeReportOrdinanceModel.objects.all()

    context = {
        'user': user,
        'resolution': resolution,
        'ordinance': ordinance,
    }    
    return render(request, template_name, context)

# Create committee reports
@authorize
@login_required
def create_committee_resolution_reports(request, id):
    template_name = "elegislative/committee_reports/create_committee_resolution_reports.html"
    user = get_object_or_404(models.User, email=request.user.email) 
    resolution = get_object_or_404(models.ResolutionModel, id=id)

    if request.method == 'GET':
        form = forms.CommitteeReportResolutionForm(request.GET or None)
    elif request.method == 'POST':
        form = forms.CommitteeReportResolutionForm(request.POST or None) 
        if form.is_valid():
            instance = form.save(commit=False)
            instance.resolution_committee_report_fk = resolution
            instance.save()
            return HttpResponseRedirect(reverse_lazy("elegislative:committee_reports")) 

    context = {
        'user': user,
        'resolution': resolution,
        'form': form,
    }    
    return render(request, template_name, context)

@authorize
@login_required
def edit_committee_resolution_reports(request, id):
    template_name = "elegislative/committee_reports/edit_committee_resolution_reports.html"
    user = get_object_or_404(models.User, email=request.user.email) 
    committee_report = get_object_or_404(models.CommitteeReportResolutionModel, id=id)

    if request.method == 'GET':
        form = forms.EditCommitteeReportResolutionForm(request.GET or None, instance=committee_report)
    elif request.method == 'POST':
        form = forms.EditCommitteeReportResolutionForm(request.POST or None, request.FILES, instance=committee_report) 
        if form.is_valid(): 
            form.save()
            return HttpResponseRedirect(reverse_lazy("elegislative:committee_reports")) 
    context = {
        'user': user,
        'committee_report': committee_report,      
        'form'  : form,
    }

    return render(request, template_name, context)

@authorize
@login_required
def delete_committee_resolution_reports(request, id):
    data = dict()
    template_name = "elegislative/committee_reports/delete_committee_resolution_reports.html"
    user = get_object_or_404(models.User, email=request.user.email)
    committee_report = get_object_or_404(models.CommitteeReportResolutionModel, id=id)
    if request.is_ajax():
        if request.method == 'GET':
            context = {
                'committee_report': committee_report,
            }
            data['html_form'] = render_to_string(template_name, context, request)
        elif request.method == 'POST':
            data['form_is_valid'] = True
            committee_report.delete() 
        return JsonResponse(data)
    else:
        raise Http404

@authorize
@login_required
def print_committee_resolution_reports(request, id):
    template_name = "elegislative/committee_reports/print_committee_resolution_reports.html"
    user = get_object_or_404(models.User, email=request.user.email)
    committee_report = get_object_or_404(models.CommitteeReportResolutionModel, id=id)
    
    context = {
        'user': user,
        'committee_report':committee_report,
    }
    return render(request, template_name, context)

"""
[END] -> Manage Committee Reports Features
"""


"""
[START] -> Manage Resolution Features
""" 
@authorize
@login_required
def resolution(request):
    template_name = "elegislative/resolution/resolution.html"
    user = get_object_or_404(models.User, email=request.user.email) 
    resolutions = models.ResolutionModel.objects.all()
    context = {
        'user': user,
        'resolutions': resolutions,
    }    
    return render(request, template_name, context)


@authorize
@login_required
def create_resolutions(request, id):
    template_name = "elegislative/resolution/create_resolution.html"
    user = get_object_or_404(models.User, email=request.user.email) 
    agenda = get_object_or_404(models.AgendaModel, id=id)

    if request.method == 'GET':
        form = forms.ResolutionForm(request.GET or None)
    elif request.method == 'POST':
        form = forms.ResolutionForm(request.POST or None) 
        if form.is_valid():
            instance = form.save(commit=False)
            instance.agenda_fk = agenda
            instance.save()
            return HttpResponseRedirect(reverse_lazy("elegislative:resolution")) 

    context = {
        'user': user,
        'form': form,
        'agenda': agenda,
    }    
    return render(request, template_name, context)

@authorize
@login_required
def edit_resolution(request, id):
    template_name = "elegislative/resolution/edit_resolution.html"
    user = get_object_or_404(models.User, email=request.user.email) 
    resolution = get_object_or_404(models.ResolutionModel, id=id)

    if request.method == 'GET':
        form = forms.EditResolutionForm(request.GET or None, instance=resolution)
    elif request.method == 'POST':
        form = forms.EditResolutionForm(request.POST or None, request.FILES, instance=resolution) 
        if form.is_valid(): 
            form.save()
            return HttpResponseRedirect(reverse_lazy("elegislative:resolution")) 

    context = {
        'user': user,
        'form': form,
        'resolution': resolution,
    }    
    return render(request, template_name, context)


@authorize
@login_required
def delete_resolution(request, id):
    data = dict()
    template_name = "elegislative/resolution/delete_resolution.html"    
    user = get_object_or_404(models.User, email=request.user.email)
    resolution = get_object_or_404(models.ResolutionModel, id=id)

    if request.is_ajax():
        if request.method == 'GET': 
            context = {
                'resolution': resolution,
            }
            data['html_form'] = render_to_string(template_name, context, request)
        elif request.method == 'POST':            
            data['form_is_valid'] = True
            resolution.delete() 
        return JsonResponse(data)
    else: 
        raise Http404()


@authorize
@login_required
def print_resolution(request, id):
    template_name = "elegislative/resolution/print_resolution.html"  
    user = get_object_or_404(models.User, email=request.user.email)
    resolution = get_object_or_404(models.ResolutionModel, id=id)
    context = {
        'user': user,
        'resolution':resolution,
    }
    return render(request, template_name, context)


"""
[END] -> Manage Resolution Features
"""

"""
[START] -> Manage Ordinance features
"""
@login_required
def ordinance(request):
    template_name = "elegislative/ordinance/ordinance.html"
    user = get_object_or_404(models.User, email=request.user.email) 
    ordinance = models.OrdinanceModel.objects.all()
    context = {
        'user': user,
        'ordinance': ordinance,
    }    
    return render(request, template_name, context)

@login_required
def create_ordinance(request, id):
    template_name = "elegislative/ordinance/create_ordinance.html"
    user = get_object_or_404(models.User, email=request.user.email) 
    agenda = get_object_or_404(models.AgendaModel, id=id)
    if request.method == 'GET':
        form = forms.OrdinanceForm(request.GET or None)
    elif request.method == 'POST':
        form = forms.OrdinanceForm(request.POST or None) 
        if form.is_valid():
            instance = form.save(commit=False)
            instance.agenda_fk = agenda
            instance.save()
            return HttpResponseRedirect(reverse_lazy("elegislative:ordinance_page")) 

    context = {
        'user': user,
        'form': form,
        'agenda': agenda,
    }    
    return render(request, template_name, context)

@authorize
@login_required
def edit_ordinance(request, id):
    template_name = "elegislative/ordinance/edit_ordinance.html"
    user = get_object_or_404(models.User, email=request.user.email) 
    ordinance = get_object_or_404(models.OrdinanceModel, id=id)

    if request.method == 'GET':
        form = forms.EditOrdinanceForm(request.GET or None, instance=ordinance)
    elif request.method == 'POST':
        form = forms.EditOrdinanceForm(request.POST or None, request.FILES, instance=ordinance) 
        if form.is_valid(): 
            form.save()
            return HttpResponseRedirect(reverse_lazy("elegislative:ordinance_page")) 

    context = {
        'user': user,
        'form': form,
        'ordinance': ordinance,
    }    
    return render(request, template_name, context)


@authorize
@login_required
def delete_ordinance(request, id):
    data = dict()
    template_name = "elegislative/ordinance/delete_ordinance.html"    
    user = get_object_or_404(models.User, email=request.user.email)
    ordinance = get_object_or_404(models.OrdinanceModel, id=id)

    if request.is_ajax():
        if request.method == 'GET': 
            context = {
                'ordinance': ordinance,
            }
            data['html_form'] = render_to_string(template_name, context, request)
        elif request.method == 'POST':            
            data['form_is_valid'] = True
            ordinance.delete() 
        return JsonResponse(data)
    else: 
        raise Http404()

@authorize
@login_required
def print_ordinance(request, id):
    template_name = "elegislative/ordinance/print_ordinance.html"  
    user = get_object_or_404(models.User, email=request.user.email)
    ordinance = get_object_or_404(models.OrdinanceModel, id=id)
    context = {
        'user': user,
        'ordinance':ordinance,
    }
    return render(request, template_name, context)
"""
[END] -> Manage Ordinance features
"""

"""
[START] -> Manage Records
"""
@login_required
def records(request):
    template_name = "elegislative/records/records.html"
    user = get_object_or_404(models.User, email=request.user.email) 
    context = {
        'user': user,
    }    
    return render(request, template_name, context)
"""
[END] -> Manage Records
""" 

"""
[START] -> Manage Minutes of the meeting features
"""
@login_required
def minutes_of_the_meeting(request):
    template_name = "elegislative/minutes_of_the_meeting/minutes_of_the_meeting.html"
    user = get_object_or_404(models.User, email=request.user.email) 
    context = {
        'user': user,
    }    
    return render(request, template_name, context)
"""
[END] -> Manage Minutes of the meeting features
"""
 
"""
[START] -> Manage announcement features
"""
@login_required
def announcements(request):
    template_name = "elegislative/announcements/announcements.html"
    user = get_object_or_404(models.User, email=request.user.email) 
    context = {
        'user': user,
    }    
    return render(request, template_name, context)
"""
[END] -> Manage announcement features
"""