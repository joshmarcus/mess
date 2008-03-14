from mess import settings

def project(request): 
    """Adds the project url context variable to the context.""" 
    return {'PROJECT_URL': settings.PROJECT_URL} 
