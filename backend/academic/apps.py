from django.apps import AppConfig


class AcademicConfig(AppConfig):
    name = 'academic'

    def ready(self):
        import academic.signals  # noqa: F401
