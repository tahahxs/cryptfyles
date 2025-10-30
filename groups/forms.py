"""
Group Forms
"""
from django import forms
from .models import FileGroup
from users.models import CustomUser


class GroupCreateForm(forms.ModelForm):
    """Form for creating a new group"""
    
    class Meta:
        model = FileGroup
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter group name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe what this group is for',
                'rows': 4
            })
        }


class GroupEditForm(forms.ModelForm):
    """Form for editing an existing group"""
    
    class Meta:
        model = FileGroup
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4
            })
        }


class AddMemberForm(forms.Form):
    """Form for adding a member to a group"""
    
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter username to add'
        })
    )
    
    def __init__(self, *args, **kwargs):
        self.group = kwargs.pop('group', None)
        super().__init__(*args, **kwargs)
    
    def clean_username(self):
        """Validate username exists and is not already a member"""
        username = self.cleaned_data.get('username')
        
        # Check if user exists
        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            raise forms.ValidationError('User with this username does not exist.')
        
        # Check if already a member
        if self.group and self.group.is_member(user):
            raise forms.ValidationError('This user is already a member of the group.')
        
        return username
