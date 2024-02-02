from wcommon import models


def create_initial_data(apps, schema_editor):
    models.Muser.objects.create(
        username="admin",
        password="1qaz2wsx",
        usernume_zh="admin",
        is_active=True,
        is_staff=True,
    )
