from django.contrib.contenttypes.models import ContentType
from .models import ActionLog

def get_client_ip(request):
    """Helper function to get client's IP address from request."""
    if not request:
        return None
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def create_action_log(
    user, 
    action_verb, 
    related_object=None, 
    details=None, 
    request=None 
):
    """
    Creates an ActionLog entry.
    """
    content_type = None
    object_id = None
    ip_address = get_client_ip(request) if request else None

    if related_object:
        content_type = ContentType.objects.get_for_model(related_object)
        object_id = related_object.pk

    ActionLog.objects.create(
        user=user if user and user.is_authenticated else None,
        action_verb=action_verb,
        content_type=content_type,
        object_id=object_id,
        details=details or {},
        ip_address=ip_address
    )
    print(f"Audit Log: User '{user if user else 'System'}' performed '{action_verb}' on '{related_object if related_object else 'N/A'}'")