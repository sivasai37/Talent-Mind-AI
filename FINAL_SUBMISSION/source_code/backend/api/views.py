from io import StringIO

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView

from .models import Candidate, RankingJob, RankingResult
from .serializers import CandidateSerializer, RankingJobSerializer
from .services import ranking
from .services.jd_understanding import analyze_job_description


class RankAPIView(APIView):
    """POST /api/rank/  { title?, job_description, top_k }"""

    def post(self, request):
        data = request.data
        title = data.get("title", "")
        job_description = data.get("job_description", "")
        top_k = int(data.get("top_k", 10))

        jd_struct = analyze_job_description(job_description, title=title)
        ranking.build_index()
        results = ranking.search_job(job_description, top_k=top_k, job_struct=jd_struct)

        job = RankingJob.objects.create(
            title=title,
            job_description=job_description,
            job_analysis=jd_struct,
        )

        for idx, item in enumerate(results, start=1):
            candidate = get_object_or_404(Candidate, pk=item["candidate_id"])
            RankingResult.objects.create(
                ranking_job=job,
                candidate=candidate,
                rank=idx,
                semantic_score=item.get("semantic_score", 0.0),
                skill_score=item.get("skill_score", 0.0),
                experience_score=item.get("experience_score", 0.0),
                recruitability_score=item.get("recruitability_score", 0.0),
                llm_score=item.get("llm_score", 0.0),
                final_score=item.get("final_score", 0.0),
                strengths=item.get("strengths", []),
                weaknesses=item.get("weaknesses", []),
                missing_skills=item.get("missing_skills", []),
                recruiter_summary=item.get("recruiter_ai", {}).get("recruiter_summary", ""),
                payload=item,
            )

        serializer = RankingJobSerializer(job)
        data = serializer.data
        data["job_structure"] = jd_struct
        return Response(data, status=status.HTTP_200_OK)


class AnalyzeJDAPIView(APIView):
    """POST /api/analyze-jd/ { title?, job_description } -> structured JD"""

    def post(self, request):
        data = request.data
        text = data.get("job_description", "")
        title = data.get("title")
        jd_struct = analyze_job_description(text, title=title)
        return Response(jd_struct, status=status.HTTP_200_OK)


class CandidateListAPIView(APIView):
    def get(self, request):
        candidates = Candidate.objects.all().order_by("full_name")
        serializer = CandidateSerializer(candidates, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RankingListAPIView(APIView):
    def get(self, request):
        jobs = RankingJob.objects.order_by("-created_at")
        serializer = RankingJobSerializer(jobs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RankingExportAPIView(APIView):
    def get(self, request):
        job_id = request.query_params.get("job_id")
        export_format = request.query_params.get("format")
        if not job_id:
            # default to latest ranking job
            job = RankingJob.objects.order_by("-created_at").first()
            if job is None:
                return Response({"detail": "No ranking job available to export."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            job = get_object_or_404(RankingJob, pk=job_id)
        buffer = StringIO()
        if export_format == "submission":
            buffer.write(
                "candidate_id,full_name,final_score,recommendation,strengths,weaknesses,missing_skills,recruiter_summary\n"
            )
            for result in job.results.order_by("rank"):
                strength_text = " | ".join(result.strengths)
                weakness_text = " | ".join(result.weaknesses)
                missing_text = " | ".join(result.missing_skills)
                recommendation = result.payload.get("recruiter_ai", {}).get("recommendation", "")
                buffer.write(
                    f"{result.candidate.id},{result.candidate.full_name},{result.final_score},{recommendation},{strength_text},{weakness_text},{missing_text},{result.recruiter_summary}\n"
                )
        else:
            buffer.write(
                "candidate_id,full_name,semantic_score,skill_score,experience_score,recruitability_score,llm_score,final_score,recommendation,strengths,weaknesses,missing_skills,recruiter_summary\n"
            )
            for result in job.results.order_by("rank"):
                strength_text = " | ".join(result.strengths)
                weakness_text = " | ".join(result.weaknesses)
                missing_text = " | ".join(result.missing_skills)
                recommendation = result.payload.get("recruiter_ai", {}).get("recommendation", "")
                buffer.write(
                    f"{result.candidate.id},{result.candidate.full_name},{result.semantic_score},{result.skill_score},{result.experience_score},{result.recruitability_score},{result.llm_score},{result.final_score},{recommendation},{strength_text},{weakness_text},{missing_text},{result.recruiter_summary}\n"
                )
        response = HttpResponse(buffer.getvalue(), content_type="text/csv")
        response["Content-Disposition"] = f"attachment; filename=ranked_candidates_{job.id}.csv"
        return response
