from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Post, Comment


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    referral_code = forms.CharField(max_length=20, required=False, widget=forms.HiddenInput())

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            ref_code = self.cleaned_data.get('referral_code', '')
            referred_by = None
            if ref_code:
                try:
                    referred_by = Profile.objects.get(referral_code=ref_code)
                except Profile.DoesNotExist:
                    pass
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.referred_by = referred_by
            profile.save()
        return user


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'avatar', 'cover_image', 'location', 'website', 'birth_date']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Write something about yourself...'}),
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'website': forms.URLInput(attrs={'placeholder': 'https://yourwebsite.com'}),
            'location': forms.TextInput(attrs={'placeholder': 'City, Country'}),
        }


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': "What's on your mind?",
                'class': 'post-input',
            }),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.TextInput(attrs={
                'placeholder': 'Write a comment...',
                'class': 'comment-input',
            }),
        }
