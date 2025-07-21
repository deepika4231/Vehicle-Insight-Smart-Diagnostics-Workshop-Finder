from decimal import Decimal
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render,redirect,get_object_or_404
from .forms import*
from .models import *
from django.contrib import messages
from django.db.models import Q, Count
from django.db.models.functions import TruncMonth, TruncDate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import date, datetime
from django.utils import timezone



def adminhomepage(request):
    if 'adminid' not in request.session:
        return redirect('userlogin')

    total_orders = order.objects.filter(payment_status='1').count()
    total_workshops = workshop.objects.count()
    total_experts = experts.objects.count()
    total_users = Users.objects.count()
    pendingusers = login.objects.filter(status='0',user_type='user').count()
    pendingworkshops = login.objects.filter(status='0',user_type='workshop').count()
    pendingexperts = login.objects.filter(status='0',user_type='expert').count()
    complaints = complaint.objects.all()
    total_cancels = order.objects.filter(cancel_status='1').count()
    total_complaints = complaint.objects.count()
    orders_per_day = (
        order.objects.filter(payment_status='1')
        .annotate(day=TruncDate('order_date'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )
    order_days = [o['day'].strftime('%Y-%m-%d') for o in orders_per_day]
    order_day_counts = [o['count'] for o in orders_per_day]

    # Cancels per day for chart (aligned with order_days)
    cancels_per_day = (
        order.objects.filter(cancel_status='1')
        .annotate(day=TruncDate('order_date'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )
    cancel_day_dict = {c['day'].strftime('%Y-%m-%d'): c['count'] for c in cancels_per_day}
    cancel_day_count = [cancel_day_dict.get(day, 0) for day in order_days]
    orders = (
        order.objects.filter(payment_status='1')
        .annotate(month=TruncMonth('order_date'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    cancels = (
        order.objects.filter(cancel_status='1')
        .annotate(month=TruncMonth('order_date'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    labels = [o['month'].strftime('%b %Y') for o in orders]
    order_counts = [o['count'] for o in orders]
    cancel_counts = [next((c['count'] for c in cancels if c['month'] == o['month']), 0) for o in orders]

    total_order_parts = sum(order_day_counts)
    total_cancel_parts = sum(cancel_day_count)
    total_active_orders = order.objects.filter(payment_status='1', refund_status='0').count()
   
    total_notifications=pendingusers + pendingexperts +pendingworkshops + total_active_orders

    context = {
        'total_orders': total_orders,
        'total_workshops': total_workshops,
        'total_experts': total_experts,
        'total_users': total_users,
        'chart_labels': labels,
        'chart_orders': order_counts,
        'chart_cancels': cancel_counts,
        'complaints': complaints,
        'total_cancels': total_cancels,
        'total_complaints': total_complaints,
        'order_days': order_days,
        'order_day_counts': order_day_counts,
        'cancel_day_counts': cancel_day_count,
        'total_order_parts': total_order_parts,
        'total_cancel_parts': total_cancel_parts,
        'total_active_orders': total_active_orders,
        'total_notifications': total_notifications,
        'pendinguser' : pendingusers,
        'pendingworkshop' : pendingworkshops,
        'pendingexpert' : pendingexperts,
    }
    return render(request, 'adminhomepage.html', context)

def admin_reply_complaint(request, complaint_id):
   
    if request.method == 'POST':
        comp = get_object_or_404(complaint, id=complaint_id)
        reply = request.POST.get('complaint_replay')
        if reply:
            comp.complaint_replay = reply
            comp.save()
        return redirect('adminhomepage')  
    else:
        return redirect('adminhomepage')

def admin_u_details(request):
    if 'adminid' not in request.session:
        return redirect('userlogin')
    users=Users.objects.all()
    return render(request,'admin_u_details.html' ,{'users':users}) 
def admin_w_details(request):
    if 'adminid' not in request.session:
        return redirect('userlogin')
    users=workshop.objects.all()
    return render(request, 'admin_w_details.html',{'users':users})
def admin_e_details(request):
    if 'adminid' not in request.session:
        return redirect('userlogin')
    users=experts.objects.all()
    return render(request, 'admin_e_details.html',{'users':users})
def index(request):
    return render(request,'index.html')
def userpage(request):
    if 'userid' not in request.session:
        return redirect('userlogin')
    log=request.session.get('userid')
    logid=get_object_or_404(Users,userid=log)
    return render(request,'userpage.html',{'log':logid})
def workshoppage(request):
    if 'workshopid' not in request.session:
        return redirect('userlogin')
    log=request.session.get('workshopid')
    logid=get_object_or_404(workshop,workshopid=log)
    return render(request,'workshoppage.html',{'log':logid})
def expertpage(request):
    if 'expertid' not in request.session:
        return redirect('userlogin')
    log=request.session.get('expertid')
    logid=get_object_or_404(experts,userid=log)
    return render(request,'expertpage.html',{'log':logid})
def accepted(request, id):
    var = get_object_or_404(login, id=id)
    var.status = '1' 
    var.save()
    return redirect('admin_w_details')

def rejected(request, id):  
    var = get_object_or_404(login, id=id)
    var.status = '2'  
    var.save()
    return redirect('admin_w_details')
def accepteduser(request, id):
    var = get_object_or_404(login, id=id)
    var.status = '1'  
    var.save()
    return redirect('admin_u_details')

def rejecteduser(request, id):  
    var = get_object_or_404(login, id=id)
    var.status = '2'  
    var.save()
    messages.success(request, "User has been rejected.")
    return redirect('admin_u_details')
def acceptedexpert(request, id):
    var = get_object_or_404(login, id=id)
    var.status = '1'  
    var.save()
    return redirect('admin_e_details')

def rejectedexpert(request, id):  
    var = get_object_or_404(login, id=id)
    var.status = '2'  
    var.save()
    messages.success(request, "User has been rejected.")
    return redirect('admin_e_details')
def userregister(request):
    if request.method == 'POST':
        form1=UserForm(request.POST)
        form2=Loginform(request.POST)
        if form1.is_valid() and form2.is_valid():
            flag=form2.save(commit=False)
            flag.user_type='user'
            flag.save()
            flag1=form1.save(commit=False)
            flag1.userid=flag
            flag1.save()
            return redirect('/')
    else:

        form1=UserForm()
        form2=Loginform()
    return render(request,'registerations.html',{'form1':form1,'form2':form2})
def adminregister(request):
    if request.method == 'POST':
    
        form=Loginform(request.POST)
        if form.is_valid():
            flag=form.save(commit=False)
            flag.user_type='admin'
            flag.status='1' 
            flag.save()
            
            return redirect('/')
    else:

        form2=Loginform()
    return render(request,'registeradmin.html',{'form2':form2})
def expertregister(request):
    if request.method == 'POST':
        form1=expertform(request.POST,request.FILES)
        form2=Loginform(request.POST)
        if form1.is_valid() and form2.is_valid():
            flag=form2.save(commit=False)
            flag.user_type='expert'
            flag.save()
            flag1=form1.save(commit=False)
            flag1.userid=flag
            flag1.save()
            return redirect('/')
    else:

        form1=expertform()
        form2=Loginform()
    return render(request,'registerations.html',{'form1':form1,'form2':form2})
  
def signup(request):
    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        email1 = request.POST.get('email')
        password = request.POST.get('password')
        contact = request.POST.get('contact')

        print(email1)
        print(password)

        if login.objects.filter(email=email1).exists():
            messages.error(request, "This email is already registered. Please use a different email.")
            return redirect('userlogin')

        login_obj = login.objects.create(
            email=email1,
            password=password,
            user_type=user_type,
            status='0'
        )

        if user_type == 'user':
            name = request.POST.get('user_name')
            print(name)
            address = request.POST.get('user_address')
            Users.objects.create(userid=login_obj, name=name, contact=contact, Adress=address)

        elif user_type == 'workshop':
            workshopname = request.POST.get('workshop_name')
            address = request.POST.get('w_address')
            district = request.POST.get('w_district')
            city = request.POST.get('w_city')
            BRNs = request.POST.get('workshop_BRN')
            latitude = request.POST.get('w_latitude')
            longitude = request.POST.get('w_longitude')
            workshop.objects.create(
                workshopid=login_obj,
                workshopname=workshopname,
                adress=address,
                district=district,
                city=city,
                wcontactno=contact,
                BRN=BRNs,
                latitude=latitude,
                longitude=longitude
            )


        elif user_type == 'expert':
            name = request.POST.get('expert_name')
            experience = request.POST.get('e_experience')
            experience_certificates = request.FILES.get('experience_certificate')
            experts.objects.create(
                userid=login_obj,
                name=name,
                experience=experience,
                contact=contact,
                experience_certificate=experience_certificates
            )

    messages.success(request, "Registration successful")
    return redirect('userlogin')



def workshopregister(request):
    if request.method == 'POST':
        form1=workshopform(request.POST)
        form2=Loginform(request.POST)
        if form1.is_valid() and form2.is_valid():
            flag=form2.save(commit=False)
            flag.user_type='workshop'
            flag.save()
            flag1=form1.save(commit=False)
            flag1.workshopid=flag
            flag1.save()
            return redirect('/')
    else:

        form1=workshopform()
        form2=Loginform()
    return render(request,'register.html',{'form1':form1,'form2':form2}) 

def userlogin(request):
    if request.method == 'POST':
        form = Loginform1(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                user = login.objects.get(email=email)
                if user.password == password:
                    if user.user_type == 'user':
                        if user.status != 1:
                            messages.error(request, 'Your account has not been approved.')
                            return redirect('userlogin')
                        request.session['usertype'] = user.user_type
                        request.session['userid'] = user.id
                        request.session['email'] = user.email
                        return redirect('../userpage')
                    elif user.user_type == 'workshop':
                        if user.status != 1:
                            messages.error(request, 'Your account has not been approved.')
                            return redirect('userlogin')
                        request.session['workshoptype'] = user.user_type
                        request.session['workshopid'] = user.id
                        request.session['email'] = user.email
                        return redirect('../workshoppage')
                    elif user.user_type == 'expert':
                        if user.status != 1:
                            messages.error(request, 'Your account has not been approved.')
                            return redirect('userlogin')
                        request.session['experttype'] = user.user_type
                        request.session['expertid'] = user.id
                        request.session['email'] = user.email
                        return redirect('../expertpage')
                    elif user.user_type == 'admin':
                        request.session['admintype'] = user.user_type
                        request.session['adminid'] = user.id
                        request.session['email'] = user.email
                        return redirect('../adminhomepage')
                else:
                    messages.error(request, 'invalid password')
            except login.DoesNotExist:
                messages.error(request, 'user does not exist')
    else:
        form = Loginform1()
    return render(request, 'login.html', {'form': form})
def logout_view(request):
    request.session.flush()
    return redirect('./') 

def edituser(request):
    if 'email' in request.session:
        id = request.session['userid']
        user = get_object_or_404(login, id=id)
        userdata = Users.objects.get(userid=user)
        if request.method == 'POST':
           form = UserForm(request.POST,instance=userdata)
           
           if form.is_valid():
               form.save()
               
               return redirect('userpage')
        else:

            form = UserForm(instance=userdata)
            
        return render(request,'edituserprofile.html',{'form':form})
    else:
        return redirect('userlogin')
def editexpert(request):
    if 'email' in request.session:
        id = request.session['expertid']
        user = get_object_or_404(login, id=id)
        userdata = experts.objects.get(userid=user)
        if request.method == 'POST':
           form = expertform(request.POST ,request.FILES, instance=userdata)
           if form.is_valid():
               form.save()
             
               return redirect('expertpage')
        else:

            form = expertform(instance=userdata)
        return render(request,'editprofile.html',{'form':form})
    else:
        return redirect('userlogin')
def editworkshop(request):
    if 'email' in request.session:
        id = request.session['workshopid']
        user = get_object_or_404(login, id=id)
        try:
            userdata = workshop.objects.get(workshopid=user)
        except workshop.DoesNotExist:
            messages.error(request, "Workshop details not found.")
            return redirect('workshoppage')
        print(id)
        if request.method == 'POST':
            form = workshopform(request.POST, instance=userdata)
            if form.is_valid():
                form.save()
               
                return redirect('workshoppage')
            else:
                messages.error(request, "Please correct the errors below.")
        else:
            form = workshopform(instance=userdata)

        return render(request, 'editworkshopprofile.html', {'form': form})
    else:
        
        return redirect('userlogin')
def workshopdetailpage(request):
    if 'email' not in request.session:
        return redirect('userlogin')
    if request.method == 'POST':
        form = searchform(request.POST)
        if form.is_valid():
            search = form.cleaned_data['search']
            workshops = workshop.objects.filter(
                Q(workshopname__icontains=search) |
                Q(district__icontains=search) |
                Q(city__icontains=search)
            )
        else:
            workshops = workshop.objects.all()
    else:
        form = searchform()  
        workshops = workshop.objects.all()  

    return render(request, 'workshopdetailpage.html', {'form': form, 'workshops': workshops})


def appointment(request, slot_id, workshopid):
    if 'email' in request.session:
        id = request.session['userid']
        user = get_object_or_404(login, id=id)
        userdata = Users.objects.get(userid=user)
        work = get_object_or_404(workshop, id=workshopid)  
        slot = get_object_or_404(WorkshopSlot, id=slot_id)

        if request.method == 'POST':
            form = vehicleissueform(request.POST)
            if form.is_valid():
                issue = form.save(commit=False)
                issue.userid = userdata
                issue.workshopid = work
                issue.status = 'pending'
                issue.slot = slot
                issue.save()
                slot.is_available = False
                slot.save()
                return redirect('viewappoinment')
        else:
            form = vehicleissueform()
        return render(request, 'appointment.html', {'form': form})
    else:
        return redirect('userlogin')
def viewappoinment(request):
    if 'userid' not in request.session:
        return redirect('userlogin')
    log=request.session.get('userid')
    logid=get_object_or_404(Users,userid=log)
    issues = Appoinment.objects.filter(userid=logid).order_by('-scheduled_date')
    return render(request,'viewappoinment.html',{'issues': issues})
def edit_appoinment(request, complaint_id):
    if 'userid' not in request.session:
        return redirect('userlogin')
    user_id = request.session['userid']
    complaint = get_object_or_404(Appoinment, id=complaint_id, userid__userid=user_id)
    workshop_obj = complaint.workshopid
    available_slots = WorkshopSlot.objects.filter(workshop=workshop_obj, is_available=True) | WorkshopSlot.objects.filter(id=complaint.slot.id)
    if request.method == 'POST':
        issue_form = vehicleissueform(request.POST, instance=complaint)
        slot_id = request.POST.get('slotid')
        if issue_form.is_valid() and slot_id:
            old_slot = complaint.slot
            new_slot = get_object_or_404(WorkshopSlot, id=slot_id)
            issue = issue_form.save(commit=False)
            issue.slot = new_slot
            issue.save()
            if old_slot != new_slot:
                old_slot.is_available = True
                old_slot.save()
                new_slot.is_available = False
                new_slot.save()
            return redirect('viewappoinment')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        issue_form = vehicleissueform(instance=complaint)
    return render(request, 'edit_appoinment.html', {
        'issue_form': issue_form,
        'slots': available_slots.distinct(),
        'current_slot_id': complaint.slot.id if complaint.slot else None,
    })
def all_workshops_with_slots(request):
    if 'userid' not in request.session:
        return redirect('userlogin')

    today = date.today()
    now = datetime.now().time()
    user_id = request.session['userid']

    complaints = Appoinment.objects.filter(
        userid__userid=user_id,
        status__in=['pending', 'accepted', 'processing']
    ).count()

    workshops = workshop.objects.all()
    workshop_slots = []

    for ws in workshops:
        future_slots = WorkshopSlot.objects.filter(
            workshop=ws
        ).filter(
            Q(date__gt=today) |
            Q(date=today, time__gte=now)
        ).order_by('date', 'time')

        if future_slots.exists():
            workshop_slots.append({'workshop': ws, 'slots': future_slots})

    return render(request, 'all_workshops_with_slots.html', {
        'workshop_slots': workshop_slots,
        'today': today,
        'now': now,
        'complaints': complaints
    })
# def all_workshops_with_slots(request):
#     if 'userid' not in request.session:
#         return redirect('userlogin')
    
#     today = date.today()
#     now = datetime.now().time()  # ← extract current time only
    
#     user_id = request.session['userid']
#     complaints = Appoinment.objects.filter(
#         userid__userid=user_id,
#         status__in=['pending', 'accepted', 'processing']
#     ).count()

#     workshops = workshop.objects.all()
#     workshop_slots = []
#     for ws in workshops:
#         slots = WorkshopSlot.objects.filter(
#             workshop=ws,
#             date__gte=today
#         )| WorkshopSlot.objects.filter(
#             workshop=ws,
#             date=today,
#             time__gte=now
#         ).order_by('date', 'time')
#         if slots.exists():
#             workshop_slots.append({'workshop': ws, 'slots': slots})

#     return render(request, 'all_workshops_with_slots.html', {
#         'workshop_slots': workshop_slots,
#         'today': today,
#         'now': now,  # now is a time object
#         'complaints': complaints
#     })
def workshop_slots(request, workshop_id):
    if 'userid' not in request.session: 
        return redirect('userlogin')
    user_id = request.session['userid']
    complaints = Appoinment.objects.filter(userid__userid=user_id, status__in=['pending', 'accepted','processing']).count()

    workshop_obj = get_object_or_404(workshop, id=workshop_id)
    now = datetime.now()
    
    slots = WorkshopSlot.objects.filter(
        workshop=workshop_obj,
        is_available=True
    ).filter(
        date__gt=now.date()
    ) | WorkshopSlot.objects.filter(
        workshop=workshop_obj,
        is_available=True,
        date=now.date(),
        time__gte=now.time()
    )
    slots = slots.order_by('date', 'time')
    return render(request, 'workshop_slots.html', {
        'workshop': workshop_obj,
        'slots': slots,
        'complaints': complaints,
        'today': now.date()
    })
def delete_appoinment(request, complaint_id):
    if 'userid' not in request.session:
        return redirect('userlogin')
    user = get_object_or_404(Appoinment,id=complaint_id)
    user.slot.is_available = True
    user.slot.save()
    user.delete()
    return redirect('viewappoinment')
def workshopappoinmentview(request):
    if 'workshopid' not in request.session:
        return redirect('userlogin')
    log=request.session.get('workshopid')
    logid=get_object_or_404(workshop,workshopid=log)
    issues = Appoinment.objects.filter(workshopid=logid).order_by('-scheduled_date')
    return render(request,'workshopappoinmentview.html',{'issues': issues})
def update_service(request, issue_id):
    if request.method == 'POST':
        service = request.POST.get('service')
        issue = get_object_or_404(Appoinment, id=issue_id)  # Replace with your model name
        issue.service = service
        issue.save()
        messages.success(request, "Service updated successfully.")
    return redirect('workshopappoinmentview')  # Use your actual view name

# def add_service_charge(request, id):
#     appointment = get_object_or_404(Appoinment, id=id)

#     if request.method == 'POST':
#         amount = request.POST.get('amount')
#         try:
#             appointment.service_charge = amount
#             appointment.amount = Decimal(amount) 
#             appointment.save()
#             messages.success(request, "Service charge added successfully.")
#         except Exception as e:
#             messages.error(request, "Error adding service charge.")
#     return redirect('workshopappoinmentview')

def addprogress(request, complaint_id):
    if 'workshopid' not in request.session:
        return redirect('loginuser')

    workshop_id = request.session['workshopid']
    complaint = get_object_or_404(Appoinment, id=complaint_id, workshopid__workshopid=workshop_id)

    old_status = complaint.status.lower()
    old_payment_status = complaint.payment_status  

    if request.method == 'POST':
        form = progressform(request.POST, instance=complaint)
        if form.is_valid():
            new_status = form.cleaned_data['status']

            # Rule 1: Prevent reverting to 'pending' from 'accepted'
            if old_status == 'accepted' and new_status in ['pending']:
                messages.error(request, "You cannot revert status from 'Accepted' to 'Pending'.")
                return redirect('addprogress', complaint_id=complaint_id)
            if old_status == 'processing' and new_status in ['pending', 'accepted','rejected']:
                messages.error(request, "You cannot revert status from 'Processing' to 'Pending' or 'Rejected'.")
                return redirect('addprogress', complaint_id=complaint_id)
            if old_status == 'completed' and new_status in ['pending', 'accepted', 'processing','rejected']:
                messages.error(request, "You cannot revert status from 'Completed' to 'Pending', 'Accepted', 'Processing', or 'Rejected'.")
                return redirect('addprogress', complaint_id=complaint_id)
            if old_status == 'rejected' and new_status in ['pending', 'accepted', 'processing','completed']:
                messages.error(request, "You cannot revert status from 'Rejected' to 'Pending', 'Accepted',completed, or 'Processing'.")
                return redirect('addprogress', complaint_id=complaint_id)
            if old_status =='pending' and new_status in ['completed','processing']:
                messages.error(request, "You cannot revert status from 'Pending' to 'Accepted' or 'Rejected'.")
                return redirect('addprogress', complaint_id=complaint_id)

            # Rule 2: Prevent setting to 'pending' or 'rejected' if payment is completed
            if old_payment_status == '1' and new_status in ['pending', 'rejected']:
                messages.error(request, "Status cannot be changed to 'Pending' or 'Rejected' after payment is completed.")
                return redirect('addprogress', complaint_id=complaint_id)
            if old_payment_status == '0' and new_status in ['processing', 'completed']:
                messages.error(request, "Status cannot be changed to 'Processing' or 'Completed' after payment is not completed.")
                return redirect('addprogress', complaint_id=complaint_id)
            form.save()
            messages.success(request, "Work progress updated successfully.")
            return redirect('workshopappoinmentview')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = progressform(instance=complaint)

    return render(request, 'progressaddingworkshop.html', {'form': form})
def update_service(request, issue_id):
    if request.method == 'POST':
        service = request.POST.get('service')
        issue = get_object_or_404(Appoinment, id=issue_id)  # Replace with your actual model
        issue.service = service
        issue.save()
        messages.success(request, "Progress comment updated.")
    return redirect('workshopappoinmentview')
    

def complaintadding(request, id):
    if 'userid' not in request.session:
        return redirect('userlogin')
    log = request.session.get('userid')
    comp= get_object_or_404(Appoinment, id=id)  
    if request.method == 'POST':
        form = complaintform(request.POST)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.complaint_user = comp.userid
            complaint.complaint_workshop = comp.workshopid           
            complaint.save()
            
            return redirect('workcomplaint')
    else:
        form = complaintform()
    return render(request, 'registercomplaint.html', {'form': form})
def complaintview(request):
    if 'adminid' not in request.session:
        return redirect('userlogin')
    comps=complaint.objects.all()
    return render(request,'complaintview.html' ,{'comps':comps})
def workcomplaint(request):
    if 'userid' not in request.session:
        return redirect('userlogin')
    log=request.session.get('userid')    
    logid=get_object_or_404(Users,userid=log)
    issues = complaint.objects.filter(complaint_user=logid)
    print(issues)
    return render(request,'complaintuserview.html' ,{'issues': issues})

def edit_complaint(request, complaint_id):
    if 'userid' not in request.session:
        return redirect('loginuser')  

    comp = get_object_or_404(complaint, id=complaint_id)

    if request.method == 'POST':
        form = complaintform(request.POST, instance=comp)
        if form.is_valid():
            form.save()
            return redirect('workcomplaint')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = complaintform(instance=comp)

    return render(request, 'editcomplaint.html', {'form': form})

def delete_complaint(request, id):
    if 'userid' not in request.session:
        return redirect('userlogin')
    user = get_object_or_404(complaint,id=id)
    user.delete()
    return redirect('workcomplaint')
def adminreplaycomplaint(request, complaint_id):
    complaints = get_object_or_404(complaint, id=complaint_id)
    if request.method == 'POST':
        form = adminreplayform(request.POST, instance=complaints)
        if form.is_valid():
            form.save()
            
            return redirect('complaintview')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = adminreplayform(instance=complaints)
    return render(request, 'progressadding.html', {'form': form})
def partsadd(request):
    if 'adminid' not in request.session:
        return redirect('userlogin')
    if request.method == 'POST':
        form = partsform(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('partlist')    
    else:
        form = partsform()
    return render(request, 'partsadding.html', {'form': form})  
def partlist(request):
    if 'adminid' not in request.session:
        return redirect('userlogin')
    ppart = parts.objects.all()
    return render(request, 'partlist.html', {'ppart': ppart})
def delete_part(request, id):
    if 'adminid' not in request.session:
        return redirect('userlogin')
    part = get_object_or_404(parts, id=id)
    part.delete()
    return redirect('partlist')

def edit_part(request, id):
    if 'adminid' not in request.session:
        return redirect('userlogin')
    part = get_object_or_404(parts, id=id)
    if request.method == 'POST':   
        form = partsform(request.POST, request.FILES, instance=part)
        if form.is_valid():
            form.save()
            
            return redirect('partlist')
    else:
        form = partsform(instance=part)
    return render(request, 'partsediting.html', {'form': form})

def partsview(request):
    if 'userid' not in request.session:
        return redirect('userlogin')
    if request.method == 'POST':
        form = searchform(request.POST)
        if form.is_valid():
            search = form.cleaned_data['search']
            part = parts.objects.filter(part_name__icontains=search) | parts.objects.filter(company__icontains=search) | parts.objects.filter(vehicle_model__icontains=search) | parts.objects.filter(part_year__icontains=search) | parts.objects.filter(part_price__icontains=search)
        else:
            part = parts.objects.all()
    else:
        form = searchform()  
        part = parts.objects.all()  

    return render(request, 'partsview.html', {'form': form, 'part': part})



def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            contact_number = form.cleaned_data['contact_number']
            try:
                user_login = login.objects.get(email=email)
                user_type = user_login.user_type  # Assuming this field exists

                match = False
                if user_type == 'user':
                    match = Users.objects.filter(userid=user_login, contact=contact_number).exists()
                elif user_type == 'workshop':
                    match = workshop.objects.filter(userid=user_login, contact=contact_number).exists()
                elif user_type == 'expert':
                    match = experts.objects.filter(userid=user_login, contact=contact_number).exists()

                if match:
                    request.session['reset_login_id'] = user_login.id
                    messages.success(request, "Validation successful. Please set your new password.")
                    return redirect('reset_password')
                else:
                    messages.error(request, "Contact number does not match our records for this user type.")
            except login.DoesNotExist:
                messages.error(request, "Email not found.")
    else:
        form = ForgotPasswordForm()
    return render(request, 'forgot_password.html', {'form': form})

def reset_password(request):
    login_id = request.session.get('reset_login_id')
    if not login_id:
        return redirect('forgot_password')
    user_login = get_object_or_404(login, id=login_id)
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            confirm_password = form.cleaned_data['confirm_password']
            if new_password == confirm_password:
                user_login.password = new_password  # If not using Django's auth User
                user_login.save()
                del request.session['reset_login_id']
                
                return redirect('userlogin')
            else:
                messages.error(request, "Passwords do not match.")
    else:
        form = ResetPasswordForm()
    return render(request, 'reset_password.html', {'form': form})




def orderforparts(request, partid):
    if 'email' in request.session:
        id = request.session['userid']
        user = get_object_or_404(login, id=id)
        userdata = Users.objects.get(userid=user)
        part = get_object_or_404(parts, id=partid)

        
        if order.objects.filter(part_id=part, order_user=userdata ,order_status='1').exists():
            messages.warning(request, "This part is already in your cart.")
            return redirect('cartdetails')
        else:
            order.objects.create(part_id=part, order_user=userdata ,order_status='1')
            return redirect('cartdetails')
    else:
        return redirect('userlogin')
def cartdetails(request):
    if 'userid' not in request.session:
        return redirect('userlogin')
    log=request.session.get('userid')    
    logid=get_object_or_404(Users,userid=log)
    items= order.objects.filter(order_user=logid,order_status=1)
    return render(request,'cartdetails.html',{'items': items})
def deletecart(request, id):
    if 'userid' not in request.session:
        return redirect('userlogin')
    order_item = get_object_or_404(order, id=id)
    order_item.delete()
    return redirect('cartdetails')
def partsorder(request):
    if 'adminid' not in request.session:
        return redirect('userlogin')
    items= order.objects.filter(payment_status='1', refund_status='0')
    return render(request,'partsorder.html',{'items': items})
def quantity_selection(request, partid):
    part = get_object_or_404(order, id=partid)
    st= part.part_id.stock
    if request.method == 'POST':
        form = QuantityForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            if quantity > st:
                return redirect('quantity_selection', partid=partid)
            else:
                part.order_quantity = quantity
                part.save()
                return redirect('buying', partid=partid)  
    else:
        form = QuantityForm()

    return render(request, 'quantity_selection.html', {'form': form, 'part': part, 'st': st})

def partsorderhistory(request):
    if 'adminid' not in request.session:
        return redirect('userlogin')
    items= order.objects.filter(payment_status='1')
    paymentdones=payment.objects.filter(orderid__in=items)
    refundones=refund.objects.filter(orderid__in=items)
    return render(request,'partsorderhistory.html',{'items': items,'paymentdones': paymentdones , 'refundones': refundones})

# def buying(request, partid):
#     if 'email' in request.session:
#         id = request.session['userid']
#         user = get_object_or_404(login, id=id)
#         userdata = Users.objects.get(userid=user)
#         order_item = get_object_or_404(order, id=partid, order_user=userdata)
#         part = order_item.part_id  
#         total_amount = part.part_price * order_item.order_quantity

#         if request.method == 'POST':
#             form1 = cardPaymentForm(request.POST)
#             if form1.is_valid():
                
#                 cardno = form1.cleaned_data['cardno']
#                 expirymonth = form1.cleaned_data['expirymonth']
#                 expiryyear = form1.cleaned_data['expiryyear']
#                 cvv = form1.cleaned_data['cvv']

               
#                 try:
#                     bank_account = demobank.objects.get(
#                         cardno=cardno,
#                         expirymonth=expirymonth,
#                         expiryyear=expiryyear,
#                         cvv=cvv
#                     )
#                 except demobank.DoesNotExist:
#                     return render(request, 'paymentindex.html', {'form1': form1})

               
#                 if bank_account.balance < total_amount:
#                     messages.error(request, "Insufficient balance in your demo bank account.")
#                     return render(request, 'paymentindex.html', {'form1': form1})

                
#                 bank_account.balance -= total_amount
#                 bank_account.save()

#                 pay = form1.save(commit=False)
#                 pay.amount = total_amount
#                 pay.userid = userdata
#                 pay.orderid = order_item
#                 pay.save()
#                 part.stock -= order_item.order_quantity
#                 part.save()
#                 return redirect('payment_process', partid=partid)
#             else:
#                 print("Form errors:", form1.errors)  
#         else:
#             form1 = cardPaymentForm()

#         return render(request, 'paymentindex.html', {'form1': form1})
#     else:
#         return redirect('loginuser')
def buying(request, partid):
    if 'email' in request.session:
        id = request.session['userid']
        user = get_object_or_404(login, id=id)
        userdata = Users.objects.get(userid=user)
        order_item = get_object_or_404(order, id=partid, order_user=userdata)
        part = order_item.part_id  
        total_amount = part.part_price * order_item.order_quantity

        if request.method == 'POST':
            form1 = cardPaymentForm(request.POST)
            if form1.is_valid():
                cardno = form1.cleaned_data['cardno']
                expirymonth = form1.cleaned_data['expirymonth']
                expiryyear = form1.cleaned_data['expiryyear']
                cvv = form1.cleaned_data['cvv']

                try:
                    bank_account = demobank.objects.get(
                        cardno=cardno,
                        expirymonth=expirymonth,
                        expiryyear=expiryyear,
                        cvv=cvv
                    )
                except demobank.DoesNotExist:
                    messages.error(request, "Bank account not found.")
                    return render(request, 'paymentindex.html', {'form1': form1})

                if bank_account.balance < total_amount:
                    messages.error(request, "Insufficient balance in your demo bank account.")
                    return render(request, 'paymentindex.html', {'form1': form1})
                bank_account.balance -= total_amount
                bank_account.save()
                try:
                    admin_account = demobank.objects.get(cardno='1000000000000000')
                    admin_account.balance += total_amount
                    admin_account.save()
                except demobank.DoesNotExist:
                    messages.error(request, "Admin account not found. Payment could not be processed.")
                    return render(request, 'paymentindex.html', {'form1': form1})
                pay = form1.save(commit=False)
                pay.amount = total_amount
                pay.userid = userdata
                pay.orderid = order_item
                pay.save()
                part.stock -= order_item.order_quantity
                part.save()

                return redirect('payment_process', partid=partid)
            else:
                print("Form errors:", form1.errors)
        else:
            form1 = cardPaymentForm()

        return render(request, 'paymentindex.html', {'form1': form1})
    else:
        return redirect('loginuser')

def payment_process(request, partid):
    if 'email' in request.session:
        id = request.session['userid']
        user = get_object_or_404(login, id=id)
        userdata = Users.objects.get(userid=user)
        order_item = get_object_or_404(order, id=partid, order_user=userdata)
        card_payment = payment.objects.filter(orderid=order_item).last()

        order_item.payment_status = '1'
        order_item.order_status = '0'
        order_item.save()

        return render(request, 'payment_process.html', {'order_item': order_item, 'card_payment': card_payment})
    else:
        return redirect('userlogin')


def cancelpaymentprocess(request, partid):
    if 'email' in request.session:
        id = request.session['userid']
        user = get_object_or_404(login, id=id)
        userdata = Users.objects.get(userid=user)
        order_item = get_object_or_404(order, id=partid, order_user=userdata)
        card_payment = payment.objects.filter(orderid=order_item).last()

        if card_payment:
            try:
               
                user_account = demobank.objects.get(cardno=card_payment.cardno)
                user_account.balance += card_payment.amount
                user_account.save()

               
                admin_account = demobank.objects.get(cardno='1000000000000000')
                if admin_account.balance >= card_payment.amount:
                    admin_account.balance -= card_payment.amount
                    admin_account.save()
                else:
                    messages.error(request, "Admin account has insufficient balance to process the refund.")
                    return redirect('cartdetails')

            except demobank.DoesNotExist:
                messages.error(request, "Bank account not found. Refund could not be processed.")
                return redirect('cartdetails')

            card_payment.delete()

       
        part = order_item.part_id
        part.stock += order_item.order_quantity
        part.save()

        order_item.order_quantity = 0
        order_item.payment_status = '0'
        order_item.order_status = '1'
        order_item.save()

        messages.success(request, "Payment canceled, stock restored, and refund processed.")
        return redirect('cartdetails')
    else:
        return redirect('userlogin')


# def orderdetails(request):
#     if 'userid' not in request.session:
#         return redirect('userlogin')
#     log = request.session.get('userid')    
#     logid = get_object_or_404(Users, userid=log)
#     items = order.objects.filter(order_user=logid, payment_status='1').exclude(cancel_status='1')
#     now = timezone.now()
#     for item in items:
#         item.cancel_disabled = item.payment_status == '1' and (now - item.order_date).days > 1
#     return render(request, 'orderdetails.html', {'items': items})

def orderdetails(request):
    if 'userid' not in request.session:
        return redirect('userlogin')
    log = request.session.get('userid')    
    logid = get_object_or_404(Users, userid=log)
   
    items = order.objects.filter(order_user=logid, payment_status='1').exclude(cancel_status='1').order_by('-order_date')
    now = timezone.now()
    for item in items:
        item.cancel_disabled = item.payment_status == '1' and (now - item.order_date).days > 30
    return render(request, 'orderdetails.html', {'items': items})

def cancelproduct(request, id):
    if 'userid' not in request.session:
        return redirect('userlogin')
    order_item = get_object_or_404(order, id=id)
    part = order_item.part_id

    try:
        part.stock += order_item.order_quantity  
        part.save()
        order_item.cancel_status = '1'
        order_item.save()
       
    except Exception as e:
        messages.error(request, f"An error occurred while updating stock: {e}")

    return redirect('canceldetails')
def canceldetails(request):
    if 'userid' not in request.session:
        return redirect('userlogin')
    log=request.session.get('userid')    
    logid=get_object_or_404(Users,userid=log)
    items= order.objects.filter(order_user=logid , cancel_status='1').order_by('-order_date')
    return render(request,'cancelproduct.html',{'items': items})

def refundpayment(request, id):
    order_item = get_object_or_404(order, id=id)
    part = order_item.part_id
    total_amount = part.part_price * order_item.order_quantity

    
    if order_item.refund_status == '1':
        messages.info(request, "Refund has already been processed for this order.")
        return redirect('refund_receipt', orderid=order_item.id)

    
    user_payment = payment.objects.filter(orderid=order_item).last()
    if not user_payment:
        messages.error(request, "Original payment record not found for this order.")
        return redirect('orderdetails')

    if request.method == 'POST':
        form = refundPaymentForm(request.POST)
        if form.is_valid():
            cardno = form.cleaned_data['cardno']
            expirymonth = form.cleaned_data['expirymonth']
            expiryyear = form.cleaned_data['expiryyear']
            cvv = form.cleaned_data['cvv']

            try:
                
                user_bank = demobank.objects.get(
                    cardno=str(user_payment.cardno),
                    expirymonth=user_payment.expirymonth,
                    expiryyear=user_payment.expiryyear,
                    cvv=str(user_payment.cvv)
                )
            except demobank.DoesNotExist:
                messages.error(request, "User's demo bank account not found for refund.")
                return render(request, 'paymentindex.html', {'form': form, 'order_item': order_item})

            try:
                
                bank_account = demobank.objects.get(
                    cardno=str(cardno),
                    expirymonth=expirymonth,
                    expiryyear=expiryyear,
                    cvv=str(cvv)
                )
            except demobank.DoesNotExist:
                messages.error(request, "Refund bank account not found.")
                return render(request, 'paymentindex.html', {'form': form, 'order_item': order_item})

            if bank_account.balance < total_amount:
                messages.error(request, "Insufficient balance in your demo bank account.")
                return render(request, 'paymentindex.html', {'form': form, 'order_item': order_item})

         
            bank_account.balance -= total_amount
            bank_account.save()

            user_bank.balance += total_amount
            user_bank.save()

            refund_entry = form.save(commit=False)
            refund_entry.refund_amount = total_amount
            refund_entry.refund_user = order_item.order_user
            refund_entry.orderid = order_item
            refund_entry.name = form.cleaned_data['name']
            refund_entry.cardno = str(form.cleaned_data['cardno'])
            refund_entry.expirymonth = expirymonth
            refund_entry.expiryyear = expiryyear
            refund_entry.cvv = str(cvv)
            refund_entry.save()

            order_item.refund_status = '1'
            order_item.save()

            part.stock += order_item.order_quantity
            part.save()

            messages.success(request, "Refund processed successfully.")
            return redirect('refund_receipt', orderid=order_item.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = refundPaymentForm()

    return render(request, 'paymentindex.html', {'form': form, 'order_item': order_item})




def refundlist(request):
    if 'adminid' not in request.session:
        return redirect('userlogin')
    items= order.objects.filter(refund_status='1')
    return render(request,'refundlist.html',{'items': items})

def refund_receipt(request, orderid):
    order_item = get_object_or_404(order, id=orderid)
    card_payment = get_object_or_404(refund, orderid=order_item)
    user_detail =get_object_or_404(payment, orderid=order_item)
    part = order_item.part_id 
    return render(request, 'refund_receipt.html', {'order_item': order_item,'user_detail': user_detail ,'card_payment': card_payment, 'part': part})
def refund_receiptuser(request, orderid):
    order_item = get_object_or_404(order, id=orderid)
    card_payment = get_object_or_404(refund, orderid=order_item)
    user_detail =get_object_or_404(payment, orderid=order_item)
    part = order_item.part_id 
    return render(request, 'refund_receiptuser.html', {'order_item': order_item,'user_detail':user_detail ,'card_payment': card_payment, 'part': part})

def payment_receipt(request, orderid):
    order_item = get_object_or_404(order, id=orderid)
    card_payment = get_object_or_404(payment, orderid=order_item)
    admin_account=get_object_or_404(demobank, cardno=1000000000000000)
    part = order_item.part_id 
    return render(request, 'payment_receipt.html', {'order_item': order_item,'admin_account':admin_account ,'card_payment': card_payment, 'part': part})
def payment_receiptuser(request, orderid):
    order_item = get_object_or_404(order, id=orderid)
    card_payment = get_object_or_404(payment, orderid=order_item)
    admin_account=get_object_or_404(demobank, cardno=1000000000000000)
    part = order_item.part_id 
    return render(request, 'payment_receiptuser.html', {'order_item': order_item,'admin_account':admin_account , 'card_payment': card_payment, 'part': part})


def videocall(request, video_call_id):
    
    return render(request,'videocall.html', {'pk': video_call_id})
@csrf_exempt
def save_appointment_url(request,pk): # Debugging
    if request.method == 'POST':
        data = json.loads(request.body)
        url = data.get('url') 
        if url:
            appointment = get_object_or_404(SlotBooking, pk=pk)
            appointment.url = url
           
            appointment.save()
            return JsonResponse({'success': True, 'message': 'URL saved successfully'})
        return JsonResponse({'success': False, 'message': 'No URL provided'}, status=400)
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)

def expertdetails(request):
    if request.method == 'POST':
        form = searchform(request.POST)
        if form.is_valid():
            search = form.cleaned_data['search']
            experts_list = experts.objects.filter(name__icontains=search) | experts.objects.filter(contact__icontains=search) | experts.objects.filter(experience__icontains=search)
        else:
            experts_list = experts.objects.all()
    else:
        form = searchform()  
        experts_list = experts.objects.all()  
    return render(request, 'expertdetails.html', {'form': form, 'experts_list':  experts_list})

def add_expert_slot(request):
    if 'expertid' not in request.session:
        return redirect('userlogin')
    expert = get_object_or_404(experts, userid=request.session['expertid'])
    if request.method == 'POST':
        form = ExpertSlotForm(request.POST)
        if form.is_valid():
            slot_date = form.cleaned_data['date']
            start_time = form.cleaned_data['start_time']
            end_time = form.cleaned_data['end_time']

            
            if start_time == datetime.strptime("00:00", "%H:%M").time():
                messages.error(request, "Starting time cannot be 12:00 AM.")
                return render(request, 'add_expert_slot.html', {'form': form})

            
            if start_time >= end_time:
                messages.error(request, "Starting time must be less than ending time!")
                return render(request, 'add_expert_slot.html', {'form': form})

            
            duration = (datetime.combine(slot_date, end_time) - datetime.combine(slot_date, start_time)).total_seconds() / 3600
            if duration > 4:
                messages.error(request, "Slot duration cannot exceed 4 hours.")
                return render(request, 'add_expert_slot.html', {'form': form})

            slot_datetime = datetime.combine(slot_date, start_time)
            if slot_datetime < datetime.now():
                messages.error(request, "Cannot add a slot in the past!")
                return render(request, 'add_expert_slot.html', {'form': form})

            overlap = ExpertSlot.objects.filter(
                expert=expert,
                date=slot_date
            ).filter(
                start_time__lt=end_time,
                end_time__gt=start_time
            ).exists()

            if overlap:
                messages.error(request, "This slot overlaps with an existing slot!")
                return render(request, 'add_expert_slot.html', {'form': form})

            slot = form.save(commit=False)
            slot.expert = expert
            slot.save()
            messages.success(request, "Slot added successfully.")
            return redirect('view_expert_slots')
    else:
        form = ExpertSlotForm()
    return render(request, 'add_expert_slot.html', {'form': form})



def view_expert_slots(request):
    if 'expertid' not in request.session:
        return redirect('userlogin')
    expert = get_object_or_404(experts, userid=request.session['expertid'])
    slots = ExpertSlot.objects.filter(expert=expert).order_by('date', 'start_time')
    return render(request, 'view_expert_slots.html', {'slots': slots,'today': date.today()})

def delete_expert_slot(request, slot_id):
    slot = get_object_or_404(ExpertSlot, id=slot_id)
   
    slot.delete()
       
    return redirect('view_expert_slots')



def available_slots(request):
    if 'userid' not in request.session:
        return redirect('userlogin')
    now = datetime.now()
    slots = ExpertSlot.objects.filter(
        is_booked=False
    ).filter(
        date__gt=now.date()
    ) | ExpertSlot.objects.filter(
        is_booked=False,
        date=now.date(),
        end_time__gte=now.time()
    )
    slots = slots.order_by('date', 'start_time')
    return render(request, 'available_slots.html', {'slots': slots, 'today': now.date()})

def viewexpertslot(request, id):
    if 'userid' not in request.session:
        return redirect('userlogin')
    now = datetime.now()
    slots = ExpertSlot.objects.filter(
        is_booked=False,
        expert=id
    ).filter(
        date__gt=now.date()
    ) | ExpertSlot.objects.filter(
        is_booked=False,
        expert=id,
        date=now.date(),
        end_time__gte=now.time()
    )
    slots = slots.order_by('date', 'start_time')
    return render(request, 'available_slots.html', {'slots': slots, 'today': now.date()})

    return render(request, 'available_slots.html', {'slots': slots,'today': date.today()})


def book_slot(request, slot_id):
    if 'userid' not in request.session:
        return redirect('userlogin')

    user = get_object_or_404(Users, userid=request.session['userid'])

    now = timezone.now().astimezone()  # Ensure timezone-aware comparison

    # Check if the user already has an active or upcoming booking
    active_bookings = SlotBooking.objects.filter(
        user=user,
        slot__date__gt=now.date()
    ) | SlotBooking.objects.filter(
        user=user,
        slot__date=now.date(),
        slot__end_time__gte=now.time()
    )

    if active_bookings.exists():
        messages.error(
            request,
            "You already have an active or upcoming expert booking. You can book the next slot only after your current booking's end time."
        )
        return redirect('available_slots')

    # Now fetch and book the slot if available
    slot = get_object_or_404(ExpertSlot, id=slot_id, is_booked=False)

    # Create the booking
    SlotBooking.objects.create(slot=slot, user=user)
    slot.is_booked = True
    slot.save()

    messages.success(
        request,
        "Slot booked successfully. View your booked slots in 'Booking Experts'."
    )
    return redirect('available_slots')

def view_slot_bookings(request):
    if 'expertid' not in request.session:
        return redirect('userlogin')
    expert = get_object_or_404(experts, userid=request.session['expertid'])
    bookings = SlotBooking.objects.filter(slot__expert=expert).order_by('-booked_at')
    return render(request, 'view_slot_bookings.html', {'bookings': bookings,'today': date.today(),
    'now_time': datetime.now().time(),})
def my_booked_slots(request):
    if 'userid' not in request.session:
        return redirect('userlogin')
    user = get_object_or_404(Users, userid=request.session['userid'])
    bookings = SlotBooking.objects.filter(user=user).order_by('-booked_at')
    # bookings = SlotBooking.objects.filter(user=user)
    return render(request, 'my_booked_slots.html', {'bookings': bookings,'today': date.today(),
    'now_time': datetime.now().time(),})

def cancel_slot_booking(request, booking_id):
    if 'userid' not in request.session:
        return redirect('userlogin')
    user = get_object_or_404(Users, userid=request.session['userid'])
    booking = get_object_or_404(SlotBooking, id=booking_id, user=user)
    slot = booking.slot
    slot.is_booked = False
    slot.save()
    booking.delete()
    messages.success(request, "Your slot booking has been cancelled.")
    return redirect('my_booked_slots')
def add_workshop_review(request, workshop_id):
    if 'userid' not in request.session:
        return redirect('userlogin')
    user = get_object_or_404(Users, userid=request.session['userid'])
    workshop_obj = get_object_or_404(workshop, id=workshop_id)
    review = WorkshopReview.objects.filter(user=user, workshop=workshop_obj).first()
    if request.method == 'POST':
        form = WorkshopReviewForm(request.POST, instance=review)
        if form.is_valid():
            review_obj = form.save(commit=False)
            review_obj.user = user
            review_obj.workshop = workshop_obj
            review_obj.save()     
            workshop_obj.update_average_rating()
            
            return redirect('workshopdetailpage')
    else:
        form = WorkshopReviewForm(instance=review)
    return render(request, 'add_workshop_review.html', {'form': form, 'workshop': workshop_obj})
def workshopreview(request, workshop_id):
    if 'userid' not in request.session:
        return redirect('userlogin')
    workshop_obj = get_object_or_404(workshop, id=workshop_id)
    reviews = WorkshopReview.objects.filter(workshop=workshop_obj).select_related('user')
    return render(request, 'workshop_reviews.html', {
        'workshop': workshop_obj,
        'reviews': reviews
    })
def viewreview(request):
    if 'workshopid' not in request.session:
        return redirect('workshoplogin')  
    workshop_obj = get_object_or_404(workshop, workshopid=request.session['workshopid'])
    reviews = WorkshopReview.objects.filter(workshop=workshop_obj).select_related('user')
    return render(request, 'workshop_view_reviews.html', {
        'workshop': workshop_obj,
        'reviews': reviews
    })

def view_all_workshops(request):
    workshops = workshop.objects.all()
    return render(request, 'view_all_workshops.html', {'workshops': workshops})

def w_review(request, workshop_id):
    if 'userid' not in request.session:
        return redirect('userlogin')
    workshop_obj = get_object_or_404(workshop, id=workshop_id)
    reviews = WorkshopReview.objects.filter(workshop=workshop_obj).select_related('user')
    return render(request, 'w_reviews.html', {
        'workshop': workshop_obj,
        'reviews': reviews
    })
def view_all_experts(request):
    experts_list = experts.objects.all()
    return render(request, 'view_all_experts.html', {'experts_list': experts_list})
def view_all_parts(request):
    parts_list = parts.objects.all()
    return render(request, 'view_all_parts.html', {'parts_list': parts_list})
def add_workshop_slot(request):
    if 'workshopid' not in request.session:
        return redirect('userlogin')
    workshop_obj = get_object_or_404(workshop, workshopid=request.session['workshopid'])
    if request.method == 'POST':
        form = WorkshopSlotForm(request.POST)
        if form.is_valid():
            slot_date = form.cleaned_data['date']
            slot_time = form.cleaned_data['time']
            slot_datetime = datetime.combine(slot_date, slot_time)
            if slot_datetime < datetime.now():
                messages.error(request, "❌ Failed to add slot,Cannot add a slot in the past!")
                return render(request, 'add_workshop_slot.html', {'form': form})
            overlap = WorkshopSlot.objects.filter(
                workshop=workshop_obj,
                date=slot_date,
                time=slot_time
            ).exists()
            if overlap:
                messages.error(request, "❌ Failed to add slot,This slot overlaps with an existing slot!")
                return render(request, 'add_workshop_slot.html', {'form': form})
            slot = form.save(commit=False)
            slot.workshop = workshop_obj
            slot.save()
            messages.success(request, "✅ Slot added successfully.")
            
    else:
        form = WorkshopSlotForm()
    return render(request, 'add_workshop_slot.html', {'form': form})

def view_workshop_slots(request):
    if 'workshopid' not in request.session:
        return redirect('userlogin')
    wid=request.session['workshopid']
    workshop_obj = get_object_or_404(workshop, workshopid=wid)
    slots = WorkshopSlot.objects.filter(workshop=workshop_obj).order_by('date', 'time')
    slot_bookings = {}
    for slot in slots:
        bookings = Appoinment.objects.filter(slot=slot)
        slot_bookings[slot.id] = [
            {
                'user': booking.userid.name,  
                'status': 'Paid' if booking.payment_status == '1' else 'Pending'
            }
            for booking in bookings
        ]
    payslots = Appoinment.objects.filter(slot__in=slots, payment_status=1)
    print(payslots)
    paid_slot_ids = WorkshopSlot.objects.filter(id__in=payslots.values_list('slot__id'))
    print(paid_slot_ids)
    return render(request, 'view_workshop_slots.html', {'slots': slots,'today': date.today(),'payslots':payslots,'paid_slot_ids':paid_slot_ids,'slot_bookings_json': json.dumps(slot_bookings, cls=DjangoJSONEncoder),})

def delete_workshop_slot(request, slot_id):
    if 'workshopid' not in request.session:
        return redirect('userlogin')
    workshop_obj = get_object_or_404(workshop, workshopid=request.session['workshopid'])
    slot = get_object_or_404(WorkshopSlot, id=slot_id, workshop=workshop_obj)
   
    slot.delete()
       
    return redirect('view_workshop_slots')





def edit_expertslot(request, expertslot_id):
    if 'userid' not in request.session:
        
        return redirect('userlogin')
    booking = get_object_or_404(SlotBooking, id=expertslot_id)
    expertslot = booking.slot
    expert_obj = expertslot.expert
    now = datetime.now()

    available_slots = ExpertSlot.objects.filter(
        expert=expert_obj,
        is_booked=False
        ).filter(
        date__gt=now.date()
        ) | ExpertSlot.objects.filter(
        expert=expert_obj,is_booked=False, date=now.date(), start_time__gte=now.time()) | ExpertSlot.objects.filter(id=expertslot.id)
    if request.method == 'POST':
        slot_id = request.POST.get('slotid')
        if slot_id:
            old_slot = booking.slot
            new_slot = get_object_or_404(ExpertSlot, id=slot_id)
            if old_slot != new_slot:
                
                old_slot.is_booked = False
                old_slot.save()
                
                new_slot.is_booked = True
                new_slot.save()
                
                booking.slot = new_slot
                booking.save(update_fields=['slot'])
            messages.success(request, "Expert slot booking updated successfully.")
            return redirect('my_booked_slots')
        else:
            messages.error(request, "Please select a slot.")

    return render(request, 'editexpertappoinment.html', {
        'slots': available_slots.distinct(),
        'current_slot_id': booking.slot.id if booking.slot else None,
    })          
def servicecharge(request, id):
   
    order_item = get_object_or_404(Appoinment, id=id)

    if request.method == 'POST':
        form1 = ServiceChargePaymentForm(request.POST)
        if form1.is_valid():
            cardno = form1.cleaned_data['cardno']
            expirymonth = form1.cleaned_data['expirymonth']
            expiryyear = form1.cleaned_data['expiryyear']
            cvv = form1.cleaned_data['cvv']            
            try:
                bank_account = demobank.objects.get(
                cardno=cardno,
                expirymonth=expirymonth,
                expiryyear=expiryyear,
                cvv=cvv
                )
            except demobank.DoesNotExist:
                return render(request, 'paymentindex.html', {'form1': form1})        
            if bank_account.balance < order_item.amount:
                messages.error(request, "Insufficient balance in your demo bank account.")
                return render(request, 'paymentindex.html', {'form1': form1})
            bank_account.balance -= order_item.amount
            bank_account.save()
            
            pay = form1.save(commit=False)
            pay.amount = order_item.amount

            pay.userid = order_item.userid
            pay.appoinmentid = order_item
            pay.name = form1.cleaned_data['name']
            pay.cardno = form1.cleaned_data['cardno']
            pay.expirymonth = form1.cleaned_data['expirymonth']
            pay.expiryyear = form1.cleaned_data['expiryyear']
            pay.cvv = form1.cleaned_data['cvv']
            pay.save()
            order_item.payment_status = 1
            order_item.save()
            return redirect('service_charge_receipt', ap_id=order_item.id)
    else:
        form1 = ServiceChargePaymentForm()
    return render(request, 'paymentindex.html', {'form': form1, 'order_item': order_item})

def service_charge_receipt(request, ap_id):
    appoin = get_object_or_404(Appoinment, id=ap_id)
    card_payment = get_object_or_404(servicechargepayment, appoinmentid=appoin)
    part = appoin.workshopid
    return render(request, 'service_receipt.html', {'order_item': appoin, 'card_payment': card_payment, 'part': part})
def service_charge_receiptworkshop(request, ap_id):
    appoin = get_object_or_404(Appoinment, id=ap_id)
    card_payment = get_object_or_404(servicechargepayment, appoinmentid=appoin)
    part = appoin.workshopid
    return render(request, 'service_receipt_workshop.html', {'order_item': appoin, 'card_payment': card_payment, 'part': part})
def user_dashboard(request):
    if 'userid' not in request.session:
        return redirect('userlogin')
    user_id = request.session['userid']
    user = Users.objects.get(userid=user_id)
    now = timezone.now()    
    active_workshop_bookings = Appoinment.objects.filter(
        userid=user,
        status__in=['pending', 'accepted', 'processing'],
        slot__date__gte=date.today()
    ).order_by('slot__date', 'slot__time')
    active_expert_bookings = SlotBooking.objects.filter(
        user=user,
        slot__date__gt=now.date()
    ) | SlotBooking.objects.filter(
        user=user,
        slot__date=now.date(),
        slot__end_time__gte=now.time()
    )
    active_expert_bookings = active_expert_bookings.order_by('slot__date', 'slot__start_time')

    return render(request, 'user_dashboard.html', {
        'active_workshop_bookings': active_workshop_bookings,
        'active_expert_bookings': active_expert_bookings,
    })
def todays_expert_bookings(request):
    if 'expertid' not in request.session:
        return redirect('userlogin')
    expert = get_object_or_404(experts, userid=request.session['expertid'])
    today = date.today()
    now_time = datetime.now().time()
  
    bookings = SlotBooking.objects.filter(
        slot__expert=expert,
        slot__date=today
    ).order_by('slot__start_time')
    return render(request, 'todays_expert_bookings.html', {
        'bookings': bookings,
        'today': today,
        'now_time': now_time
    })
def todays_workshop_bookings(request):
    if 'workshopid' not in request.session:
        return redirect('userlogin')
    workshop_obj = get_object_or_404(workshop, workshopid=request.session['workshopid'])
    today = date.today()
    bookings = Appoinment.objects.filter(
        workshopid=workshop_obj,
        slot__date=today
    ).order_by('slot__time')
    return render(request, 'todays_workshop_bookings.html', {
        'bookings': bookings,
        'today': today,
    })
def adddemoaccount(request):
    if request.method == 'POST':
        form = demobankform(request.POST)
        if form.is_valid():
            form.save()
            return redirect('viewdemobank')  
        else:
            print(form.errors)
    else:
        form = demobankform()
    return render(request, 'demobank.html', {'form': form})
def aboutus(request):
    return render(request, 'aboutus.html')
def viewdemobank(request):
    accounts = demobank.objects.all()
    return render(request, 'viewdemobank.html', {'accounts': accounts})
def add_amount_demobank(request, account_id):
    account = get_object_or_404(demobank, id=account_id)
    if request.method == "POST":
        add_amount_str = request.POST.get("add_amount", "").strip()
        try:
            add_amount = Decimal(add_amount_str)
            if add_amount > 0:
                account.balance += add_amount
                account.save()
                messages.success(request, f"₹{add_amount} added successfully!")
            
        except Exception:
            messages.error(request, "Invalid input. Please enter a valid number.")
    return redirect('viewdemobank')
def delete_demobank(request, account_id):
    account = get_object_or_404(demobank, id=account_id)
    account.delete()
    
    return redirect('viewdemobank')
def admin_dashboard(request):
    new_users_count = Users.objects.filter(status=0).count()
    return render(request, 'admin_w_details.html', {
        
        'new_users_count': new_users_count,
    })


import re
import requests
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils.safestring import mark_safe

ENDPOINT = "https://integrate.api.nvidia.com/v1/chat/completions"
MODEL = "meta/llama3-70b-instruct"
API_KEY = "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"
def format_diagnosis_to_html(raw_text):
    if not raw_text:
        return ""

    # Convert markdown-style bold and italic
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', raw_text)
    text = re.sub(r'(?<!\*)\*(?!\*)(.*?)\*(?!\*)', r'<em>\1</em>', text)

    lines = text.strip().splitlines()
    html_lines = []
    in_ul, in_ol = False, False

    for line in lines:
        stripped = line.strip()

        # Unordered list detection (- or * at start)
        if stripped.startswith(("-", "*")):
            if not in_ul:
                if in_ol:
                    html_lines.append("</ol>")
                    in_ol = False
                html_lines.append("<ul>")
                in_ul = True
            html_lines.append(f"<li>{stripped[1:].strip()}</li>")
            continue

        # Ordered list detection (e.g. 1., 2.)
        match = re.match(r'^(\d+)\.\s+(.*)', stripped)
        if match:
            if not in_ol:
                if in_ul:
                    html_lines.append("</ul>")
                    in_ul = False
                html_lines.append("<ol>")
                in_ol = True
            html_lines.append(f"<li>{match.group(2).strip()}</li>")
            continue

        # Close open lists before other blocks
        if in_ul:
            html_lines.append("</ul>")
            in_ul = False
        if in_ol:
            html_lines.append("</ol>")
            in_ol = False

        # Headings & Paragraphs
        if stripped.lower().startswith("vehicle issue:"):
            html_lines.append(f"<h4 class='text-danger mt-4'>{stripped}</h4>")
        elif stripped.lower().startswith("symptom") or stripped.lower().startswith("diagnostic"):
            html_lines.append(f"<h5 class='text-primary mt-3'>{stripped}</h5>")
        elif stripped.lower().startswith("potential cause"):
            html_lines.append(f"<h5 class='text-warning mt-3'>{stripped}</h5>")
        else:
            html_lines.append(f"<p>{stripped}</p>")

    # Close any unclosed list tags
    if in_ul:
        html_lines.append("</ul>")
    if in_ol:
        html_lines.append("</ol>")

    return mark_safe('\n'.join(html_lines))


@csrf_exempt
def vehicle_diagnosis_view(request):
    diagnosis_html = error = None

    if request.method == "POST":
        fault = request.POST.get("vehicle_fault", "").strip()

        if fault:
            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": "You are an expert automobile technician."},
                    {"role": "user", "content": f"Vehicle issue: {fault}. Diagnose and suggest a solution."}
                ],
                "temperature": 0.7,
                "top_p": 1,
                "max_tokens": 700
            }

            try:
                response = requests.post(ENDPOINT, headers=headers, json=payload, timeout=30)
                response.raise_for_status()
                ai_output = response.json()['choices'][0]['message']['content']
                diagnosis_html = format_diagnosis_to_html(ai_output)

            except requests.exceptions.RequestException as e:
                error = f"API Request Failed: {e}"
            except Exception as ex:
                error = f"Unexpected error: {ex}"

    return render(request, 'vehicleissue.html', {
        'diagnosis': diagnosis_html,
        'error': error
    })





import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2) ** 2

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c  # in kilometers


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from decimal import Decimal
from math import radians, sin, cos, sqrt, atan2
from .models import Appoinment, complaint

def add_service_charge(request, id):
    appointment = get_object_or_404(Appoinment, id=id)

    if request.method == 'POST':
        SER_CHARGE = request.POST.get('amount')
        try:
            # Ensure the appointment has both user and workshop coordinates
            if appointment.latitude and appointment.longitude and \
               appointment.workshopid.latitude and appointment.workshopid.longitude:

                user_lat = appointment.latitude
                user_lng = appointment.longitude
                work_lat = appointment.workshopid.latitude
                work_lng = appointment.workshopid.longitude

                # Haversine formula
                def haversine(lat1, lon1, lat2, lon2):
                    R = 6371  # Radius of Earth in km
                    phi1 = radians(lat1)
                    phi2 = radians(lat2)
                    dphi = radians(lat2 - lat1)
                    dlambda = radians(lon2 - lon1)
                    a = sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlambda / 2) ** 2
                    c = 2 * atan2(sqrt(a), sqrt(1 - a))
                    return R * c

                distance = haversine(user_lat, user_lng, work_lat, work_lng)
                distance = round(distance, 2)

                # Charges
                service_charge = Decimal(25)
                amount = Decimal(25) * Decimal(distance) + Decimal(SER_CHARGE)

                # Save values
                appointment.service_charge = SER_CHARGE
                appointment.amount = amount
                appointment.status = 'accepted'
                appointment.save()

                messages.success(request, f"Amount ₹{amount:.2f} added based on distance {distance} km (₹25/km).")
            else:
                messages.error(request, "Location data missing in appointment.")

        except Exception as e:
            messages.error(request, f"Error calculating distance: {e}")

    return redirect('workshopappoinmentview')