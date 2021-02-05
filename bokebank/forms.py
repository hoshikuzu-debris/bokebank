from django import forms

from .models import Department, User, Question, Answer

class AnswerForm(forms.ModelForm):
    
    class Meta:
        model = Answer
        fields = ['question', 'panelist', 'text']