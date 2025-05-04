# from django import forms
# from .models import UserEvents

# class UserEventForm(forms.ModelForm):
#     class Meta:
#         model = UserEvents
#         fields = ['title', 'description', 'venue', 'date', 'time', 'category', 'apply_link', 'host_name', 'host_email', 'host_phone']
#         widgets = {
#             'date': forms.DateInput(attrs={'type': 'date'}),
#             'time': forms.TimeInput(attrs={'type': 'time'}),
#         }


from django import forms
from .models import UserEvents, Category, Department

class UserEventForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label="Select Category",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        empty_label=None,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    host_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly'
        })
    )

    host_email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly'
        })
    )

    host_phone = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly'
        })
    )

    class Meta:
        model = UserEvents
        fields = ['title', 'description', 'venue', 'date', 'time', 'image', 'category', 
                 'apply_link', 'host_name', 'host_email', 'host_phone', 'department']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            # Lock department field for non-superusers
            if not user.is_superuser:
                self.fields['department'].widget.attrs['disabled'] = 'disabled'
                if user.department:
                    self.fields['department'].queryset = Department.objects.filter(id=user.department.id)
                    self.fields['department'].initial = user.department

            # Set initial values for host fields
            self.fields['host_name'].initial = user.first_name
            self.fields['host_email'].initial = user.email
            self.fields['host_phone'].initial = user.phone

            # Disable host fields from being edited
            self.fields['host_name'].widget.attrs['readonly'] = True
            self.fields['host_email'].widget.attrs['readonly'] = True
            self.fields['host_phone'].widget.attrs['readonly'] = True

from django import forms
from .models import EventPost  # Import the correct model

class EventPostForm(forms.ModelForm):
    class Meta:
        model = EventPost
        fields = ['event_title', 'image', 'caption']  # Match with your model fields

