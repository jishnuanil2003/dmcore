from django import forms
from .models import AudioRecord, KeywordConfig ,BottleAdd


ALLOWED_AUDIO_EXTENSIONS = ['.mp3', '.wav', '.m4a', '.ogg', '.flac', '.webm', '.mp4', '.opus', '.aac', '.wma', '.amr']
MAX_FILE_SIZE_MB = 25


class AudioUploadForm(forms.ModelForm):
    class Meta:
        model = AudioRecord
        fields = ['audio_file']
        widgets = {
            'audio_file': forms.FileInput(attrs={
                'accept': 'audio/*',
                'class': 'form-file',
            }),
        }

    def clean_audio_file(self):
        f = self.cleaned_data.get('audio_file')
        if f:
            import os
            ext = os.path.splitext(f.name)[1].lower()
            if ext not in ALLOWED_AUDIO_EXTENSIONS:
                raise forms.ValidationError(
                    f"Unsupported format '{ext}'. Allowed: {', '.join(ALLOWED_AUDIO_EXTENSIONS)}"
                )
            if f.size > MAX_FILE_SIZE_MB * 1024 * 1024:
                raise forms.ValidationError(
                    f"File too large ({f.size / (1024*1024):.1f} MB). Max allowed: {MAX_FILE_SIZE_MB} MB."
                )
        return f


class KeywordForm(forms.ModelForm):
    class Meta:
        model = KeywordConfig
        fields = ['keyword', 'is_active']
        widgets = {
            'keyword': forms.TextInput(attrs={
                'placeholder': 'Enter keyword...',
                'class': 'form-input',
            }),
        }

    def clean_keyword(self):
        return self.cleaned_data['keyword'].lower().strip()


class FilterForm(forms.Form):

    bucket = forms.ModelChoiceField(
        queryset=BottleAdd.objects.all(),
        required=False,
        empty_label="All Bottles"
    )

    status = forms.ChoiceField(
        choices=[('', 'All Status')] + AudioRecord.STATUS_CHOICES,
        required=False
    )

    keyword = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search by name, phone...',
            'class': 'form-input',
        })
    )

    has_keywords = forms.BooleanField(
        required=False,
        label='Only with keywords detected'
    )