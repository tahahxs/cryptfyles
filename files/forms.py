"""
File Upload Form
"""
from django import forms


class FileUploadForm(forms.Form):
    """Form for uploading encrypted files"""
    
    file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '*/*'  # Accept all file types
        }),
        help_text='Maximum file size: 10GB'
    )
    
    def clean_file(self):
        """Validate file size"""
        file = self.cleaned_data.get('file')
        
        if file:
            # Check file size (10GB limit)
            max_size = 10 * 1024 * 1024 * 1024  # 10GB in bytes
            
            if file.size > max_size:
                raise forms.ValidationError(
                    f'File too large. Maximum size is 10GB. '
                    f'Your file is {file.size / (1024**3):.2f}GB.'
                )
        
        return file
