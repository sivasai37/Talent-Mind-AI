from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse, HttpResponse
from rest_framework.schemas import get_schema_view


def root(request):
    return JsonResponse({
        "name": "TalentMind AI",
        "description": "AI-powered candidate ranking system",
        "version": "1.0.0",
        "endpoints": "/api/",
    })


def swagger_ui(request):
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <title>TalentMind AI API Docs</title>
      <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@4/swagger-ui.css" />
    </head>
    <body>
      <div id="swagger-ui"></div>
      <script src="https://unpkg.com/swagger-ui-dist@4/swagger-ui-bundle.js"></script>
      <script>
        const ui = SwaggerUIBundle({
          url: '/api/schema/',
          dom_id: '#swagger-ui',
          presets: [SwaggerUIBundle.presets.apis],
          layout: 'BaseLayout',
        });
      </script>
    </body>
    </html>
    """
    return HttpResponse(html)

schema_view = get_schema_view(title="TalentMind AI API", description="API documentation for TalentMind AI", version="1.0.0")

urlpatterns = [
    path("", root),
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    path("api/schema/", schema_view, name="api-schema"),
    path("api/docs/", swagger_ui, name="api-docs"),
]
