def language_context_processor(request):
    """
    Add language context variables to the template context
    """
    return {
        'LANGUAGE_CODE': getattr(request, 'LANGUAGE_CODE', 'en'),
        'LANGUAGE_BIDI': getattr(request, 'LANGUAGE_BIDI', False),
    } 