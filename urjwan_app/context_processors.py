# urjwan_app/context_processors.py

def add_user_to_context(request):
    return {
        'logged_in_user': request.user if request.user.is_authenticated else None
    }
