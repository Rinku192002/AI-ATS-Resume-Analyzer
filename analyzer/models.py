from django.db import models
from django.contrib.auth.models import User

class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resume = models.FileField(upload_to='resumes/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # AI Analysis Fields
    ats_score = models.IntegerField(default=0)
    job_match_score = models.IntegerField(default=0)
    ai_analysis = models.TextField(blank=True)
    job_match_analysis = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"