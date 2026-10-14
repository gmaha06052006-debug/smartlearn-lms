from django import forms
from .models import Assignment, AssignmentSubmission


class AssignmentSubmissionForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ['file', 'notes']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control sl-input', 'id': 'file'}),
            'notes': forms.Textarea(attrs={'class': 'form-control sl-input', 'rows': 4, 'placeholder': 'Add notes, comments or links for your instructor...', 'id': 'notes'}),
        }


class AssignmentCreateForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['course', 'title', 'description', 'due_date', 'max_score', 'attachment']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-select sl-input'}),
            'title': forms.TextInput(attrs={'class': 'form-control sl-input', 'placeholder': 'Assignment title'}),
            'description': forms.Textarea(attrs={'class': 'form-control sl-input', 'rows': 5, 'placeholder': 'Provide instructions and requirements...'}),
            'due_date': forms.DateTimeInput(attrs={'class': 'form-control sl-input', 'type': 'datetime-local'}),
            'max_score': forms.NumberInput(attrs={'class': 'form-control sl-input'}),
            'attachment': forms.FileInput(attrs={'class': 'form-control sl-input'}),
        }


class AssignmentGradeForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ['score', 'feedback', 'status']
        widgets = {
            'score': forms.NumberInput(attrs={'class': 'form-control sl-input', 'step': '0.5'}),
            'feedback': forms.Textarea(attrs={'class': 'form-control sl-input', 'rows': 4, 'placeholder': 'Constructive feedback for the student...'}),
            'status': forms.Select(attrs={'class': 'form-select sl-input'}),
        }
