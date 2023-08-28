from django import forms
from .models import Profile, Leave
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class CreateUserForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': "pl-8 p-3 my-3 w-full focus:outline-gray-300 rounded-sm border border-gray-200",
        'type':"text",
        "placeholder": "username"
    }
    ))
    email = forms.CharField(widget=forms.TextInput(attrs={
        'class': "pl-8 p-3 my-3 w-full focus:outline-gray-300 rounded-sm border border-gray-200",
        'type':"email",
        "placeholder": "email"
    }
    ))
    password1 = forms.CharField(widget=forms.TextInput(attrs={
        'class': "pl-8 p-3 my-3 w-full focus:outline-gray-300 rounded-sm border border-gray-200",
        'type':"password",
        "placeholder": "password"
    }
    ))
    password2 = forms.CharField(widget=forms.TextInput(attrs={
        'class': "pl-8 p-3 my-3 w-full focus:outline-gray-300 rounded-sm border border-gray-200",
        'type':"password",
        "placeholder": "comfirm password"
    }
    ))

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class UserUpdateForm(forms.ModelForm):
    email = forms.CharField(widget=forms.TextInput(attrs={
        'class': "bg-[#7fddd21e] py-3 px-1 w-full md:w-[100%] focus:outline-[#5c9f98cb]",
        'type':"email",
    }
    ))
    class Meta:
        model = User
        fields = ['email']


class EditProfileForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': "bg-[#7fddd21e] py-3 px-1 w-full md:w-[100%] focus:outline-[#5c9f98cb]",
        'type':"text",
    }
    ))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': "bg-[#7fddd21e] py-3 px-1 w-full md:w-[100%] focus:outline-[#5c9f98cb]",
        'type':"text",
    }
    ))
    phone = forms.CharField(widget=forms.TextInput(attrs={
        'class': "bg-[#7fddd21e] py-3 px-1 w-full md:w-[100%] focus:outline-[#5c9f98cb]",
        'type':"text",
    }
    ))
    position = forms.CharField(widget=forms.TextInput(attrs={
        'class': "bg-[#7fddd21e] py-3 px-1 w-full md:w-[100%] focus:outline-[#5c9f98cb]",
        'type':"text",
    }
    ))
    profile_pic = forms.ImageField(label="Select an Image", widget=forms.ClearableFileInput(attrs={'class': 'p-2 mr-2 rounded-md border border-gray-200'}))

    class Meta:
        model = Profile
        fields = "__all__"
        exclude = ["user", "role"]


class LeaveCreationForm(forms.ModelForm):
    class Meta:
        model = Leave
        fields = ['user', 'leave_type', 'start_date', 'end_date', 'note']