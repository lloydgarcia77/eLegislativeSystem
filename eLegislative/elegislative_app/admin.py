from django.contrib import admin
from elegislative_app import models
<<<<<<< HEAD
from import_export.admin import ImportExportModelAdmin

=======
from import_export.admin import ImportExportModelAdmin  
from django.contrib.auth.admin import UserAdmin
from django import forms
>>>>>>> a0f404c1f3694bd7b35a48cf87e9173805dc872d
admin.site.site_header = 'e-Legislative Super Administrator'
admin.site.index_title = 'Super Administrator Page'
admin.site.site_title = 'Super Administrator Panel'
admin.site.site_url = "/elegislative/dashboard/"
<<<<<<< HEAD

=======
<<<<<<< HEAD
  
# Custom user model and admin
=======
 # Custom user model and admin
>>>>>>> 07d2935e7c82f6a4bd47cbec067c196153d0b170
# https://docs.djangoproject.com/en/3.0/topics/auth/customizing/#custom-users-admin-full-example
# Change password
# https://docs.djangoproject.com/en/3.1/topics/auth/default/
 
>>>>>>> a0f404c1f3694bd7b35a48cf87e9173805dc872d
admin.site.register(models.User)

# class CustomUserAdmin(UserAdmin, ImportExportModelAdmin):
#     # as an example, this custom user admin orders users by email address
#     ordering = ('email',)
#     list_display = ("id","password","key_id","email","image","f_name","m_name","l_name","gender","dob","age","address", "title", "date_added")
#     add_fieldsets = ()
# # admin.site.unregister(models.User)
# admin.site.register(models.User, CustomUserAdmin)

<<<<<<< HEAD
=======

>>>>>>> 07d2935e7c82f6a4bd47cbec067c196153d0b170

class AgendaAdmin(ImportExportModelAdmin):
    list_display = ("id","no","title","version","author","is_delete","status","is_signed","hard_copy","content","date_filed")
    list_editable = ("no","title","version","author","is_delete","status","is_signed","hard_copy","content",)
    list_per_page = 10
    search_fields = ("id","no","title",)
    list_filter = ("author","status","is_signed",)


admin.site.register(models.AgendaModel, AgendaAdmin)

class ResolutionAdmin(ImportExportModelAdmin):
    list_display = ("id","agenda_fk","no","title","version","author","is_delete","status","is_signed","is_public","hard_copy","content","date_filed")
    list_editable = ("no","agenda_fk","title","version","author","is_delete","status","is_signed","is_public","hard_copy","content",)
    list_per_page = 10
    search_fields = ("id","no","title",)
    list_filter = ("author","status","is_signed",)

admin.site.register(models.ResolutionModel, ResolutionAdmin)

class CommitteeReportResolutionAdmin(ImportExportModelAdmin):
    list_display = ("id","resolution_committee_report_fk","no","title","version","author","is_delete","status","is_signed","hard_copy","content","date_filed")
    list_editable = ("no","resolution_committee_report_fk","title","version","author","is_delete","status","is_signed","hard_copy","content",)
    list_per_page = 10
    search_fields = ("id","no","title",)
    list_filter = ("author","status","is_signed",)

admin.site.register(models.CommitteeReportResolutionModel, CommitteeReportResolutionAdmin)

class CommentsRecomendationResolutionAdmin(ImportExportModelAdmin):
    list_display = ("id","resolution_comments_recommendation_fk","commentor_resolution","message","date_filed")
    list_editable = ("resolution_comments_recommendation_fk","commentor_resolution","message",)
    list_per_page = 10
    search_fields = ("id","commentor_resolution","message","date_filed",)
    list_filter = ("commentor_resolution",)

admin.site.register(models.CommentsRecomendationResolutionModel, CommentsRecomendationResolutionAdmin)


class OrdinanceAdmin(ImportExportModelAdmin):
    list_display = ("id","agenda_fk","no","title","version","author","is_delete","status","is_signed","is_public","hard_copy","content","date_filed")
    list_editable = ("no","agenda_fk","title","version","author","is_delete","status","is_signed","is_public","hard_copy","content",)
    list_per_page = 10
    search_fields = ("id","no","title",)
    list_filter = ("author","status","is_signed",)

admin.site.register(models.OrdinanceModel, OrdinanceAdmin)

class CommitteeReportOrdinanceAdmin(ImportExportModelAdmin):
    list_display = ("id","ordinance_committee_report_fk","no","title","version","author","is_delete","status","is_signed","hard_copy","content","date_filed")
    list_editable = ("no","ordinance_committee_report_fk","title","version","author","is_delete","status","is_signed","hard_copy","content",)
    list_per_page = 10
    search_fields = ("id","no","title",)
    list_filter = ("author","status","is_signed",)

admin.site.register(models.CommitteeReportOrdinanceModel, CommitteeReportOrdinanceAdmin)


class CommentsRecomendationOrdinanceAdmin(ImportExportModelAdmin):
    list_display = ("id","ordinance_comments_recomendation_fk","commentor_ordiance","message","date_filed")
    list_editable = ("ordinance_comments_recomendation_fk","commentor_ordiance","message",)
    list_per_page = 10
    search_fields = ("id","commentor_ordiance","message","date_filed",)
    list_filter = ("commentor_ordiance",)

admin.site.register(models.CommentsRecomendationOrdinanceModel, CommentsRecomendationOrdinanceAdmin)



class MOMAdmin(ImportExportModelAdmin):
    list_display = ("id","no","title","version","author","is_delete","status","is_signed","hard_copy","content","date_filed")
    list_editable = ("no","title","version","author","is_delete","status","is_signed","hard_copy","content",)
    list_per_page = 10
    search_fields = ("id","no","title",)
    list_filter = ("author","status","is_signed",)


admin.site.register(models.MOMModel, MOMAdmin)

class AnnouncementAdmin(ImportExportModelAdmin):
    list_display = ("id","title","subject","author","content","date_filed")
    list_editable = ("title","subject","author","content",)
    list_per_page = 10
    search_fields = ("id","title","subject","content","date_filed",)
    list_filter = ("date_filed",)


admin.site.register(models.AnnouncementModel, AnnouncementAdmin)

class NotificationsAdmin(ImportExportModelAdmin):
    list_display = ("id","sender","receiver","message","is_read","tags","url","date_filed")
    list_editable = ("sender","receiver","message","is_read","tags","url",)
    list_per_page = 10
    search_fields = ("id","sender","receiver","message","date_filed","tags",)
    list_filter = ("sender","receiver","date_filed","tags",)


admin.site.register(models.NotificationsModel, NotificationsAdmin)


class MessagesAdmin(ImportExportModelAdmin):
    list_display = ("id", "sender", "receiver", "subject", "content", "is_read", "date_filed")
    list_editable = ( "sender", "receiver", "subject", "content", "is_read",)
    list_per_page = 10
    search_field = ("id", "sender", "receiver", "subject", "content", )
    list_filter = ("sender", "receiver")

admin.site.register(models.MessagesModel, MessagesAdmin)

class SentMessagesAdmin(ImportExportModelAdmin):
    list_display = ("id", "sender", "receiver", "subject", "content", "date_filed")
    list_editable = ( "sender", "receiver", "subject", "content",)
    list_per_page = 10
    search_field = ("id", "sender", "receiver", "subject", "content", )
    list_filter = ("sender", "receiver")

admin.site.register(models.SentMessagesModel, SentMessagesAdmin)


class WebExAdmin(ImportExportModelAdmin):
    list_display = ("id", "url", "display_text", "protcol", "remarks", "author", "date_filed")
    list_editable = ( "url", "display_text", "protcol", "remarks", "author",)
    list_per_page = 10
    search_field = ("id", "url", "display_text", "protcol", "remarks","author",)
    list_filter = ("protcol", "author",)

admin.site.register(models.WebExModel, WebExAdmin)


class OldDocumentsAdmin(ImportExportModelAdmin):
    list_display = ("id", "files", "name", "size", "content_type", "year", "remarks", "date_uploaded")
    list_editable = ( "files", "name", "size", "content_type", "year", "remarks",)
    list_per_page = 10
    search_field = ("id", "files", "name", "size", "content_type", "year", "remarks",)
    list_filter = ("year", "content_type",)

admin.site.register(models.OldDocumentsModel, OldDocumentsAdmin)
