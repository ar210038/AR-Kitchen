# shop/forms.py
from django import forms
from .models import Order, FAQ , Feedback
from django.utils import timezone

class CheckoutForm(forms.ModelForm):
    
    delivery_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'min': timezone.now().date()}),
        help_text="Select your preferred delivery/pickup date"
    )
    
    class Meta:
        model = Order
        fields = ['name', 'phone', 'address', 'delivery_method', 'delivery_date', 'note']
        widgets = {
           'note': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Any special instructions?'}),
            'address': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Full address (required for delivery)'}),
        }
    def clean(self):
        cleaned_data = super().clean()
        method = cleaned_data.get('delivery_method')
        address = cleaned_data.get('address', '')

        if method == 'delivery' and not address.strip():
            self.add_error('address', "Address is required for home delivery.")
        return cleaned_data
    
# shop/forms.py
from django import forms
from .models import CustomCakeRequest

class CustomCakeForm(forms.ModelForm):
    class Meta:
        model = CustomCakeRequest
        fields = ['name', 'phone', 'email', 'flavor', 'weight', 'delivery_date','message', 'design_image', 'note']
        widgets = {
            'delivery_date': forms.DateInput(attrs={'type': 'date', 'min': timezone.now().strftime('%Y-%m-%d')}),
            'message': forms.Textarea(attrs={'rows': 3}),
            'note': forms.Textarea(attrs={'rows': 2}),
            'design_image': forms.FileInput(attrs={'accept': 'image/*'}),
        }
        
# shop/forms.py
class FAQForm(forms.ModelForm):
    class Meta:
        model = FAQ
        fields = ['question', 'asked_by']
        widgets = {
            'question': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Ask your question...'}),
            'asked_by': forms.TextInput(attrs={'placeholder': 'Your Name (optional)'}),
        }        
        
# shop/forms.py
class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['name', 'email', 'message', 'rating', 'photo']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Share your experience...'}),
            'rating': forms.RadioSelect,
        }        