import logging
from json import dumps, loads

from django.apps import apps
from django.core.exceptions import ImproperlyConfigured

from django_swagger_tester.response_validation.utils import get_response_schema
from django_swagger_tester.utils import get_paths, validate_inputs, resolve_path, convert_resolved_route

logger = logging.getLogger('django_swagger_tester')


class LoadDrfYasgSchema:

    def __init__(self, route: str, status_code: int, method: str) -> None:
        """
        Loads OpenAPI schema when schema is dynamically generated by drf_yasg.

        :param route: a django-resolved endpoint path
        :param status_code: the relevant HTTP response status code to check in the OpenAPI schema
        :param method: the relevant HTTP method to check in the OpenAPI schema
        """
        validate_inputs(route, status_code, method)
        self.validation()

        from drf_yasg.openapi import Info
        from drf_yasg.generators import OpenAPISchemaGenerator
        self.schema_generator = OpenAPISchemaGenerator(info=Info(title='', default_version=''))

        self.route = self.get_drf_yasg_compatible_route(route)
        self.status_code = status_code
        self.method = method

    @staticmethod
    def validation() -> None:
        """
        For drf_yasg-generated schemas, it's important that we verify:
        1. The package is installed
        2. Json is installed, for parsing the schema
        3. drf_yasg is in the projects installed_apps
        """
        try:
            import drf_yasg  # noqa: F401
        except ModuleNotFoundError:
            raise ImproperlyConfigured('The package `drf_yasg` is required. Please run `pip install drf_yasg` to install it.')

        if 'drf_yasg' not in apps.app_configs.keys():
            raise ImproperlyConfigured(
                'The package `drf_yasg` is missing from INSTALLED_APPS. Please add it to your '
                '`settings.py`, as it is required for this implementation')

    def get_schema(self) -> dict:
        """
        Generates OpenAPI schema.
        """
        odict_schema = self.schema_generator.get_schema(None, True)
        return loads(dumps(odict_schema.as_odict()))

    def get_path_prefix(self) -> str:
        """
        Returns the drf_yasg specified path prefix.

        Drf_yasg `cleans` schema paths by finding recurring path patterns, and cutting them out of the generated openapi schema.
        For example, `/api/v1/example` might then just become `/example`
        """
        return self.schema_generator.determine_path_prefix(get_paths())

    def get_drf_yasg_compatible_route(self, route: str) -> str:
        """
        Returns a url that matches the urls found in a drf_yasg-generated schema.

        :param route: Django resolved route
        """
        resolved_route = resolve_path(route)
        converted_route = convert_resolved_route(resolved_route)
        path_prefix = self.get_path_prefix()  # typically might be 'api/' or 'api/v1/'
        return converted_route.replace(path_prefix, '')

    def get_response_schema(self) -> dict:
        """
        Indexes schema by url, HTTP method, and status code to get the section of a schema related to a specific response.
        """
        schema = self.get_schema()
        return get_response_schema(schema=schema, method=self.method, status_code=self.status_code, route=self.route)
