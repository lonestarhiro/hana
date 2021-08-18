from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

class CustomUserManager(UserManager):
    """ユーザーマネージャー"""
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """カスタムユーザーモデル　usernameを使わず、emailアドレスをユーザー名として使うようにしています。"""
    email = models.EmailField(_('メールアドレス'), unique=True)
    last_name = models.CharField(_('姓'), max_length=30, blank=True)
    first_name = models.CharField(_('名'), max_length=30, blank=True)
    password = models.CharField(max_length=128)

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'),
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

    last_kana  = models.CharField(verbose_name="せい",max_length=30)
    first_kana = models.CharField(verbose_name="めい",max_length=30)
    short_name = models.CharField(verbose_name="短縮名",max_length=30,default="")
    birthday = models.DateField(verbose_name="生年月日",blank=True, null=True)
    staff_no = models.PositiveSmallIntegerField(verbose_name="社員番号",blank=True, null=True,unique=True)
    postcode = models.CharField(verbose_name="郵便番号",max_length=7)
    adr_ken  = models.CharField(verbose_name="都道府県",max_length=4)
    adr_siku = models.CharField(verbose_name="市区町村",max_length=30)
    adr_tyou = models.CharField(verbose_name="町名・番地",max_length=30)
    adr_bld  = models.CharField(verbose_name="ビル・マンション名",max_length=40,default="",blank=True)
    tel      = models.CharField(verbose_name="電話番号",max_length=15,default="",blank=True)
    phone    = models.CharField(verbose_name="携帯",max_length=15,default="",blank=True)
    shaho    = models.BooleanField(verbose_name="社会保険加入",default=False)
    join     = models.DateField(verbose_name="入社日",blank=True, null=True)
    biko     = models.TextField(verbose_name="備考",default="",blank=True)
    kanri    = models.BooleanField(verbose_name="管理者",default=False)
    jimu     = models.BooleanField(verbose_name="事務員",default=False)
    reader   = models.BooleanField(verbose_name="グループリーダー",default=False)
    caremane = models.BooleanField(verbose_name="ケアマネージャー",default=False)
    servkan  = models.BooleanField(verbose_name="サービス提供責任者",default=False)
    kaigo    = models.BooleanField(verbose_name="介護職員",default=False)
    yougu    = models.BooleanField(verbose_name="福祉用具専門相談員",default=False)
    kango    = models.BooleanField(verbose_name="看護職員",default=False)
    kinou    = models.BooleanField(verbose_name="機能訓練指導員",default=False)
    seikatu  = models.BooleanField(verbose_name="生活相談員",default=False)
    ishi     = models.BooleanField(verbose_name="医師",default=False)
    riha     = models.BooleanField(verbose_name="リハ職員",default=False)
    ope      = models.BooleanField(verbose_name="オペレーター",default=False)
    ryouyou  = models.BooleanField(verbose_name="療養管理指導員",default=False)
    jihakan  = models.BooleanField(verbose_name="児童発達支援管理責任者",default=False)
    sidou    = models.BooleanField(verbose_name="指導員",default=False)
    hoiku    = models.BooleanField(verbose_name="保育士",default=False)
    jisou    = models.BooleanField(verbose_name="児童指導員",default=False)
    driver   = models.BooleanField(verbose_name="ドライバー",default=False)
    eiyou    = models.BooleanField(verbose_name="栄養士",default=False)
    tyouri   = models.BooleanField(verbose_name="調理師",default=False)
    gengo    = models.BooleanField(verbose_name="言語機能訓練指導員",default=False)
    tyounou  = models.BooleanField(verbose_name="聴能訓練指導員",default=False)

    objects = CustomUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in
        between."""
        full_name = '%s %s' % (self.last_name,self.first_name, )
        return full_name.strip()

    def get_short_name(self):

        if self.short_name == None or self.short_name=="":
            s_name = self.last_name
        else:
            s_name = self.short_name

        return s_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    @property
    def username(self):
        return self.email

    def __str__(self):
        return f"{self.last_name} {self.first_name}" 
