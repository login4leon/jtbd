from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from app01 import models
from app01.utils.bootstrap import BootstrapModelForm, BootstrapStyle
from app01.utils.encrypt import md5

# class UserModelForm(BootstrapModelForm):
#     class Meta:
#         model = models.UserInfo
#         fields = ['name', 'gender', 'password', 'age', 'account', 'create_time', 'depart']
#
# class NumModelForm(BootstrapModelForm):
#     mobile = forms.CharField(
#         label='手机号',
#         validators=[RegexValidator(r'^1[3-9]\d{9}$', '手机号码格式错误'), ],
#         widget=forms.TextInput(attrs={'class': 'form-control'}),
#     )
#
#     class Meta:
#         model = models.PrettyNum
#         fields = ['mobile', 'price', 'level', 'status']
#         # fields = "__all__"
#         # exclude = ['price']
#
#     def clean_mobile(self):
#         txt_mobile = self.cleaned_data['mobile']
#         exists = models.PrettyNum.objects.filter(mobile=txt_mobile).exists()
#         if exists:
#             raise ValidationError('手机号已存在')
#         return txt_mobile

# class NumEditModelForm(BootstrapModelForm):
#     mobile = forms.CharField(
#         validators=[RegexValidator(r'^1[3-9]\d{9}$', '手机号码格式错误'), ],
#         label='手机号',
#         widget=forms.TextInput(attrs={'class': 'form-control'}),
#     )
#
#     class Meta:
#         model = models.PrettyNum
#         fields = ['mobile', 'price', 'level', 'status']
#         # fields = "__all__"
#         # exclude = ['price']
#
#     def clean_mobile(self):
#         txt_mobile = self.cleaned_data['mobile']
#         exists = models.PrettyNum.objects.exclude(id=self.instance.pk).filter(mobile=txt_mobile).exists()
#         if exists:
#             raise ValidationError('手机号已存在')
#         return txt_mobile

# class AdminModelForm(BootstrapModelForm):
#     confirm_password = forms.CharField(
#         label='确认密码',
#         widget=forms.PasswordInput(render_value=True),
#     )
#     class Meta:
#         model = models.Admin
#         fields = ['username', 'password', 'confirm_password']
#         widgets = {
#             'password': forms.PasswordInput(render_value=True),
#         }
#
#     def clean_password(self):
#         password = self.cleaned_data['password']
#         return md5(password)
#
#     def clean_confirm_password(self):
#         confirm_password = md5(self.cleaned_data['confirm_password'])
#         password = self.cleaned_data['password']
#
#         if password != confirm_password:
#             raise ValidationError('密码不一致')
#
#         return confirm_password
#
# class AdminEditModelForm(BootstrapModelForm):
#     class Meta:
#         model = models.Admin
#         fields = ['username']

class AdminResetModelForm(BootstrapModelForm):
    confirm_password = forms.CharField(
        label='确认密码',
        widget=forms.PasswordInput(render_value=True),
    )

    class Meta:
        model = models.Admin
        fields = ['password', 'confirm_password']
        widgets = {
            'password': forms.PasswordInput(render_value=True),
        }

    def clean_password(self):
        password = self.cleaned_data.get('password')
        md5_pwd = md5(password)
        exists = models.Admin.objects.filter(id=self.instance.pk, password=md5_pwd).exists()
        if exists:
            raise ValidationError('不能重复原密码')
        return md5_pwd

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = md5(self.cleaned_data.get('confirm_password'))
        if not password:
            return confirm_password
        if password != confirm_password:
            raise ValidationError('密码不一致')
        return confirm_password


class AgentAddForm(BootstrapModelForm):
    class Meta:
        model = models.Agents
        fields = ['name', 'description', 'system_prompt', 'user_prompt', 'output']

    def clean_name(self):
        name = self.cleaned_data['name']
        exists = models.Agents.objects.filter(name=name).exists()
        if exists:
            raise ValidationError('Agent名称不能重复')
        return name


class AgentEditForm(BootstrapModelForm):
    # Agent名称不能修改
    # name = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = models.Agents
        fields = ['name', 'description', 'system_prompt', 'user_prompt', 'output']

class FlowAddForm(BootstrapModelForm):
    class Meta:
        model = models.Flows
        fields = '__all__'

class StepEditForm(BootstrapModelForm):
    class Meta:
        model = models.Steps
        fields = ['index', 'agent']

    def clean_index(self):
        index = self.cleaned_data['index']
        fid = self.instance.flow_id
        exists = models.Steps.objects.exclude(id=self.instance.pk).filter(flow_id=fid, index=index).exists()
        if exists:
            raise ValidationError('序号不能重复')
        return index

class StepAddForm(BootstrapModelForm):
    class Meta:
        model = models.Steps
        fields = ['index', 'agent']

    def clean_index(self):
        index = self.cleaned_data['index']
        fid = self.instance.flow_id
        exists = models.Steps.objects.filter(flow_id=fid, index=index).exists()
        if exists:
            raise ValidationError('序号不能重复')
        return index

class LoginForm(BootstrapStyle, forms.Form):
    username = forms.CharField(
        label='用户名',
        widget=forms.TextInput,
    )
    password = forms.CharField(
        label='密码',
        widget=forms.PasswordInput,
    )
    captcha = forms.CharField(
        label='验证码',
        max_length=4,
    )
    def clean_password(self):
        password = self.cleaned_data.get('password')
        return md5(password)

class RegisterForm(BootstrapStyle, forms.ModelForm):
    password2 = forms.CharField(
        label='确认密码',
        widget=forms.PasswordInput,
    )
    captcha = forms.CharField(
        label='验证码',
        max_length=4,
    )

    class Meta:
        model = models.Users
        fields = ['username', 'password']
        widgets = {
            'password': forms.PasswordInput(render_value=True),
        }

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise ValidationError('密码不一致')
        return cd['password2']
