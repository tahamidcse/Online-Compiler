from . forms import CreateUserForm, LoginForm

from django.contrib.auth.models import auth
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponse
from django.shortcuts import render, redirect
import json 
import os
import subprocess
import sys



def homepage(request):

    return render(request, 'editorapp/indx.html')




def register(request):

    form = CreateUserForm()

    if request.method == "POST":

        form = CreateUserForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect("my-login")


    context = {'registerform':form}

    return render(request, 'editorapp/register.html', context=context)



def my_login(request):

    form = LoginForm()

    if request.method == 'POST':

        form = LoginForm(request, data=request.POST)

        if form.is_valid():

            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:

                auth.login(request, user)

                return redirect("home")


    context = {'loginform':form}

    return render(request, 'editorapp/my-login.html', context=context)


def user_logout(request):

    auth.logout(request)

    return redirect("ide/")









@login_required(login_url="my-login")
def runcode(request):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    gcomp = 'g++ -o ' + (os.path.join(BASE_DIR, 'a.out'))
    gccomp = 'gcc -o ' + (os.path.join(BASE_DIR, 'a.out'))
    compiler = {'CPP': gcomp, 'JAVA': 'javac', 'C': gccomp, 'Python': 'python -m py_compile'}
    code_extent = {'CPP': 'cpp', 'JAVA': 'java', 'C': 'c', 'Python': 'py'}
    aftercomp = {'CPP': 'a.out', 'JAVA': ' TestClass ', 'C': 'a.out', 'Python': 'code.py'}
    beforecomp = {'CPP': ' ', 'JAVA': 'java -cp ', 'C': ' ', 'Python': 'python '}

    if request.POST:
        # get input from request
        source = request.POST['source']
        inputtext=request.POST['input']
        language=request.POST['lang']
        data = {
                        'source': source,
            'input':inputtext,
            'lang':language
                }
        if language=='JAVA' and source.find('class TestClass ')==-1:
            return HttpResponse(json.dumps("Class name chaged \nRename the class to TestClass"),content_type='application/json')
        cmd=""
        # check if there is input
        if inputtext:
            f=open((os.path.join(BASE_DIR,"input.txt")),'w')
            f.write(inputtext)
            f.close()
            cmd=" <"+(os.path.join(BASE_DIR,"input.txt"))

        # create file to compile

        f = open((os.path.join(BASE_DIR, 'code.'+code_extent[language])),'w')
        f.write(source)
        f.close()
        compilation_error=""

        # try compiling the code
        try:
            subprocess.check_output( compiler[language]+' '+(os.path.join(BASE_DIR,"code."+code_extent[language])), stderr=subprocess.PIPE,shell=True)
        except subprocess.CalledProcessError as e:
            compilation_error= e.stderr.decode(sys.getfilesystemencoding())

        if not compilation_error:
            p=subprocess.Popen(beforecomp[language]+os.path.join(BASE_DIR,aftercomp[language])+cmd+" >"+ (os.path.join(BASE_DIR,"out.txt")),shell=True)
            print(beforecomp[language]+os.path.join(BASE_DIR,aftercomp[language])+cmd+" >out.txt")
            try:
                p.wait(10)
            except subprocess.TimeoutExpired:
                p.kill()
                output="Process was terminated as it took longer than 10 seconds, was your code expecting an input?"
                data=json.dumps(output)
                return HttpResponse(data,content_type='application/json')
            output=open((os.path.join(BASE_DIR,'out.txt')),'r').read()
            print(BASE_DIR)
            data=json.dumps(output)
            return HttpResponse(data,content_type='application/json')

        else :
            data=json.dumps(compilation_error)
            return HttpResponse(data,content_type='application/json')
    else:
        return HttpResponseForbidden()

def home(request):

    return render(request, "editorapp/index.html")

