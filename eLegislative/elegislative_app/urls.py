from django.urls import path
from elegislative_app import views

app_name = "elegislative"

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard_page, name="dashboard_page"),
    # agenda
    path('agenda/', views.agenda_page, name="agenda_page"),
    path('create-agenda/', views.create_agenda_page, name="create_agenda_page"),
    path('edit-agenda/<int:id>/', views.edit_agenda_page, name="edit_agenda_page"),
    path('delete-agenda/<int:id>/', views.delete_agenda_page, name="delete_agenda_page"),
    path('print-agenda/<int:id>/', views.print_agenda_page, name="print_agenda_page"),
    
    # Proposed Ordinance & Resolution
    path('comments-and-recommendation/', views.comments_and_recommendation, name="comments_and_recommendation"),
    path('posting-resolution/<int:id>', views.posting_resolution, name="posting_resolution"),
    path('posting-resolution/post-comment/<int:id>', views.posting_resolution_post_comment, name="posting_resolution_post_comment"),
    path('posting-resolution/delete-comment/<int:id>/<int:rid>', views.posting_resolution_delete_comment, name="posting_resolution_delete_comment"),
    path('posting-ordinance/<int:id>', views.posting_ordinance, name="posting_ordinance"),
    path('posting-ordinance/post-comment/<int:id>', views.posting_ordinance_post_comment, name="posting_ordinance_post_comment"),
    path('posting-ordinance/delete-comment/<int:id>/<int:oid>', views.posting_ordinance_delete_comment, name="posting_ordinance_delete_comment"),
    # Committee Reports for resolution
    path('committee-reports/', views.committee_reports, name="committee_reports"),
    path('create-committee-resolution-reports/<int:id>', views.create_committee_resolution_reports, name="create_committee_resolution_reports"),
    path('edit-committe-resolution-reports/<int:id>', views.edit_committee_resolution_reports, name="edit_committee_resolution_reports"),
    path('delete-committe-resolution-reports/<int:id>', views.delete_committee_resolution_reports, name="delete_committee_resolution_reports"),
    path('print-committe-resolution-reports/<int:id>', views.print_committee_resolution_reports, name="print_committee_resolution_reports"),
    # Committee Reports for Ordinance
    path('create-committee-ordinance-reports/<int:id>', views.create_committee_ordinance_reports, name="create_committee_ordinance_reports"),
    path('edit-committe-ordinance-reports/<int:id>', views.edit_committee_ordinance_reports, name="edit_committee_ordinance_reports"),
    path('delete-committe-ordinance-reports/<int:id>', views.delete_committee_ordinance_reports, name="delete_committee_ordinance_reports"),
    path('print-committe-ordinance-reports/<int:id>', views.print_committee_ordinance_reports, name="print_committee_ordinance_reports"),

    # Resolution
    path('resolution/', views.resolution, name="resolution"),
    path('create-resolution/<int:id>/', views.create_resolutions, name="create_resolutions"),
    path('edit-resolution/<int:id>/', views.edit_resolution, name="edit_resolution"),
    path('delete-resolution/<int:id>/', views.delete_resolution, name="delete_resolution"),
    path('print-resolution/<int:id>/', views.print_resolution, name="print_resolution"),
    # Ordinance
    path('ordinance/', views.ordinance, name="ordinance_page"),
    path('create-ordinance/<int:id>', views.create_ordinance, name="create_ordinance_page"),
    path('edit-ordinance/<int:id>', views.edit_ordinance, name="edit_ordinance"),
    path('delete-ordinance/<int:id>', views.delete_ordinance, name="delete_ordinance"),
    path('print-ordinance/<int:id>', views.print_ordinance, name="print_ordinance"),
    # Records
    path('records/', views.records, name="records"),
    # Minutes of the meeing
    path('minutes-of-the-meeting/', views.minutes_of_the_meeting, name="minutes_of_the_meeting"),    
    path('create-minutes-of-the-meeting/', views.create_minutes_of_the_meeting, name="create_minutes_of_the_meeting"), 
    path('edit-minutes-of-the-meeting/<int:id>', views.edit_minutes_of_the_meeting, name="edit_minutes_of_the_meeting"), 
    path('delete-minutes-of-the-meeting/<int:id>', views.delete_minutes_of_the_meeting, name="delete_minutes_of_the_meeting"), 
    path('print-minutes-of-the-meeting/<int:id>', views.print_minutes_of_the_meeting, name="print_minutes_of_the_meeting"), 

  
    # Annoucements
    path('announcements/', views.announcements, name="announcements"),    
]