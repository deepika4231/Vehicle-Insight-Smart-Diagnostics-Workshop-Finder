from django import forms
from . models import *
class UserForm(forms.ModelForm):
    class Meta:
        model=Users
        
        fields=['name','contact','Adress']
       

class Loginform(forms.ModelForm):
    password=forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model=login
        fields=['email','password']
class workshopform(forms.ModelForm):
    class Meta:
        model=workshop
        fields=['workshopname','BRN','adress','district','city','wcontactno', 'latitude', 'longitude']
        widgets = {
            'latitude': forms.TextInput(attrs={'readonly': 'readonly'}),
            'longitude': forms.TextInput(attrs={'readonly': 'readonly'}),
        }
class Loginform1(forms.Form):
    email=forms.CharField(max_length=100)
    password=forms.CharField(widget=forms.PasswordInput())
class emailform(forms.ModelForm):
    class Meta:
        model=login
        fields=['email']
class searchform(forms.Form):
    search=forms.CharField(max_length=100)
class vehicleissueform(forms.ModelForm):
    # status_choice=[('pending','Pending',),('confirmed','Confirmed'),('completed','Completed')]
    # status=forms.ChoiceField(initial='pending', choices=status_choice)
    class Meta:
        model=Appoinment
        fields=['vehiclectegory','company','modelname','issue','latitude', 'longitude']
        widgets = {
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }
class SlotForm(forms.ModelForm):
    class Meta:
        model = Appoinment
        fields = ['slot']

class progresscommentform(forms.ModelForm):
    class Meta:
        model=Appoinment
        fields=['service']
class progressform(forms.ModelForm):
    status_choice=[('pending','Pending',),('accepted','Accepted'),('rejected','Rejected'),('processing','Processing'),('completed','Completed')]
    status=forms.ChoiceField(initial='pending', choices=status_choice)
    class Meta:
        model=Appoinment
        fields=['status']

class complaintform(forms.ModelForm):
    class Meta:
        model=complaint
        fields=['complaint_subject','complaint_text']
       
class adminreplayform(forms.ModelForm):
    status_choice=[('pending','Pending',),('accepted','Accepted'),('completed','Completed')]
    complaint_status=forms.ChoiceField(initial='pending', choices=status_choice)
    class Meta:
        model=complaint
        fields=['complaint_replay','complaint_status']
class partsform(forms.ModelForm):
    class Meta:
        model=parts
        fields=['part_name','part_number','company','vehicle_model','part_year','part_price','stock','part_image']
class QuantityForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        label="Quantity",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter quantity'}),initial=1)
class cardPaymentForm(forms.ModelForm):
   class Meta:
       model=payment
       fields=['cardno','name','expirymonth','expiryyear','cvv']
class refundPaymentForm(forms.ModelForm):
   class Meta:
       model=refund
       fields=['cardno','name','expirymonth','expiryyear','cvv']

class expertform(forms.ModelForm):
    class Meta:
        model=experts
        fields=['name','contact','experience', 'experience_certificate']

class ExpertSlotForm(forms.ModelForm):
    class Meta:
        model = ExpertSlot
        fields = ['date', 'start_time', 'end_time']
class WorkshopSlotForm(forms.ModelForm):
    class Meta:
        model = WorkshopSlot
        fields = ['date', 'time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }
class ServiceChargePaymentForm(forms.ModelForm):
   class Meta:
       model=servicechargepayment
       fields=['cardno','name','expirymonth','expiryyear','cvv']

class WorkshopReviewForm(forms.ModelForm):
    class Meta:
        model = WorkshopReview
        fields = ['rating', 'comment']
class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(label="Email")
    contact_number = forms.CharField(label="Contact Number", max_length=10)

class ResetPasswordForm(forms.Form):
    new_password = forms.CharField(label="New Password", widget=forms.PasswordInput)
    confirm_password = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

class demobankform(forms.ModelForm):
    class Meta:
        model = demobank
        fields = ['name', 'cardno', 'expirymonth', 'expiryyear', 'cvv', 'ifsc_code', 'bank_name', 'branch_name', 'balance']

