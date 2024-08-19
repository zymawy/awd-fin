from django.core.management.base import BaseCommand, CommandError
from urjwan_app.data import import_scripts

class Command(BaseCommand):
    help = 'Imports data from CSV files into the database'

    def handle(self, *args, **options):
        try:
            import_scripts.create_groups()
            print('Groups created')
            import_scripts.import_user('urjwan_app/data/dummys/users.csv')
            print('Users imported')
            import_scripts.import_userProfile('urjwan_app/data/dummys/students.csv')
            print('Students imported')
            import_scripts.import_course('urjwan_app/data/dummys/courses.csv')
            print('Courses imported')
            import_scripts.import_studentenrollment('urjwan_app/data/dummys/student_enrollments.csv')
            print('Student enrollments imported')
            import_scripts.import_assignment('urjwan_app/data/dummys/assignments.csv')
            print('Assignments imported')
            import_scripts.import_material('urjwan_app/data/dummys/materials.csv')
            print('Materials imported')
            import_scripts.import_feedback('urjwan_app/data/dummys/feedbacks.csv')
            print('Feedbacks imported')
            import_scripts.import_notification('urjwan_app/data/dummys/notifications.csv')
            print('Notifications imported')
            self.stdout.write(self.style.SUCCESS('Done! Data import successful.'))

        except Exception as e:
            print(e)
            self.stdout.write(self.style.ERROR('Data import failed.'))
            raise CommandError(f'Error during import: {e}')
