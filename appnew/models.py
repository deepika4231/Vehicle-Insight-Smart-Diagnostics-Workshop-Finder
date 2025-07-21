from django.db import models
from django.core.validators import RegexValidator
# Create your models here.
class login(models.Model):
    email=models.EmailField(unique=True)
    password=models.CharField(max_length=100)
    user_type=models.CharField(max_length=100)
    status = models.IntegerField(
        choices=[(0, 'Pending'), (1, 'Accepted'), (2, 'Rejected')],
        default=0)
class Users(models.Model):
    name = models.CharField(max_length=100)
    contact = models.CharField(
        max_length=10,
        validators=[RegexValidator(regex=r'^\d{10}$', message="Contact number must be exactly 10 digits.")]
    )
    userid = models.ForeignKey(login, on_delete=models.CASCADE)
    Adress = models.CharField(max_length=225)
    registered_at = models.DateTimeField(auto_now_add=True)

class workshop(models.Model):
    workshopname = models.CharField(max_length=100)
    adress = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    wcontactno = models.CharField(
        max_length=10,
        validators=[RegexValidator(regex=r'^\d{10}$', message="Contact number must be exactly 10 digits.")]
    )
    BRN=models.CharField(max_length=50,default=0)
    workshopid = models.ForeignKey(login, on_delete=models.CASCADE)
    average_rating = models.FloatField(default=0.0)
    
    average_rating = models.FloatField(default=0.0)

    # New fields
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def update_average_rating(self):
        from appnew.models import WorkshopReview
        reviews = WorkshopReview.objects.filter(workshop=self)
        if reviews.exists():
            avg = reviews.aggregate(models.Avg('rating'))['rating__avg']
            self.average_rating = round(avg, 2)
        else:
            self.average_rating = 0.0
        self.save()
        
class WorkshopSlot(models.Model):
    workshop = models.ForeignKey(workshop, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    is_available = models.BooleanField(default=True)

class Appoinment(models.Model):
    vehiclectegory=models.CharField(max_length=100)
    company=models.CharField(max_length=100)
    modelname=models.CharField(max_length=100)
    issue = models.CharField(max_length=100)
    userid=models.ForeignKey(Users,on_delete=models.CASCADE)
    workshopid=models.ForeignKey(workshop,on_delete=models.CASCADE)
    service=models.CharField(max_length=200 )
    scheduled_date=models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=100)
    slot=models.ForeignKey(WorkshopSlot, on_delete=models.CASCADE)
    service_charge=models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount=models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status=models.CharField(max_length=1,default=0)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

class servicechargepayment(models.Model):
    cardno=models.CharField(max_length=100,
        validators=[RegexValidator(regex=r'^\d{16}$', message="Card number must be exactly 16 digits.")])
    name=models.CharField(max_length=100)
    expirymonth=models.IntegerField()
    expiryyear=models.IntegerField()
    cvv=models.IntegerField(
        validators=[RegexValidator(regex=r'^\d{4}$', message="CVV must be exactly 4 digits.")])
    amount=models.DecimalField(max_digits=10, decimal_places=2)
    current_date=models.DateTimeField(auto_now_add=True)
    userid=models.ForeignKey(Users, on_delete=models.CASCADE)
    appoinmentid=models.ForeignKey(Appoinment,on_delete=models.CASCADE)

class experts(models.Model):
    name=models.CharField(max_length=100)
    contact=models.CharField(max_length=10,
        validators=[RegexValidator(regex=r'^\d{10}$', message="Contact number must be exactly 10 digits.")])
    userid=models.ForeignKey(login,on_delete=models.CASCADE)
    experience=models.IntegerField(default=1)
    experience_certificate = models.ImageField(upload_to='experiences_certificates/' , blank=True, null=True)

class ExpertSlot(models.Model):
    expert = models.ForeignKey(experts, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)

class SlotBooking(models.Model):
    slot = models.ForeignKey(ExpertSlot, on_delete=models.CASCADE)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    booked_at = models.DateTimeField(auto_now_add=True)
    url=models.CharField(max_length=100,default=0)

class complaint(models.Model):
    complaint_text = models.TextField()
    complaint_subject = models.CharField(max_length=200)
    complaint_date = models.DateTimeField(auto_now_add=True)
    complaint_user = models.ForeignKey(Users, on_delete=models.CASCADE)
    complaint_workshop = models.ForeignKey(workshop, on_delete=models.CASCADE)
    complaint_status = models.CharField(max_length=100, default='Pending')
    complaint_replay=models.CharField(max_length=100)

     # Add these fields
    


class parts(models.Model):
    part_name = models.CharField(max_length=100)
    part_number = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    vehicle_model = models.CharField(max_length=100)
    stock = models.IntegerField(default=0)
    part_year = models.CharField(max_length=100)
    part_price = models.DecimalField(max_digits=10, decimal_places=2)
    part_image = models.ImageField(upload_to='parts_images/')
class order(models.Model):
    order_date = models.DateTimeField(auto_now_add=True)
    part_id=models.ForeignKey(parts, on_delete=models.CASCADE)
    order_user = models.ForeignKey(Users, on_delete=models.CASCADE)
    order_quantity=models.IntegerField(default=1)
    payment_status=models.CharField(max_length=1,default=0)
    cancel_status=models.CharField(max_length=1,default=0)
    refund_status=models.CharField(max_length=1,default=0)
    payment_mode=models.CharField(max_length=100,default=0)
    order_status=models.CharField(max_length=1,default=0)
    
class payment(models.Model):
    cardno=models.CharField(max_length=100)
    name=models.CharField(max_length=100)
    expirymonth=models.IntegerField()
    expiryyear=models.IntegerField()
    cvv=models.IntegerField()
    amount=models.DecimalField(max_digits=10, decimal_places=2)
    current_date=models.DateTimeField(auto_now_add=True)
    userid=models.ForeignKey(Users, on_delete=models.CASCADE)
    orderid=models.ForeignKey(order,on_delete=models.CASCADE)
class refund(models.Model):
    refund_date = models.DateTimeField(auto_now_add=True)   
    refund_user = models.ForeignKey(Users, on_delete=models.CASCADE)
    refund_amount = models.DecimalField(default=0,max_digits=10, decimal_places=2)
    orderid=models.ForeignKey(order, on_delete=models.CASCADE)
    name=models.CharField(max_length=100)
    cardno=models.CharField(max_length=100)
    expirymonth=models.IntegerField(default=0)
    expiryyear=models.IntegerField(default=0)
    cvv=models.IntegerField()

class demobank(models.Model):
    name= models.CharField(max_length=100)
    cardno=models.CharField(max_length=100,
        validators=[RegexValidator(regex=r'^\d{16}$', message="Card number must be exactly 16 digits.")],unique=True)
    expirymonth=models.IntegerField()
    expiryyear=models.IntegerField()
    cvv=models.IntegerField(
        validators=[RegexValidator(regex=r'^\d{4}$', message="CVV must be exactly 4 digits.")])
    balance=models.DecimalField(max_digits=10, decimal_places=2)
    bank_name=models.CharField(max_length=100)
    branch_name=models.CharField(max_length=100, blank=True, null=True)
    ifsc_code=models.CharField(max_length=11)

    


class WorkshopReview(models.Model):
    workshop = models.ForeignKey('workshop', on_delete=models.CASCADE)
    user = models.ForeignKey('Users', on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)






