from django.http import JsonResponse, Http404, HttpResponseRedirect, HttpResponse
from django.urls import reverse, reverse_lazy

from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.conf import settings
from elegislative_app import forms, models, admin

from django.contrib.auth.decorators import login_required

# for encrypting of primary keys
from cryptography.fernet import Fernet
import base64
import logging
import traceback

import json

# Complex Query
from functools import wraps, reduce
import operator
from itertools import chain

# import datetime
from datetime import timezone, datetime, timedelta
from django.core.exceptions import FieldDoesNotExist, FieldError

# Pagination
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
# Create your views here.

import os

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

            if user.is_active:
                login(request, user)
                # https://stackoverflow.com/questions/3024153/how-to-expire-session-due-to-inactivity-in-django

                # https://stackoverflow.com/questions/35796195/how-to-redirect-to-previous-page-in-django-after-post-request/35796330
                # https://stackoverflow.com/questions/806835/django-redirect-to-previous-page-after-login
                # https://stackoverflow.com/questions/38431166/redirect-to-next-after-login-in-django
                request.session.set_expiry(request.session.get_expiry_age())
                previous_page = request.GET.get('next',reverse("elegislative:dashboard_page"))
                return HttpResponseRedirect(previous_page)
                # return HttpResponseRedirect(reverse("elegislative:dashboard_page"))
            else:
                messages.error(request, "Your account is INVALID! please try again.")
        else:
            messages.error(request, "Your account is INVALID! please try again.")


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
            messages.success(request, "You have successfully registered, please try to login.")
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
"""
START-[DECORATORS]
"""
# https://stackoverflow.com/questions/5469159/how-to-write-a-custom-decorator-in-django
def authorize(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        user = get_object_or_404(models.User, email=request.user.email)
        if  request.user.is_active:
            return function(request, *args, **kwargs)
        else:
            raise Http404
            # return HttpResponseRedirect('/')
    return wrap

def roles(**rules):
    def _method_wrapper(view_method):
        def _arguments_wrapper(request, *args, **kwargs):
            if request.user.is_active:
                is_arocc_manager = rules.get('is_arocc_manager',False)
                is_mom_manager = rules.get('is_mom_manager',False)
                is_records_manager = rules.get('is_records_manager',False)
                is_announcement_manager = rules.get('is_announcement_manager',False)
                is_old_documents_manager = rules.get('is_old_documents_manager',False)
                is_webex_manager = rules.get('is_webex_manager',False)

                if is_arocc_manager:
                    if request.user.is_arocc_manager:
                        return view_method(request, *args, **kwargs)
                    else:
                        raise Http404()
                if is_mom_manager:
                    if request.user.is_mom_manager:
                        return view_method(request, *args, **kwargs)
                    else:
                        raise Http404()
                if is_records_manager:
                    if request.user.is_records_manager:
                        return view_method(request, *args, **kwargs)
                    else:
                        raise Http404()
                if is_announcement_manager:
                    if request.user.is_announcement_manager:
                        return view_method(request, *args, **kwargs)
                    else:
                        raise Http404()

                if is_old_documents_manager:
                    if request.user.is_old_documents_manager:
                        return view_method(request, *args, **kwargs)
                    else:
                        raise Http404()
                if is_webex_manager:
                    if request.user.is_webex_manager:
                        return view_method(request, *args, **kwargs)
                    else:
                        raise Http404()

            else:
                raise Http404()
        return _arguments_wrapper
    return _method_wrapper

def get_notification(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        user = get_object_or_404(models.User, email=request.user.email)
        notifications = models.NotificationsModel.objects.all().filter(Q(receiver=user)).order_by('-id')
        kwargs['notifications'] = notifications
        return function(request, *args, **kwargs)
    return wrap

# https://stackoverflow.com/questions/9030255/django-add-optional-arguments-to-decorator
def create_notification(url_target, message, tags):
    def _method_wrapper(view_method):
        def _arguments_wrapper(request, *args, **kwargs) :
            """
            Wrapper with arguments to invoke the method
            """
            user = get_object_or_404(models.User, email=request.user.email)

            users = models.User.objects.all()

            url = reverse_lazy(url_target)

            for u in users:
                models.NotificationsModel.objects.create(
                    sender=user,
                    receiver=u,
                    message=message,
                    tags=tags,
                    url=url,
                )

            return view_method(request, *args, **kwargs)
        return _arguments_wrapper
    return _method_wrapper

"""
END-[DECORATORS]
"""
def add_notification(request, url_target, message, tags):
    user = get_object_or_404(models.User, email=request.user.email)

    users = models.User.objects.all()

    url = reverse_lazy(url_target)

    for u in users:
        models.NotificationsModel.objects.create(
            sender=user,
            receiver=u,
            message=message,
            tags=tags,
            url=url,
        )

def delete_notification(request, id):
    data = dict()
    if request.is_ajax():
        notification = get_object_or_404(models.NotificationsModel,id=id)
        if request.method == 'POST':
            notification.delete()
            data['status'] = True
        return JsonResponse(data)
    else:
        raise Http404()

def delete_all_notifications(request):
    data = dict()
    if request.is_ajax():
        if request.method == 'POST':
            user = get_object_or_404(models.User, email=request.user.email)
            models.NotificationsModel.objects.all().filter(Q(receiver=user)).delete()
            data['status'] = True
        return JsonResponse(data)
    else:
        raise Http404()
# @create_notification('elegislative:agenda_page', "Agenda has been created!", settings.NOTIFICATION_TAGS[1][0])
@login_required
@authorize
@get_notification
def dashboard_page(request, *args, **kwargs):
    template_name = "elegislative/dashboard.html"
    user = get_object_or_404(models.User, email=request.user.email)
    agenda = models.AgendaModel.objects.all().filter(Q(is_delete=False)) if user.is_overall else models.AgendaModel.objects.all().filter(Q(author=user), Q(is_delete=False))
    resolution = models.ResolutionModel.objects.all().filter(Q(is_delete=False)) if user.is_overall else models.ResolutionModel.objects.all().filter(Q(author=user), Q(is_delete=False))
    ordinance = models.OrdinanceModel.objects.all().filter(Q(is_delete=False)) if user.is_overall else models.OrdinanceModel.objects.all().filter(Q(author=user), Q(is_delete=False))
    mom = models.MOMModel.objects.all().filter(Q(is_delete=False)) if user.is_overall else models.MOMModel.objects.all().filter(Q(author=user), Q(is_delete=False))
    cr_ord = models.CommitteeReportOrdinanceModel.objects.all().filter(Q(is_delete=False)) if user.is_overall else models.CommitteeReportOrdinanceModel.objects.all().filter(Q(author=user), Q(is_delete=False))
    cr_res = models.CommitteeReportResolutionModel.objects.all().filter(Q(is_delete=False)) if user.is_overall else models.CommitteeReportResolutionModel.objects.all().filter(Q(author=user), Q(is_delete=False))
    announcement = models.AnnouncementModel.objects.all() if user.is_overall else models.AnnouncementModel.objects.all().filter(Q(author=user))
    com_rec_res = models.CommentsRecomendationResolutionModel.objects.all()
    com_rec_ord = models.CommentsRecomendationOrdinanceModel.objects.all()
    com_rec_total = int(com_rec_res.count()) + int(com_rec_ord.count())
    announcement_display = models.AnnouncementModel.objects.all().filter(Q(visible=True))


    model_list = [
        models.AgendaModel,
        models.ResolutionModel,
        models.CommitteeReportResolutionModel,
        models.OrdinanceModel,
        models.CommitteeReportOrdinanceModel,
        models.MOMModel,
    ]

    signed, unsigned, approved, denied, pending, uncategorized = 0,0,0,0,0,0

    for m in model_list:
        signed += m.objects.all().filter(Q(is_signed=True), Q(is_delete=False)).count() if user.is_overall else m.objects.all().filter(Q(is_signed=True), Q(author=user), Q(is_delete=False)).count()
        unsigned += m.objects.all().filter(Q(is_signed=False), Q(is_delete=False)).count() if user.is_overall else m.objects.all().filter(Q(is_signed=False), Q(author=user), Q(is_delete=False)).count()
        approved += m.objects.all().filter(Q(status='Approved'), Q(is_delete=False)).count() if user.is_overall else m.objects.all().filter(Q(status='Approved'), Q(author=user), Q(is_delete=False)).count()
        denied += m.objects.all().filter(Q(status='Denied'), Q(is_delete=False)).count() if user.is_overall else m.objects.all().filter(Q(status='Denied'), Q(author=user), Q(is_delete=False)).count()
        pending += m.objects.all().filter(Q(status='Pending'), Q(is_delete=False)).count() if user.is_overall else m.objects.all().filter(Q(status='Pending'), Q(author=user), Q(is_delete=False)).count()
        uncategorized += m.objects.all().filter(Q(status='None'), Q(is_delete=False)).count() if user.is_overall else m.objects.all().filter(Q(status='None'), Q(author=user), Q(is_delete=False)).count()

    context = {
        'user': user,
        'agenda': agenda,
        'resolution': resolution,
        'ordinance': ordinance,
        'mom': mom,
        'cr_ord': cr_ord,
        'cr_res': cr_res,
        'announcement': announcement,
        'com_rec_total': com_rec_total,
        'announcement_display': announcement_display,
        'notifications':kwargs['notifications'],
        'signed':signed,
        'unsigned':unsigned,
        'approved':approved,
        'denied':denied,
        'pending':pending,
        'uncategorized':uncategorized,
    }
    return render(request, template_name, context)

@login_required
@authorize
@get_notification
def search(request, *args, **kwargs):
    template_name = "elegislative/search/search_results.html"
    user = get_object_or_404(models.User, email=request.user.email)

    search_term = request.GET.get('q')
    model_list = [
        models.AgendaModel,
        models.ResolutionModel,
        models.CommitteeReportResolutionModel,
        # models.CommentsRecomendationResolutionModel,
        models.OrdinanceModel,
        models.CommitteeReportOrdinanceModel,
        # models.CommentsRecomendationOrdinanceModel,
        models.MOMModel,
        models.AnnouncementModel,
    ]
    excluded_fields = [
        'id',
        'resolution_fk',
        'ordinance_fk',
        'is_signed',
        'hard_copy',
        'resolution_committee_report_fk',
        'resolution_comments_recommendation_fk',
        'agenda_fk',
        'resolution_comments_recommendation_fk',
        'commentor_resolution',
        'ordinance_committee_report_fk',
        'ordinance_comments_recomendation_fk',
        'is_public',
        'visible',
        'commentor_ordiance',
    ]
    queryset = []
    for ml in model_list:


        # https://treyhunner.com/2018/10/asterisks-in-python-what-they-are-and-how-to-use-them/
        # https://stackoverflow.com/questions/9122169/calling-filter-with-a-variable-for-field-name
        # https://stackoverflow.com/questions/852414/how-to-dynamically-compose-an-or-query-filter-in-django
        # https://stackoverflow.com/questions/21809112/what-does-tuple-and-dict-mean-in-python
        """
        def foo(x, y):
            print(x, y)

        d = {'x':1, 'y':2}
        foo(**d)
        1 2

        >> d = {'a': 1}
        >> {'b': 2, **d}
        {'b': 2, 'a': 1}

        def foo(**d):
            print(d)

        >> foo(x=1, y=2)
        {'y': 2, 'x': 1}
        """

        try:
            fn = [field for field in [field.name for field in ml._meta.get_fields() if not (field.many_to_one or field.one_to_one)] if field not in excluded_fields]
            frn = [field for field in [field.name for field in ml._meta.get_fields() if (field.many_to_one or field.one_to_one)] if field not in excluded_fields]

            queries = [Q(**{f+"__icontains":search_term}) for f in fn] + [Q(Q(**{f+"__l_name__icontains":search_term}) | Q(**{f+"__f_name__icontains":search_term})) for f in frn]
            que = queries.pop()

            for q in queries:
                que |= q
            field = getattr(ml,'is_delete',False)
            if field:
                query = ml.objects.all().filter(que, Q(is_delete=False)) if user.is_overall else ml.objects.all().filter(Q(que),Q(author=user), Q(is_delete=False))
            else:
                query = ml.objects.all().filter(que) if user.is_overall else ml.objects.all().filter(Q(que),Q(author=user))

            if query:
                queryset.append(query)
        except FieldError as e:
            print(e)
            continue

    # for a in queryset:
    #     print(a.model.__name__)

    # filter the query on each model
    records_filtered = []
    for qs in queryset:
        for q in qs:
            records_filtered.append(q)

    page = request.GET.get('page', 1)

    paginator = Paginator(records_filtered, 10)
    try:
        query_records = paginator.page(page)
    except PageNotAnInteger:
        query_records = paginator.page(1)
    except EmptyPage:
        query_records = paginator.page(paginator.num_pages)


    base_url = request.path + f'?q={search_term}'

    context = {
        'records_filtered': records_filtered,
        'query_records': query_records,
        'base_url': base_url,
        'notifications':kwargs['notifications'],
    }

    return render(request, template_name, context)


"""
[START] -> CRUD, Manage Agenda Features
"""

# Agenda Feature
@login_required
@roles(is_arocc_manager=True)
@authorize
@get_notification
def agenda_page(request, *args, **kwargs):
    template_name = "elegislative/agenda/agenda.html"
    user = get_object_or_404(models.User, email=request.user.email)
    agenda = models.AgendaModel.objects.all().filter(Q(is_delete=False)) if user.is_overall else models.AgendaModel.objects.all().filter(Q(author=user), Q(is_delete=False))
    context = {
        'user': user,
        'agenda': agenda,
        'notifications':kwargs['notifications'],
    }
    return render(request, template_name, context)

# @create_notification('elegislative:agenda_page', "Agenda has been created!", settings.NOTIFICATION_TAGS[1][0])
@login_required
@roles(is_arocc_manager=True)
@authorize
@get_notification
def create_agenda_page(request, *args, **kwargs):
    template_name = "elegislative/agenda/create_new_agenda.html"
    user = get_object_or_404(models.User, email=request.user.email)

    if user.is_view_mode:
        raise Http404()

    if request.method == 'GET':
        form = forms.AgendaForm(request.GET or None)
    elif request.method == 'POST':
        form = forms.AgendaForm(request.POST or None)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.author = user
            instance.save()
            add_notification(request,'elegislative:agenda_page', f"Agenda ({instance.no}) has been created!", settings.NOTIFICATION_TAGS[1][0])
            return HttpResponseRedirect(reverse_lazy("elegislative:agenda_page"))

    context = {
        'user': user,
        'form':form,
        'notifications':kwargs['notifications'],
    }
    return render(request, template_name, context)

@login_required
@roles(is_arocc_manager=True)
@authorize
@get_notification
def edit_agenda_page(request, *args, **kwargs):
    template_name = "elegislative/agenda/edit_agenda.html"
    user = get_object_or_404(models.User, email=request.user.email)
    # kwargs['id] is from url
    agenda = get_object_or_404(models.AgendaModel, Q(is_delete=False), id=kwargs['id']) if user.is_overall else get_object_or_404(models.AgendaModel,Q(author=user), Q(is_delete=False), id=kwargs['id'])

    if user.is_view_mode:
        raise Http404()

    if request.method == 'GET':
        form = forms.EditAgendaForm(request.GET or None, instance=agenda)
    elif request.method == 'POST':
        form = forms.EditAgendaForm(request.POST or None, request.FILES, instance=agenda)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.author = user
            instance.save()
            return HttpResponseRedirect(reverse_lazy("elegislative:agenda_page"))
    context = {
        'user': user,
        'form':form,
        'agenda': agenda,
        'notifications':kwargs['notifications'],
    }
    return render(request, template_name, context)

@roles(is_arocc_manager=True)
@authorize
@login_required
def delete_agenda_page(request, id):
    data = dict()
    template_name = "elegislative/agenda/delete_agenda.html"
    user = get_object_or_404(models.User, email=request.user.email)
    # ~ not
    agenda = get_object_or_404(models.AgendaModel, Q(is_delete=False), id=id) if user.is_overall else get_object_or_404(models.AgendaModel,Q(author=user),Q(is_delete=False), id=id)

    if user.is_view_mode:
        raise Http404()

    if request.is_ajax():
        if request.method == 'GET':
            context = {
                'agenda': agenda,
            }

            data['html_form'] = render_to_string(template_name, context, request)
        elif request.method == 'POST':
            data['form_is_valid'] = True
            agenda.is_delete = True
            agenda.save()
            # agenda.delete()
        return JsonResponse(data)
    else:
        raise Http404()

@roles(is_arocc_manager=True)
@authorize
@login_required
def print_agenda_page(request, id):
    template_name = "elegislative/agenda/print_agenda.html"
    user = get_object_or_404(models.User, email=request.user.email)
    agenda = get_object_or_404(models.AgendaModel, Q(is_delete=False), id=id) if user.is_overall else get_object_or_404(models.AgendaModel,Q(author=user), Q(is_delete=False), id=id)
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
@login_required
@roles(is_arocc_manager=True)
@authorize
@get_notification
def comments_and_recommendation(request, *args, **kwargs):
    template_name = "elegislative/comments_recommendation/comments_recommendation.html"
    user = get_object_or_404(models.User, email=request.user.email)
    resolutions = models.ResolutionModel.objects.all().filter(Q(Q(is_public=True) & Q(is_signed=False)), Q(is_delete=False))
    ordinances = models.OrdinanceModel.objects.all().filter(Q(Q(is_public=True) & Q(is_signed=False)), Q(is_delete=False),)

    # combine = list(resolutions) + list(ordinances)

    # # get modelname based on query
    # # for c in combine:
    # #     print(combine.model.__name__)

    context = {
        'user': user,
        'resolutions': resolutions,
        'ordinances': ordinances,
        'notifications':kwargs['notifications'],
    }
    return render(request, template_name, context)

@login_required
@roles(is_arocc_manager=True)
@authorize
@get_notification
def posting_resolution(request, *args, **kwargs):
    template_name = "elegislative/comments_recommendation/posting_resolution.html"
    user = get_object_or_404(models.User, email=request.user.email)
    resolution = get_object_or_404(models.ResolutionModel, Q(is_delete=False), Q(is_signed=False), id=kwargs['id'])
    com_rec = models.CommentsRecomendationResolutionModel.objects.all().filter(resolution_comments_recommendation_fk=resolution)
    context = {
        'user': user,
        'resolution': resolution,
        'notifications':kwargs['notifications'],
        'com_rec': com_rec,
    }
    return render(request, template_name, context)

@login_required
@roles(is_arocc_manager=True)
@authorize
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

@login_required
@roles(is_arocc_manager=True)
@authorize
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
@login_required
@roles(is_arocc_manager=True)
@authorize
@get_notification
def posting_ordinance(request, *args, **kwargs):
    template_name = "elegislative/comments_recommendation/posting_ordinance.html"
    user = get_object_or_404(models.User, email=request.user.email)
    ordinance = get_object_or_404(models.OrdinanceModel, Q(is_delete=False), Q(is_signed=False), id=kwargs['id'])
    com_rec = models.CommentsRecomendationOrdinanceModel.objects.all().filter(ordinance_comments_recomendation_fk=ordinance)
    context = {
        'user': user,
        'ordinance': ordinance,
        'com_rec': com_rec,
        'notifications':kwargs['notifications'],
    }
    return render(request, template_name, context)

@login_required
@roles(is_arocc_manager=True)
@authorize
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

@login_required
@roles(is_arocc_manager=True)
@authorize
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
@login_required
@roles(is_arocc_manager=True)
@authorize
@get_notification
def committee_reports(request, *args, **kwargs):
    template_name = "elegislative/committee_reports/committee_reports.html"
    user = get_object_or_404(models.User, email=request.user.email)
    c_resolutions = models.CommitteeReportResolutionModel.objects.all()
    c_ordinances = models.CommitteeReportOrdinanceModel.objects.all()
    # result_list = list(chain(c_resolutions, c_ordinances))
    resolution = models.CommitteeReportResolutionModel.objects.all().filter(Q(is_delete=False)) if user.is_overall else models.CommitteeReportResolutionModel.objects.all().filter(Q(author=user), Q(is_delete=False))
    ordinance = models.CommitteeReportOrdinanceModel.objects.all().filter(Q(is_delete=False)) if user.is_overall else models.CommitteeReportOrdinanceModel.objects.all().filter(Q(author=user), Q(is_delete=False))

    context = {
        'user': user,
        'resolution': resolution,
        'ordinance': ordinance,
        'notifications':kwargs['notifications'],
    }
    return render(request, template_name, context)

# CRUD committee reports for resolution
@login_required
@roles(is_arocc_manager=True)
@authorize
@get_notification
def create_committee_resolution_reports(request, *args, **kwargs):
    template_name = "elegislative/committee_reports/create_committee_resolution_reports.html"
    user = get_object_or_404(models.User, email=request.user.email)
    resolution = get_object_or_404(models.ResolutionModel, Q(is_delete=False), id=kwargs['id']) if user.is_overall else get_object_or_404(models.ResolutionModel, Q(author=user), Q(is_delete=False), id=kwargs['id'])

    if user.is_view_mode:
        raise Http404()

    if request.method == 'GET':
        form = forms.CommitteeReportResolutionForm(request.GET or None)
    elif request.method == 'POST':
        form = forms.CommitteeReportResolutionForm(request.POST or None)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.resolution_committee_report_fk = resolution
            instance.author = user
            instance.save()
            add_notification(request,'elegislative:committee_reports', f"Com. Rep. Res ({instance.no}) has been created!", settings.NOTIFICATION_TAGS[6][0])
            return HttpResponseRedirect(reverse_lazy("elegislative:committee_reports"))

    context = {
        'user': user,
        'resolution': resolution,
        'form': form,
        'notifications':kwargs['notifications'],
    }
    return render(request, template_name, context)

@login_required
@roles(is_arocc_manager=True)
@authorize
@get_notification
def edit_committee_resolution_reports(request, *args, **kwargs):
    template_name = "elegislative/committee_reports/edit_committee_resolution_reports.html"
    user = get_object_or_404(models.User, email=request.user.email)
    committee_report = get_object_or_404(models.CommitteeReportResolutionModel, Q(is_delete=False), id=kwargs['id']) if user.is_overall else get_object_or_404(models.CommitteeReportResolutionModel, Q(author=user), Q(is_delete=False), id=kwargs['id'])

    if user.is_view_mode:
        raise Http404()

    if request.method == 'GET':
        form = forms.EditCommitteeReportResolutionForm(request.GET or None, instance=committee_report)
    elif request.method == 'POST':
        form = forms.EditCommitteeReportResolutionForm(request.POST or None, request.FILES, instance=committee_report)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.author = user
            instance.save()
            return HttpResponseRedirect(reverse_lazy("elegislative:committee_reports"))
    context = {
        'user': user,
        'committee_report': committee_report,
        'form'  : form,
        'notifications':kwargs['notifications'],
    }

    return render(request, template_name, context)

@login_required
@roles(is_arocc_manager=True)
@authorize
def delete_committee_resolution_reports(request, id):
    data = dict()
    template_name = "elegislative/committee_reports/delete_committee_resolution_reports.html"
    user = get_object_or_404(models.User, email=request.user.email)
    committee_report = get_object_or_404(models.CommitteeReportResolutionModel, Q(is_delete=False), id=id) if user.is_overall else get_object_or_404(models.CommitteeReportResolutionModel, Q(author=user), Q(is_delete=False), id=id)

    if user.is_view_mode:
        raise Http404()

    if request.is_ajax():
        if request.method == 'GET':
            context = {
                'committee_report': committee_report,
            }
            data['html_form'] = render_to_string(template_name, context, request)
        elif request.method == 'POST':
            data['form_is_valid'] = True
            committee_report.is_delete = True
            committee_report.save()
            # committee_report.delete()
        return JsonResponse(data)
    else:
        raise Http404

@login_required
@roles(is_arocc_manager=True)
@authorize
def print_committee_resolution_reports(request, id):
    template_name = "elegislative/committee_reports/print_committee_resolution_reports.html"
    user = get_object_or_404(models.User, email=request.user.email)
    committee_report = get_object_or_404(models.CommitteeReportResolutionModel, Q(is_delete=False), id=id) if user.is_overall else get_object_or_404(models.CommitteeReportResolutionModel, Q(author=user), Q(is_delete=False), id=id)

    context = {
        'user': user,
        'committee_report':committee_report,
    }
    return render(request, template_name, context)

# CRUD committee reports for ordinance
@login_required
@roles(is_arocc_manager=True)
@authorize
@get_notification
def create_committee_ordinance_reports(request, *args, **kwargs):
    template_name = "elegislative/committee_reports/create_committee_ordinance_reports.html"
    user = get_object_or_404(models.User, email=request.user.email)
    ordinance = get_object_or_404(models.OrdinanceModel, Q(is_delete=False), id=kwargs['id']) if user.is_overall else get_object_or_404(models.OrdinanceModel, Q(author=user), Q(is_delete=False), id=kwargs['id'])

    if user.is_view_mode:
        raise Http404()

    if request.method == 'GET':
        form = forms.CommitteeReportOrdinanceForm(request.GET or None)
    elif request.method == 'POST':
        form = forms.CommitteeReportOrdinanceForm(request.POST or None)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.ordinance_committee_report_fk = ordinance
            instance.author = user
            instance.save()
            add_notification(request,'elegislative:committee_reports', f"Com. Rep. Ord ({instance.no}) has been created!", settings.NOTIFICATION_TAGS[6][0])
            return HttpResponseRedirect(reverse_lazy("elegislative:committee_reports"))

    context = {
        'user': user,
        'form': form,
        'ordinance': ordinance,
        'notifications':kwargs['notifications'],
    }

    return render(request, template_name, context)

@login_required
@roles(is_arocc_manager=True)
@authorize
@get_notification
def edit_committee_ordinance_reports(request, *args, **kwargs):
    template_name = "elegislative/committee_reports/edit_committee_ordinance_reports.html"
    user = get_object_or_404(models.User, email=request.user.email)
    committee_report = get_object_or_404(models.CommitteeReportOrdinanceModel, Q(is_delete=False), id=kwargs['id']) if user.is_overall else get_object_or_404(models.CommitteeReportOrdinanceModel, Q(author=user), Q(is_delete=False), id=kwargs['id'])

    if user.is_view_mode:
        raise Http404()

    if request.method == 'GET':
        form = forms.EditCommitteeReportResolutionForm(request.GET or None, instance=committee_report)
    elif request.method == 'POST':
        form = forms.EditCommitteeReportResolutionForm(request.POST or None, request.FILES, instance=committee_report)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.author = user
            instance.save()
            return HttpResponseRedirect(reverse_lazy("elegislative:committee_reports"))
    context = {
        'user': user,
        'committee_report': committee_report,
        'form'  : form,
        'notifications':kwargs['notifications'],
    }

    return render(request, template_name, context)

@login_required
@roles(is_arocc_manager=True)
@authorize
def delete_committee_ordinance_reports(request, id):
    data = dict()
    template_name = "elegislative/committee_reports/delete_committee_ordinance_reports.html"
    user = get_object_or_404(models.User, email=request.user.email)
    committee_report = get_object_or_404(models.CommitteeReportOrdinanceModel, Q(is_delete=False), id=id) if user.is_overall else get_object_or_404(models.CommitteeReportOrdinanceModel, Q(author=user), Q(is_delete=False), id=id)

    if user.is_view_mode:
        raise Http404()

    if request.is_ajax():
        if request.method == 'GET':
            context = {
                'committee_report': committee_report,
            }
            data['html_form'] = render_to_string(template_name, context, request)
        elif request.method == 'POST':
            data['form_is_valid'] = True
            committee_report.is_delete = True
            committee_report.save()
            # committee_report.delete()
        return JsonResponse(data)
    else:
        raise Http404()

@login_required
@roles(is_arocc_manager=True)
@authorize
def print_committee_ordinance_reports(request, id):
    template_name = "elegislative/committee_reports/print_committee_ordinance_reports.html"
    user = get_object_or_404(models.User, email=request.user.email)
    committee_report = get_object_or_404(models.CommitteeReportOrdinanceModel, Q(is_delete=False), id=id) if user.is_overall else get_object_or_404(models.CommitteeReportOrdinanceModel, Q(author=user), Q(is_delete=False), id=id)

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
@login_required
@roles(is_arocc_manager=True)
@authorize
@get_notification
def resolution(request, *args, **kwargs):
    template_name = "elegislative/resolution/resolution.html"
    user = get_object_or_404(models.User, email=request.user.email)
    resolutions = models.ResolutionModel.objects.all().filter(Q(is_delete=False)) if user.is_overall else models.ResolutionModel.objects.all().filter(Q(author=user), Q(is_delete=False))
    context = {
        'user': user,
        'resolutions': resolutions,
        'notifications':kwargs['notifications'],
    }
    return render(request, template_name, context)

@login_required
@roles(is_arocc_manager=True)
@authorize
@get_notification
def create_resolutions(request, *args, **kwargs):
    template_name = "elegislative/resolution/create_resolution.html"
    user = get_object_or_404(models.User, email=request.user.email)
    agenda = get_object_or_404(models.AgendaModel, Q(is_delete=False), id=kwargs['id']) if user.is_overall else get_object_or_404(models.AgendaModel, Q(author=user), Q(is_delete=False), id=kwargs['id'])

    if user.is_view_mode:
        raise Http404()

    if request.method == 'GET':
        form = forms.ResolutionForm(request.GET or None)
    elif request.method == 'POST':
        form = forms.ResolutionForm(request.POST or None)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.agenda_fk = agenda
            instance.author = user
            instance.save()
            add_notification(request,'elegislative:resolution', f"Resolution ({instance.no}) has been created!", settings.NOTIFICATION_TAGS[2][0])
            return HttpResponseRedirect(reverse_lazy("elegislative:resolution"))

    context = {
        'user': user,
        'form': form,
        'agenda': agenda,
        'notifications':kwargs['notifications'],
    }
    return render(request, template_name, context)

@login_required
@roles(is_arocc_manager=True)
@authorize
@get_notification
def edit_resolution(request, *args, **kwargs):
    template_name = "elegislative/resolution/edit_resolution.html"
    user = get_object_or_404(models.User, email=request.user.email)
    resolution = get_object_or_404(models.ResolutionModel, Q(is_delete=False), id=kwargs['id']) if user.is_overall else get_object_or_404(models.ResolutionModel, Q(author=user), Q(is_delete=False), id=kwargs['id'])

    if user.is_view_mode:
        raise Http404()

    if request.method == 'GET':
        form = forms.EditResolutionForm(request.GET or None, instance=resolution)
    elif request.method == 'POST':
        form = forms.EditResolutionForm(request.POST or None, request.FILES, instance=resolution)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.author = user
            instance.save()
            return HttpResponseRedirect(reverse_lazy("elegislative:resolution"))

    context = {
        'user': user,
        'form': form,
        'resolution': resolution,
        'notifications':kwargs['notifications'],
    }
    return render(request, template_name, context)

@roles(is_arocc_manager=True)
@authorize
@login_required
def delete_resolution(request, id):
    data = dict()
    template_name = "elegislative/resolution/delete_resolution.html"
    user = get_object_or_404(models.User, email=request.user.email)
    resolution = get_object_or_404(models.ResolutionModel, Q(is_delete=False), id=id) if user.is_overall else get_object_or_404(models.ResolutionModel, Q(author=user), Q(is_delete=False), id=id)

    if user.is_view_mode:
        raise Http404()

    if request.is_ajax():
        if request.method == 'GET':
            context = {
                'resolution': resolution,
            }
            data['html_form'] = render_to_string(template_name, context, request)
        elif request.method == 'POST':
            data['form_is_valid'] = True
            resolution.is_delete = True
            resolution.save()
            # resolution.delete()
        return JsonResponse(data)
    else:
        raise Http404()

@roles(is_arocc_manager=True)
@authorize
@login_required
def print_resolution(request, id):
    template_name = "elegislative/resolution/print_resolution.html"
    user = get_object_or_404(models.User, email=request.user.email)
    resolution = get_object_or_404(models.ResolutionModel, Q(is_delete=False), id=id) if user.is_overall else get_object_or_404(models.ResolutionModel,Q(is_delete=False), Q(author=user), id=id)
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
@roles(is_arocc_manager=True)
@authorize
@get_notification
def ordinance(request, *args, **kwargs):
    template_name = "elegislative/ordinance/ordinance.html"
    user = get_object_or_404(models.User, email=request.user.email)
    ordinance = models.OrdinanceModel.objects.all().filter(Q(is_delete=False)) if user.is_overall else models.OrdinanceModel.objects.all().filter(Q(author=user),Q(is_delete=False))
    context = {
        'user': user,
        'ordinance': ordinance,
        'notifications':kwargs['notifications'],
    }
    return render(request, template_name, context)

@login_required
@roles(is_arocc_manager=True)
@authorize
@get_notification
def create_ordinance(request, *args, **kwargs):
    template_name = "elegislative/ordinance/create_ordinance.html"
    user = get_object_or_404(models.User, email=request.user.email)
    agenda = get_object_or_404(models.AgendaModel, Q(is_delete=False), id=kwargs['id']) if user.is_overall else get_object_or_404(models.AgendaModel, Q(author=user), Q(is_delete=False), id=kwargs['id'])

    if user.is_view_mode:
        raise Http404()

    if request.method == 'GET':
        form = forms.OrdinanceForm(request.GET or None)
    elif request.method == 'POST':
        form = forms.OrdinanceForm(request.POST or None)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.agenda_fk = agenda
            instance.author = user
            instance.save()
            add_notification(request,'elegislative:ordinance_page', f"Ordinance ({instance.no}) has been created!", settings.NOTIFICATION_TAGS[3][0])
            return HttpResponseRedirect(reverse_lazy("elegislative:ordinance_page"))

    context = {
        'user': user,
        'form': form,
        'agenda': agenda,
        'notifications':kwargs['notifications'],
    }
    return render(request, template_name, context)

@login_required
@roles(is_arocc_manager=True)
@authorize
@get_notification
def edit_ordinance(request, *args, **kwargs):
    template_name = "elegislative/ordinance/edit_ordinance.html"
    user = get_object_or_404(models.User, email=request.user.email)
    ordinance = get_object_or_404(models.OrdinanceModel, Q(is_delete=False), id=kwargs['id']) if user.is_overall else get_object_or_404(models.OrdinanceModel, Q(author=user), Q(is_delete=False), id=kwargs['id'])

    if user.is_view_mode:
        raise Http404()

    if request.method == 'GET':
        form = forms.EditOrdinanceForm(request.GET or None, instance=ordinance)
    elif request.method == 'POST':
        form = forms.EditOrdinanceForm(request.POST or None, request.FILES, instance=ordinance)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.author = user
            instance.save()
            return HttpResponseRedirect(reverse_lazy("elegislative:ordinance_page"))

    context = {
        'user': user,
        'form': form,
        'ordinance': ordinance,
        'notifications':kwargs['notifications'],
    }
    return render(request, template_name, context)

@login_required
@roles(is_arocc_manager=True)
@authorize
def delete_ordinance(request, id):
    data = dict()
    template_name = "elegislative/ordinance/delete_ordinance.html"
    user = get_object_or_404(models.User, email=request.user.email)
    ordinance = get_object_or_404(models.OrdinanceModel, Q(is_delete=False), id=id) if user.is_overall else get_object_or_404(models.OrdinanceModel, Q(author=user), Q(is_delete=False), id=id)

    if user.is_view_mode:
        raise Http404()

    if request.is_ajax():
        if request.method == 'GET':
            context = {
                'ordinance': ordinance,
            }
            data['html_form'] = render_to_string(template_name, context, request)
        elif request.method == 'POST':
            data['form_is_valid'] = True
            ordinance.is_delete = True
            ordinance.save()
            # ordinance.delete()
        return JsonResponse(data)
    else:
        raise Http404()

@login_required
@roles(is_arocc_manager=True)
@authorize
def print_ordinance(request, id):
    template_name = "elegislative/ordinance/print_ordinance.html"
    user = get_object_or_404(models.User, email=request.user.email)
    ordinance = get_object_or_404(models.OrdinanceModel, Q(is_delete=False), id=id) if user.is_overall else get_object_or_404(models.OrdinanceModel, Q(author=user), Q(is_delete=False), id=id)
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
def date_formatter(date_parse, date_format, date):
    # x = 'Jan. 19, 2021, 05:08 AM'
    # x = datetime.strptime(x, '%b. %d, %Y, %I:%M %p')
    # 2021-01-14 04:57:37.396125
    # https://www.w3schools.com/python/python_datetime.asp
    # b = x.strftime("%Y-%m-%d %H:%M:%S.%f")
    # agenda = models.AgendaModel.objects.all().filter(date_filed__range=(b, b))
    dp = datetime.strptime(date, date_parse)
    df = dp.strftime(date_format)

    return df

def report_generator(database_name, date_from, date_to, keyword, signature, user):

    query, cols = False, False

    if database_name == 'Agenda':

        if date_from and date_to and keyword and signature:
            date_from = date_formatter('%m/%d/%Y','%Y-%m-%d %H:%M:%S.%f',date_from)
            date_to = date_formatter('%m/%d/%Y','%Y-%m-%d %H:%M:%S.%f',date_to)
            filters = Q(Q(date_filed__range=(date_from, date_to)) &
                        Q(Q(id__icontains=keyword) |
                        Q(no__icontains=keyword) |
                        Q(title__icontains=keyword) |
                        Q(author__l_name__icontains=keyword) |
                        Q(author__f_name__icontains=keyword) |
                        Q(date_filed__icontains=keyword)))
            if signature == 'Signed Only':
                filters = Q(Q(date_filed__range=(date_from, date_to)) &
                            Q(Q(id__icontains=keyword) |
                            Q(no__icontains=keyword) |
                            Q(title__icontains=keyword) |
                            Q(author__l_name__icontains=keyword) |
                            Q(author__f_name__icontains=keyword) |
                            Q(date_filed__icontains=keyword)) &
                            Q(is_signed=True)
                            )
            elif signature == 'Unsigned Only':
                filters = Q(Q(date_filed__range=(date_from, date_to)) &
                            Q(Q(id__icontains=keyword) |
                            Q(no__icontains=keyword) |
                            Q(title__icontains=keyword) |
                            Q(author__l_name__icontains=keyword) |
                            Q(author__f_name__icontains=keyword) |
                            Q(date_filed__icontains=keyword)) &
                            Q(is_signed=False)
                            )
            query = models.AgendaModel.objects.all().filter(filters, Q(is_delete=False)).order_by('-id') if user.is_overall else models.AgendaModel.objects.all().filter(filters,Q(author=user),Q(is_delete=False)).order_by('-id')

        elif date_from and date_to:
            date_from = date_formatter('%m/%d/%Y','%Y-%m-%d %H:%M:%S.%f',date_from)
            date_to = date_formatter('%m/%d/%Y','%Y-%m-%d %H:%M:%S.%f',date_to)
            query = models.AgendaModel.objects.all().filter(Q(date_filed__range=(date_from, date_to)), Q(is_delete=False)).order_by('-id') if user.is_overall else models.AgendaModel.objects.all().filter(Q(date_filed__range=(date_from, date_to)), Q(author=user), Q(is_delete=False)).order_by('-id')

        elif keyword:
            filters = Q(
                Q(id__icontains=keyword) |
                Q(no__icontains=keyword) |
                Q(title__icontains=keyword) |
                Q(author__l_name__icontains=keyword) |
                Q(author__f_name__icontains=keyword) |
                Q(date_filed__icontains=keyword)
                )
            query = models.AgendaModel.objects.all().filter(filters, Q(is_delete=False)).order_by('-id') if user.is_overall else models.AgendaModel.objects.all().filter(filters, Q(author=user), Q(is_delete=False)).order_by('-id')

        elif signature:
            if signature == 'Signed Only':
                query = models.AgendaModel.objects.all().filter(Q(is_signed=True), Q(is_delete=False)).order_by('-id') if user.is_overall else models.AgendaModel.objects.all().filter(Q(is_signed=True), Q(author=user), Q(is_delete=False)).order_by('-id')
            elif signature == 'Unsigned Only':
                query = models.AgendaModel.objects.all().filter(Q(is_signed=False), Q(is_delete=False)).order_by('-id') if user.is_overall else models.AgendaModel.objects.all().filter(Q(is_signed=False), Q(author=user), Q(is_delete=False)).order_by('-id')
            else:
                query = models.AgendaModel.objects.all().filter(Q(is_delete=False)) if user.is_overall else models.AgendaModel.objects.all().filter(Q(author=user), Q(is_delete=False))
        else:
            query = models.AgendaModel.objects.all().filter(Q(is_delete=False)) if user.is_overall else models.AgendaModel.objects.all().filter(Q(author=user), Q(is_delete=False))

        cols = admin.AgendaAdmin.list_display
        cols = list(cols)
        cols.remove('content')
        cols.remove('hard_copy')
        cols.remove('is_delete')
        cols = [c.replace("_"," ").upper() for c in cols]

    elif database_name == 'Ordinance':
        if date_from and date_to and keyword and signature:
            date_from = date_formatter('%m/%d/%Y','%Y-%m-%d %H:%M:%S.%f',date_from)
            date_to = date_formatter('%m/%d/%Y','%Y-%m-%d %H:%M:%S.%f',date_to)
            filters = Q(Q(date_filed__range=(date_from, date_to)) &
                        Q(Q(id__icontains=keyword) |
                        Q(no__icontains=keyword) |
                        Q(title__icontains=keyword) |
                        Q(author__l_name__icontains=keyword) |
                        Q(author__f_name__icontains=keyword) |
                        Q(date_filed__icontains=keyword)))
            if signature == 'Signed Only':
                filters = Q(Q(date_filed__range=(date_from, date_to)) &
                            Q(Q(id__icontains=keyword) |
                            Q(no__icontains=keyword) |
                            Q(title__icontains=keyword) |
                            Q(author__l_name__icontains=keyword) |
                            Q(author__f_name__icontains=keyword) |
                            Q(date_filed__icontains=keyword)) &
                            Q(is_signed=True)
                            )
            elif signature == 'Unsigned Only':
                filters = Q(Q(date_filed__range=(date_from, date_to)) &
                            Q(Q(id__icontains=keyword) |
                            Q(no__icontains=keyword) |
                            Q(title__icontains=keyword) |
                            Q(author__l_name__icontains=keyword) |
                            Q(author__f_name__icontains=keyword) |
                            Q(date_filed__icontains=keyword)) &
                            Q(is_signed=False)
                            )
            query = models.OrdinanceModel.objects.all().filter(filters, Q(is_delete=False)).order_by('-id') if user.is_overall else models.OrdinanceModel.objects.all().filter(filters, Q(author=user), Q(is_delete=False)).order_by('-id')

        elif date_from and date_to:
            date_from = date_formatter('%m/%d/%Y','%Y-%m-%d %H:%M:%S.%f',date_from)
            date_to = date_formatter('%m/%d/%Y','%Y-%m-%d %H:%M:%S.%f',date_to)
            query = models.OrdinanceModel.objects.all().filter(Q(date_filed__range=(date_from, date_to)), Q(is_delete=False)).order_by('-id') if user.is_overall else models.OrdinanceModel.objects.all().filter(Q(date_filed__range=(date_from, date_to)), Q(author=user), Q(is_delete=False)).order_by('-id')

        elif keyword:
            filters = Q(
                Q(id__icontains=keyword) |
                Q(no__icontains=keyword) |
                Q(title__icontains=keyword) |
                Q(author__l_name__icontains=keyword) |
                Q(author__f_name__icontains=keyword) |
                Q(date_filed__icontains=keyword)
                )
            query = models.OrdinanceModel.objects.all().filter(filters, Q(is_delete=False)).order_by('-id') if user.is_overall else models.OrdinanceModel.objects.all().filter(filters, Q(author=user), Q(is_delete=False)).order_by('-id')

        elif signature:
            if signature == 'Signed Only':
                query = models.OrdinanceModel.objects.all().filter(Q(is_signed=True), Q(is_delete=False)).order_by('-id') if user.is_overall else models.OrdinanceModel.objects.all().filter(Q(is_signed=True), Q(author=user), Q(is_delete=False)).order_by('-id')
            elif signature == 'Unsigned Only':
                query = models.OrdinanceModel.objects.all().filter(Q(is_signed=False), Q(is_delete=False)).order_by('-id') if user.is_overall else models.OrdinanceModel.objects.all().filter(Q(is_signed=False), Q(author=user), Q(is_delete=False)).order_by('-id')
            else:
                query = models.OrdinanceModel.objects.all().filter(Q(is_delete=False)) if user.is_overall else models.OrdinanceModel.objects.all().filter(Q(author=user), Q(is_delete=False))

        else:
            query = models.OrdinanceModel.objects.all().filter(Q(is_delete=False)) if user.is_overall else models.OrdinanceModel.objects.all().filter(Q(author=user), Q(is_delete=False))
        cols = admin.OrdinanceAdmin.list_display
        cols = list(cols)
        cols.remove('content')
        cols.remove('hard_copy')
        cols.remove('agenda_fk')
        cols.remove('is_public')
        cols.remove('is_delete')
        cols = [c.replace("_"," ").upper() for c in cols]

    elif database_name == 'Resolution':
        if date_from and date_to and keyword and signature:
            date_from = date_formatter('%m/%d/%Y','%Y-%m-%d %H:%M:%S.%f',date_from)
            date_to = date_formatter('%m/%d/%Y','%Y-%m-%d %H:%M:%S.%f',date_to)
            filters = Q(Q(date_filed__range=(date_from, date_to)) &
                        Q(Q(id__icontains=keyword) |
                        Q(no__icontains=keyword) |
                        Q(title__icontains=keyword) |
                        Q(author__l_name__icontains=keyword) |
                        Q(author__f_name__icontains=keyword) |
                        Q(date_filed__icontains=keyword)))
            if signature == 'Signed Only':
                filters = Q(Q(date_filed__range=(date_from, date_to)) &
                            Q(Q(id__icontains=keyword) |
                            Q(no__icontains=keyword) |
                            Q(title__icontains=keyword) |
                            Q(author__l_name__icontains=keyword) |
                            Q(author__f_name__icontains=keyword) |
                            Q(date_filed__icontains=keyword)) &
                            Q(is_signed=True)
                            )
            elif signature == 'Unsigned Only':
                filters = Q(Q(date_filed__range=(date_from, date_to)) &
                            Q(Q(id__icontains=keyword) |
                            Q(no__icontains=keyword) |
                            Q(title__icontains=keyword) |
                            Q(author__l_name__icontains=keyword) |
                            Q(author__f_name__icontains=keyword) |
                            Q(date_filed__icontains=keyword)) &
                            Q(is_signed=False)
                            )
            query = models.ResolutionModel.objects.all().filter(filters, Q(is_delete=False)).order_by('-id') if user.is_overall else models.ResolutionModel.objects.all().filter(filters, Q(author=user), Q(is_delete=False)).order_by('-id')

        elif date_from and date_to:
            date_from = date_formatter('%m/%d/%Y','%Y-%m-%d %H:%M:%S.%f',date_from)
            date_to = date_formatter('%m/%d/%Y','%Y-%m-%d %H:%M:%S.%f',date_to)
            query = models.ResolutionModel.objects.all().filter(Q(date_filed__range=(date_from, date_to)), Q(is_delete=False)).order_by('-id') if user.is_overall else models.ResolutionModel.objects.all().filter(Q(date_filed__range=(date_from, date_to)), Q(author=user), Q(is_delete=False)).order_by('-id')

        elif keyword:
            filters = Q(
                Q(id__icontains=keyword) |
                Q(no__icontains=keyword) |
                Q(title__icontains=keyword) |
                Q(author__l_name__icontains=keyword) |
                Q(author__f_name__icontains=keyword) |
                Q(date_filed__icontains=keyword)
                )
            query = models.ResolutionModel.objects.all().filter(filters, Q(is_delete=False)).order_by('-id') if user.is_overall else models.ResolutionModel.objects.all().filter(filters, Q(author=user), Q(is_delete=False)).order_by('-id')

        elif signature:
            if signature == 'Signed Only':
                query = models.ResolutionModel.objects.all().filter(Q(is_signed=True), Q(is_delete=False)).order_by('-id') if user.is_overall else models.ResolutionModel.objects.all().filter(Q(is_signed=True), Q(author=user), Q(is_delete=False)).order_by('-id')
            elif signature == 'Unsigned Only':
                query = models.ResolutionModel.objects.all().filter(Q(is_signed=False), Q(is_delete=False)).order_by('-id') if user.is_overall else models.ResolutionModel.objects.all().filter(Q(is_signed=False), Q(author=user), Q(is_delete=False)).order_by('-id')
            else:
                query = models.ResolutionModel.objects.all().filter(Q(is_delete=False)) if user.is_overall else  models.ResolutionModel.objects.all().filter(Q(author=user),Q(is_delete=False))

        else:
            query = models.ResolutionModel.objects.all().filter(Q(is_delete=False)) if user.is_overall else  models.ResolutionModel.objects.all().filter(Q(author=user), Q(is_delete=False))
        cols = admin.ResolutionAdmin.list_display
        cols = list(cols)
        cols.remove('content')
        cols.remove('hard_copy')
        cols.remove('agenda_fk')
        cols.remove('is_public')
        cols.remove('is_delete')
        cols = [c.replace("_"," ").upper() for c in cols]

    elif database_name == 'Committee Reports (Resolution)':
        if date_from and date_to and keyword and signature:
            date_from = date_formatter('%m/%d/%Y','%Y-%m-%d %H:%M:%S.%f',date_from)
            date_to = date_formatter('%m/%d/%Y','%Y-%m-%d %H:%M:%S.%f',date_to)
            filters = Q(Q(date_filed__range=(date_from, date_to)) &
                        Q(Q(id__icontains=keyword) |
                        Q(no__icontains=keyword) |
                        Q(title__icontains=keyword) |
                        Q(author__l_name__icontains=keyword) |
                        Q(author__f_name__icontains=keyword) |
                        Q(date_filed__icontains=keyword)))
            if signature == 'Signed Only':
                filters = Q(Q(date_filed__range=(date_from, date_to)) &
                            Q(Q(id__icontains=keyword) |
                            Q(no__icontains=keyword) |
                            Q(title__icontains=keyword) |
                            Q(author__l_name__icontains=keyword) |
                            Q(author__f_name__icontains=keyword) |
                            Q(date_filed__icontains=keyword)) &
                            Q(is_signed=True)
                            )
            elif signature == 'Unsigned Only':
                filters = Q(Q(date_filed__range=(date_from, date_to)) &
                            Q(Q(id__icontains=keyword) |
                            Q(no__icontains=keyword) |
                            Q(title__icontains=keyword) |
                            Q(author__l_name__icontains=keyword) |
                            Q(author__f_name__icontains=keyword) |
                            Q(date_filed__icontains=keyword)) &
                            Q(is_signed=False)
                            )
            query = models.CommitteeReportResolutionModel.objects.all().filter(filters, Q(is_delete=False)).order_by('-id') if user.is_overall else models.CommitteeReportResolutionModel.objects.all().filter(filters, Q(author=user), Q(is_delete=False)).order_by('-id')

        elif date_from and date_to:
            date_from = date_formatter('%m/%d/%Y','%Y-%m-%d %H:%M:%S.%f',date_from)
            date_to = date_formatter('%m/%d/%Y','%Y-%m-%d %H:%M:%S.%f',date_to)
            query = models.CommitteeReportResolutionModel.objects.all().filter(Q(date_filed__range=(date_from, date_to)), Q(is_delete=False)).order_by('-id') if user.is_overall else models.CommitteeReportResolutionModel.objects.all().filter(Q(date_filed__range=(date_from, date_to)), Q(author=user), Q(is_delete=False)).order_by('-id')

        elif keyword:
            filters = Q(
                Q(id__icontains=keyword) |
                Q(no__icontains=keyword) |
                Q(title__icontains=keyword) |
                Q(author__l_name__icontains=keyword) |
                Q(author__f_name__icontains=keyword) |
                Q(date_filed__icontains=keyword)
                )
            query = models.CommitteeReportResolutionModel.objects.all().filter(filters, Q(is_delete=False)).order_by('-id') if user.is_overall else models.CommitteeReportResolutionModel.objects.all().filter(filters, Q(author=user), Q(is_delete=False)).order_by('-id')

        elif signature:
            if signature == 'Signed Only':
                query = models.CommitteeReportResolutionModel.objects.all().filter(Q(is_signed=True), Q(is_delete=False)).order_by('-id') if user.is_overall else models.CommitteeReportResolutionModel.objects.all().filter(Q(is_signed=True), Q(author=user), Q(is_delete=False)).order_by('-id')
            elif signature == 'Unsigned Only':
                query = models.CommitteeReportResolutionModel.objects.all().filter(Q(is_signed=False), Q(is_delete=False)).order_by('-id') if user.is_overall else models.CommitteeReportResolutionModel.objects.all().filter(Q(is_signed=False), Q(author=user), Q(is_delete=False)).order_by('-id')
            else:
                query = models.CommitteeReportResolutionModel.objects.all().filter(Q(is_delete=False)) if user.is_overall else models.CommitteeReportResolutionModel.objects.all().filter(Q(author=user), Q(is_delete=False))

        else:
            query = models.CommitteeReportResolutionModel.objects.all().filter(Q(is_delete=False)) if user.is_overall else models.CommitteeReportResolutionModel.objects.all().filter(Q(author=user), Q(is_delete=False))
        cols = admin.CommitteeReportResolutionAdmin.list_display
        cols = list(cols)
        cols.remove('content')
        cols.remove('hard_copy')
        cols.remove('resolution_committee_report_fk')
        cols.remove('is_delete')
        cols = [c.replace("_"," ").upper() for c in cols]

    elif database_name == 'Committee Reports (Ordinance)':

        if date_from and date_to and keyword and signature:
            date_from = date_formatter('%m/%d/%Y','%Y-%m-%d %H:%M:%S.%f',date_from)
            date_to = date_formatter('%m/%d/%Y','%Y-%m-%d %H:%M:%S.%f',date_to)
            filters = Q(Q(date_filed__range=(date_from, date_to)) &
                        Q(Q(id__icontains=keyword) |
                        Q(no__icontains=keyword) |
                        Q(title__icontains=keyword) |
                        Q(author__l_name__icontains=keyword) |
                        Q(author__f_name__icontains=keyword) |
                        Q(date_filed__icontains=keyword)))
            if signature == 'Signed Only':
                filters = Q(Q(date_filed__range=(date_from, date_to)) &
                            Q(Q(id__icontains=keyword) |
                            Q(no__icontains=keyword) |
                            Q(title__icontains=keyword) |
                            Q(author__l_name__icontains=keyword) |
                            Q(author__f_name__icontains=keyword) |
                            Q(date_filed__icontains=keyword)) &
                            Q(is_signed=True)
                            )
            elif signature == 'Unsigned Only':
                filters = Q(Q(date_filed__range=(date_from, date_to)) &
                            Q(Q(id__icontains=keyword) |
                            Q(no__icontains=keyword) |
                            Q(title__icontains=keyword) |
                            Q(author__l_name__icontains=keyword) |
                            Q(author__f_name__icontains=keyword) |
                            Q(date_filed__icontains=keyword)) &
                            Q(is_signed=False)
                            )
            query = models.CommitteeReportOrdinanceModel.objects.all().filter(filters, Q(is_delete=False)).order_by('-id') if user.is_overall else models.CommitteeReportOrdinanceModel.objects.all().filter(filters, Q(author=user), Q(is_delete=False)).order_by('-id')

        elif date_from and date_to:
            date_from = date_formatter('%m/%d/%Y','%Y-%m-%d %H:%M:%S.%f',date_from)
            date_to = date_formatter('%m/%d/%Y','%Y-%m-%d %H:%M:%S.%f',date_to)
            query = models.CommitteeReportOrdinanceModel.objects.all().filter(Q(date_filed__range=(date_from, date_to)), Q(is_delete=False)).order_by('-id') if user.is_overall else models.CommitteeReportOrdinanceModel.objects.all().filter(Q(date_filed__range=(date_from, date_to)), Q(author=user), Q(is_delete=False)).order_by('-id')

        elif keyword:
            filters = Q(
                Q(id__icontains=keyword) |
                Q(no__icontains=keyword) |
                Q(title__icontains=keyword) |
                Q(author__l_name__icontains=keyword) |
                Q(author__f_name__icontains=keyword) |
                Q(date_filed__icontains=keyword)
                )
            query = models.CommitteeReportOrdinanceModel.objects.all().filter(filters, Q(is_delete=False)).order_by('-id') if user.is_overall else models.CommitteeReportOrdinanceModel.objects.all().filter(filters, Q(author=user), Q(is_delete=False)).order_by('-id')

        elif signature:
            if signature == 'Signed Only':
                query = models.CommitteeReportOrdinanceModel.objects.all().filter(Q(is_signed=True), Q(is_delete=False)).order_by('-id') if user.is_overall else models.CommitteeReportOrdinanceModel.objects.all().filter(Q(is_signed=True), Q(author=user), Q(is_delete=False)).order_by('-id')
            elif signature == 'Unsigned Only':
                query = models.CommitteeReportOrdinanceModel.objects.all().filter(Q(is_signed=False), Q(is_delete=False)).order_by('-id') if user.is_overall else models.CommitteeReportOrdinanceModel.objects.all().filter(Q(is_signed=False), Q(author=user), Q(is_delete=False)).order_by('-id')
            else:
                query = models.CommitteeReportOrdinanceModel.objects.all().filter(Q(is_delete=False)) if user.is_overall else models.CommitteeReportOrdinanceModel.objects.all().filter(Q(author=user), Q(is_delete=False))

        else:
            query = models.CommitteeReportOrdinanceModel.objects.all().filter(Q(is_delete=False)) if user.is_overall else models.CommitteeReportOrdinanceModel.objects.all().filter(Q(author=user), Q(is_delete=False))
        cols = admin.CommitteeReportOrdinanceAdmin.list_display
        cols = list(cols)
        cols.remove('content')
        cols.remove('hard_copy')
        cols.remove('ordinance_committee_report_fk')
        cols.remove('is_delete')
        cols = [c.replace("_"," ").upper() for c in cols]

    elif database_name == 'Minutes of the meeting':

        if date_from and date_to and keyword and signature:
            date_from = date_formatter('%m/%d/%Y','%Y-%m-%d %H:%M:%S.%f',date_from)
            date_to = date_formatter('%m/%d/%Y','%Y-%m-%d %H:%M:%S.%f',date_to)
            filters = Q(Q(date_filed__range=(date_from, date_to)) &
                        Q(Q(id__icontains=keyword) |
                        Q(no__icontains=keyword) |
                        Q(title__icontains=keyword) |
                        Q(author__l_name__icontains=keyword) |
                        Q(author__f_name__icontains=keyword) |
                        Q(date_filed__icontains=keyword)))
            if signature == 'Signed Only':
                filters = Q(Q(date_filed__range=(date_from, date_to)) &
                            Q(Q(id__icontains=keyword) |
                            Q(no__icontains=keyword) |
                            Q(title__icontains=keyword) |
                            Q(author__l_name__icontains=keyword) |
                            Q(author__f_name__icontains=keyword) |
                            Q(date_filed__icontains=keyword)) &
                            Q(is_signed=True)
                            )
            elif signature == 'Unsigned Only':
                filters = Q(Q(date_filed__range=(date_from, date_to)) &
                            Q(Q(id__icontains=keyword) |
                            Q(no__icontains=keyword) |
                            Q(title__icontains=keyword) |
                            Q(author__l_name__icontains=keyword) |
                            Q(author__f_name__icontains=keyword) |
                            Q(date_filed__icontains=keyword)) &
                            Q(is_signed=False)
                            )
            query = models.MOMModel.objects.all().filter(filters, Q(is_delete=False)).order_by('-id') if user.is_overall else models.MOMModel.objects.all().filter(filters, Q(author=user), Q(is_delete=False)).order_by('-id')

        elif date_from and date_to:
            date_from = date_formatter('%m/%d/%Y','%Y-%m-%d %H:%M:%S.%f',date_from)
            date_to = date_formatter('%m/%d/%Y','%Y-%m-%d %H:%M:%S.%f',date_to)
            query = models.MOMModel.objects.all().filter(Q(date_filed__range=(date_from, date_to)), Q(is_delete=False)).order_by('-id') if user.is_overall else models.MOMModel.objects.all().filter(Q(date_filed__range=(date_from, date_to)), Q(author=user), Q(is_delete=False)).order_by('-id')

        elif keyword:
            filters = Q(
                Q(id__icontains=keyword) |
                Q(no__icontains=keyword) |
                Q(title__icontains=keyword) |
                Q(author__l_name__icontains=keyword) |
                Q(author__f_name__icontains=keyword) |
                Q(date_filed__icontains=keyword)
                )
            query = models.MOMModel.objects.all().filter(filters, Q(is_delete=False)).order_by('-id') if user.is_overall else models.MOMModel.objects.all().filter(filters, Q(author=user), Q(is_delete=False)).order_by('-id')

        elif signature:
            if signature == 'Signed Only':
                query = models.MOMModel.objects.all().filter(Q(is_signed=True), Q(is_delete=False)).order_by('-id') if user.is_overall else models.MOMModel.objects.all().filter(Q(is_signed=True), Q(author=user), Q(is_delete=False)).order_by('-id')
            elif signature == 'Unsigned Only':
                query = models.MOMModel.objects.all().filter(Q(is_signed=False), Q(is_delete=False)).order_by('-id') if user.is_overall else models.MOMModel.objects.all().filter(Q(is_signed=False), Q(author=user), Q(is_delete=False)).order_by('-id')
            else:
                query = models.MOMModel.objects.all().filter(Q(is_delete=False)) if user.is_overall else models.MOMModel.objects.all().filter(Q(author=user), Q(is_delete=False))

        else:
            query = models.MOMModel.objects.all().filter(Q(is_delete=False)) if user.is_overall else models.MOMModel.objects.all().filter(Q(author=user), Q(is_delete=False))
        cols = admin.MOMAdmin.list_display
        cols = list(cols)
        cols.remove('content')
        cols.remove('hard_copy')
        cols.remove('is_delete')
        cols = [c.replace("_"," ").upper() for c in cols]

    return query, cols

@login_required
@roles(is_records_manager=True)
@authorize
@get_notification
def records(request, *args, **kwargs):
    template_name = "elegislative/records/records.html"
    user = get_object_or_404(models.User, email=request.user.email)

    if request.method == 'GET':
        database_selection = request.GET.get('database_seletection')
        report_title = request.GET.get('report_title')
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        query_keyword = request.GET.get('query_keyword')
        header = request.GET.get('header')
        signature = request.GET.get('signed_document')
        query, cols = report_generator(database_selection, date_from, date_to, query_keyword, signature, user)

    context = {
        'user': user,
        'query': query,
        'cols': cols,
        'notifications':kwargs['notifications'],
    }
    return render(request, template_name, context)

@login_required
@roles(is_records_manager=True)
@authorize
def print_records(request):
    template_name = "elegislative/records/print_records.html"
    user = get_object_or_404(models.User, email=request.user.email)
    if request.method == 'GET':
        database_selection = request.GET.get('database_seletection')
        report_title = request.GET.get('report_title')
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        query_keyword = request.GET.get('query_keyword')
        header = request.GET.get('header')
        signature = request.GET.get('signed_document')
        query, cols = report_generator(database_selection, date_from, date_to, query_keyword, signature, user)

    date_today = datetime.now()
    date_today = date_today.strftime('%m/%d/%Y')
    context = {
        'user': user,
        'query': query,
        'cols': cols,
        'date_today': date_today,
    }
    return render(request, template_name, context)
"""
[END] -> Manage Records
"""

"""
[START] -> Manage Minutes of the meeting features
"""

@login_required
@roles(is_mom_manager=True)
@authorize
@get_notification
def minutes_of_the_meeting(request, *args, **kwargs):
    template_name = "elegislative/minutes_of_the_meeting/minutes_of_the_meeting.html"
    user = get_object_or_404(models.User, email=request.user.email)
    mom = models.MOMModel.objects.all().filter(Q(is_delete=False)) if user.is_overall else models.MOMModel.objects.all().filter(Q(author=user), Q(is_delete=False))
    context = {
        'user': user,
        'mom': mom,
        'notifications':kwargs['notifications'],
    }
    return render(request, template_name, context)

@login_required
@roles(is_mom_manager=True)
@authorize
@get_notification
def create_minutes_of_the_meeting(request, *args, **kwargs):
    template_name = "elegislative/minutes_of_the_meeting/create_minutes_of_the_meeting.html"
    user = get_object_or_404(models.User, email=request.user.email)

    if user.is_view_mode:
        raise Http404()

    if request.method == 'GET':
        form = forms.MOMForm(request.GET or None)
    elif request.method == 'POST':
        form = forms.MOMForm(request.POST or None)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.author = user
            instance.save()
            add_notification(request,'elegislative:minutes_of_the_meeting', f"MoM ({instance.no}) has been created!", settings.NOTIFICATION_TAGS[4][0])
            return HttpResponseRedirect(reverse_lazy("elegislative:minutes_of_the_meeting"))

    context = {
        'user': user,
        'form': form,
        'notifications':kwargs['notifications'],
    }
    return render(request, template_name, context)

@login_required
@roles(is_mom_manager=True)
@authorize
@get_notification
def edit_minutes_of_the_meeting(request, *args, **kwargs):
    template_name = "elegislative/minutes_of_the_meeting/edit_minutes_of_the_meeting.html"
    user = get_object_or_404(models.User, email=request.user.email)
    mom = get_object_or_404(models.MOMModel, Q(is_delete=False), id=kwargs['id']) if user.is_overall else get_object_or_404(models.MOMModel, Q(author=user), Q(is_delete=False), id=kwargs['id'])

    if user.is_view_mode:
        raise Http404()

    if request.method == 'GET':
        form = forms.EditMOMForm(request.GET or None, instance=mom)
    elif request.method == 'POST':
        form = forms.EditMOMForm(request.POST or None, request.FILES, instance=mom)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.author = user
            instance.save()
            return HttpResponseRedirect(reverse_lazy("elegislative:minutes_of_the_meeting"))

    context = {
        'user': user,
        'form': form,
        'mom': mom,
        'notifications':kwargs['notifications'],
    }
    return render(request, template_name, context)

@login_required
@roles(is_mom_manager=True)
@authorize
def delete_minutes_of_the_meeting(request, id):
    data = dict()
    template_name = "elegislative/minutes_of_the_meeting/delete_minutes_of_the_meeting.html"
    user = get_object_or_404(models.User, email=request.user.email)
    mom = get_object_or_404(models.MOMModel, Q(is_delete=False), id=id) if user.is_overall else get_object_or_404(models.MOMModel, Q(author=user), Q(is_delete=False), id=id)

    if user.is_view_mode:
        raise Http404()
    if request.is_ajax():
        if request.method == 'GET':
            context = {
                'mom': mom,
            }
            data['html_form'] = render_to_string(template_name, context, request)
        elif request.method == 'POST':
            data['form_is_valid'] = True
            mom.is_delete = True
            mom.save()
            # mom.delete()

        return JsonResponse(data)
    else:
        raise Http404()

@login_required
@roles(is_mom_manager=True)
@authorize
def print_minutes_of_the_meeting(request, id):
    template_name = "elegislative/minutes_of_the_meeting/print_minutes_of_the_meeting.html"
    user = get_object_or_404(models.User, email=request.user.email)
    mom = get_object_or_404(models.MOMModel, Q(is_delete=False), id=id)
    context = {
        'user': user,
        'mom':mom,
    }
    return render(request, template_name, context)
"""
[END] -> Manage Minutes of the meeting features
"""

"""
[START] -> Manage announcement features
"""
@login_required
@roles(is_announcement_manager=True)
@authorize
@get_notification
def announcements(request, *args, **kwargs):
    template_name = "elegislative/announcements/announcements.html"
    user = get_object_or_404(models.User, email=request.user.email)
    announcements = models.AnnouncementModel.objects.all() if user.is_overall else models.AnnouncementModel.objects.all().filter(Q(author=user))
    context = {
        'user': user,
        'announcements': announcements,
        'notifications':kwargs['notifications'],
    }
    return render(request, template_name, context)

@login_required
@roles(is_announcement_manager=True)
@authorize
def create_announcements(request):
    data = dict()
    template_name = "elegislative/announcements/create_announcement.html"
    user = get_object_or_404(models.User, email=request.user.email)

    if user.is_view_mode:
        raise Http404()

    if request.is_ajax():
        if request.method == 'GET':
            form = forms.AnnouncementForm(request.GET or None)
        elif request.method == 'POST':
            form = forms.AnnouncementForm(request.POST or None)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.author = user
                instance.save()
                a_response = {
                    'aid': instance.id,
                    'title' : instance.title,
                    'subject' : instance.subject,
                    'content' : instance.content,
                    'visible' : instance.visible,
                    'author': f'{instance.author.f_name} {instance.author.l_name}',
                    'date_filed' : instance.date_filed.strftime("%b. %d, %Y, %I:%M %p"),
                    'edit_url': reverse_lazy('elegislative:edit_announcements', kwargs={'id':instance.id}),
                    'delete_url':reverse_lazy('elegislative:delete_announcements', kwargs={'id':instance.id}),
                }
                data['a_response'] = a_response
                data['form_is_valid'] = True
                add_notification(request,'elegislative:announcements', f"Anno. ({instance.title}) has been created!", settings.NOTIFICATION_TAGS[9][0])
        context = {
            'user': user,
            'form': form,
        }
        data['html_form'] = render_to_string(template_name, context, request)
        return JsonResponse(data)
    else:
        raise Http404()

@login_required
@roles(is_announcement_manager=True)
@authorize
def edit_announcements(request, id):
    data = dict()
    template_name = "elegislative/announcements/edit_announcement.html"
    user = get_object_or_404(models.User, email=request.user.email)
    announcement = get_object_or_404(models.AnnouncementModel, id=id) if user.is_overall else get_object_or_404(models.AnnouncementModel, Q(author=user), id=id)

    if user.is_view_mode:
        raise Http404()

    if request.is_ajax():
        if request.method == 'GET':
            form = forms.AnnouncementForm(request.GET or None, instance=announcement)
        elif request.method == 'POST':
            form = forms.AnnouncementForm(request.POST or None, instance=announcement)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.author = user
                instance.save()
                a_response = {
                    'title' : instance.title,
                    'subject' : instance.subject,
                    'content' : instance.content,
                    'author' : f'{instance.author.f_name} {instance.author.l_name}',
                    'visible' : instance.visible
                }
                data['a_response'] = a_response
                data['form_is_valid'] = True

        context = {
            'user': user,
            'form': form,
            'announcement': announcement,
        }
        data['html_form'] = render_to_string(template_name, context, request)
        return JsonResponse(data)
    else:
        raise Http404()

@login_required
@roles(is_announcement_manager=True)
@authorize
def delete_announcements(request, id):
    data = dict()
    template_name = "elegislative/announcements/delete_announcement.html"
    user = get_object_or_404(models.User, email=request.user.email)
    announcement = get_object_or_404(models.AnnouncementModel, id=id) if user.is_overall else get_object_or_404(models.AnnouncementModel, Q(author=user), id=id)

    if user.is_view_mode:
        raise Http404()

    if request.is_ajax():
        if request.method == 'GET':
            context = {
                'user': user,
                'announcement': announcement,
            }
            data['html_form'] = render_to_string(template_name, context, request)
        elif request.method == 'POST':
            announcement.delete()
            data['form_is_valid'] = True

        return JsonResponse(data)
    else:
        raise Http404()

"""
[END] -> Manage announcement features
"""

"""
[START] -> Messages features
"""
@login_required
@authorize
@get_notification
def messages_manager(request, *args, **kwargs):
    template_name = "elegislative/messages/messages.html"
    user = get_object_or_404(models.User, email=request.user.email)
    unread_messages_count = models.MessagesModel.objects.all().filter(Q(receiver=user),Q(is_read=False)).count()
    inbox = models.MessagesModel.objects.all().filter(Q(receiver=user))
    sent_messages = models.SentMessagesModel.objects.all().filter(Q(sender=user))
    context = {
        'user': user,
        'inbox': inbox,
        'unread_messages_count': unread_messages_count,
        'sent_messages': sent_messages,
        'notifications':kwargs['notifications'],
    }
    return render(request, template_name, context)


@login_required
@authorize
@get_notification
def create_message(request, *args, **kwargs):
    template_name = "elegislative/messages/create_message.html"
    user = get_object_or_404(models.User, email=request.user.email)
    unread_messages_count = models.MessagesModel.objects.all().filter(Q(receiver=user),Q(is_read=False)).count()
    reciepients = models.User.objects.all().filter(~Q(email=user),Q(is_active=True))
    sent_messages = models.SentMessagesModel.objects.all().filter(Q(sender=user))
    if request.method == 'GET':
        form = forms.MessageForm(request.GET or None)
    elif request.method == 'POST':
        form = forms.MessageForm(request.POST or None)
        if form.is_valid():
            receivers = request.POST.getlist("receivers", False)
            for r in receivers:
                receiver = get_object_or_404(models.User, email=r)
                content = form.cleaned_data.get("content")
                subject = form.cleaned_data.get("subject")
                models.MessagesModel.objects.create(
                    sender=user,
                    receiver=receiver,
                    subject=subject,
                    content=content,
                )
                models.SentMessagesModel.objects.create(
                    sender=user,
                    receiver=receiver,
                    subject=subject,
                    content=content,
                )
            return HttpResponseRedirect(reverse_lazy("elegislative:messages"))

    context = {
        'user': user,
        'form': form,
        'reciepients': reciepients,
        'unread_messages_count': unread_messages_count,
        'notifications':kwargs['notifications'],
        'sent_messages': sent_messages,
    }
    return render(request, template_name, context)


@login_required
@authorize
@get_notification
def view_message(request, *args, **kwargs):
    template_name = "elegislative/messages/view_message.html"
    user = get_object_or_404(models.User, email=request.user.email)
    sent_messages = models.SentMessagesModel.objects.all().filter(Q(sender=user))
    message = get_object_or_404(models.MessagesModel, Q(receiver=user), id=kwargs['id'])
    message.is_read = True
    message.save()
    unread_messages_count = models.MessagesModel.objects.all().filter(Q(receiver=user),Q(is_read=False)).count()
    context = {
        'message': message,
        'user': user,
        'unread_messages_count': unread_messages_count,
        'notifications':kwargs['notifications'],
        'sent_messages': sent_messages,
    }
    return render(request, template_name, context)


@login_required
@authorize
def delete_messages(request, *args, **kwargs):
    data = dict()
    template_name = "elegislative/messages/delete_message.html"
    user = get_object_or_404(models.User, email=request.user.email)
    if request.is_ajax():
        if request.method == 'GET':
            context = {
                'user': user,
            }
            data['html_form'] = render_to_string(template_name, context, request)
        elif request.method == 'POST':
            json_request = json.loads(request.body)
            id_list = json_request["id_list"]
            for item in id_list:
                message = get_object_or_404(models.MessagesModel, Q(receive=user),id=int(item))
                message.delete()
            data['status'] = True

        return JsonResponse(data)
    else:
        raise Http404()


@login_required
@authorize
@get_notification
def sent_messages(request, *args, **kwargs):
    template_name = "elegislative/messages/sent_messages.html"
    user = get_object_or_404(models.User, email=request.user.email)
    unread_messages_count = models.MessagesModel.objects.all().filter(Q(receiver=user),Q(is_read=False)).count()
    sent_messages = models.SentMessagesModel.objects.all().filter(Q(sender=user))
    context = {
        'user': user,
        'unread_messages_count': unread_messages_count,
        'sent_messages': sent_messages,
        'notifications':kwargs['notifications'],
    }
    return render(request, template_name, context)


@login_required
@authorize
@get_notification
def view_sent_messages(request, *args, **kwargs):
    template_name = "elegislative/messages/view_sent_messaage.html"
    user = get_object_or_404(models.User, email=request.user.email)
    unread_messages_count = models.MessagesModel.objects.all().filter(Q(receiver=user),Q(is_read=False)).count()
    sent_messages = models.SentMessagesModel.objects.all().filter(Q(sender=user))
    message = get_object_or_404(models.SentMessagesModel, Q(sender=user), id=kwargs['id'])
    context = {
        'user': user,
        'unread_messages_count': unread_messages_count,
        'sent_messages': sent_messages,
        'message': message,
        'notifications':kwargs['notifications'],
    }
    return render(request, template_name, context)


@login_required
@authorize
def delete_sent_messages(request, *args, **kwargs):
    data = dict()
    template_name = "elegislative/messages/delete_sent_message.html"
    user = get_object_or_404(models.User, email=request.user.email)
    if request.is_ajax():
        if request.method == 'GET':
            context = {
                'user': user,
            }
            data['html_form'] = render_to_string(template_name, context, request)
        elif request.method == 'POST':
            json_request = json.loads(request.body)
            id_list = json_request["id_list"]
            for item in id_list:
                message = get_object_or_404(models.SentMessagesModel, Q(sender=user), id=int(item))
                message.delete()
            data['status'] = True

        return JsonResponse(data)
    else:
        raise Http404()
"""
[END] -> Messages features
"""

"""
[START] -> OLD DOCUMENTS features
"""
@login_required
@roles(is_old_documents_manager=True)
@authorize
@get_notification
def old_documents(request, *args, **kwargs):
    template_name = "elegislative/old_documents/old_documents.html"
    user = get_object_or_404(models.User, email=request.user.email)

    old_documents = models.OldDocumentsModel.objects.all()

    context = {
        'user': user,
        'old_documents': old_documents,
        'notifications':kwargs['notifications'],
    }
    return render(request, template_name, context)

@login_required
@roles(is_old_documents_manager=True)
@authorize
@get_notification
def upload_old_documents(request, *args, **kwargs):
    template_name = "elegislative/old_documents/upload_documents.html"
    user = get_object_or_404(models.User, email=request.user.email)

    if request.method == 'GET':
        pass
    elif request.method == 'POST':

        f = request.FILES['file']
        fname = f.name # Gives name
        fcontent_type = f.content_type # Gives Content type text/html etc
        fsize = f.size # Gives file's size in byte
        kb = f.size * 0.001 # kb
        mb = kb * 0.001 # ml
        # f.read() # Reads file
        data = request.POST.get('data', False)
        data = json.loads(data)
        year = data['year']
        remarks = data['remarks']

        old_document = models.OldDocumentsModel(files=f,name=fname,size=fsize,content_type=fcontent_type,year=year,remarks=remarks)
        old_document.save()
        f.close()

    context = {
        'user': user,
        'notifications':kwargs['notifications'],
    }
    return render(request, template_name, context)

@login_required
@roles(is_old_documents_manager=True)
@authorize
@get_notification
def delete_old_documents(request, *args, **kwargs):
    data = dict()
    template_name = "elegislative/old_documents/delete_documents.html"
    user = get_object_or_404(models.User, email=request.user.email)
    if request.is_ajax():
        if request.method == 'GET':
            context = {
                'user': user,
            }
            data['html_form'] = render_to_string(template_name, context, request)
        elif request.method == 'POST':
            json_request = json.loads(request.body)
            id_list = json_request["id_list"]
            for item in id_list:
                old_document = get_object_or_404(models.OldDocumentsModel,  id=int(item))
                old_document.delete()
            data['status'] = True

        return JsonResponse(data)
    else:
        raise Http404()

"""
[END] -> OLD DOCUMENTS features
"""


"""
[START] -> WebEx features
"""
@login_required
@roles(is_webex_manager=True)
@authorize
@get_notification
def webex(request, *args, **kwargs):
    template_name = "elegislative/webex/webex.html"
    user = get_object_or_404(models.User, email=request.user.email)
    webex = models.WebExModel.objects.all() if user.is_overall else models.WebExModel.objects.all().filter(Q(author=user))
    context = {
        'user': user,
        'webex': webex,
        'notifications':kwargs['notifications'],
    }
    return render(request, template_name, context)


@login_required
@roles(is_webex_manager=True)
@authorize
@get_notification
def add_webex_link(request, *args, **kwargs):
    data = dict()
    template_name = "elegislative/webex/add_webex_link.html"
    user = get_object_or_404(models.User, email=request.user.email)
    if request.is_ajax():
        if request.method == 'GET':
            form = forms.WebExForm(request.GET or None)
            context = {
                'user': user,
                'form': form,
            }
            data['html_form'] = render_to_string(template_name, context, request)
        elif request.method == 'POST':
            form = forms.WebExForm(request.POST or None)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.author = user
                instance.save()
                webex = {
                    'id': instance.id,
                    'url': instance.url,
                    'display_text': instance.display_text,
                    'protocol': instance.protcol,
                    'remarks': instance.remarks,
                    'author': f'{instance.author.f_name} {instance.author.l_name}',
                    'date_filed': str(instance.date_filed.strftime("%b. %d, %Y, %I:%M %p")),
                    'eurl': str(reverse_lazy('elegislative:edit_webex_link', kwargs={'id':instance.id})),
                    'durl': str(reverse_lazy('elegislative:delete_webex_link', kwargs={'id':instance.id})),
                }
                webex = json.dumps(webex)
                data['webex'] = json.loads(webex)
                data['form_is_valid'] = True

        return JsonResponse(data)
    else:
        raise Http404()


@login_required
@roles(is_webex_manager=True)
@authorize
@get_notification
def edit_webex_link(request, *args, **kwargs):
    data = dict()
    template_name = "elegislative/webex/edit_webex_link.html"
    user = get_object_or_404(models.User, email=request.user.email)
    webex_link = get_object_or_404(models.WebExModel, id=kwargs['id']) if user.is_overall else get_object_or_404(models.WebExModel, Q(author=user), id=kwargs['id'])
    if request.is_ajax():
        if request.method == 'GET':
            form = forms.WebExForm(request.GET or None, instance=webex_link)
            context = {
                'user': user,
                'webex_link': webex_link,
                'form': form,
            }
            data['html_form'] = render_to_string(template_name, context, request)
        elif request.method == 'POST':
            form = forms.WebExForm(request.POST or None, instance=webex_link)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.save()
                webex = {
                    'url': instance.url,
                    'display_text': instance.display_text,
                    'protocol': instance.protcol,
                    'remarks': instance.remarks,
                    'author': f'{instance.author.f_name} {instance.author.l_name}',
                }
                webex = json.dumps(webex)
                data['webex'] = json.loads(webex)
                data['form_is_valid'] = True

        return JsonResponse(data)
    else:
        raise Http404()

@login_required
@roles(is_webex_manager=True)
@authorize
@get_notification
def delete_webex_link(request, *args, **kwargs):
    data = dict()
    template_name = "elegislative/webex/delete_webex_link.html"
    user = get_object_or_404(models.User, email=request.user.email)
    webex_link = get_object_or_404(models.WebExModel, id=kwargs['id']) if user.is_overall else get_object_or_404(models.WebExModel, Q(author=user), id=kwargs['id'])
    if request.is_ajax():
        if request.method == 'GET':
            context = {
                'user': user,
                'webex_link': webex_link,
            }
            data['html_form'] = render_to_string(template_name, context, request)
        elif request.method == 'POST':
            webex_link.delete()
            data['form_is_valid'] = True

        return JsonResponse(data)
    else:
        raise Http404()

"""
[END] -> WebEx features
"""

"""
[START] -> Trash features
"""
@login_required
@authorize
@get_notification
def trash(request, *args, **kwargs):
    template_name = "elegislative/trash/trash.html"
    user = get_object_or_404(models.User, email=request.user.email)

    model_list = [
        models.AgendaModel,
        models.ResolutionModel,
        models.CommitteeReportResolutionModel,
        # models.CommentsRecomendationResolutionModel,
        models.OrdinanceModel,
        models.CommitteeReportOrdinanceModel,
        # models.CommentsRecomendationOrdinanceModel,
        models.MOMModel,
    ]
    queryset = [query.objects.all().filter(Q(is_delete=True)) for query in model_list]

    context = {
        'user': user,
        'notifications':kwargs['notifications'],
        'queryset': queryset,
    }
    return render(request, template_name, context)


@login_required
@authorize
def trash_delete(request, *args, **kwargs):
    data = dict()
    template_name = "elegislative/trash/trash_delete.html"
    user = get_object_or_404(models.User, email=request.user.email)

    model_dictionary = {
        "AgendaModel": models.AgendaModel,
        "ResolutionModel": models.ResolutionModel,
        "CommitteeReportResolutionModel": models.CommitteeReportResolutionModel,
        "OrdinanceModel": models.OrdinanceModel,
        "CommitteeReportOrdinanceModel": models.CommitteeReportOrdinanceModel,
        "MOMModel": models.MOMModel,
    }
    if request.is_ajax():
        if request.method == 'GET':
            context = {
                'user': user,
            }
            data['html_form'] = render_to_string(template_name, context, request)
        elif request.method == 'POST':
            json_request = json.loads(request.body)
            container = json_request["container"]
            for array in container:
                table = array[0]
                uid = array[1]
                record = get_object_or_404(model_dictionary[table], Q(is_delete=True), id=uid) if user.is_overall else get_object_or_404(model_dictionary[table], Q(is_delete=True), Q(author=user), id=uid)
                record.delete()
            data['status'] = True

        return JsonResponse(data)
    else:
        raise Http404()

@login_required
@authorize
def restore_deleted(request, *args, **kwargs):
    data = dict()
    template_name = "elegislative/trash/trash_restore.html"
    user = get_object_or_404(models.User, email=request.user.email)

    model_dictionary = {
        "AgendaModel": models.AgendaModel,
        "ResolutionModel": models.ResolutionModel,
        "CommitteeReportResolutionModel": models.CommitteeReportResolutionModel,
        "OrdinanceModel": models.OrdinanceModel,
        "CommitteeReportOrdinanceModel": models.CommitteeReportOrdinanceModel,
        "MOMModel": models.MOMModel,
    }
    if request.is_ajax():
        if request.method == 'GET':
            context = {
                'user': user,
            }
            data['html_form'] = render_to_string(template_name, context, request)
        elif request.method == 'POST':
            json_request = json.loads(request.body)
            container = json_request["container"]
            for array in container:
                table = array[0]
                uid = array[1]
                record = get_object_or_404(model_dictionary[table], Q(is_delete=True), id=uid) if user.is_overall else get_object_or_404(model_dictionary[table], Q(is_delete=True), Q(author=user), id=uid)
                record.is_delete = False
                record.save()
            data['status'] = True

        return JsonResponse(data)
    else:
        raise Http404()
"""
[END] -> Trash features
"""
