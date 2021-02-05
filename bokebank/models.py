import re

from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.validators import RegexValidator, EmailValidator
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.db import models
from django.urls import reverse

# Department
class Department(models.Model):
    """クラス 兼任不可"""

    name = models.CharField(_('クラス'), max_length=15, unique=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('クラス')
        verbose_name_plural = _('クラス')


# Question
class Question(models.Model):
    questioner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        verbose_name=_('出題者'),
        related_name="question_set",
        related_query_name="question",        
    )
    text = models.CharField(verbose_name=_('お題'), max_length=60)
    evaluate_counter =  models.IntegerField(verbose_name=_('採点人数'), default=0, blank=True)
    created_date = models.DateTimeField(verbose_name=_('作成時刻'), default=timezone.now, blank=True)
    asked_date = models.DateTimeField(verbose_name=_('出題時刻'), default=timezone.now)
    was_asked = models.BooleanField(
        _('出題済み'),
        default=False,
        help_text=_(
            'このお題が出題済みかどうかを示す'
        ),
    )
    was_evaluated = models.BooleanField(
        _('採点済み'),
        default=False,
        help_text=_(
            'このお題が採点済みかどうかを示す'
        ),
    )


    def ask(self):
        self.asked_date = timezone.now()
        self.was_asked = True
        self.save()
    """
    def evaluate(self):
        '''
        15人に採点されたら終了
        '''
        self.evaluate_counter += 1
        if evaluate_counter == 15:
            self.was_evaluated = True
        self.save()


    def get_absolute_url(self):
        if was_evaluated:
            return reverse('bokebank:detail', kwargs={'pk': self.pk})
        else:
            return reverse('bokebank:check', kwargs={'pk': self.pk})
    """

    def __str__(self):
        return self.text
    
    class Meta:
        verbose_name = _('お題')
        verbose_name_plural = _('お題')

# Answer
class Answer(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        verbose_name=_('お題'),
        related_name="answer_set",
        related_query_name="answer",     
    )
    panelist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        verbose_name=_('回答者'),
        related_name="answer_set",
        related_query_name="answer",
    )
    text = models.TextField(verbose_name=_('回答'))
    score = models.IntegerField(default=0)
    favorite = models.IntegerField(default=0)
    answered_date = models.DateTimeField(default=timezone.now)

    def answer(self):
        self.answered_date = timezone.now()
        self.save()

    def evaluate(self, point):
        self.score += point
        self.save()

    def __str__(self):
        return self.text
    
    class Meta:
        verbose_name = _('回答')
        verbose_name_plural = _('回答')


# User
@deconstructible
class UnicodeUsernameValidator(RegexValidator):
    regex = r'^[a-zA-Z0-9_]{4,15}$'
    message = _(
        'Enter a valid username. This value may contain only letters, '
        'numbers, and _ characters.'
    )
    flags = 0

@deconstructible
class UnicodeAccountnameValidator(RegexValidator):
    regex = r'^.{1,10}$'
    message = _(
        'Enter a valid acount_name. This value may contain only letters, '
        'numbers, and @/./+/-/_ characters.'
    )
    flags = 0


class UserManager(BaseUserManager):
    """
    UserManagerをコピペして編集する
    """
    use_in_migrations = True

    def _create_user(self, username, account_name, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        account_name = self.model.normalize_username(account_name)
        user = self.model(username=username, account_name=account_name, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, account_name=None, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, account_name, email, password, **extra_fields)

    def create_superuser(self, username, account_name=None, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, account_name, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    AbstractUserをコピペして編集する
    """
    username_validator = UnicodeUsernameValidator()
    email_validator = EmailValidator()
    account_name_validator = UnicodeAccountnameValidator()

    username = models.CharField(
        _('username'),
        max_length=15,
        unique=True,
        help_text=_('Required. 4 ~ 15 characters. Letters, digits and _ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    account_name = models.CharField(
        _('アカウント名'),
        validators=[account_name_validator],
        max_length=10,
        help_text=_('Required. 1 ~ 10 characters.'),
    )
    email = models.EmailField(
        _('email address'),
        validators=[email_validator],
        blank=True
    )
    departments = models.ManyToManyField(
        Department,
        verbose_name=_('クラス'),
        blank=True,
        help_text=_('Specific Departments for this user.'),
        related_name="user_set",
        related_query_name="user",
    )
    rate = models.IntegerField(default=1500)
    short_match = models.IntegerField(default=0)
    long_match = models.IntegerField(default=0)
    short_win = models.IntegerField(default=0)
    long_win = models.IntegerField(default=0)
    '''
    favorite_answers = models.ManyToManyField(
        Answer,
        verbose_name=_('お気に入り'),
        blank=True,
        help_text=_('お気に入りの回答'),
        related_name="favorite_user_set",
        related_query_name="favorite_user",
    )
    '''
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['account_name', 'email']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        return self.account_name

    def get_short_name(self):
        return self.account_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)