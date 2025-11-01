# shop/forms.py
from django import forms
from .models import Order, CustomCake , FAQ , Feedback

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['name', 'phone', 'address', 'delivery_method', 'payment_method', 'note']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'note': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Special instructions...'}),
        }

class CustomCakeForm(forms.ModelForm):
    class Meta:
        model = CustomCake
        fields = '__all__'
        widgets = {
            'message': forms.Textarea(attrs={'rows': 2}),
            'note': forms.Textarea(attrs={'rows': 3}),
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