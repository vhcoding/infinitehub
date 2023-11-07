from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, re_path
from apps.home.views import assets, collaborators, inventory, login, profile, projects, balance

projects_list_urls = [

    path('projects/create', projects.create_project, name='create_project'),

    path('projects/id=<int:id>/', projects.details, name='project_details'),

    path("projects/", projects.page_list, name="project_list"),

    path("projects/<str:situation>/", projects.page_list, name="project_list"),

    path('projects/id=<int:id>/delete', projects.delete, name='delete_project'),

    path('projects/working/archive=<int:id>/redirect-to=<str:situation_page>', projects.archive,
         name='archive_project'),

    path('projects/archive/unarchive=<int:id>/redirect-to=<str:situation_page>', projects.unarchive,
         name='unarchive_project'),

    path('projects/change-status=<int:project_id>/redirect-to=<str:situation_page>', projects.change_project_status,
         name='change_project_status'),
]

projects_page_urls = [

    path('projects/id=<int:id>/upload', projects.upload_file, name='upload_file'),

    path('projects/id=<int:project_id>/delete=<int:file_id>', projects.delete_file, name='delete_file'),

    path('download_file/<int:file_id>/', projects.download_file, name='download_file'),

    path('projects/id=<int:id>/change-picture', projects.change_picture, name='change_picture'),

    path('projects/id=<int:project_id>/submit-task', projects.submit_task, name='submit_task'),

    path('projects/id=<int:project_id>/task=<int:task_id>/change-status', projects.change_task_status,
         name='change_task_status'),

    path('projects/id=<int:project_id>/edit=<int:task_id>/', projects.edit_task, name='edit_task'),

    path('projects/id=<int:project_id>/delete-task=<int:task_id>', projects.delete_task, name='delete_task'),
]

assets_urls = [

    path('assets/', assets.assets_hub, name='assets_hub'),

    path('assets/<str:category>/', assets.assets_list, name='assets_list'),

    path('assets/<str:category>/delete=<int:file_id>', assets.delete_file_from_storage_with_category,
         name='delete_file_from_storage_with_category'),

    path('assets/delete=<int:file_id>', assets.delete_file_from_storage,
         name='delete_file_from_storage'),
]

balance_urls = [

    path('balance/', balance.page, name='balance_page'),
]

collaborators_urls = [

    path('collaborators/', collaborators.page_list, name='collaborators_list'),

    path('collaborators/<str:name>', collaborators.details, name='collaborator_details'),
]

inventory_urls = [

    path('inventory/', inventory.inventory_list, name='inventory_list'),

    path('inventory/new', inventory.inventory_list, name='new_equipment'),

    path('inventory/id=<int:id>', inventory.inventory_list, name='equipment_details'),

    path('inventory/delete=<int:id>', inventory.delete_equipment, name='delete_equipment'),

    path('inventory/download/qrcode=<int:equipment_id>', inventory.download_qrcode_inventory,
         name='download_file_from_inventory'),
]

profile_urls = [

    path('profile/', profile.details, name='profile'),

    path('profile/change-picture', profile.change_picture, name='change_profile_picture'),
]

base_urls = [

    path('', login.index, name='home'),

    # Matches any html file
    re_path(r'^.*\.*', login.pages, name='pages'),

]

urlpatterns = projects_list_urls + projects_page_urls + assets_urls + collaborators_urls + inventory_urls + profile_urls
urlpatterns += balance_urls + base_urls

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
