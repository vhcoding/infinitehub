from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, re_path
from apps.home.views import (
    assets, collaborators, equipments, login, profile, projects, balance, clients, offices,
    meetings
)

projects_list_urls = [

    path("projects/", projects.home, name="project_list"),
    path('projects/create', projects.create_project, name='create_project'),
    path('projects/clients-branches/', projects.client_branches, name='clients_branches'),
    path("projects/sub/<str:situation>/", projects.home, name="project_list"),

    path('projects/working/archive=<slug:slug>/redirect-to=<str:situation_page>', projects.change_archive,
         name='archive_project'),
    path('projects/archive/unarchive=<slug:slug>/redirect-to=<str:situation_page>', projects.change_archive,
         name='unarchive_project'),
    path('projects/change-status=<slug:slug>/redirect-to=<str:situation_page>', projects.change_project_status,
         name='change_project_status'),

    path('projects/order', projects.sort_and_filter_projects, name='sort_projects'),
    path('projects/filter', projects.filter_projects, name='filter_projects'),

    path('projects/order:<str:sorted_by>-<str:sort_type>', projects.home, name='sorted_projects'),
    path('projects/filters:<str:filters>', projects.home, name='filtered_projects'),
    path('projects/order:<str:sorted_by>-<str:sort_type>/filters:<str:filters>', projects.home,
         name='sorted_filtered_projects'),

    path('projects/<slug:slug>/', projects.details, name='project_details'),
    path('projects/<slug:slug>/delete', projects.delete, name='delete_project'),

]

projects_page_urls = [
    path('projects/<slug:slug>/edit', projects.edit, name='project_edit'),

    path('projects/<slug:slug>/upload', projects.upload_file, name='upload_file'),
    path('projects/<slug:slug>/delete=<int:file_id>', projects.delete_file, name='delete_file'),
    path('download_file/<int:file_id>/', projects.download_file, name='download_file'),

    path('projects/<slug:slug>/submit-task', projects.submit_task, name='submit_task'),
    path('projects/<slug:slug>/task=<int:task_id>/change-status', projects.change_task_status,
         name='change_task_status'),
    path('projects/<slug:slug>/edit=<int:task_id>/', projects.edit_task, name='edit_task'),
    path('projects/<slug:slug>/delete-task=<int:task_id>', projects.delete_task, name='delete_task'),

    path('projects/<slug:slug>/task=<int:task_id>/submit-subtask', projects.submit_subtask, name='submit_subtask'),
    path('projects/<slug:slug>/task=<int:task_id>/subtask=<int:subtask_id>/change-status',
         projects.change_subtask_status, name='change_subtask_status'),
    path('projects/<slug:slug>/task=<int:task_id>/edit=<int:subtask_id>/', projects.edit_subtask, name='edit_subtask'),
    path('projects/<slug:slug>/task=<int:task_id>/delete-subtask=<int:subtask_id>', projects.delete_subtask,
         name='delete_subtask'),

    path('projects/<slug:slug>/link', projects.add_link, name='add_link'),
    path('projects/<slug:slug>/delete-link=<int:link_id>', projects.delete_link, name='delete_link'),
]

assets_urls = [

    path('inventory/assets/', assets.assets_hub, name='assets_hub'),

    path('inventory/assets/<str:category>/', assets.assets_list, name='assets_list'),

    path('inventory/assets/<str:category>/delete=<int:file_id>', assets.delete_file_from_storage_with_category,
         name='delete_file_from_storage_with_category'),

    path('inventory/assets/delete=<int:file_id>', assets.delete_file_from_storage,
         name='delete_file_from_storage'),
]

balance_urls = [

    # path('balance/', balance.home, name='balance_page'),

    # path('balance/new', balance.new_bill, name='new_bill'),
    # path('balance/delete-bill=<int:bill_id>/', balance.delete_bill, name='delete_bill'),
    # path('balance/edit-bill=<int:bill_id>/', balance.edit_bill, name='edit_bill'),
    # path('balance/change-bill-status=<int:bill_id>', balance.change_status, name='change_bill_status'),

    # path('balance/order', balance.sort_and_filter_bills, name='sort_bills'),
    # path('balance/filter', balance.filter_bills, name='filter_bills'),

    # path('balance/order:<str:sorted_by>-<str:sort_type>', balance.home, name='sorted_bills'),
    # path('balance/filters:<str:filters>', balance.home, name='filtered_bills'),
    # path('balance/order:<str:sorted_by>-<str:sort_type>/filters:<str:filters>', balance.home,
    #      name='sorted_filtered_bills'),

    # path('balance/download-bill=<int:bill_id>', balance.download_bill, name='download_proof'),
]

clients_list_urls = [

    path('clients/', clients.home, name='clients_home'),

    path('clients/new', clients.create, name='create_client'),
    path('clients/<slug:slug>/delete', clients.delete, name='delete_client'),

    path('clients/order', clients.sort, name='sort_clients'),
    path('clients/order:<str:sorted_by>-<str:sort_type>', clients.home, name='sorted_clients'),
    path('clients/filter', clients.filter_clients, name='filter_clients'),
    path('clients/filters:<str:filters>', clients.home, name='filtered_clients'),
    path('clients/order:<str:sorted_by>-<str:sort_type>/filters:<str:filters>', clients.home,
         name='sorted_filtered_clients'),
]

client_page_urls = [

    path('clients/<slug:slug>/', clients.details, name='client_details'),
    path('clients/<slug:slug>/edit', clients.details, name='edit_client'),
    path('clients/<slug:slug>/picture', clients.change_picture, name='change_client_picture'),

    path('clients/<slug:slug>/new-branch', clients.new_branch, name='new_client_branch'),
    path('clients/<slug:slug>/edit-branch=<int:branch_id>', clients.edit_branch, name='edit_client_branch'),
    path('clients/<slug:slug>/delete-branch=<int:branch_id>', clients.delete_branch, name='delete_client_branch'),

]

client_balance_urls = [

    path('clients/<slug:slug>/balance/', clients.balance_page, name='client_balance'),
    path('clients/<slug:slug>/balance/new', clients.new_bill, name='new_client_bill'),
    path('clients/<slug:slug>/edit=<int:bill_id>', clients.edit_bill, name='edit_client_bill'),
    path('clients/<slug:slug>/balance/change-status=<int:bill_id>', clients.change_status,
         name='change_client_bill_status'),

    path('clients/<slug:slug>/balance/bill=<int:bill_id>/edit=<int:installment_id>',
         clients.installment_edit, name='edit_client_bill_installment'),
    path('clients/<slug:slug>/balance/bill=<int:bill_id>/edit-installments', clients.installments_edit_all,
         name='edit_client_bill_all_installments'),
    path('clients/<slug:slug>/balance/bill=<int:bill_id>/change-status=<int:installment_id>',
         clients.installment_change_status, name='change_client_bill_installment_status'),
    path('clients/<slug:slug>/balance/bill=<int:bill_id>/delete=<int:installment_id>',
         clients.installment_delete, name='delete_client_bill_installment'),

    path('clients/<slug:slug>/balance/delete/<int:bill_id>', clients.delete_bill, name='delete_client_bill'),
    path('clients/<slug:slug>/balance/upload-proofs', clients.upload_proofs, name='upload_client_bill_proofs'),
    path('clients/<slug:slug>/balance/delete-proof-<int:proof_id>', clients.delete_proof,
         name='delete_client_bill_proof'),
    path('clients/<slug:slug>/balance/download-bill=<int:bill_id>_<int:proof_id>', clients.download_bill,
         name='download_client_proof'),

    path('clients/<slug:slug>/balance/order', clients.sort_and_filter_bills, name='sort_client_balance'),
    path('clients/<slug:slug>/balance/filter', clients.filter_bills, name='filter_client_balance'),

    path('clients/<slug:slug>/balance/order:<str:sorted_by>-<str:sort_type>', clients.balance_page,
         name='sorted_client_balance'),
    path('clients/<slug:slug>/balance/filters:<str:filters>', clients.balance_page, name='filtered_client_balance'),
    path('clients/<slug:slug>/balance/order:<str:sorted_by>-<str:sort_type>/filters:<str:filters>', clients.balance_page,
         name='sorted_filtered_client_balance'),
]

client_documents_urls = [

    path('clients/<slug:slug>/new-doc', clients.new_document, name='new_client_document'),
    path('clients/<slug:slug>/edit-doc=<int:doc_id>', clients.new_document, name='edit_client_document'),
    path('clients/<slug:slug>/delete-doc=<int:document_id>', clients.delete_document, name='delete_client_document'),
    path('clients/<slug:slug>/documents', clients.documents_page, name='client_documents'),
    path('clients/<slug:slug>/documents/download=<int:document_id>', clients.download_document,
         name='download_client_document'),

    path('clients/<slug:slug>/documents/order', clients.sort_and_filter_documents, name='sort_client_documents'),
    path('clients/<slug:slug>/documents/filter', clients.filter_documents, name='filter_client_documents'),

    path('clients/<slug:slug>/documents/order:<str:sorted_by>-<str:sort_type>', clients.documents_page,
         name='sorted_client_documents'),
    path('clients/<slug:slug>/documents/filters:<str:filters>', clients.documents_page, name='filtered_client_documents'),
    path('clients/<slug:slug>/documents/order:<str:sorted_by>-<str:sort_type>/filters:<str:filters>',
         clients.documents_page, name='sorted_filtered_client_documents'),

]

collaborators_page_urls = [

    path('collaborators/<slug:slug>/', collaborators.details, name='collaborator_details'),
    path('collaborators/new-document=<int:collab_id>', collaborators.newdoc, name='document_new'),
    path('collaborators/download=<int:document_id>', collaborators.download_document,
         name='download_collaborator_document'),
    path('collaborators/<slug:slug>/delete-document=<int:document_id>', collaborators.delete_document,
         name='delete_document'),
    path('collaborators/<slug:slug>/edit-document=<int:document_id>', collaborators.edit_document,
         name='edit_document'),

    path('collaborators/<slug:slug>/filter', collaborators.filter_docs, name='filter_documents'),
    path('collaborators/<slug:slug>/order', collaborators.sort_docs, name='sort_documents'),
    path('collaborators/<slug:slug>/order:<str:sorted_by>-<str:sort_type>', collaborators.details,
         name='sorted_documents'),
    path('collaborators/<slug:slug>/filters:<str:filters>', collaborators.details,
         name='filtered_documents'),
    path('collaborators/<slug:slug>/order:<str:sorted_by>-<str:sort_type>/filters:<str:filters>', collaborators.details,
         name='sorted_filtered_documents'),

    path('collaborators/<slug:slug>/add-account', collaborators.add_bank_account, name='collaborator_add_bank_account'),
    path('collaborators/<slug:slug>/edit-account=<int:bank_account_id>', collaborators.edit_bank_account,
         name='collaborator_edit_bank_account'),
    path('collaborators/<slug:slug>/delete-account=<int:bank_account_id>', collaborators.delete_bank_account,
         name='collaborator_delete_bank_account'),
]

collaborators_list_urls = [

    path('collaborators/', collaborators.page_list, name='collaborators_list'),

    path('collaborators/change=<int:collab_id>', collaborators.change_status, name='collaborator_change_status'),

    path('collaborators/order/', collaborators.sort_collaborators, name='sort_collaborators'),

    path('collaborators/filter/', collaborators.filter_collaborators, name='filter_collaborators'),

    path('collaborators/order:<str:sorted_by>-<str:sort_type>', collaborators.page_list, name='sorted_collaborators'),

    path('collaborators/filters:<str:filters>', collaborators.page_list, name='filtered_collaborators'),

    path('collaborators/order:<str:sorted_by>-<str:sort_type>/filters:<str:filters>', collaborators.page_list,
         name='sorted_filtered_collaborators'),

    path('collaborators/fill=<str:slug>', collaborators.fill_collaborator_initial_infos, name='fill_collaborator'),

    path('collaborators/qr-code=<str:slug>', collaborators.download_collaborator_qrcode,
         name='download_qrcode_collaborator'),
]

equipments_urls = [

    path('inventory/equipments/', equipments.inventory_list, name='inventory_list'),

    path('inventory/equipments/new', equipments.inventory_list, name='new_equipment'),

    path('inventory/equipments/id=<int:id>', equipments.inventory_list, name='equipment_details'),

    path('inventory/equipments/delete=<int:id>', equipments.delete_equipment, name='delete_equipment'),

    path('inventory/equipments/download/qrcode=<int:equipment_id>', equipments.download_qrcode_inventory,
         name='download_file_from_inventory'),
]

profile_urls = [

    path('profile/', profile.details, name='profile'),

    path('profile/change-picture', profile.change_picture, name='change_profile_picture'),

    path('profile/edit', profile.edit, name='edit_profile'),

    path('profile/save', profile.edit, name='send_edit_profile'),

    path('profile/delete-file=<int:file_id>', profile.delete_file, name='delete_file_from_profile'),

    path('profile/qrcode', profile.download_qrcode, name='profile_download_qrcode'),
]

offices_urls = [

    path('offices/', offices.home, name='offices_home'),
    path('offices/new', offices.create, name='offices_create'),
    path('offices/delete=<int:office_id>', offices.delete, name='offices_delete'),

    path('offices/<slug:slug>/', offices.details, name='office_details'),
    path('offices/<slug:slug>/edit', offices.edit, name='offices_edit'),

    path('offices/<slug:slug>/bank-account', offices.add_bank_account, name='offices_add_bank_account'),
    path('offices/<slug:slug>/bank-account/edit=<int:bank_account_id>', offices.edit_bank_account,
         name='offices_edit_bank_account'),
    path('offices/<slug:slug>/bank-account/delete=<int:bank_account_id>', offices.delete_bank_account,
         name='offices_delete_bank_account'),

    # path('offices/<slug:slug>/balance/', offices.balance, name='office_balance'),
    # path('offices/<slug:slug>/balance/new', offices.new_bill, name='new_office_bill'),
    # path('offices/<slug:slug>/edit=<int:bill_id>', offices.edit_bill, name='edit_office_bill'),
    # path('offices/<slug:slug>/balance/change-status=<int:bill_id>', offices.change_status,
    #      name='change_office_bill_status'),

    # path('offices/<slug:slug>/balance/bill=<int:bill_id>/edit=<int:installment_id>',
    #      offices.installment_edit, name='edit_office_bill_installment'),
    # path('offices/<slug:slug>/balance/bill=<int:bill_id>/change-status=<int:installment_id>',
    #      offices.installment_change_status, name='change_office_bill_installment_status'),
    # path('clients/<slug:slug>/balance/bill=<int:bill_id>/delete=<int:installment_id>',
    #      offices.installment_delete, name='delete_office_bill_installment'),

    # path('offices/<slug:slug>/balance/delete/<int:bill_id>', offices.delete_bill, name='delete_office_bill'),
    # path('offices/<slug:slug>/balance/download-bill=<int:bill_id>', offices.download_bill,
    #      name='download_office_proof'),

    # path('offices/<slug:slug>/balance/order', offices.sort_and_filter_bills, name='sort_office_balance'),
    # path('offices/<slug:slug>/balance/filter', offices.filter_bills, name='filter_office_balance'),

    # path('offices/<slug:slug>/balance/order:<str:sorted_by>-<str:sort_type>', offices.balance,
    #      name='sorted_office_balance'),
    # path('offices/<slug:slug>/balance/filters:<str:filters>', offices.balance, name='filtered_office_balance'),
    # path('offices/<slug:slug>/balance/order:<str:sorted_by>-<str:sort_type>/filters:<str:filters>', offices.balance,
    #      name='sorted_filtered_office_balance'),

    path('offices/<slug:slug>/documents/', offices.documents, name='office_documents'),
    path('offices/<slug:slug>/documents/new', offices.new_document, name='office_new_document'),
    path('offices/<slug:slug>/documents/edit=<int:document_id>', offices.new_document, name='office_edit_document'),
    path('offices/<slug:slug>/documents/delete=<int:document_id>', offices.delete_document,
         name='office_delete_document'),
    path('offices/<slug:slug>/documents/download=<int:document_id>', offices.download_document,
         name='office_download_document'),

    path('offices/<slug:slug>/documents/order', offices.sort_and_filter_documents, name='sort_office_documents'),
    path('offices/<slug:slug>/documents/filter', offices.filter_documents, name='filter_office_documents'),

    path('offices/<slug:slug>/documents/order:<str:sorted_by>-<str:sort_type>', offices.documents,
         name='sorted_office_documents'),
    path('offices/<slug:slug>/documents/filters:<str:filters>', offices.documents, name='filtered_office_documents'),
    path('offices/<slug:slug>/documents/order:<str:sorted_by>-<str:sort_type>/filters:<str:filters>',
         offices.documents, name='sorted_filtered_office_documents'),
]

meetings_urls = [

    path('meetings/', meetings.home, name='meetings_home'),

    path('meetings/id=<int:meeting_id>/', meetings.details, name='meeting_details'),
    path('meetings/edit=<int:meeting_id>', meetings.details, name='meeting_edit'),

    path('meetings/id=<int:meeting_id>/edit-task=<int:task_id>', meetings.edit_task, name='meeting_edit_task'),
    path('meetings/id=<int:meeting_id>/delete-task=<int:task_id>', meetings.delete_task, name='meeting_delete_task'),
    path('meetings/id=<int:meeting_id>/change-task-status=<int:task_id>', meetings.change_task_status,
         name='meeting_change_task_status'),

    path('meetings/id=<int:meeting_id>/task=<int:task_id>/submit-subtask', meetings.submit_subtask,
         name='meeting_submit_subtask'),
    path('meetings/id=<int:meeting_id>/task=<int:task_id>/subtask=<int:subtask_id>/change-status',
         meetings.change_subtask_status, name='meeting_change_subtask_status'),
    path('meetings/id=<int:meeting_id>/task=<int:task_id>/edit=<int:subtask_id>/', meetings.edit_subtask,
         name='meeting_edit_subtask'),
    path('meetings/id=<int:meeting_id>/task=<int:task_id>/delete-subtask=<int:subtask_id>', meetings.delete_subtask,
         name='meeting_delete_subtask'),
]

base_urls = [
    path('', login.index, name='home'),
    # Matches any html file
    re_path(r'^.*\.*', login.pages, name='pages'),
]

urlpatterns = [
    *projects_list_urls, *projects_page_urls, *assets_urls, *collaborators_page_urls, *collaborators_list_urls,
    *balance_urls, *equipments_urls, *profile_urls, *clients_list_urls, *offices_urls, *client_page_urls,
    *client_balance_urls, *client_documents_urls, *meetings_urls, *base_urls
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
