from .models import Department, User, Question, Answer
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from django.utils.translation import gettext, gettext_lazy as _

class UserInlineInDepartment(admin.TabularInline):
    model = User.departments.through
    extra = 0


class AnswerInlineInQuestion(admin.TabularInline):
    model = Answer
    extra = 0

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    #fieldsets = (
    #    (None, {'fields': ('username',)}),
    #)

    #def username(self, obj):
    #    return ','.join([user.username for user in obj.user_set.all()])
    #inlines = [
    #    UserInline,
    #]
    inlines = [
        UserInlineInDepartment,
    ]
    pass

@admin.register(User)
class UserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('account_name', 'email', 'departments')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('ボケバンク'),{'fields':('favorite_answers',)}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('username', 'account_name', 'email', 'is_staff')
    search_fields = ('username', 'account_name', 'email')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('questioner', 'text',)}),
    )
    inlines = [
        AnswerInlineInQuestion,
    ]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('panelist', )}),
    )