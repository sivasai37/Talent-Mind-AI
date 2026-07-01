from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse, HttpResponse
from rest_framework.schemas import get_schema_view


def root(request):
    return JsonResponse({
        "name": "HireGenius AI",
        "tagline": "Beyond Keywords. Intelligent Hiring Starts Here.",
        "description": "AI-powered recruitment intelligence platform",
        "version": "2.0.0",
        "endpoints": "/api/",
        "docs": "/api/docs/",
    })


def swagger_ui(request):
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <title>HireGenius AI — API Documentation</title>
      <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@4/swagger-ui.css" />
      <style>
        body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
        .topbar { background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important; }
        .topbar-wrapper img { display: none; }
        .topbar-wrapper::before { content: 'HireGenius AI'; color: white; font-size: 20px; font-weight: 700; }
      </style>
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
          deepLinking: true,
          displayRequestDuration: true,
        });
      </script>
    </body>
    </html>
    """
    return HttpResponse(html)


schema_view = get_schema_view(
    title="HireGenius AI API",
    description="AI-powered recruitment intelligence platform API — Beyond Keywords, Intelligent Hiring Starts Here.",
    version="2.0.0",
)

urlpatterns = [
    path("", root),
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    path("api/schema/", schema_view, name="api-schema"),
    path("api/docs/", swagger_ui, name="api-docs"),
]
