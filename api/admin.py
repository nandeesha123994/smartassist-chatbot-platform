from django.contrib import admin
from .models import Project, Prompt, ChatMessage, ProjectFile

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at',)

@admin.register(Prompt)
class PromptAdmin(admin.ModelAdmin):
    list_display = ('project', 'created_at')
    list_filter = ('created_at', 'project')
    readonly_fields = ('created_at',)

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('project', 'role', 'timestamp')
    list_filter = ('role', 'timestamp', 'project')
    readonly_fields = ('timestamp',)
    search_fields = ('content',)

@admin.register(ProjectFile)
class ProjectFileAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'uploaded_at')
    list_filter = ('uploaded_at', 'project')
    readonly_fields = ('uploaded_at',)
