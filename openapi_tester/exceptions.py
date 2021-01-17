import json
from typing import Any

from openapi_tester.schema_converter import SchemaToPythonConverter


class DocumentationError(Exception):
    """
    Custom exception raised when package tests fail.
    """

    def __init__(
        self,
        message: str,
        response: Any,
        schema: dict,
        hint: str = '',
        reference: str = '',
    ) -> None:
        converted_schema = SchemaToPythonConverter(schema or {}).result
        super().__init__(
            self.format(
                response=self._sort_data(response),
                example_item=self._sort_data(converted_schema),
                hint=hint,
                message=message,
                reference=reference,
            )
        )

    @staticmethod
    def _sort_data(data_object: Any) -> Any:
        if isinstance(data_object, dict):
            return dict(sorted(data_object.items()))
        elif isinstance(data_object, list):
            try:
                return sorted(data_object)
            except TypeError:
                return data_object

    def format(self, example_item: Any, response: Any, reference: str, message: str, hint: str) -> str:
        """
        Formats and returns a standardized error message for easy debugging.

        """
        message = [
            f'Error: {message}\n\n',
            f'Expected: {json.dumps(example_item)}\n\n',
            f'Received: {json.dumps(response)}\n\n',
        ]
        if hint:
            message += [f'Hint: {hint}\n\n']
        if reference:
            message += [
                f'Sequence: {reference}\n',
            ]
        return ''.join(message)


class CaseError(Exception):
    """
    Custom exception raised when items are not cased correctly.
    """

    def __init__(self, key: str, case: str, expected: str) -> None:
        super().__init__(f'The response key `{key}` is not properly {case}. Expected value: {expected}')


class OpenAPISchemaError(Exception):
    """
    Custom exception raised for invalid schema specifications.
    """

    pass


class UndocumentedSchemaSectionError(Exception):
    """
    Custom exception raised when we cannot find a schema section.
    """

    pass