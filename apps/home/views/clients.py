import datetime
from django.db.models import Q, Sum, F
from django.shortcuts import render, redirect, get_object_or_404
from apps.home.models import Profile, Client, Office, Document, Bill, BillInstallment
from django.contrib.auth.models import User
from apps.home.views.balance import INCOME_CATEGORIES, EXPENSE_CATEGORIES, unmask_money, check_late_bills
from django.core.files.storage import default_storage
from django.http import HttpResponse


def check_expired_documents():
    expired_documents = Document.objects.filter(Q(expiration__lt=datetime.datetime.now().date()) & Q(expired=False))
    for doc in expired_documents:
        doc.expired = True
        doc.save()

    unexpected_expired_documents = Document.objects.filter(
        Q(expiration__gt=datetime.datetime.now().date()) & Q(expired=True))
    for doc in unexpected_expired_documents:
        doc.expired = False
        doc.save()


def get_permission(request, permission_type, model='client'):
    return request.user.has_perm(f'home.{permission_type}_{model}')


############################################


def home(request, filters=None, sorted_by=None, sort_type=None):
    if not get_permission(request, 'view'):
        return render(request, 'home/page-404.html')

    check_expired_documents()

    clients = filter_clients_objects(request, filters)
    clients = sort_clients_objects(clients, sorted_by, sort_type)

    context = {
        'user_profile': Profile.objects.get(user=request.user),
        'clients': clients,
        'offices': Office.objects.all(),
        'filters': filters,
        'sorted_by': sorted_by,
        'sort_type': sort_type,
    }

    return render(request, 'home/clients-list.html', context)


def create(request):
    if not get_permission(request, 'add'):
        return render(request, 'home/page-404.html')

    if request.method == 'POST':
        client = Client(
            name=request.POST.get('name', ''),
            cnpj=request.POST.get('cnpj', ''),
            area=request.POST.get('area', ''),
            office=Office.objects.get(id=request.POST['office']) if request.POST.get('office') else None,
            location=request.POST.get('address', ''),
            contact_email=request.POST.get('contact_email', ''),
            phone=request.POST.get('phone', ''),
            xml_email=request.POST.get('xml_email', ''),
            description=request.POST.get('about', ''),
        )

        client.save()

        return redirect('client_details', slug=client.slug)

    return redirect('clients_home')


def delete(request, slug):
    if not get_permission(request, 'delete'):
        return render(request, 'home/page-404.html')

    client = Client.objects.get(slug=slug)
    client.delete()

    return redirect('clients_home')


def sort(request):
    sorted_by = request.POST['sort_by'].replace('_', '-') if request.POST.get('sort_by', False) else ''
    sort_type = 'asc' if request.POST.get('asc', False) else 'desc'
    filters = request.POST.get('filters', 'None')

    print(f'sorted_by: {sorted_by} | sort_type: {sort_type} | filters: {filters}')

    if sorted_by != '' and filters != 'None':
        return redirect('sorted_filtered_clients', sorted_by=sorted_by, sort_type=sort_type, filters=filters)
    elif sorted_by != '':
        return redirect('sorted_clients', sorted_by=sorted_by, sort_type=sort_type)
    elif filters != 'None':
        return redirect('filtered_clients', filters=filters)
    else:
        return redirect('clients_home')


def filter_clients_objects(request, filters):
    clients = Client.objects.all()

    if filters:
        filters_list = filters.split('&')

        office = 'all'

        for item in filters_list:
            office = item.split('=')[1] if item.startswith('office') else office

        if office != 'all':
            clients = clients.filter(office=office if office else None)

    return clients


def sort_clients_objects(clients, sorted_by, sort_type):
    if sorted_by is not None:
        sorted_by = sorted_by.replace('-', '_')
    else:
        sorted_by = ''

    if sorted_by == 'office':
        if sort_type == 'desc':
            clients = sorted(clients, key=lambda client: client.office.name if client.office else '')
        else:
            clients = sorted(clients, key=lambda client: client.office.name if client.office else 'z')
    else:
        clients = sorted(clients, key=lambda client: getattr(client, sorted_by, ''))

    if sort_type == 'desc':
        clients = reversed(clients)

    return clients


def filter_clients(request):
    office = request.POST['office']

    filter_list = [
        f'office={office}' if office != 'all' else '%',
    ]

    filter_string = '&'.join(filter_list)
    if filter_string.startswith('%&'):
        filter_string = filter_string[2:]
    if filter_string.endswith('&'):
        filter_string = filter_string[:-1]

    filter_string = filter_string.replace('%&', '')
    filter_string = filter_string.replace('/', '-')
    filter_string = filter_string[:-2] if filter_string.endswith('&%') else filter_string

    if request.POST['sort_by'] != 'None' and filter_string != '%':
        return redirect('sorted_filtered_clients',
                        sorted_by=request.POST['sort_by'].replace('_', '-'),
                        sort_type=request.POST['sort_type'],
                        filters=filter_string)
    elif filter_string == '%' and request.POST['sort_by'] != 'None':
        return redirect('sorted_clients',
                        sorted_by=request.POST['sort_by'].replace('_', '-'),
                        sort_type=request.POST['sort_type'])
    elif filter_string == '%':
        return redirect('clients_home')
    else:
        return redirect('filtered_clients', filters=filter_string)


############################################


def details(request, slug):
    if not get_permission(request, 'change'):
        return render(request, 'home/page-404.html')

    check_expired_documents()

    client = Client.objects.get(slug=slug)

    if request.method == 'POST':
        client.name = request.POST.get('name', client.name)
        client.cnpj = request.POST.get('cnpj', client.cnpj)
        client.area = request.POST.get('area', client.area)
        client.office = Office.objects.get(id=request.POST['office']) if request.POST.get('office') else client.office
        client.location = request.POST.get('address', client.location)
        client.contact_email = request.POST.get('contact_email', client.contact_email)
        client.phone = request.POST.get('phone', client.phone)
        client.xml_email = request.POST.get('xml_email', client.xml_email)
        client.description = request.POST.get('about', client.description)

        client.save()

        return redirect('client_details', slug=client.slug)

    client_bills = Bill.objects.filter(client=client, paid=True)

    income_bills = client_bills.filter(category__in=INCOME_CATEGORIES)
    expense_bills = client_bills.filter(category__in=EXPENSE_CATEGORIES)
    total_income = sum([bill.total for bill in income_bills])
    total_expense = sum([bill.total for bill in expense_bills])

    last_month_bills = client_bills.filter(
        paid_at__gte=datetime.datetime.now().date() - datetime.timedelta(days=30)
    )

    last_month_bills_income = last_month_bills.filter(category__in=INCOME_CATEGORIES)
    last_month_bills_expense = last_month_bills.filter(category__in=EXPENSE_CATEGORIES)
    total_last_month_income = sum([bill.total for bill in last_month_bills_income])
    total_last_month_expense = sum([bill.total for bill in last_month_bills_expense])

    if total_income + total_expense != 0 and total_income != 0:
        income_percentage = total_income / (total_income + total_expense) * 100
    else:
        income_percentage = 0

    if total_income + total_expense != 0 and total_expense != 0:
        expense_percentage = total_expense / (total_income + total_expense) * 100
    else:
        expense_percentage = 0

    last_month_balance = total_last_month_income - total_last_month_expense
    last_month_difference = abs((total_income - total_expense) - last_month_balance)

    if (last_month_difference != 0 and last_month_balance != 0 and
            not str(last_month_difference).endswith('$0.00') and not str(last_month_balance).endswith('$0.00')):
        last_month_percentage = last_month_balance / last_month_difference * 100
    else:
        last_month_percentage = 0

    context = {
        'currency': 'BRL',  # TODO: Change to currency variable when implemented
        'user_profile': Profile.objects.get(user=request.user),
        'client': client,
        'collaborators': Profile.objects.filter(user__username__endswith='@infinitefoundry.com').exclude(
            user__username__startswith='admin').exclude(user__username__startswith='hub'),
        'balance': total_income - total_expense,
        'income_percentage': round(income_percentage),
        'expense_percentage': round(expense_percentage),
        'last_month_balance': last_month_balance,
        'last_month_balance_percentage': round(last_month_percentage, 1),
    }

    return render(request, 'home/client-page.html', context)


def change_picture(request, slug):
    if not get_permission(request, 'change'):
        return render(request, 'home/page-404.html')

    client = Client.objects.get(slug=slug)

    if request.method == 'POST':
        previous_avatar = client.avatar
        if 'placeholder' not in previous_avatar.name and request.FILES.get('avatar'):
            previous_avatar.delete(save=False)

        client.avatar = request.FILES.get('avatar', client.avatar)
        client.save()

        return redirect(request.POST.get('redirect_to', 'client_details'), slug=client.slug)

    return redirect('client_details', slug=client.slug)


############################################


def documents_page(request, slug, sorted_by=None, sort_type=None, filters=None):
    if not get_permission(request, 'view', 'document'):
        return render(request, 'home/page-404.html')

    check_expired_documents()

    client = Client.objects.get(slug=slug)
    documents = filter_documents_objects(filters, slug)[0]
    if sorted_by is not None:
        documents = documents.order_by(f'{"-" if sort_type == "desc" else ""}{sorted_by}')

    context = {
        'user_profile': Profile.objects.get(user=request.user),
        'client': client,
        'sorted_by': sorted_by,
        'sort_type': sort_type,
        'filters': filters,
        'documents': documents,
    }

    return render(request, 'home/client-documents.html', context)


def new_document(request, slug, doc_id=None):
    if not get_permission(request, 'add', 'document'):
        return render(request, 'home/page-404.html')

    client = Client.objects.get(slug=slug)

    redirect_to = request.POST.get('redirect_to', 'client_details')

    if request.method == 'POST':
        expiration = request.POST.get('expiration', None)
        if not doc_id:
            document = Document(
                client=client,
                uploaded_by=User.objects.get(username=request.user.username),
                name=request.POST.get('name', ''),
                expiration=expiration if expiration else None,
                category=request.POST.get('category', ''),
                description=request.POST.get('description', ''),
                file=request.FILES['file'],
            )
        else:
            document = Document.objects.get(id=doc_id)
            document.name = request.POST.get('name', document.name)
            document.expiration = expiration if expiration else None
            document.category = request.POST.get('category', document.category)
            document.description = request.POST.get('description', document.description)
            document.file = request.FILES['file'] if request.FILES.get('file') else document.file

        document.save()

        if redirect_to == 'client_documents':
            sorted_by = request.POST['sort_by'] if request.POST.get('sort_by', False) else ''
            sort_type = 'asc' if request.POST.get('asc', False) else 'desc'
            filters = request.POST.get('filters', 'None')

            if sorted_by not in ['', 'None'] and filters != 'None':
                return redirect('sorted_filtered_client_documents', slug=slug,
                                sorted_by=sorted_by, sort_type=sort_type, filters=filters)
            elif sorted_by not in ['', 'None']:
                return redirect('sorted_client_documents', slug=slug, sorted_by=sorted_by, sort_type=sort_type)
            elif filters != 'None':
                return redirect('filtered_client_documents', slug=slug, filters=filters)
            else:
                return redirect('client_documents', slug=slug)

    return redirect(redirect_to, slug=client.slug)


def delete_document(request, slug, document_id):
    if not get_permission(request, 'delete', 'document'):
        return render(request, 'home/page-404.html')

    if request.method == 'POST':
        redirect_to = request.POST.get('redirect_to', 'client_details')
        document = Document.objects.get(id=document_id)
        file = document.file
        if file:
            file.delete(save=False)

        document.delete()

        if redirect_to == 'client_documents':
            sorted_by = request.POST['sort_by'] if request.POST.get('sort_by', False) else ''
            sort_type = 'asc' if request.POST.get('asc', False) else 'desc'
            filters = request.POST.get('filters', 'None')

            if sorted_by not in ['', 'None'] and filters != 'None':
                return redirect('sorted_filtered_client_documents', slug=slug,
                                sorted_by=sorted_by, sort_type=sort_type, filters=filters)
            elif sorted_by not in ['', 'None']:
                return redirect('sorted_client_documents', slug=slug, sorted_by=sorted_by, sort_type=sort_type)
            elif filters != 'None':
                return redirect('filtered_client_documents', slug=slug, filters=filters)
            else:
                return redirect(redirect_to, slug=slug)

    return redirect('client_details', slug=slug)


def download_document(request, slug, document_id):
    if not get_permission(request, 'view', 'document'):
        return render(request, 'home/page-404.html')

    document = get_object_or_404(Document, id=document_id)

    document_name = document.file.name
    file_content = default_storage.open(document_name).read()
    response = HttpResponse(file_content, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{document_name.split("/")[-1]}"'
    return response


def sort_and_filter_documents(request, slug):
    sorted_by = request.POST['sort_by'] if request.POST.get('sort_by', False) else ''
    sort_type = 'asc' if request.POST.get('asc', False) else 'desc'
    filters = request.POST.get('filters', 'None')

    if sorted_by not in ['', 'None'] and filters != 'None':
        return redirect('sorted_filtered_client_documents', slug=slug,
                        sorted_by=sorted_by, sort_type=sort_type, filters=filters)
    elif sorted_by not in ['', 'None']:
        return redirect('sorted_client_documents', slug=slug, sorted_by=sorted_by, sort_type=sort_type)
    elif filters != 'None':
        return redirect('filtered_client_documents', slug=slug, filters=filters)
    else:
        return redirect('client_documents', slug=slug)


def filter_documents_objects(filters, slug):
    documents = Document.objects.filter(client=Client.objects.get(slug=slug))

    if filters is not None:
        filters_list = filters.split('&')

        category = 'all'
        from_date, to_date = False, False

        for item in filters_list:
            from_date = datetime.datetime.strptime(item.split('=')[1], '%Y-%m-%d') if item.startswith('from') else from_date
            to_date = datetime.datetime.strptime(item.split('=')[1], '%Y-%m-%d') if item.startswith('to') else to_date
            category = item.split('=')[1] if item.startswith('category') else category

            if from_date and to_date and from_date < to_date:
                documents = documents.filter(expiration__gte=from_date)
                documents = documents.filter(expiration__lte=to_date)
            elif from_date:
                documents = documents.filter(expiration__gte=from_date)
            elif to_date:
                documents = documents.filter(expiration__lte=to_date)

            if category != 'all':
                documents = documents.filter(category=category)

    return documents, documents.order_by('-id').first().id if documents.count() > 0 else 0


def filter_documents(request, slug):
    from_date = request.POST['from']
    to_date = request.POST['to']
    category = request.POST['category']

    filter_list = [
        f'from={from_date}' if from_date != '' and from_date != to_date else '%',
        f'to={to_date}' if to_date != '' and from_date != to_date else '%',
        f'category={category}' if category != 'all' else '%',
    ]

    # Convert the list to a string with appropriate format, avoiding empty values
    filter_string = '&'.join(filter_list)
    if filter_string.startswith('%&'):
        filter_string = filter_string[2:]
    if filter_string.endswith('&'):
        filter_string = filter_string[:-1]

    filter_string = filter_string.replace('%&', '')
    filter_string = filter_string.replace('/', '-')
    filter_string = filter_string[:-2] if filter_string.endswith('&%') else filter_string

    if request.POST['sort_by'] != 'None' and filter_string != '%':
        return redirect('sorted_filtered_client_documents', slug=slug,
                        sorted_by=request.POST['sort_by'].replace('_', '-'),
                        sort_type=request.POST['sort_type'],
                        filters=filter_string)
    elif filter_string == '%' and request.POST['sort_by'] != 'None':
        return redirect('sorted_client_documents', slug=slug,
                        sorted_by=request.POST['sort_by'].replace('_', '-'),
                        sort_type=request.POST['sort_type'])
    elif filter_string == '%':
        return redirect('client_documents', slug=slug)
    else:
        return redirect('filtered_client_documents', filters=filter_string, slug=slug)


############################################


def balance_page(request, slug, sorted_by=None, sort_type=None, filters=None):
    if not get_permission(request, 'view', 'document'):
        return render(request, 'home/page-404.html')

    check_late_bills()

    client = Client.objects.get(slug=slug)
    bills = filter_bill_objects(filters, slug)[0]
    if sorted_by is not None:
        if sorted_by == 'date':
            sort_string = 'created_at'
        elif sorted_by == 'expiration':
            sort_string = 'due_date'
        elif sorted_by == 'installments_value':
            bills = bills.annotate(installments_value=Sum('installments__value') / F('installments_number'))
            sort_string = sorted_by
        elif sorted_by == 'office':
            sort_string = 'office__name'
        else:
            sort_string = sorted_by

        bills = bills.order_by(f'{"-" if sort_type == "desc" else ""}{sort_string}')

    income_bills = bills.filter(category__in=INCOME_CATEGORIES)
    expense_bills = bills.filter(category__in=EXPENSE_CATEGORIES)

    context = {
        'user_profile': Profile.objects.get(user=request.user),
        'client': client,
        'bills': bills,
        'received': sum([bill.total for bill in income_bills if bill.paid]),
        'income': sum([bill.total for bill in income_bills]),
        'pending_income': sum([bill.total for bill in income_bills if not bill.paid]),
        'late_income': sum([bill.total for bill in income_bills if bill.late]),
        'paid': sum([bill.total for bill in expense_bills if bill.paid]),
        'expense': sum([bill.total for bill in expense_bills]),
        'pending_expense': sum([bill.total for bill in expense_bills if not bill.paid]),
        'late_expense': sum([bill.total for bill in expense_bills if bill.late]),
        'documents': Bill.objects.filter(client=client),
        'income_categories': sorted(INCOME_CATEGORIES),
        'expense_categories': sorted(EXPENSE_CATEGORIES),
        'offices': Office.objects.all(),
        'sorted_by': sorted_by,
        'sort_type': sort_type,
        'filters': filters,
    }

    return render(request, 'home/client-balance.html', context)


def new_bill(request, slug):
    if not get_permission(request, 'add', 'bill'):
        context = {
            'user_profile': Profile.objects.get(user=request.user),
        }
        return render(request, 'home/page-404.html', context)

    if request.method == 'POST':
        currency = request.POST.get('currency', 'USD')
        bill = Bill(
            # Foreign Keys
            client=Client.objects.get(slug=slug),
            office=Office.objects.get(id=request.POST['office_id']) if request.POST.get('office_id') != '' else None,
            created_by=request.user,
            # Char Fields
            title=request.POST.get('title', ''),
            category=request.POST.get('category', ''),
            method=request.POST.get('method', ''),
            origin=request.POST.get('origin', ''),
            # Date Fields
            due_date=request.POST.get('due_date', None) if request.POST.get('due_date', None) != '' else None,
            # Money Fields
            total=unmask_money(request.POST.get('total', ''), currency),
            # Integer Fields
            installments_number=request.POST.get('installments', 0),
            # File Fields
            proof=request.FILES.get('proof', None),
        )

        status = request.POST.get('status', 'Pending')
        if 'Paid' in status:
            bill.paid = True
            bill.paid_at = datetime.datetime.now()

        if 'reconciled' in status:
            bill.reconciled = True

        bill.save()

        if request.POST.get('installments') and request.POST.get('installments_value'):
            installments = request.POST.get('installments')
            installments_value = unmask_money(request.POST.get('installments_value', ''), currency)
            # installments_date = request.POST.get('installments_date', None)

            for i in range(1, int(installments) + 1):
                installment = BillInstallment(
                    bill=bill,
                    partial_id=i,
                    value=installments_value,
                    # due_date=installments_date,
                )
                installment.save()

        sorted_by = request.POST['sort_by'] if request.POST.get('sort_by', False) else ''
        sort_type = 'asc' if request.POST.get('asc', False) else 'desc'
        filters = request.POST.get('filters', 'None')

        if sorted_by != '' and filters != 'None':
            return redirect('sorted_filtered_client_balance', slug=slug,
                            sorted_by=sorted_by, sort_type=sort_type, filters=filters)
        if sorted_by not in ['', 'None']:
            return redirect('sorted_client_balance', slug=slug, sorted_by=sorted_by, sort_type=sort_type)
        elif filters != 'None':
            return redirect('filtered_client_balance', slug=slug, filters=filters)
        else:
            return redirect('client_balance', slug=slug)

    return redirect('client_balance', slug=slug)


def delete_bill(request, slug, bill_id):
    if not get_permission(request, 'delete', 'bill'):
        context = {
            'user_profile': Profile.objects.get(user=request.user),
        }
        return render(request, 'home/page-404.html', context)

    bill = Bill.objects.get(id=bill_id)
    file = bill.proof
    if file:
        file.delete(save=False)

    bill.delete()

    sorted_by = request.POST['sort_by'] if request.POST.get('sort_by', False) else ''
    sort_type = 'asc' if request.POST.get('asc', False) else 'desc'
    filters = request.POST.get('filters', 'None')

    if sorted_by != '' and filters != 'None':
        return redirect('sorted_filtered_client_balance', slug=slug,
                        sorted_by=sorted_by, sort_type=sort_type, filters=filters)
    if sorted_by not in ['', 'None']:
        return redirect('sorted_client_balance', slug=slug, sorted_by=sorted_by, sort_type=sort_type)
    elif filters != 'None':
        return redirect('filtered_client_balance', slug=slug, filters=filters)
    else:
        return redirect('client_balance', slug=slug)


def edit_bill(request, slug, bill_id):
    if not get_permission(request, 'change', 'bill'):
        context = {
            'user_profile': Profile.objects.get(user=request.user),
        }
        return render(request, 'home/page-404.html', context)

    bill = Bill.objects.get(id=bill_id)
    if request.method == 'POST':
        due_date = request.POST.get('due_date', bill.due_date)
        currency = request.POST.get('currency', 'USD')
        bill.client = Client.objects.get(slug=request.POST['client_slug'])
        bill.office = Office.objects.get(id=request.POST['office_id']) if request.POST.get(
            'office_id') else bill.office if request.POST.get('office_id') != '' else None
        bill.title = request.POST.get('title', bill.title)
        bill.category = request.POST.get('category', bill.category)
        bill.method = request.POST.get('method', bill.method)
        bill.due_date = due_date if due_date != '' else None
        bill.total = unmask_money(request.POST['total'], currency) if request.POST.get('total') else bill.total

        installments_number_from_form = int(request.POST.get('installments', 0))
        installments_value_from_form = unmask_money(request.POST.get('installments_value', ''), currency)
        if installments_number_from_form != bill.installments_number and installments_number_from_form > 1:
            installments = BillInstallment.objects.filter(bill=bill)
            installments.delete()
            bill.installments_number = installments_number_from_form
            for i in range(1, installments_number_from_form + 1):
                installment = BillInstallment(
                    bill=bill,
                    partial_id=i,
                    value=installments_value_from_form,
                    # due_date=request.POST.get('installments_date', None),
                )
                installment.save()

        elif installments_number_from_form == bill.installments_number and installments_value_from_form != bill.installments.first().value:
            installments = BillInstallment.objects.filter(bill=bill)
            for installment in installments:
                installment.value = installments_value_from_form
                installment.save()

        if request.FILES.get('proof') and request.FILES.get('proof') != bill.proof and bill.proof:
            file = bill.proof
            if file:
                file.delete(save=False)
            bill.proof = request.FILES['proof']
        else:
            bill.proof = request.FILES.get('proof', bill.proof)

        bill.save()

    sorted_by = request.POST['sort_by'] if request.POST.get('sort_by', False) else ''
    sort_type = 'asc' if request.POST.get('asc', False) else 'desc'
    filters = request.POST.get('filters', 'None')

    if sorted_by != '' and filters != 'None':
        return redirect('sorted_filtered_client_balance', slug=slug, sorted_by=sorted_by, sort_type=sort_type, filters=filters)
    if sorted_by not in ['', 'None']:
        return redirect('sorted_client_balance', slug=slug, sorted_by=sorted_by, sort_type=sort_type)
    elif filters != 'None':
        return redirect('filtered_client_balance', slug=slug, filters=filters)
    else:
        return redirect('client_balance', slug=slug)


def download_bill(request, slug, bill_id):
    if not get_permission(request, 'view', 'bill'):
        context = {
            'user_profile': Profile.objects.get(user=request.user),
        }
        return render(request, 'home/page-404.html', context)

    bill = Bill.objects.get(id=bill_id)
    file_name = bill.proof.name
    file_content = default_storage.open(file_name).read()
    response = HttpResponse(file_content, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{file_name.split("/")[-1]}"'
    return response


def change_status(request, slug, bill_id):
    if not get_permission(request, 'change', 'bill'):
        return render(request, 'home/page-404.html')

    bill = Bill.objects.get(id=bill_id)
    reconcile = request.POST.get('reconcile', False)

    if not bill.paid:
        bill.paid_at = datetime.datetime.now()
    else:
        bill.paid_at = None

    bill.paid = not bill.paid

    if reconcile:
        bill.reconciled = True

    bill.save()

    sorted_by = request.POST['sort_by'] if request.POST.get('sort_by', False) else ''
    sort_type = 'asc' if request.POST.get('asc', False) else 'desc'
    filters = request.POST.get('filters', 'None')

    if sorted_by != '' and filters != 'None':
        return redirect('sorted_filtered_client_balance', slug=slug,
                        sorted_by=sorted_by, sort_type=sort_type, filters=filters)
    if sorted_by not in ['', 'None']:
        return redirect('sorted_client_balance', slug=slug, sorted_by=sorted_by, sort_type=sort_type)
    elif filters != 'None':
        return redirect('filtered_client_balance', slug=slug, filters=filters)
    else:
        return redirect('client_balance', slug=slug)


def sort_and_filter_bills(request, slug):
    sorted_by = request.POST['sort_by'] if request.POST.get('sort_by', False) else ''
    sort_type = 'asc' if request.POST.get('asc', False) else 'desc'
    filters = request.POST.get('filters', 'None')

    if sorted_by != '' and filters != 'None':
        return redirect('sorted_filtered_client_balance', slug=slug,
                        sorted_by=sorted_by, sort_type=sort_type, filters=filters)
    if sorted_by not in ['', 'None']:
        return redirect('sorted_client_balance', slug=slug, sorted_by=sorted_by, sort_type=sort_type)
    elif filters != 'None':
        return redirect('filtered_client_balance', slug=slug, filters=filters)
    else:
        return redirect('client_balance', slug=slug)


def filter_bill_objects(filters, slug):
    bills = Bill.objects.filter(client=Client.objects.get(slug=slug))

    if filters is not None:
        filters_list = filters.split('&')

        office, method, category, client = 'all', 'all', 'all', 'all'
        from_date, to_date = False, False
        late, paid, pending = True, True, True
        min_value, max_value = None, None

        for item in filters_list:
            office = item.split('=')[1] if item.startswith('office') else office
            from_date = datetime.datetime.strptime(item.split('=')[1], '%Y-%m-%d') if item.startswith('from') else from_date
            to_date = datetime.datetime.strptime(item.split('=')[1], '%Y-%m-%d') if item.startswith('to') else to_date
            method = item.split('=')[1] if item.startswith('method') else method
            client = item.split('=')[1] if item.startswith('client') else client
            category = item.split('=')[1] if item.startswith('category') else category
            late = item.split('=')[1] if item.startswith('late') else late
            paid = item.split('=')[1] if item.startswith('paid') else paid
            pending = item.split('=')[1] if item.startswith('pending') else pending
            min_value = item.split('=')[1] if item.startswith('value_min') else min_value
            max_value = item.split('=')[1] if item.startswith('value_max') else max_value

            if office != 'all':
                bills = bills.filter(office__id=int(office))

            if from_date and to_date and from_date < to_date:
                bills = bills.filter(due_date__gte=from_date)
                bills = bills.filter(due_date__lte=to_date)
            elif from_date:
                bills = bills.filter(due_date__gte=from_date)
            elif to_date:
                bills = bills.filter(due_date__lte=to_date)

            if method != 'all':
                bills = bills.filter(method=method)

            if client != 'all':
                bills = bills.filter(client__id=client)

            if category != 'all':
                bills = bills.filter(category=category)

            if late == 'false':
                bills = bills.filter(late=False)

            if paid == 'false':
                bills = bills.filter(paid=False)

            if pending == 'false':
                bills = bills.filter(Q(paid=True, late=False) | Q(paid=False, late=True))

            if min_value:
                bills = bills.filter(total__gte=min_value)

            if max_value:
                bills = bills.filter(total__lte=max_value)

    return bills, bills.order_by('-id').first().id if bills.count() > 0 else 0


def filter_bills(request):
    universal_min_value = str(Bill.objects.all().order_by('total').first().total).replace(
        '$' if request.POST.get('currency', 'BRL') == 'USD' else 'R$' if request.POST.get('currency',
                                                                                          'BRL') == 'BRL' else '€',
        '').replace(',', '') if Bill.objects.all().count() > 0 else 0
    universal_max_value = str(Bill.objects.all().order_by('-total').first().total).replace(
        '$' if request.POST.get('currency', 'BRL') == 'USD' else 'R$' if request.POST.get('currency',
                                                                                          'BRL') == 'BRL' else '€',
        '').replace(',', '') if Bill.objects.all().count() > 0 else 0

    office = request.POST['office']
    from_date = request.POST['start_date']
    to_date = request.POST['end_date']
    method = request.POST['method']
    client = request.POST['client']
    category = request.POST['category']
    late = request.POST.get('late_filter', 'false')
    paid = request.POST.get('paid_filter', 'false')
    pending = request.POST.get('pending_filter', 'false')
    min_value = request.POST['range_value_low']
    max_value = request.POST['range_value_high']

    filter_list = [
        f'office={office}' if office != 'all' else '%',
        f'from={from_date}' if from_date != '' and from_date != to_date else '%',
        f'to={to_date}' if to_date != '' and from_date != to_date else '%',
        f'method={method}' if method != 'all' else '%',
        f'client={client}' if client != 'all' else '%',
        f'category={category}' if category != 'all' else '%',
        f'late={late}' if late == 'false' else '%',
        f'paid={paid}' if paid == 'false' else '%',
        f'pending={pending}' if pending == 'false' else '%',
        f'value_min={min_value}' if min_value != '' and min_value != universal_min_value else '%',
        f'value_max={max_value}' if max_value != '' and max_value != universal_max_value else '%',
    ]

    # Convert the list to a string with appropriate format, avoiding empty values
    filter_string = '&'.join(filter_list)
    if filter_string.startswith('%&'):
        filter_string = filter_string[2:]
    if filter_string.endswith('&'):
        filter_string = filter_string[:-1]

    filter_string = filter_string.replace('%&', '')
    filter_string = filter_string.replace('/', '-')
    filter_string = filter_string[:-2] if filter_string.endswith('&%') else filter_string

    if request.POST['sort_by'] != 'None' and filter_string != '%':
        return redirect('sorted_filtered_client_balance',
                        sorted_by=request.POST['sort_by'].replace('_', '-'),
                        sort_type=request.POST['sort_type'],
                        filters=filter_string)
    elif filter_string == '%' and request.POST['sort_by'] != 'None':
        return redirect('sorted_client_balance',
                        sorted_by=request.POST['sort_by'].replace('_', '-'),
                        sort_type=request.POST['sort_type'])
    elif filter_string == '%':
        return redirect('client_balance')
    else:
        return redirect('filtered_client_balance', filters=filter_string)
