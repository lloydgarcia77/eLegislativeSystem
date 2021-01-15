from django import forms 
from elegislative_app.models import User
from elegislative_app import models

 
class RegisterForm(forms.ModelForm):  

    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    dob = forms.DateField(
        widget=forms.DateInput(
            format='%m/%d/%Y',
            attrs={
                'id': 'dob',
                'type': 'text',
                'class': 'form-control pull-right',
                'placeholder': 'Date of birth',
                'readonly':'readonly',
            }
        ),
        input_formats=('%m/%d/%Y', )
    )

    class Meta:
        model = User
        fields = ("email", "f_name", "m_name", "l_name", "gender","dob" ,"age", "address", "image",)

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)

        self.fields['email'].widget.attrs = {
            'type': 'text',
            'class': 'form-control',
            'placeholder': 'E-Mail',
        }

        self.fields['f_name'].widget.attrs = {
            'type': 'text',
            'class': 'form-control',
            'placeholder': 'First Name',
        }

        self.fields['m_name'].widget.attrs = {
            'type': 'text',
            'class': 'form-control',
            'placeholder': 'Middle Name',
        }

        self.fields['l_name'].widget.attrs = {
            'type': 'text',
            'class': 'form-control',
            'placeholder': 'Last Name',
        }

        self.fields['gender'].widget.attrs = {
            'type': 'text',
            'class': 'form-control select2',
            'placeholder': 'Gender',
        }

        self.fields['age'].widget.attrs = {
            'type': 'text',
            'class': 'form-control',
            'placeholder': 'Age',
        }

        self.fields['address'].widget.attrs = {
            'type': 'text',
            'class': 'form-control',
            'placeholder': 'Address',
        } 

        self.fields['password1'].widget.attrs = {
            'type': 'text',
            'class': 'form-control',
            'placeholder': 'Password',
        }

        self.fields['password2'].widget.attrs = {
            'type': 'text',
            'class': 'form-control',
            'placeholder': 'Confirm Password',
        }

    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = User.objects.filter(email=email)
        if qs.exists():
            raise forms.ValidationError("E-mail is taken")
        return email

    def clean_password2(self):
        """ 
        http://www.learningaboutelectronics.com/Articles/How-to-check-a-password-in-Django.php
        from django.contrib.auth.hashers import check_password 
        def changepassword(requests):

            currentpassword= request.user.password #user's current password

            form = ChangePasswordform(request.POST or None)

            if form.is_valid():
                currentpasswordentered= form.cleaned_data.get("lastpassword")
                password1= form.cleaned_data.get("newpassword1")
                password2= form.cleaned_data.get("newpassword2")

                matchcheck= check_password(currentpasswordentered, currentpassword)

            if matchcheck:
                #change password code
        """
        # Check that the two password entries match
        # add more complexity
        # upper lower
        # lenght
        # special chars
        # Non repeatable
        # common dict password
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if len(password1) < 8 and len(password2) < 8:
            raise forms.ValidationError("Password is too short!")
        else:
            if password1 and password2 and password1 != password2:
                raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(RegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class AgendaForm(forms.ModelForm):
    class Meta:
        model = models.AgendaModel
        exclude = ("date_filed","status","is_signed","hard_copy")

    def __init__(self, *args, **kwargs):
        super(AgendaForm, self).__init__(*args, **kwargs)

        self.fields['no'].widget.attrs = {
            'type': 'text',
            'class': 'form-control',
            'placeholder': 'Agenda No',
            'required': 'required',
        }

        self.fields['title'].widget.attrs = {
            'type': 'text',
            'class': 'form-control',
            'placeholder': 'Title',
            'required': 'required',
        }

        self.fields['version'].widget.attrs = {
            'type': 'text',
            'class': 'form-control',
            'placeholder': 'Version',
            'required': 'required',
        }

        self.fields['author'].widget.attrs = {
            'type': 'text',
            'class': 'form-control',
            'placeholder': 'author',
            'required': 'required',
        }

        self.fields['content'].widget.attrs = { 
            'id': 'compose_textarea',
            'class': 'form-control', 
            'style': 'height: 300px',
            'required': 'required',
        }

class EditAgendaForm(forms.ModelForm):
    class Meta:
        model = models.AgendaModel
        exclude = ("date_filed",)
    def __init__(self, *args, **kwargs):
        super(EditAgendaForm, self).__init__(*args, **kwargs)

        self.fields['no'].widget.attrs = {
            'type': 'text',
            'class': 'form-control',
            'placeholder': 'Agenda No',
            'required': 'required',
        }

        self.fields['title'].widget.attrs = {
            'type': 'text',
            'class': 'form-control',
            'placeholder': 'Title',
            'required': 'required',
        }

        self.fields['version'].widget.attrs = {
            'type': 'text',
            'class': 'form-control',
            'placeholder': 'Version',
            'required': 'required',
        }

        self.fields['author'].widget.attrs = {
            'type': 'text',
            'class': 'form-control',
            'placeholder': 'author',
            'required': 'required',
        }

        self.fields['content'].widget.attrs = { 
            'id': 'compose_textarea',
            'class': 'form-control', 
            'style': 'height: 300px',
            'required': 'required',
        }

        self.fields['status'].widget.attrs = { 
            'class': 'form-control select2', 
            'style': 'width: 100%', 
        }

class ResolutionForm(forms.ModelForm):
    class Meta:
        model = models.ResolutionModel
        exclude = ("agenda_fk","date_filed","status","is_signed","hard_copy")

    def __init__(self, *args, **kwargs):
        super(ResolutionForm, self).__init__(*args, **kwargs)

        self.fields['no'].widget.attrs = {
            'type': 'text',
            'class': 'form-control',
            'placeholder': 'Resolution No',
            'required': 'required',
        }

        self.fields['title'].widget.attrs = {
            'type': 'text',
            'class': 'form-control',
            'placeholder': 'Title',
            'required': 'required',
        }

        self.fields['version'].widget.attrs = {
            'type': 'text',
            'class': 'form-control',
            'placeholder': 'Version',
            'required': 'required',
        }

        self.fields['author'].widget.attrs = {
            'type': 'text',
            'class': 'form-control',
            'placeholder': 'author',
            'required': 'required',
        }

        self.fields['content'].widget.attrs = { 
            'id': 'compose_textarea',
            'class': 'form-control', 
            'style': 'height: 300px',
            'required': 'required',
        }

class EditResolutionForm(forms.ModelForm):
    class Meta:
        model = models.ResolutionModel
        exclude = ("agenda_fk","date_filed",)
    def __init__(self, *args, **kwargs):
        super(EditResolutionForm, self).__init__(*args, **kwargs)

        self.fields['no'].widget.attrs = {
            'type': 'text',
            'class': 'form-control',
            'placeholder': 'Resolution No',
            'required': 'required',
        }

        self.fields['title'].widget.attrs = {
            'type': 'text',
            'class': 'form-control',
            'placeholder': 'Title',
            'required': 'required',
        }

        self.fields['version'].widget.attrs = {
            'type': 'text',
            'class': 'form-control',
            'placeholder': 'Version',
            'required': 'required',
        }

        self.fields['author'].widget.attrs = {
            'type': 'text',
            'class': 'form-control',
            'placeholder': 'author',
            'required': 'required',
        }

        self.fields['content'].widget.attrs = { 
            'id': 'compose_textarea',
            'class': 'form-control', 
            'style': 'height: 300px',
            'required': 'required',
        }

        self.fields['status'].widget.attrs = { 
            'class': 'form-control select2', 
            'style': 'width: 100%', 
        }

class OrdinanceForm(forms.ModelForm):
    class Meta:
        model = models.OrdinanceModel
        exclude = ("agenda_fk","date_filed","status","is_signed","hard_copy")

    def __init__(self, *args, **kwargs):
        super(OrdinanceForm, self).__init__(*args, **kwargs)

        self.fields['no'].widget.attrs = {
            'type': 'text',
            'class': 'form-control',
            'placeholder': 'Resolution No',
            'required': 'required',
        }

        self.fields['title'].widget.attrs = {
            'type': 'text',
            'class': 'form-control',
            'placeholder': 'Title',
            'required': 'required',
        }

        self.fields['version'].widget.attrs = {
            'type': 'text',
            'class': 'form-control',
            'placeholder': 'Version',
            'required': 'required',
        }

        self.fields['author'].widget.attrs = {
            'type': 'text',
            'class': 'form-control',
            'placeholder': 'author',
            'required': 'required',
        }

        self.fields['content'].widget.attrs = { 
            'id': 'compose_textarea',
            'class': 'form-control', 
            'style': 'height: 300px',
            'required': 'required',
        }

class EditOrdinanceForm(forms.ModelForm):
    class Meta:
        model = models.OrdinanceModel
        exclude = ("agenda_fk","date_filed",)
    def __init__(self, *args, **kwargs):
        super(EditOrdinanceForm, self).__init__(*args, **kwargs)

        self.fields['no'].widget.attrs = {
            'type': 'text',
            'class': 'form-control',
            'placeholder': 'Resolution No',
            'required': 'required',
        }

        self.fields['title'].widget.attrs = {
            'type': 'text',
            'class': 'form-control',
            'placeholder': 'Title',
            'required': 'required',
        }

        self.fields['version'].widget.attrs = {
            'type': 'text',
            'class': 'form-control',
            'placeholder': 'Version',
            'required': 'required',
        }

        self.fields['author'].widget.attrs = {
            'type': 'text',
            'class': 'form-control',
            'placeholder': 'author',
            'required': 'required',
        }

        self.fields['content'].widget.attrs = { 
            'id': 'compose_textarea',
            'class': 'form-control', 
            'style': 'height: 300px',
            'required': 'required',
        }

        self.fields['status'].widget.attrs = { 
            'class': 'form-control select2', 
            'style': 'width: 100%', 
        }
