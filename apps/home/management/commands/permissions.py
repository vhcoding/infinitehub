from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Permission
from decouple import config


class Command(BaseCommand):
    help = 'Add permissions to users'

    def handle(self, *args, **options):

        admin_group = config('ADMIN_USERS', 'admin').split(',')

        staff_group = config('STAFF_USERS', 'admin').split(',')

        collaborators_key = config('COLLABORATORS_KEY', 'collaborator')

        collaborators_permissions_list = [
            'view_client',
            'view_office',
        ]

        admin_permissions_list = [
            'add_bill',
            'change_bill',
            'delete_bill',
            'view_bill',
            'add_client',
            'change_client',
            'delete_client',
            'change_collaborator',
            'delete_collaborator',
            'add_document',
            'change_document',
            'delete_document',
            'view_document',
            'add_office',
            'change_office',
            'delete_office',
            'add_branch',
            'change_branch',
            'delete_branch',
            'view_branch',
            'add_bankaccount',
            'change_bankaccount',
            'delete_bankaccount',
            'view_bankaccount',
            'add_billproof',
            'change_billproof',
            'delete_billproof',
            'view_billproof',
        ] + collaborators_permissions_list

        staff_permissions_list = [
            'add_logentry',
            'change_logentry',
            'delete_logentry',
            'view_logentry',
            'add_group',
            'change_group',
            'delete_group',
            'view_group',
            'add_permission',
            'change_permission',
            'delete_permission',
            'view_permission',
            'add_user',
            'change_user',
            'delete_user',
            'view_user',
            'add_contenttype',
            'change_contenttype',
            'delete_contenttype',
            'view_contenttype',
            'add_session',
            'change_session',
            'delete_session',
            'view_session',
        ] + collaborators_permissions_list

        admin_permissions = Permission.objects.filter(codename__in=admin_permissions_list)

        collaborators_permissions = Permission.objects.filter(codename__in=collaborators_permissions_list)

        staff_permissions = Permission.objects.filter(codename__in=staff_permissions_list)

        for user in User.objects.all():
            if user.username in admin_group:
                user.user_permissions.set(admin_permissions)
                self.stdout.write(f'Administrator permissions added to user: {self.style.SUCCESS(user.username)}')
            elif collaborators_key in user.username:
                if user.username in staff_group:
                    user.user_permissions.set(staff_permissions)
                    self.stdout.write(f'Staff permissions added to user: {self.style.SUCCESS(user.username)}')
                else:
                    user.user_permissions.set(collaborators_permissions)
                    self.stdout.write(f'Collaborator permissions added to user: {self.style.SUCCESS(user.username)}')
            else:
                delete_user = input(f'User seems to be invalid: {self.style.ERROR(user.username)}. Delete it? (y/n): ')
                if delete_user.lower() == 'y':
                    user.delete()
                    self.stdout.write(f'User deleted: {self.style.ERROR(user.username)}')
                else:
                    self.stdout.write(f'User not deleted: {self.style.SUCCESS(user.username)}')
