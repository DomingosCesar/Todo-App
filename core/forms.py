from django import forms
from django.core.validators import RegexValidator
from django.forms import ModelForm



class UserRegisterForm(forms.Form):
    email = forms.EmailField(
        label='Email',
        max_length=150,
        widget=forms.EmailInput,
        required=True,
        validators=[
            RegexValidator(
                r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',
                message='Por favor, insira um endereço de email válido.',
            )
        ],
        error_messages={
            'required': 'Por favor digite seu enderço de e-mail.',
            'max_length': 'O endereço de e-mail é muito longo.',
            'min_length': 'O endereço de e-mail é muito curto.',
            }
        )
    
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput,
        max_length=150,
        min_length=8,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^[A-Za-z0-9\@]+$',
                message='Por favor, insira uma Senha válida.',
            )
        ],
        error_messages={
            'required': 'Por favor digite sua senha.',
            'max_length': 'A senha é muito longa.',
            'min_length': 'A senha é muito curta.',
            }
    )
    
    confirm_password = forms.CharField(
        label='Confirmar Senha',
        widget=forms.PasswordInput,
        max_length=150,
        min_length=8,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^[A-Za-z0-9\@]+$',
                message='Por favor, insira uma Senha válida.',
            )
        ],
        error_messages={
            'required': 'Por favor digite sua senha.',
            'max_length': 'A senha é muito longa.',
            'min_length': 'A senha é muito curta.',
            }
    )
    


class UserLoginForm(forms.Form):
    identifier = forms.CharField(
        label='Email ou Telefone',
        max_length=255,
        required=True,
        help_text='Digite o seu email ou número de telefone',
        error_messages={
            'required': 'Por favor digite seu email ou número de telefone.',
            'max_length': 'Valor muito longo.',
        }
    )
    
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput,
        max_length=150,
        min_length=8,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^[A-Za-z0-9\@]+$',
                message='Por favor, insira uma Senha válida.',
            )
        ],
        error_messages={
            'required': 'Por favor digite sua senha.',
            'max_length': 'A senha é muito longa.',
            'min_length': 'A senha é muito curta.',
            }
        )
    
class PassWordResetForm(forms.Form):
    password = forms.CharField(
    label='Senha',
    widget=forms.PasswordInput,
    max_length=150,
    min_length=8,
    required=True,
    validators=[
        RegexValidator(
            regex=r'^[A-Za-z0-9\@]+$',
            message='Por favor, insira uma Senha válida.',
        )
    ],
    error_messages={
        'required': 'Por favor digite sua senha.',
        'max_length': 'A senha é muito longa.',
        'min_length': 'A senha é muito curta.',
        }
    )
    
    confirm_password = forms.CharField(
        label='Confirmar Senha',
        widget=forms.PasswordInput,
        max_length=150,
        min_length=8,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^[A-Za-z0-9\@]+$',
                message='Por favor, insira uma Senha válida.',
            )
        ],
        error_messages={
            'required': 'Por favor digite sua senha.',
            'max_length': 'A senha é muito longa.',
            'min_length': 'A senha é muito curta.',
            }
    )
