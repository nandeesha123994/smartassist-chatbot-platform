from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from .forms import RegistrationForm, ProjectForm, PromptForm, ProjectFileForm
from .models import Project, Prompt, ChatMessage, ProjectFile
from django.contrib.auth.views import LoginView
import requests
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)

def home_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')

class CustomLoginView(SuccessMessageMixin, LoginView):
    template_name = 'login.html'
    success_message = "Login successful! Welcome back."


def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            if User.objects.filter(username=username).exists():
                login(request, User.objects.get(username=username))
                messages.success(request, "Login successful! Welcome back.")
                return redirect('dashboard')
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
        'total_messages': total_messages,
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
        'mock_mode': mock_mode,
    })

def get_ai_response(message, system_prompt=None, history=None):
    # DEBUG LOGGING FOR RENDER
    api_key = settings.OPENROUTER_API_KEY
    if api_key:
        api_key = api_key.strip()
    
    is_valid_format = api_key and api_key.startswith("sk-or-v1-")
    
    print(f"DEBUG: Checking API Key...")
    if not api_key:
        print("DEBUG: API Key is None or Empty")
    else:
        masked_key = f"{api_key[:10]}...{api_key[-5:]}" if len(api_key) > 15 else "SHORT_KEY"
        print(f"DEBUG: API Key Present (Stripped). Length: {len(api_key)}. Preview: {masked_key}")
    
    # Graceful fallback for missing or placeholder keys
    if not api_key or "yourkeyhere" in api_key:
        return f"Sandbox Mode: I received your message '{message}'. Since no valid API key is set, I'm simulating a response."

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
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
    # List of models to try in order of preference (Free/Cheaper -> capabilities)
    models = [
        "meta-llama/llama-3-8b-instruct",
        "meta-llama/llama-3-70b-instruct",
        "mistralai/mistral-7b-instruct",
        "openai/gpt-3.5-turbo"
    ]

    response = None
    last_error = None

    for model in models:
        try:
            print(f"DEBUG: Attempting with model: {model}")
            data = {"model": model, "messages": messages}
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            # If successful, break the loop
            if response.status_code == 200:
                print(f"DEBUG: Success with model: {model}")
                break
            else:
                print(f"DEBUG: Failed with model {model}: {response.status_code} - {response.text}")
                last_error = response
        except Exception as e:
            print(f"DEBUG: Exception with model {model}: {str(e)}")
            last_error = e
            continue

    # If we exhausted all models and still don't have a 200 response
    if not response or response.status_code != 200:
        if isinstance(last_error, requests.Response):
             # Re-raise the last failure so the existing error handling below catches it
             response = last_error
        else:
             # It was a connection error or similar
             return f"Error: All models failed. Last error: {str(last_error)}"
        
        # DEBUG RESPONSE
        if response.status_code != 200:
            print(f"DEBUG: API Request Failed. Status: {response.status_code}")
            print(f"DEBUG: Response Body: {response.text}")

        # Handle 401 Unauthorized (User not found / Invalid Key) gracefully
        if response.status_code == 401:
            try:
                err_body = response.json()
                msg = err_body.get('error', {}).get('message', 'Unknown Auth Error')
            except:
                msg = response.text
            return f"Sandbox Mode (Auth Failed): {msg}"

        response_json = response.json()
        if "choices" not in response_json:
            error_msg = response_json.get('error', {}).get('message', 'Unknown error')
            if "User not found" in error_msg:
                 return f"Sandbox Mode (User not found): {error_msg}"
            return f"AI Error: {error_msg}"
        return response_json["choices"][0]["message"]["content"]
    except requests.Timeout:
        return "AI Error: Request timed out. Try again."
    except Exception as e:
        print(f"DEBUG: Exception during request: {e}")
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
        system_prompt = project.prompts.order_by('-created_at').first()
        prompt_content = system_prompt.content if system_prompt else "You are a helpful assistant."
        history_msgs = project.messages.order_by('-timestamp')[:10]
        chat_history = []
        for msg in reversed(history_msgs):
            chat_history.append({'role': msg.role, 'content': msg.content})
        ai_response = get_ai_response(user_message, system_prompt=prompt_content, history=chat_history)
        ChatMessage.objects.create(project=project, role='user', content=user_message)
        ChatMessage.objects.create(project=project, role='assistant', content=ai_response)
        return JsonResponse({'response': ai_response})
    except Exception as e:
        logger.exception("Chat API Error")
        return JsonResponse({'error': 'A server-side error occurred.', 'details': str(e)}, status=500)

@login_required
def chat_view(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    prompts = project.prompts.all()
    system_prompt = None
    if prompts.exists():
        system_prompt = prompts.order_by('-created_at').first().content
    if request.method == "POST":
        user_message = request.POST.get("message")
        history_msgs = project.messages.order_by('-timestamp')[:10]
        chat_history = list(reversed(history_msgs))
        bot_response = get_ai_response(user_message, system_prompt, history=chat_history)
        ChatMessage.objects.create(project=project, role='user', content=user_message)
        ChatMessage.objects.create(project=project, role='assistant', content=bot_response)
    history = project.messages.all()
    return render(request, "chat.html", {
        "project": project,
        "prompts": prompts,
        "history": history,
    })

def logout_view(request):
    logout(request)
    return redirect('login')
