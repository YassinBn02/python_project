from django.shortcuts import render,redirect,get_object_or_404
from .models import User,Event,Comment
from django.contrib import messages
from django.contrib.auth import logout
import bcrypt
from django.core.files.storage import FileSystemStorage
import datetime

def landing(request):
    events=Event.objects.all()
    context={
        "events":events
    }
    return render(request,"landing.html",context)

def login(request):
    return render(request,"login.html")


def registration(request):
    return render(request,"registration.html")


def register(request): 
    errors=User.objects.basic_validator(request.POST)
    check=User.objects.filter(email=request.POST['email'])
    if check:
        messages.error(request,"email already in database")
    if len(errors)>0:
        for key, value in errors.items():
            messages.error(request,value)
        return redirect("/register")
    password = request.POST['password']
    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    User.objects.create(first_name=request.POST['first-name'],last_name=request.POST['last-name'],email=request.POST['email'],birth=request.POST['birth'],password=pw_hash)
    request.session['name']=request.POST['first-name']
    return redirect("/login")  


def login_user(request):
    user = User.objects.filter(email=request.POST['email']) 
    if user:
        logged_user = user[0] 
        if bcrypt.checkpw(request.POST['password'].encode(), logged_user.password.encode()):
            request.session['user_id'] = logged_user.id
            request.session['name']=logged_user.first_name
            return redirect('/admin')
    messages.error(request,"invalid email or password")
    return redirect("/login") 



#make the member a creator
def creator(request,id):
    user=User.objects.filter(id=id)
    logged=user[0]
    if logged.role != 4:
        logged.role=4
        logged.save()
    else:
        logged.role=2
        logged.save()
    if logged.role==4:
        return redirect("/dashboard")
    else:
        return redirect("/admin")



def admin(request):
    if "user_id" not in request.session:
        return redirect("/login")
    user=User.objects.filter(id=request.session['user_id'])
    logged_user=user[0]
    if logged_user.role!=0:
        return redirect("/dashboard")
    all_users=User.objects.exclude(role=3).exclude(id=request.session['user_id'])
    pending_creator=User.objects.filter(role=4)
    blocked_users=User.objects.filter(role=3)
    all_events=Event.objects.filter(status=1)
    pending_events=Event.objects.filter(status=0)
    blocked_events=Event.objects.filter(status=2)
    pending_comments=Comment.objects.filter(comment_status=0)
    blocked_comments=Comment.objects.filter(comment_status=2)
    all_comments=Comment.objects.filter(comment_status=1)
    context={
        "all_users":all_users,
        "blocked_users":blocked_users,
        "all_events":all_events,
        "pending_events":pending_events,
        "blocked_events":blocked_events,
        "pending_comments":pending_comments,
        "all_comments":all_comments,
        "blocked_comments":blocked_comments,
        "pending_creator":pending_creator,
    }
    return render(request,"admin.html",context)


def block_user(request,id):
    user=User.objects.filter(id=id)
    logged=user[0]
    if logged.role==3:
        logged.role=1
        logged.save()
    else:
        logged.role=3
        print(logged.role)
        logged.save()
    return redirect("/admin")


def block_event(request,id):
    events=Event.objects.filter(id=id)
    event=events[0]
    logged_user=User.objects.get(id=request.session['user_id'])
    if event.status==0 or event.status==1:
        event.status=2
        event.save()
    else:
        event.status=1
        event.save()
    if(logged_user.role==0):
        return redirect("/admin")
    return redirect("/my_events")


def create_comment(request,id):
    events=Event.objects.filter(id=id)
    user=User.objects.get(id=request.session['user_id'])
    Comment.objects.create(event=events[0],user=user,comment=request.POST['comment'],rate=request.POST['rate'])
    event=events[0]
    return redirect(f'/view_event/{event.id}/')


def block_comment(request,id):
    comments=Comment.objects.filter(id=id)
    comment=comments[0]
    if comment.comment_status==0 or comment.comment_status==1:
        comment.comment_status=2
        comment.save()
    else:
        comment.comment_status=1
        comment.save()
    return redirect("/admin")


def publish_comment(request,id):
    comments=Comment.objects.filter(id=id)
    comment=comments[0]
    comment.comment_status=1
    comment.save()
    return redirect("/admin")


def publish_event(request,id):
    events=Event.objects.filter(id=id)
    event=events[0]
    event.status=1
    event.save()
    return redirect("/admin")


def view_event(request,id):
    if "user_id" not in request.session:
        return redirect("/login")
    events=Event.objects.filter(id=id)
    user=User.objects.get(id=request.session['user_id'])
    event=events[0]
    comments=Comment.objects.filter(comment_status=1,event=event)
    date=datetime.date.today()
    members_numb=event.members.count()
    print(members_numb)
    context={
        "event":event,
        "user":user,
        "comments":comments,
        "date":date,
        "members_numb":members_numb
    }
    return render(request,"view_event.html",context)

def logout_user(request):
    logout(request)
    return redirect("/")

def create_event(request):
    if request.method == 'POST':
        title = request.POST['title']
        location = request.POST['location']
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        description = request.POST['description']
        category = request.POST['category']
        capacity = request.POST['capacity']
        
        if 'image' in request.FILES:
            image = request.FILES['image']
            fs = FileSystemStorage('app_1/static/images')
            image_path = fs.save(image.name, image)
        else:
            image_path = None
        
        # Save event
        Event.objects.create(
            title=title,
            location=location,
            start_date=start_date,
            end_date=end_date,
            description=description,
            category=category,
            total_number=capacity,
            image=image_path,
            user=User.objects.get(id=request.session['user_id'])  # Ensure user is logged in
        )
        return redirect('/admin')
    
    return render(request, 'event.html')

# update:
def update_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    if request.method == 'POST':
        event.title = request.POST['title']
        event.location = request.POST['location']
        event.start_date = request.POST['start_date']
        event.end_date = request.POST['end_date']
        event.description = request.POST['description']
        event.category = request.POST['category']
        event.total_number = request.POST['capacity']
        
        
        if 'image' in request.FILES:
            image = request.FILES['image']
            fs = FileSystemStorage('app_1/static/images')
            image_path = fs.save(image.name, image)
            event.image = image_path
        
        event.save()
        return redirect('/dashboard')
    
    return render(request, 'update_event.html', {'event': event})


def list_events(request):
    events = Event.objects.all()
    context={
        'events':events
    }  
    return render(request, 'list_events.html',context)


#display all events organized by the user
def my_events(request):
    if "user_id" not in request.session:
        return redirect("/login")
    events=Event.objects.filter(user=User.objects.get(id=request.session['user_id']),status=1)
    context={
        'events':events
    }
    return render(request,"my_events.html",context)


#join event for user
def join_event(request,id):
    if "user_id" not in request.session:
        return redirect("/login")
    events=Event.objects.filter(id=id)
    event=events[0]
    user=User.objects.get(id=request.session['user_id'])
    event.members.add(user)
    context={
        "event":event,
    }
    return render(request,'join_event.html',context)


def end_join(request,id):
    if "user_id" not in request.session:
        return redirect("/login")
    events=Event.objects.filter(id=id)
    event=events[0]
    user=User.objects.get(id=request.session['user_id'])
    event.members.remove(user)
    return redirect("/user_events")



#save events for user
def favorite(request,id):
    if "user_id" not in request.session:
        return redirect("/login")
    events=Event.objects.filter(id=id)
    event=events[0]
    user=User.objects.get(id=request.session['user_id'])
    event.favorites.add(user)
    return redirect("/dashboard")



#delete save for user
def unsave(request,id):
    if "user_id" not in request.session:
        return redirect("/login")
    events=Event.objects.filter(id=id)
    event=events[0]
    user=User.objects.get(id=request.session['user_id'])
    event.favorites.remove(user)
    return redirect("/user_events")



#render all user's joined events
def user_events(request):
    if "user_id" not in request.session:
        return redirect("/login")
    user=User.objects.get(id=request.session['user_id'])
    events=user.favorited_events.all()
    members=user.joined_events.all()
    context={
        "events":events,
        "joined_events":members
    }
    return render(request,"user_events.html",context)




def dashboard(request):
    if "user_id" not in request.session:
        return redirect("/login")
    events=Event.objects.filter(status=1)
    user=User.objects.get(id=request.session['user_id'])
    if user.role==0:
        return redirect("/admin")
    # events=Event.objects.all()

    # for e in events:
    #     print(e.favorites.all())
    
    
    context={
        "events":events,
        "user":user
    }
    return render(request,"dashboard.html",context)

def sports(request):
    if "user_id" not in request.session:
        return redirect("/login")
    events=Event.objects.filter(status=1,category="sports")
    user=User.objects.get(id=request.session['user_id'])
    context={
        "events":events,
        "user":user
    }
    return render(request,"dashboard.html",context)


def arts(request):
    if "user_id" not in request.session:
        return redirect("/login")
    events=Event.objects.filter(status=1,category="arts")
    
    user=User.objects.get(id=request.session['user_id'])
    context={
        "events":events,
        "user":user
    }
    return render(request,"dashboard.html",context)


def business(request):
    if "user_id" not in request.session:
        return redirect("/login")
    events=Event.objects.filter(status=1,category="business")
    user=User.objects.get(id=request.session['user_id'])
    context={
        "events":events,
        "user":user
    }
    return render(request,"dashboard.html",context)

def education(request):
    if "user_id" not in request.session:
        return redirect("/login")
    events=Event.objects.filter(status=1,category="education")
    user=User.objects.get(id=request.session['user_id'])
    context={
        "events":events,
        "user":user
    }
    return render(request,"dashboard.html",context)