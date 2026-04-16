from django.apps import AppConfig


class HostelConfig(AppConfig):
    name = 'hostel'

    def ready(self):
        import hostel.signals  # noqa: F401
