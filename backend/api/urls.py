from django.urls import path
from .views import (
    RankAPIView,
    AnalyzeJDAPIView,
    CandidateListAPIView,
    RankingListAPIView,
    RankingDetailAPIView,
    RankingExportAPIView,
    DashboardStatsAPIView,
    TalentInsightsAPIView,
    RankingExcelExportAPIView,
)

urlpatterns = [
    path("rank/", RankAPIView.as_view(), name="rank"),
    path("analyze-jd/", AnalyzeJDAPIView.as_view(), name="analyze-jd"),
    path("candidates/", CandidateListAPIView.as_view(), name="candidates"),
    path("rankings/", RankingListAPIView.as_view(), name="rankings"),
    path("rankings/<int:pk>/", RankingDetailAPIView.as_view(), name="ranking-detail"),
    path("rankings/export/", RankingExportAPIView.as_view(), name="rankings-export"),
    path("stats/", DashboardStatsAPIView.as_view(), name="stats"),
    path("talent-insights/", TalentInsightsAPIView.as_view(), name="talent-insights"),
    path("export/<int:ranking_id>/", RankingExcelExportAPIView.as_view(), name="ranking-excel-export"),
]

