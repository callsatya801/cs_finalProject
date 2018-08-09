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


def createproject(request):

    context = {}
    if request.method == 'POST':
        ptitle = request.POST["ptitle"]
        ptype = request.POST["ptype"]

        # Check if same project Name exists for the user
        proj = Project.objects.filter(name=ptitle)
        if proj:
            print(f"{proj}")
            context = {"p_Success":'F', "message": f"Project Title '{ptitle}' already Exists - Please create with new name."}
            return render(request, "tasks/createproject.html",context)
        else:
            # Create Project
            try:
                newProject = Project(name=ptitle, p_type=ptype, status='A', owner=request.user)
                newProject.save()

                #Create 3 buckets for the project
                p_bucket = Bucket(project=newProject, name='Planned', seq=10)
                p_bucket.save()

                ip_bucket = Bucket(project=newProject, name='In Progress', seq=20)
                ip_bucket.save()

                c_bucket = Bucket(project=newProject, name='Completed', seq=30)
                c_bucket.save()

                #Create User list for the project
                p_user = UserProject(user=request.user, project=newProject, role='A')
                p_user.save()

                return HttpResponseRedirect(reverse(f"project" , args=(newProject.id,)))
            except Exception as e:
                context = {"p_Success":'F', "message": f"Project Title '{ptitle}' creation Failed - {e}"}
                return render(request, "tasks/createproject.html",context)
    else:
        return render(request, "tasks/createproject.html",context )



def home_view(request):

    #Validate user - redirect them if they are nor logged-in
    if not request.user.is_authenticated:
        return render(request, "tasks/login.html", {"message": 'Please Login for managing Tasks'})

    # Get - Current User and their projects - for side Navigation
    userProjects = UserProject.objects.filter(user=request.user)

    projectDict = {'Active_Personal':[], 'Active_Team':[], 'Archive_Personal':[],'Archive_Team':[] }
    l_act_p_count =0
    l_act_t_count =0
    l_arch_p_count =0
    l_arch_t_count =0
    # Extract User Active
    for uProj in userProjects:
        if uProj.project.p_type == 'P':
            if uProj.project.status == 'A':
                projectDict['Active_Personal'].append({'id':uProj.project.id,'name':uProj.project.name, 'role':uProj.get_role_display() })
                l_act_p_count = l_act_p_count+1
            else:
                projectDict['Archive_Personal'].append({'id':uProj.project.id,'name':uProj.project.name, 'role':uProj.get_role_display() })
                l_arch_p_count = l_arch_p_count +1
        else:
            if uProj.project.status == 'A':
                projectDict['Active_Team'].append({'id':uProj.project.id,'name':uProj.project.name, 'role':uProj.get_role_display() })
                l_act_t_count = l_act_t_count + 1
            else:
                projectDict['Archive_Team'].append({'id':uProj.project.id,'name':uProj.project.name, 'role':uProj.get_role_display() })
                l_arch_t_count = l_arch_t_count + 1

    l_p_task_count = Task.objects.filter(project__in= Project.objects.filter(userproject__user = request.user, p_type='P', status='A')).count()
    l_t_task_count = Task.objects.filter(project__in= Project.objects.filter(userproject__user = request.user, p_type='T', status='A')).count()

    l_ap_task_count = Task.objects.filter(project__in= Project.objects.filter(userproject__user = request.user, p_type='P', status='D')).count()
    l_at_task_count = Task.objects.filter(project__in= Project.objects.filter(userproject__user = request.user, p_type='T', status='D')).count()
    #print(f"testing if this is working {l_p_task_count}:{l_t_task_count}")


    p_tasks_stat = Task.objects.filter(project__in= Project.objects.filter(userproject__user = request.user, p_type='P', status='A')).values('bucket__name').annotate(entries=Count('id')).order_by('bucket__seq')
    t_tasks_stat = Task.objects.filter(project__in= Project.objects.filter(userproject__user = request.user, p_type='T', status='A')).values('bucket__name').annotate(entries=Count('id')).order_by('bucket__seq')

    #print(f"Personal Tasks: {p_tasks_stat}")
    #print(f"Team Tasks: {t_tasks_stat}")
    context= {'projectDict':projectDict, 'user':request.user.username,
                'l_act_p_count':l_act_p_count,'l_act_t_count':l_act_t_count,
                'l_arch_p_count':l_arch_p_count,'l_arch_t_count':l_arch_t_count
               ,'l_p_task_count':l_p_task_count,'l_t_task_count':l_t_task_count
               , 'l_act_tot_count':l_act_p_count+l_act_t_count
               ,'l_ap_task_count':l_ap_task_count
               ,'l_at_task_count':l_at_task_count
    }

    return render(request, "tasks/home.html", context)


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
        l_teammembers.append({'userid':teammember.user.id, 'username':teammember.user.username, 'firstname':teammember.user.first_name})

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
              'owner_firstname':task.owner.get_short_name(),
              'dueDate': task.dueDate, 'assignedTo':task.assignedTo.get_username(), 'assignedTo_firstname':task.assignedTo.get_short_name()}
            bTaskDict[bkt.name].append(taskJson)

    bTaskDict = json.dumps(bTaskDict, cls=DjangoJSONEncoder)
    #print(f"{bTaskDict}")

    users = User.objects.all().values_list('id','username', 'first_name', 'last_name').order_by('first_name')
    userslist= json.dumps(list(users), cls=DjangoJSONEncoder)

    print(f"{userslist}")

    context= {'projectDict':projectDict, 'buckets':buckets, 'bTaskDict':json.loads(bTaskDict)
               , 'user':request.user.get_full_name(), 'currentProject':selProject
               , 'user_short':request.user.get_short_name
               ,'QO_teammembers': teammembers
               , 'teammembers':json.dumps(l_teammembers), 'task_creation':data
               , 'all_users':userslist
    }
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

            data =  {'success':True, 'message':f"Task: '{l_title}'- Updated successfully "}

        request.task_create = data
        request.session['task_creation'] = data
        return HttpResponseRedirect(reverse(f"project" , args=(l_projectid,)))

    else:
        return HttpResponseRedirect(reverse(f"home"))


def deletetask(request):

    if request.method == 'POST':
        l_taskid = int(request.POST["taskid"])
        l_title = request.POST["title"]
        try:
            task = Task.objects.get(pk=l_taskid)
            task.delete()
            data =  {'success':True, 'message':f"Task: '{l_title}'- Removed successfully "}
        except Exception as e:
            data =  {'success':False, 'message':f"Task: '{l_title}'- Remove Failed - {e} "}

        return HttpResponse(json.dumps(data), content_type='application/json')

    else:
        return HttpResponseRedirect(reverse(f"home"))


def movetask(request):
    if request.method == 'POST':
        l_taskid = int(request.POST["taskid"])
        l_dest_bucketid = int(request.POST["dest_bucketid"])
        l_dest_bucketname = request.POST["dest_bucketname"]
        l_title = request.POST["title"]

        try:
            task = Task.objects.get(pk=l_taskid)
            l_bucket = Bucket.objects.get(pk=l_dest_bucketid)
            Task.objects.filter(pk=l_taskid).update(bucket=l_bucket)
            data =  {'success':True, 'message':f"Task: '{l_title}'- moved to '{l_dest_bucketname}' successfully "}
        except Exception as e:
            data =  {'success':False, 'message':f"Task: '{l_title}'- move Failed - {e} "}

        return HttpResponse(json.dumps(data), content_type='application/json')

    else:
        return HttpResponseRedirect(reverse(f"home"))

def createtask(request):

    if request.method == 'POST':
        l_projectid = int(request.POST["projectid_new"])
        l_bucketid = int(request.POST["bucketid_new"])
        l_title = request.POST["title_new"]
        l_description = request.POST["desc_new"]
        l_duedate = request.POST["duedate_new"]
        try:
            newTask = Task()
            newTask.project = Project.objects.get(pk=l_projectid)
            if newTask.project.p_type == 'P':
                newTask.assignedTo = request.user
            else:
                 l_assignTo = request.POST["assign_new"]
                 newTask.assignedTo = User.objects.get(pk=l_assignTo)

            newTask.bucket = Bucket.objects.get(pk=l_bucketid)
            newTask.title = l_title
            newTask.description = l_description
            newTask.owner = request.user
            newTask.dueDate = l_duedate


            newTask.save()
            data =  {'success':True, 'message':f"Task:'{l_title}' created successfully !!"}
        except Exception as e:
            print(f"exception {e}")
            data =  {'success':True, 'message':f"Task:'{l_title}' createion Failed "}

        request.task_create = data
        request.session['task_creation'] = data
        return HttpResponseRedirect(reverse(f"project" , args=(l_projectid,)))
    else:
        return HttpResponseRedirect(reverse(f"home"))



def addteam(request):

    if request.method == 'POST':
        l_projectid = int(request.POST["projectid"])
        l_project_obj = Project.objects.get(pk=l_projectid)
        userlist = request.POST.getlist('tmember')
        print(f"Userlist: {userlist}")
        for user in userlist:
            try:
                print(f"user ID:{user}")
                l_user=User.objects.get(pk=user)
                user_proj = UserProject.objects.get(user=l_user,project=l_project_obj)
            except:
                p_user = UserProject(user=User.objects.get(pk=user), project=l_project_obj, role='M')
                p_user.save()

        data =  {'success':True, 'message':f"Team members added successfully "}
        request.task_create = data
        request.session['task_creation'] = data
        return HttpResponseRedirect(reverse(f"project" , args=(l_projectid,)))

    else:
        return HttpResponseRedirect(reverse(f"home"))


def archive(request):

    if request.method == 'POST':
        l_projectid = int(request.POST["projectid"])
        l_status = request.POST["status"]

        project = Project.objects.filter(pk=l_projectid)

        print(f" archiving ProjectID:{l_projectid}")
        if project:
            project.update(status=l_status)
            if l_status == 'D':
                data =  {'success':True, 'message':f"Project Archived Successfully !! "}
            else:
                data =  {'success':True, 'message':f"Project Activated Successfully !! "}
        else:
            if l_status == 'D':
                data =  {'success':False, 'message':f"Unable to Archive Project :( "}
            else:
                data =  {'success':False, 'message':f"Unable to Activate Project :( "}

        request.task_create = data
        request.session['task_creation'] = data
        return HttpResponseRedirect(reverse(f"project" , args=(l_projectid,)))

    else:
        return HttpResponseRedirect(reverse(f"home"))

