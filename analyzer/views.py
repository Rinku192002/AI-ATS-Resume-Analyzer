import json

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required

from .forms import RegisterForm, ResumeUploadForm
from .models import Resume
from .utils import extract_text_from_pdf
from .ai import analyze_resume, match_resume_with_job


# ==========================
# Home
# ==========================
def home(request):
    return render(request, "home.html")


# ==========================
# Register
# ==========================
def register(request):

    if request.method == "POST":

        form = RegisterForm(request.POST)

        if form.is_valid():

            user = form.save()

            login(request, user)

            return redirect("dashboard")

    else:

        form = RegisterForm()

    return render(request, "register.html", {
        "form": form
    })


# ==========================
# Login
# ==========================
def user_login(request):

    if request.method == "POST":

        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():

            login(request, form.get_user())

            return redirect("dashboard")

    else:

        form = AuthenticationForm()

    return render(request, "login.html", {
        "form": form
    })


# ==========================
# Logout
# ==========================
def user_logout(request):

    logout(request)

    return redirect("home")


# ==========================
# Dashboard
# ==========================
@login_required
def dashboard(request):

    resumes = Resume.objects.filter(
        user=request.user
    ).order_by("-uploaded_at")

    context = {
        "resumes": resumes,
        "total_resumes": resumes.count(),
    }

    return render(
        request,
        "dashboard.html",
        context
    )


# ==========================
# Upload Resume
# ==========================
@login_required
def upload_resume(request):

    extracted_text = ""
    ai_result = None
    job_match = None

    if request.method == "POST":

        form = ResumeUploadForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            resume = form.save(commit=False)
            resume.user = request.user
            resume.save()

            job_description = request.POST.get(
                "job_description",
                ""
            )

            if resume.resume.name.lower().endswith(".pdf"):

                with open(
                    resume.resume.path,
                    "rb"
                ) as pdf_file:

                    extracted_text = extract_text_from_pdf(pdf_file)

                # ATS Analysis
                ai_result = analyze_resume(extracted_text)
                print("AI RESULT =", ai_result)
                print("\n========== AI RESULT ==========")
                print(ai_result)
                print("================================")

                if isinstance(ai_result, dict):

                    resume.ai_analysis = json.dumps(
                        ai_result,
                        indent=4
                    )

                    ats = ai_result.get("ats_score", 0)

                    try:
                        ats = str(ats).replace("%", "")
                        ats = ats.replace("/100", "").strip()
                        resume.ats_score = int(ats)
                    except:
                        resume.ats_score = 0

                # Job Match
                if job_description.strip():

                    job_match = match_resume_with_job(
                        extracted_text,
                        job_description
                    )

                    print("\n========== JOB MATCH ==========")
                    print(job_match)

                    if isinstance(job_match, dict):

                        resume.job_match_analysis = json.dumps(
                            job_match,
                            indent=4
                        )

                        score = job_match.get(
                            "match_score",
                            0
                        )

                        try:
                            score = str(score).replace("%", "").strip()
                            resume.job_match_score = int(score)
                        except:
                            resume.job_match_score = 0

                resume.save()

            return render(
                request,
                "upload_resume.html",
                {
                    "form": ResumeUploadForm(),
                    "text": extracted_text,
                    "ai_result": ai_result,
                    "job_match": job_match,
                },
            )

    else:

        form = ResumeUploadForm()

    return render(
        request,
        "upload_resume.html",
        {
            "form": form,
            "text": extracted_text,
            "ai_result": ai_result,
            "job_match": job_match,
        },
    )