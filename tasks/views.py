from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone
from django.db.models import Avg, Count, Min, Sum
from .forms import RegistrationForm
from .models import Project, Bucket, Task, TaskComment, UserProject
from django.core.serializers.json import DjangoJSONEncoder
import json


def login_view(request):

    context = {}
    if request.method == 'POST':
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse(f"home"))
        else:
            context = {"message": 'Invalid credentials.'}
            return render(request, "tasks/login.html",context )
    else:
        return render(request, "tasks/login.html",context )


def logout_view(request):
    logout(request)
    return render(request, "tasks/login.html" )

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("home"))
        else:
            context = {'form':form}
            return render(request, "tasks/register.html",context)
    else:
        form =RegistrationForm()
        context = {'form':form}
        return render(request, "tasks/register.html",context)


def index(request):

    #Validate user - redirect them if they are nor logged-in
    if not request.user.is_authenticated:
        return render(request, "tasks/login.html", {"message": 'Please Login for managing Tasks'})

    # Get - Current User and their projects - for side Navigation

    userProjects = UserProject.objects.filter(user=request.user)
    #print(f"{userProjects}")

    projectDict = {'Active_Personal':[], 'Active_Team':[], 'Archive_Personal':[],'Archive_Team':[] }
    # Extract User Active
    for uProj in userProjects:
        if uProj.project.p_type == 'P':
            if uProj.project.status == 'A':
                projectDict['Active_Personal'].append({'id':uProj.project.id,'name':uProj.project.name, 'role':uProj.get_role_display() })
            else:
                projectDict['Archive_Personal'].append({'id':uProj.project.id,'name':uProj.project.name, 'role':uProj.get_role_display() })
        else:
            if uProj.project.status == 'A':
                projectDict['Active_Team'].append({'id':uProj.project.id,'name':uProj.project.name, 'role':uProj.get_role_display() })
            else:
                projectDict['Archive_Team'].append({'id':uProj.project.id,'name':uProj.project.name, 'role':uProj.get_role_display() })

    #print(f"{projectDict}")

    # Get - Selected Project
    selProject = Project.objects.get(pk = 1)

    # Get - Buckets for a selected project - order by bucket seq
    buckets = Bucket.objects.filter(project=selProject).order_by('seq')
    #print(f"{buckets}")

    # For - Each Bucket Get the Task List and its contents  - order by due date
    #tasks = Task.objects.filter(project= selProject).order_by ('dueDate')
    bTaskDict = {}
    for bkt in buckets:
        tasks = Task.objects.filter(project= selProject,bucket=bkt).order_by ('dueDate')
        bTaskDict[bkt.name]=[]
        for task in tasks:
            taskJson = {'id':task.id, 'title':task.title, 'description':task.description, 'owner':task.owner.get_username(),
              'dueDate': task.dueDate, 'assignedTo':task.assignedTo.get_username()}
            bTaskDict[bkt.name].append(taskJson)

    bTaskDict = json.dumps(bTaskDict, cls=DjangoJSONEncoder)
    #print(f"{bTaskDict}")

    context= {'projectDict':projectDict, 'buckets':buckets, 'bTaskDict':json.loads(bTaskDict), 'user':request.user.username}
    return render(request, "tasks/index.html", context)

def project(request, projectid):

    #Validate user - redirect them if they are nor logged-in
    if not request.user.is_authenticated:
        return render(request, "tasks/login.html", {"message": 'Please Login for managing Tasks'})

    # Get - Current User and their projects - for side Navigation
    userProjects = UserProject.objects.filter(user=request.user)
    #print(f"{userProjects}")

    data = None
    if request.session.get('task_creation'):
         data = request.session.get('task_creation')
         print(f"message from Task Create: {data}")
         del request.session['task_creation']


    projectDict = {'Active_Personal':[], 'Active_Team':[], 'Archive_Personal':[],'Archive_Team':[] }
    # Extract User Active
    for uProj in userProjects:
        if uProj.project.p_type == 'P':
            if uProj.project.status == 'A':
                projectDict['Active_Personal'].append({'id':uProj.project.id,'name':uProj.project.name, 'role':uProj.get_role_display() })
            else:
                projectDict['Archive_Personal'].append({'id':uProj.project.id,'name':uProj.project.name, 'role':uProj.get_role_display() })
        else:
            if uProj.project.status == 'A':
                projectDict['Active_Team'].append({'id':uProj.project.id,'name':uProj.project.name, 'role':uProj.get_role_display() })
            else:
                projectDict['Archive_Team'].append({'id':uProj.project.id,'name':uProj.project.name, 'role':uProj.get_role_display() })

    #print(f"{projectDict}")

    # Get - Selected Project
    selProject = Project.objects.get(pk = projectid)

    # Get - Team Members of the Project
    teammembers = UserProject.objects.filter(project=selProject)
    l_teammembers = []
    for teammember in teammembers:
        l_teammembers.append({'userid':teammember.user.id, 'username':teammember.user.username})

    # Get - Buckets for a selected project - order by bucket seq
    buckets = Bucket.objects.filter(project=selProject).order_by('seq')

    # For - Each Bucket Get the Task List and its contents  - order by due date
    #tasks = Task.objects.filter(project= selProject).order_by ('dueDate')
    bTaskDict = {}
    for bkt in buckets:
        tasks = Task.objects.filter(project= selProject,bucket=bkt).order_by ('dueDate', 'id')
        bTaskDict[bkt.name]=[]
        for task in tasks:
            taskJson = {'id':task.id, 'title':task.title, 'description':task.description, 'owner':task.owner.get_username(),
              'dueDate': task.dueDate, 'assignedTo':task.assignedTo.get_username()}
            bTaskDict[bkt.name].append(taskJson)

    bTaskDict = json.dumps(bTaskDict, cls=DjangoJSONEncoder)
    #print(f"{bTaskDict}")

    context= {'projectDict':projectDict, 'buckets':buckets, 'bTaskDict':json.loads(bTaskDict)
               , 'user':request.user.username, 'currentProject':selProject
               ,'QO_teammembers': teammembers
               , 'teammembers':json.dumps(l_teammembers), 'task_creation':data}
    return render(request, "tasks/index.html", context)

def updatetask(request):

    if request.method == 'POST':
        l_projectid = int(request.POST["projectid_update"])
        l_taskid = int(request.POST["taskid_update"])
        l_title = request.POST[f"title_{l_taskid}"]
        l_description = request.POST[f"desc_{l_taskid}"]
        l_assignedTo = request.POST[f"assignto_{l_taskid}"]
        l_duedate = request.POST[f"duedate_{l_taskid}"]

        print(f"{l_duedate}")

        l_assign_user = User.objects.get(pk=l_assignedTo)

        if not l_title:
            data =  {'success':False, 'message':f"Task: Title cannot be empty - Update Failed "}
        else:
            Task.objects.filter(pk=l_taskid).update(title=l_title,
                        description=l_description, assignedTo=l_assign_user, dueDate =l_duedate  )
            task = Task.objects.get(pk=l_taskid)

            data =  {'success':True, 'message':f"Task: {l_title}- Updated successfully "}

        request.task_create = data
        request.session['task_creation'] = data
        return HttpResponseRedirect(reverse(f"project" , args=(l_projectid,)))

    else:
        return HttpResponseRedirect(reverse(f"home"))


def createtask(request):

    if request.method == 'POST':
        l_projectid = int(request.POST["projectid_new"])
        l_bucketid = int(request.POST["bucketid_new"])
        l_title = request.POST["title_new"]
        l_description = request.POST["desc_new"]
        l_assignTo = request.POST["assign_new"]
        l_duedate = request.POST["duedate_new"]
        try:
            newTask = Task()
            newTask.project = Project.objects.get(pk=l_projectid)
            newTask.bucket = Bucket.objects.get(pk=l_bucketid)
            newTask.title = l_title
            newTask.description = l_description
            newTask.owner = request.user
            newTask.dueDate = l_duedate
            newTask.assignedTo = User.objects.get(pk=l_assignTo)

            newTask.save()
            data =  {'success':True, 'message':f"Task:{l_title} created successfully !!"}
        except Exception as e:
            print(f"exception {e}")
            data =  {'success':True, 'message':f"Task:{l_title} createion Failed "}

        request.task_create = data
        request.session['task_creation'] = data
        return HttpResponseRedirect(reverse(f"project" , args=(l_projectid,)))
    else:
        return HttpResponseRedirect(reverse(f"home"))
