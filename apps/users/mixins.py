class ActionsMetadataMixin:
    """Surfaces `actions` metadata in OPTIONS request using SimpleMetadata.

    APIView doesn't have a `get_serializer` method by default. Which causes
    the `SimpleMetadata.determine_actions` method to not be run.
    """

    def get_serializer(self, *args, **kwargs):
        return self.serializer_class(*args, **kwargs)
