def get_ex_str(ex):
    exception_mappings = {
        TimeoutError: '⌛ TimeoutError',
        ValueError: '❗ Invalid value',
        # Add more exception types and their corresponding formatted strings with emojis here
    }

    if isinstance(ex, Exception):
        exception_type = ex.__class__
        return exception_mappings.get(exception_type, f'❌ {exception_type.__name__}')

    return str(ex)
