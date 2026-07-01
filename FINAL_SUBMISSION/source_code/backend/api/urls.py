from django.urls import path
from .views import (
    RankAPIView,
    AnalyzeJDAPIView,
    CandidateListAPIView,
    RankingListAPIView,
    RankingExportAPIView,
)

urlpatterns = [
    path("rank/", RankAPIView.as_view(), name="rank"),
    path("analyze-jd/", AnalyzeJDAPIView.as_view(), name="analyze-jd"),
    path("candidates/", CandidateListAPIView.as_view(), name="candidates"),
    path("rankings/", RankingListAPIView.as_view(), name="rankings"),
    path("rankings/export/", RankingExportAPIView.as_view(), name="rankings-export"),
]
