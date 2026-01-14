import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from .forms import RegistrationForm, ProjectForm, PromptForm, ProjectFileForm
from .models import Project, Prompt, ChatMessage, ProjectFile

from django.contrib.auth.views import LoginView
import requests
from django.conf import settings

def home_view(request):
    try:
        if request.user.is_authenticated:
            return redirect('dashboard')
        return render(request, 'home.html')
    except Exception as e:
        import traceback
        print(f"ERROR in home_view: {str(e)}")
        traceback.print_exc()
        raise

class CustomLoginView(SuccessMessageMixin, LoginView):
    template_name = 'login.html'
    success_message = "Login successful! Welcome back."

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            messages.success(request, "Registration successful! Welcome to ChatAI.")
            return redirect('dashboard')
        else:
            print("Form Errors:", form.errors)
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def dashboard_view(request):
    projects = request.user.projects.all()
    total_projects = projects.count()
    total_messages = ChatMessage.objects.filter(project__user=request.user).count()

    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            return redirect('dashboard')
    else:
        form = ProjectForm()
    
    return render(request, 'dashboard.html', {
        'projects': projects, 
        'form': form,
        'total_projects': total_projects,
        'total_messages': total_messages
    })

@login_required
def project_detail_view(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    prompts = project.prompts.all()
    files = project.files.all()
    
    prompt_form = PromptForm()
    file_form = ProjectFileForm()
    
    if request.method == 'POST':
        if 'add_prompt' in request.POST:
            prompt_form = PromptForm(request.POST)
            if prompt_form.is_valid():
                prompt = prompt_form.save(commit=False)
                prompt.project = project
                prompt.save()
                return redirect('project_detail', project_id=project.id)
        elif 'upload_file' in request.POST:
            file_form = ProjectFileForm(request.POST, request.FILES)
            if file_form.is_valid():
                p_file = file_form.save(commit=False)
                p_file.project = project
                # Use filename if name is not provided
                if not p_file.name:
                    p_file.name = request.FILES['file'].name
                p_file.save()
                return redirect('project_detail', project_id=project.id)
    
    mock_mode = not settings.OPENROUTER_API_KEY or "yourkeyhere" in settings.OPENROUTER_API_KEY
    
    return render(request, 'project_detail.html', {
        'project': project, 
        'prompts': prompts, 
        'files': files,
        'prompt_form': prompt_form,
        'file_form': file_form,
        'mock_mode': mock_mode
    })

from django.http import JsonResponse
import json

import logging

# Set up a simple logger
logger = logging.getLogger(__name__)

def get_ai_response(message, system_prompt=None, history=None):
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "Django Chatbot"
    }

    messages = []

    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    if history:
        for msg in history:
            if hasattr(msg, 'role'):
                messages.append({"role": msg.role, "content": msg.content})
            else:
                messages.append({"role": msg['role'], "content": msg['content']})

    messages.append({"role": "user", "content": message})

    data = {
        "model": "allenai/molmo-2-8b:free",
        "messages": messages
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=20)
        response_json = response.json()

        if "choices" not in response_json:
            error_msg = response_json.get('error', {}).get('message', 'Unknown error') if isinstance(response_json.get('error'), dict) else response_json.get('error', 'Unknown error')
            return f"AI Error: {error_msg}"

        return response_json["choices"][0]["message"]["content"]

    except requests.Timeout:
        return "AI Error: Request timed out. Try again."
    except Exception as e:
        return f"AI Error: {str(e)}"

@login_required
def chat_api_view(request, project_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method. Please use POST.'}, status=405)
    
    try:
        project = get_object_or_404(Project, id=project_id, user=request.user)
        
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'The server received invalid data format. Expected JSON.'}, status=400)
            
        user_message = data.get('message')
        if not user_message:
            return JsonResponse({'error': 'Message content cannot be empty.'}, status=400)
        
        # Get the latest prompt for the project to use as system instructions
        system_prompt = project.prompts.order_by('-created_at').first()
        prompt_content = system_prompt.content if system_prompt else "You are a helpful assistant."

        # Get chat history (last 10 messages for context)
        history_msgs = project.messages.order_by('-timestamp')[:10]
        chat_history = []
        for msg in reversed(history_msgs):
            chat_history.append({'role': msg.role, 'content': msg.content})

        # Get AI response
        ai_response = get_ai_response(user_message, system_prompt=prompt_content, history=chat_history)

        # Save messages to database
        ChatMessage.objects.create(project=project, role='user', content=user_message)
        ChatMessage.objects.create(project=project, role='assistant', content=ai_response)

        return JsonResponse({'response': ai_response})
    
    except Exception as e:
        logger.exception("Chat API Error")
        return JsonResponse({
            'error': 'A server-side error occurred.',
            'details': str(e)
        }, status=500)


def chat_view(request, project_id):
    print("API KEY:", settings.OPENROUTER_API_KEY)
    project = get_object_or_404(Project, id=project_id, user=request.user)
    prompts = project.prompts.all()

    system_prompt = None
    if prompts.exists():
        system_prompt = prompts.order_by('-created_at').first().content

    if request.method == "POST":
        user_message = request.POST.get("message")
        
        # Get history for context (last 10 messages)
        history_msgs = project.messages.order_by('-timestamp')[:10]
        # Reverse to get chronological order
        chat_history = list(reversed(history_msgs))
        
        bot_response = get_ai_response(user_message, system_prompt, history=chat_history)

        ChatMessage.objects.create(
            project=project,
            role='user',
            content=user_message
        )
        ChatMessage.objects.create(
            project=project,
            role='assistant',
            content=bot_response
        )

    history = project.messages.all()

    return render(request, "chat.html", {
        "project": project,
        "prompts": prompts,
        "history": history,
    })

def logout_view(request):
    logout(request)
    return redirect('login')
