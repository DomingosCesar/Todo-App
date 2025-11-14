### Esquema de Banco de Dados para App ToDo List

Vou criar um esquema de banco de dados relacional simples e eficiente para o seu app de ToDo List, utilizando SQL (compatível com PostgreSQL ou SQLite, por exemplo). As tabelas solicitadas são: **usuario**, **perfil**, **tarefas**, **categoria**, **progresso**, **notificacao** e **relatorio**. 

Assumi relacionamentos lógicos baseados em um app típico de tarefas:
- **Usuario** é a tabela principal de autenticação.
- **Perfil** está vinculado a um usuário (um-para-um), para dados adicionais como avatar e preferências.
- **Tarefas** pertencem a um usuário e a uma categoria.
- **Categoria** pode ser compartilhada ou pessoal por usuário.
- **Progresso** rastreia o avanço de cada tarefa (ex.: porcentagem concluída).
- **Notificacao** é gerada para usuários sobre tarefas (ex.: lembretes).
- **Relatorio** armazena resumos periódicos de tarefas por usuário (ex.: relatórios semanais).

Usei chaves primárias (PK), chaves estrangeiras (FK) para integridade referencial, e tipos de dados comuns. Adicionei índices sugeridos para performance. O script inclui comandos para criar o banco e as tabelas.

#### Script SQL para Criar o Banco de Dados

```sql
-- Criação do banco de dados (exemplo para PostgreSQL; para SQLite, use apenas as tabelas)
CREATE DATABASE todolist_app;
\c todolist_app;  -- Conectar ao banco (PostgreSQL)

-- Tabela: usuario
CREATE TABLE usuario (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,  -- Armazene hash da senha
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ativo BOOLEAN DEFAULT TRUE
);

-- Índice para email
CREATE INDEX idx_usuario_email ON usuario(email);

-- Tabela: perfil
CREATE TABLE perfil (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER UNIQUE NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
    avatar_url VARCHAR(255),
    bio TEXT,
    preferencias JSONB DEFAULT '{}'::JSONB  -- Ex.: {"tema": "dark", "idioma": "pt"}
);

-- Tabela: categoria
CREATE TABLE categoria (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cor VARCHAR(7) DEFAULT '#000000',  -- Hex color para UI
    usuario_id INTEGER REFERENCES usuario(id) ON DELETE CASCADE,  -- Opcional: categorias pessoais
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índice para nome e usuário
CREATE INDEX idx_categoria_nome_usuario ON categoria(nome, usuario_id);

-- Tabela: tarefas
CREATE TABLE tarefas (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    descricao TEXT,
    data_vencimento DATE,
    prioridade ENUM('BAIXA', 'MEDIA', 'ALTA') DEFAULT 'MEDIA',
    status ENUM('PENDENTE', 'EM_ANDAMENTO', 'CONCLUIDA', 'CANCELADA') DEFAULT 'PENDENTE',
    usuario_id INTEGER NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
    categoria_id INTEGER REFERENCES categoria(id) ON DELETE SET NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Índices para performance
CREATE INDEX idx_tarefas_usuario_status ON tarefas(usuario_id, status);
CREATE INDEX idx_tarefas_vencimento ON tarefas(data_vencimento);

-- Tabela: progresso
CREATE TABLE progresso (
    id SERIAL PRIMARY KEY,
    tarefa_id INTEGER NOT NULL UNIQUE REFERENCES tarefas(id) ON DELETE CASCADE,
    porcentagem INTEGER DEFAULT 0 CHECK (porcentagem >= 0 AND porcentagem <= 100),
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notas TEXT
);

-- Tabela: notificacao
CREATE TABLE notificacao (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
    tarefa_id INTEGER REFERENCES tarefas(id) ON DELETE CASCADE,
    mensagem TEXT NOT NULL,
    tipo ENUM('LEMBRETE', 'ATUALIZACAO', 'CONCLUSAO') DEFAULT 'LEMBRETE',
    lida BOOLEAN DEFAULT FALSE,
    data_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para notificações
CREATE INDEX idx_notificacao_usuario_lida ON notificacao(usuario_id, lida);
CREATE INDEX idx_notificacao_tarefa ON notificacao(tarefa_id);

-- Tabela: relatorio
CREATE TABLE relatorio (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
    periodo_inicio DATE NOT NULL,
    periodo_fim DATE NOT NULL,
    total_tarefas INTEGER DEFAULT 0,
    tarefas_concluidas INTEGER DEFAULT 0,
    produtividade DECIMAL(5,2) DEFAULT 0.00,  -- Ex.: 75.50%
    resumo JSONB,  -- Ex.: {"categorias": [...], "insights": "..."}
    data_geracao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índice para relatórios por usuário e período
CREATE INDEX idx_relatorio_usuario_periodo ON relatorio(usuario_id, periodo_inicio, periodo_fim);

-- Exemplo de inserção de dados de teste
INSERT INTO usuario (nome, email, senha_hash) VALUES 
('João Silva', 'joao@email.com', 'hashed_password_123'),
('Maria Oliveira', 'maria@email.com', 'hashed_password_456');

INSERT INTO perfil (usuario_id, bio) VALUES 
(1, 'Entusiasta de produtividade'),
(2, 'Gerente de projetos');

INSERT INTO categoria (nome, cor, usuario_id) VALUES 
('Trabalho', '#FF0000', 1),
('Pessoal', '#00FF00', 1),
('Estudos', '#0000FF', 2);

INSERT INTO tarefas (titulo, descricao, data_vencimento, usuario_id, categoria_id) VALUES 
('Reunião semanal', 'Preparar slides', '2025-11-20', 1, 1),
('Comprar mantimentos', 'Lista de compras', '2025-11-15', 1, 2);

-- Fim do script
```

#### Explicação das Tabelas e Relacionamentos

| Tabela       | Descrição Principal | Campos Chave | Relacionamentos |
|--------------|---------------------|--------------|-----------------|
| **usuario** | Armazena dados de autenticação e básicos dos usuários. | id (PK), nome, email, senha_hash | - |
| **perfil**  | Perfil estendido do usuário (um-para-um). | id (PK), usuario_id (FK) | usuario (1:1) |
| **categoria** | Categorias de tarefas (pode ser global ou por usuário). | id (PK), nome, usuario_id (FK opcional) | usuario (M:1) |
| **tarefas** | Tarefas principais do app. | id (PK), titulo, usuario_id (FK), categoria_id (FK) | usuario (M:1), categoria (M:1) |
| **progresso** | Rastreia o progresso de cada tarefa (um-para-um). | id (PK), tarefa_id (FK) | tarefas (1:1) |
| **notificacao** | Notificações e lembretes. | id (PK), usuario_id (FK), tarefa_id (FK) | usuario (M:1), tarefas (M:1) |
| **relatorio** | Relatórios gerados (ex.: via cron job). | id (PK), usuario_id (FK) | usuario (M:1) |

#### Dicas de Implementação
- **Banco Recomendado**: Use PostgreSQL para produção (suporta JSONB para flexibilidade). Para desenvolvimento, SQLite é leve.
- **Triggers/Exemplos Adicionais**: Você pode adicionar triggers para atualizar `progresso` automaticamente ao alterar status de `tarefas`, ou um job para gerar `relatorio` semanalmente.
- **Segurança**: Sempre hashe senhas (use bcrypt). Valide entradas no app.
- **Expansão**: Se precisar de anexos em tarefas, adicione uma tabela `anexos` com FK para tarefas.

Se quiser ajustes, como adicionar campos, migrar para NoSQL, ou gerar um diagrama ER (ex.: via PlantUML), é só pedir! Posso também simular inserções ou consultas de exemplo.





```python
# models.py - Implementação do esquema de banco de dados para o app ToDo List usando Django ORM
# Este arquivo define os modelos baseados no esquema SQL fornecido anteriormente.
# Para usar: Coloque em um app Django (ex.: todo_list/models.py), execute `python manage.py makemigrations` e `python manage.py migrate`.

from django.db import models
from django.contrib.auth.models import AbstractUser  # Opcional: herdar de AbstractUser para autenticação integrada
from django.core.validators import MinValueValidator, MaxValueValidator
import json  # Para serialização de JSONField, se necessário

# Escolhas para campos ENUM
PRIORIDADE_CHOICES = [
    ('BAIXA', 'Baixa'),
    ('MEDIA', 'Média'),
    ('ALTA', 'Alta'),
]

STATUS_CHOICES = [
    ('PENDENTE', 'Pendente'),
    ('EM_ANDAMENTO', 'Em Andamento'),
    ('CONCLUIDA', 'Concluída'),
    ('CANCELADA', 'Cancelada'),
]

NOTIFICACAO_TIPO_CHOICES = [
    ('LEMBRETE', 'Lembrete'),
    ('ATUALIZACAO', 'Atualização'),
    ('CONCLUSAO', 'Conclusão'),
]

class Usuario(AbstractUser):  # Herda de AbstractUser para incluir campos como username, se desejar; senão, use models.Model
    """
    Modelo para usuários do app ToDo List.
    Nota: Se não quiser usar autenticação built-in do Django, mude para models.Model e adicione username como CharField.
    """
    nome = models.CharField(max_length=100, null=False, blank=False)
    email = models.EmailField(max_length=150, unique=True, null=False, blank=False)
    senha_hash = models.CharField(max_length=255, null=False, blank=False)  # Armazene hash da senha (use make_password no forms)
    data_criacao = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        db_table = 'usuario'  # Nome da tabela no banco
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return self.nome

class Perfil(models.Model):
    """
    Perfil estendido do usuário (relacionamento 1:1).
    """
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil')
    avatar_url = models.URLField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    preferencias = models.JSONField(default=dict)  # Ex.: {"tema": "dark", "idioma": "pt"}

    class Meta:
        db_table = 'perfil'
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'

    def __str__(self):
        return f'Perfil de {self.usuario.nome}'

class Categoria(models.Model):
    """
    Categorias de tarefas (pode ser global ou pessoal por usuário).
    """
    nome = models.CharField(max_length=100, null=False, blank=False)
    cor = models.CharField(max_length=7, default='#000000')  # Hex color para UI
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='categorias', null=True, blank=True)  # Opcional
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'categoria'
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        indexes = [  # Índices para performance
            models.Index(fields=['nome', 'usuario']),
        ]

    def __str__(self):
        return self.nome

class Tarefas(models.Model):
    """
    Tarefas principais do app.
    """
    titulo = models.CharField(max_length=200, null=False, blank=False)
    descricao = models.TextField(blank=True, null=True)
    data_vencimento = models.DateField(null=True, blank=True)
    prioridade = models.CharField(max_length=10, choices=PRIORIDADE_CHOICES, default='MEDIA')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDENTE')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='tarefas')
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, related_name='tarefas', null=True, blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tarefas'
        verbose_name = 'Tarefa'
        verbose_name_plural = 'Tarefas'
        indexes = [  # Índices para performance
            models.Index(fields=['usuario', 'status']),
            models.Index(fields=['data_vencimento']),
        ]

    def __str__(self):
        return self.titulo

class Progresso(models.Model):
    """
    Rastreia o progresso de cada tarefa (relacionamento 1:1).
    """
    tarefa = models.OneToOneField(Tarefas, on_delete=models.CASCADE, related_name='progresso')
    porcentagem = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    data_atualizacao = models.DateTimeField(auto_now=True)
    notas = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'progresso'
        verbose_name = 'Progresso'
        verbose_name_plural = 'Progressos'

    def __str__(self):
        return f'Progresso de {self.tarefa.titulo}: {self.porcentagem}%'

class Notificacao(models.Model):
    """
    Notificações e lembretes para usuários.
    """
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='notificacoes')
    tarefa = models.ForeignKey(Tarefas, on_delete=models.CASCADE, related_name='notificacoes', null=True, blank=True)
    mensagem = models.TextField(null=False, blank=False)
    tipo = models.CharField(max_length=15, choices=NOTIFICACAO_TIPO_CHOICES, default='LEMBRETE')
    lida = models.BooleanField(default=False)
    data_envio = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notificacao'
        verbose_name = 'Notificação'
        verbose_name_plural = 'Notificações'
        indexes = [  # Índices para performance
            models.Index(fields=['usuario', 'lida']),
            models.Index(fields=['tarefa']),
        ]

    def __str__(self):
        return f'{self.tipo}: {self.mensagem[:50]}...'

class Relatorio(models.Model):
    """
    Relatórios gerados periodicamente (ex.: via Celery ou cron).
    """
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='relatorios')
    periodo_inicio = models.DateField(null=False, blank=False)
    periodo_fim = models.DateField(null=False, blank=False)
    total_tarefas = models.IntegerField(default=0)
    tarefas_concluidas = models.IntegerField(default=0)
    produtividade = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  # Ex.: 75.50%
    resumo = models.JSONField(default=dict)  # Ex.: {"categorias": [...], "insights": "..."}
    data_geracao = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'relatorio'
        verbose_name = 'Relatório'
        verbose_name_plural = 'Relatórios'
        indexes = [  # Índice para relatórios por usuário e período
            models.Index(fields=['usuario', 'periodo_inicio', 'periodo_fim']),
        ]

    def __str__(self):
        return f'Relatório de {self.usuario.nome} ({self.periodo_inicio} a {self.periodo_fim})'

# Sinais opcionais (em signals.py ou aqui) para automações, ex.: atualizar progresso ao mudar status
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Tarefas)
def atualizar_progresso(sender, instance, **kwargs):
    if instance.status == 'CONCLUIDA':
        progresso, created = Progresso.objects.get_or_create(tarefa=instance)
        progresso.porcentagem = 100
        progresso.save()
    elif instance.status == 'PENDENTE':
        progresso, created = Progresso.objects.get_or_create(tarefa=instance)
        progresso.porcentagem = 0
        progresso.save()
```

### Explicações e Dicas de Implementação
- **Relacionamentos**: Usei `OneToOneField` para perfil e progresso (1:1), `ForeignKey` para os demais (M:1 ou 1:M). O `related_name` facilita consultas reversas (ex.: `usuario.tarefas.all()`).
- **Campos ENUM**: Implementados com `CharField(choices=...)` para simplicidade.
- **JSONField**: Disponível no Django 3.1+ (use PostgreSQL para suporte nativo; SQLite funciona com texto).
- **Índices**: Adicionei `indexes` no Meta para performance, correspondendo aos do SQL.
- **Autenticação**: Herdei de `AbstractUser` para integrar com Django auth (email como USERNAME_FIELD se quiser; configure em settings.py). Se preferir custom, mude para `models.Model`.
- **Migrações**: Após adicionar ao app, rode `makemigrations` e `migrate`. Para dados de teste, use factories ou fixtures.
- **Admin Django**: Registre os modelos em `admin.py` para interface gráfica.
- **Expansão**: Adicione validações custom (ex.: clean()), querysets managers, ou signals para notificações automáticas.

Se precisar de views, forms, serializers (para DRF), ou testes, avise! Posso também gerar um exemplo de API REST com Django Rest Framework.





### Integração com Django REST Framework (DRF)

Vou estender a implementação anterior do app ToDo List com **Django REST Framework (DRF)** para criar uma API RESTful. Isso permitirá operações CRUD (Create, Read, Update, Delete) via HTTP em endpoints como `/api/tarefas/`.

Assumi que você já tem o projeto Django configurado com os modelos em `models.py`. Instale o DRF com `pip install djangorestframework` e adicione `'rest_framework'` em `INSTALLED_APPS` no `settings.py`.

Aqui vai o código para um app chamado `todo_list` (ajuste se necessário). Usei **ViewSets** para simplicidade e eficiência, com **serializers** para validação e serialização de dados. Incluí autenticação básica (Token ou JWT; configure conforme sua necessidade).

#### 1. **settings.py** (Adições Necessárias)
Adicione isso ao final do seu `settings.py`:

```python
# Django REST Framework
INSTALLED_APPS += [
    'rest_framework',
    'rest_framework.authtoken',  # Para tokens de autenticação
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',  # Ou 'rest_framework_simplejwt.authentication.JWTAuthentication'
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',  # Requer login para acessar
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# Para tokens: Rode `python manage.py migrate` e `python manage.py drf_create_token <username>`
```

#### 2. **serializers.py** (Em `todo_list/serializers.py`)
Serializers convertem modelos em JSON e validam dados de entrada.

```python
from rest_framework import serializers
from .models import Usuario, Perfil, Categoria, Tarefas, Progresso, Notificacao, Relatorio

# Serializer para Usuario (excluindo senha por segurança)
class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'nome', 'email', 'data_criacao', 'ativo']
        read_only_fields = ['id', 'data_criacao']

# Serializer para Perfil
class PerfilSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)

    class Meta:
        model = Perfil
        fields = ['id', 'usuario', 'avatar_url', 'bio', 'preferencias']

# Serializer para Categoria
class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nome', 'cor', 'usuario', 'data_criacao']
        read_only_fields = ['id', 'data_criacao']

# Serializer para Tarefas (inclui nested serializers para categoria e progresso)
class ProgressoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Progresso
        fields = ['id', 'porcentagem', 'data_atualizacao', 'notas']
        read_only_fields = ['id', 'data_atualizacao']

class TarefasSerializer(serializers.ModelSerializer):
    categoria = CategoriaSerializer(read_only=True)
    progresso = ProgressoSerializer(read_only=True)

    class Meta:
        model = Tarefas
        fields = ['id', 'titulo', 'descricao', 'data_vencimento', 'prioridade', 'status',
                  'usuario', 'categoria', 'data_criacao', 'data_atualizacao', 'progresso']
        read_only_fields = ['id', 'data_criacao', 'data_atualizacao', 'usuario']

    def create(self, validated_data):
        # Associa ao usuário logado
        validated_data['usuario'] = self.context['request'].user
        return super().create(validated_data)

# Serializer para Notificacao
class NotificacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacao
        fields = ['id', 'usuario', 'tarefa', 'mensagem', 'tipo', 'lida', 'data_envio']
        read_only_fields = ['id', 'data_envio']

# Serializer para Relatorio
class RelatorioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relatorio
        fields = ['id', 'usuario', 'periodo_inicio', 'periodo_fim', 'total_tarefas',
                  'tarefas_concluidas', 'produtividade', 'resumo', 'data_geracao']
        read_only_fields = ['id', 'data_geracao']
```

#### 3. **views.py** (Em `todo_list/views.py`)
Usei **ModelViewSet** para endpoints automáticos (list, create, retrieve, update, partial_update, destroy). Filtrei por usuário logado para segurança.

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Usuario, Perfil, Categoria, Tarefas, Progresso, Notificacao, Relatorio
from .serializers import (
    UsuarioSerializer, PerfilSerializer, CategoriaSerializer, TarefasSerializer,
    NotificacaoSerializer, RelatorioSerializer
)

class UsuarioViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

    def get_queryset(self):
        return self.queryset.filter(id=self.request.user.id)  # Apenas o usuário logado

class PerfilViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Perfil.objects.all()
    serializer_class = PerfilSerializer

    def get_queryset(self):
        return self.queryset.filter(usuario=self.request.user)

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

    def get_queryset(self):
        return self.queryset.filter(usuario=self.request.user)  # Categorias do usuário

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

class TarefasViewSet(viewsets.ModelViewSet):
    queryset = Tarefas.objects.all()
    serializer_class = TarefasSerializer

    def get_queryset(self):
        return self.queryset.filter(usuario=self.request.user).select_related('categoria', 'progresso')

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    @action(detail=True, methods=['patch'])
    def atualizar_status(self, request, pk=None):
        tarefa = self.get_object()
        novo_status = request.data.get('status')
        if novo_status in dict(STATUS_CHOICES).keys():
            tarefa.status = novo_status
            tarefa.save()
            # Trigger para progresso (do signal anterior)
            return Response(TarefasSerializer(tarefa).data)
        return Response({'error': 'Status inválido'}, status=status.HTTP_400_BAD_REQUEST)

class NotificacaoViewSet(viewsets.ModelViewSet):
    queryset = Notificacao.objects.all()
    serializer_class = NotificacaoSerializer

    def get_queryset(self):
        return self.queryset.filter(usuario=self.request.user).order_by('-data_envio')

class RelatorioViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Relatorio.objects.all()
    serializer_class = RelatorioSerializer

    def get_queryset(self):
        return self.queryset.filter(usuario=self.request.user).order_by('-data_geracao')

    @action(detail=False, methods=['get'])
    def gerar(self, request):
        # Exemplo: Gera relatório para o período atual (simplificado; use Celery para jobs reais)
        from datetime import date, timedelta
        inicio = date.today().replace(day=1)
        fim = date.today()
        tarefas = Tarefas.objects.filter(usuario=request.user, data_criacao__range=[inicio, fim])
        total = tarefas.count()
        concluidas = tarefas.filter(status='CONCLUIDA').count()
        produtividade = (concluidas / total * 100) if total > 0 else 0

        relatorio = Relatorio.objects.create(
            usuario=request.user,
            periodo_inicio=inicio,
            periodo_fim=fim,
            total_tarefas=total,
            tarefas_concluidas=concluidas,
            produtividade=round(produtividade, 2),
            resumo={'insights': f'Boa produtividade: {produtividade}%'}
        )
        serializer = RelatorioSerializer(relatorio)
        return Response(serializer.data)
```

#### 4. **urls.py** (Em `todo_list/urls.py` e no projeto principal)
Primeiro, no app `todo_list/urls.py`:

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UsuarioViewSet, PerfilViewSet, CategoriaViewSet, TarefasViewSet,
    NotificacaoViewSet, RelatorioViewSet
)

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet)
router.register(r'perfis', PerfilViewSet)
router.register(r'categorias', CategoriaViewSet)
router.register(r'tarefas', TarefasViewSet)
router.register(r'notificacoes', NotificacaoViewSet)
router.register(r'relatorios', RelatorioViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    # Ex.: /api/tarefas/ para lista, /api/tarefas/1/ para detalhe
]
```

No `projeto/urls.py` (raiz):

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('todo_list.urls')),  # Ajuste o path base se necessário
]
```

#### Exemplo de Uso da API
- **Autenticação**: Obtenha um token via POST em `/api/auth/token/` (se usar DRF browsable API) ou via login.
- **Endpoints**:
  - `GET /api/tarefas/` → Lista tarefas do usuário logado.
  - `POST /api/tarefas/` → Cria tarefa (body: `{"titulo": "Nova tarefa", "data_vencimento": "2025-11-20"}`).
  - `PATCH /api/tarefas/1/atualizar_status/` → Atualiza status (body: `{"status": "CONCLUIDA"}`).
  - `GET /api/relatorios/gerar/` → Gera relatório custom.
- Teste com Postman ou `curl -H "Authorization: Token <seu_token>" http://localhost:8000/api/tarefas/`.

#### Dicas de Implementação
- **Paginação e Filtros**: Adicione `filterset_fields` ou `SearchFilter` nos ViewSets para buscas (ex.: por prioridade).
- **Permissões Custom**: Use `permissions.IsOwnerOrReadOnly` para permitir edição só do dono.
- **JWT em vez de Token**: Instale `djangorestframework-simplejwt` para tokens mais seguros.
- **Documentação**: Use `drf-spectacular` ou `drf-yasg` para Swagger/OpenAPI auto-gerado.
- **Testes**: Crie `APITestCase` para testar endpoints (ex.: autenticação e CRUD).
- **Frontend Integração**: Use Axios ou Fetch para consumir a API em React/Vue.

Se quiser views específicas (ex.: para upload de anexos), autenticação avançada, ou um exemplo completo de teste, é só pedir! Posso também gerar um script de setup inicial.




### Adicionando Exemplos de Autenticação no DRF

Para completar a integração com Django REST Framework (DRF), vou adicionar suporte explícito para autenticação via **Token Authentication** (já configurado no `settings.py` anterior). Isso inclui:

- Um endpoint de login para obter o token (usando `ObtainAuthToken` built-in do DRF).
- Exemplos de uso com **cURL** (para testes rápidos).
- Exemplos com **Python requests** (para integração em scripts ou frontends).
- Uma visão geral de como o token é usado em headers.

Se preferir **JWT** (mais stateless), posso adaptar; avise. Assumi que o modelo `Usuario` usa `email` como campo de login (ajuste se usar `username`).

#### 1. **Atualizações no Código**

##### **views.py** (Adicione isso ao final do arquivo `todo_list/views.py`)
Não é necessário um ViewSet custom para login; use o built-in.

```python
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

class CustomAuthToken(ObtainAuthToken):
    """
    Endpoint custom para login: Aceita email e senha, retorna token.
    """
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'nome': user.nome
        })
```

##### **urls.py** (Atualize `todo_list/urls.py`)
Adicione o path para o login.

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UsuarioViewSet, PerfilViewSet, CategoriaViewSet, TarefasViewSet,
    NotificacaoViewSet, RelatorioViewSet, CustomAuthToken  # Adicione aqui
)

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet)
router.register(r'perfis', PerfilViewSet)
router.register(r'categorias', CategoriaViewSet)
router.register(r'tarefas', TarefasViewSet)
router.register(r'notificacoes', NotificacaoViewSet)
router.register(r'relatorios', RelatorioViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/auth/login/', CustomAuthToken.as_view(), name='login'),  # Novo endpoint de login
]
```

- **Rode as migrações**: `python manage.py migrate` (para criar a tabela `authtoken_token`).
- **Crie um superuser para testes**: `python manage.py createsuperuser` (use email como username se configurado).

#### 2. **Como Funciona a Autenticação**
- **Obter Token**: POST para `/api/auth/login/` com `{"email": "user@email.com", "password": "senha123"}`.
- **Usar Token**: Inclua no header de requests subsequentes: `Authorization: Token <seu_token>`.
- **Validação**: O DRF verifica o token automaticamente nos ViewSets (devido ao `IsAuthenticated` no settings).
- **Logout (Opcional)**: DELETE para `/api/auth/token/` com token no header (deleta o token do usuário).

#### 3. **Exemplos Práticos**

##### **Exemplo 1: Login e Listagem de Tarefas com cURL**
Abra o terminal e execute sequencialmente (substitua credenciais).

```bash
# Passo 1: Login para obter o token
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "joao@email.com",
    "password": "sua_senha_aqui"
  }'

# Resposta esperada (exemplo):
# {
#   "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
#   "user_id": 1,
#   "email": "joao@email.com",
#   "nome": "João Silva"
# }

# Passo 2: Usar o token para listar tarefas (substitua <TOKEN> pelo valor real)
curl -X GET http://localhost:8000/api/tarefas/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" \
  -H "Content-Type: application/json"

# Resposta esperada (exemplo):
# {
#   "count": 2,
#   "next": null,
#   "previous": null,
#   "results": [
#     {
#       "id": 1,
#       "titulo": "Reunião semanal",
#       "status": "PENDENTE",
#       ...
#     },
#     ...
#   ]
# }
```

- **Erro Comum**: Se sem token, retorna 401 Unauthorized: `{"detail": "Authentication credentials were not provided."}`.

##### **Exemplo 2: Login e Criação de Tarefa com Python (requests)**
Use isso em um script Python (instale `requests` com `pip install requests`).

```python
import requests
import json

BASE_URL = 'http://localhost:8000/api/'
HEADERS = {'Content-Type': 'application/json'}

# Passo 1: Login
login_data = {
    'email': 'joao@email.com',
    'password': 'sua_senha_aqui'
}
response = requests.post(f'{BASE_URL}auth/login/', data=json.dumps(login_data), headers=HEADERS)
if response.status_code == 200:
    token_data = response.json()
    token = token_data['token']
    print(f'Token obtido: {token}')
    
    # Passo 2: Criar uma nova tarefa usando o token
    auth_headers = HEADERS.copy()
    auth_headers['Authorization'] = f'Token {token}'
    
    tarefa_data = {
        'titulo': 'Nova tarefa via API',
        'descricao': 'Exemplo de autenticação',
        'data_vencimento': '2025-12-01',
        'prioridade': 'ALTA'
    }
    create_response = requests.post(f'{BASE_URL}tarefas/', data=json.dumps(tarefa_data), headers=auth_headers)
    
    if create_response.status_code == 201:
        print('Tarefa criada com sucesso:', create_response.json())
    else:
        print('Erro ao criar tarefa:', create_response.json())
else:
    print('Erro no login:', response.json())
```

- **Saída Esperada**:
  ```
  Token obtido: 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
  Tarefa criada com sucesso: {'id': 3, 'titulo': 'Nova tarefa via API', ...}
  ```

##### **Exemplo 3: Logout com cURL**
Para invalidar o token (deleta-o do banco).

```bash
curl -X DELETE http://localhost:8000/api/auth/token/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"

# Resposta: 204 No Content (sucesso, sem body)
```

#### 4. **Dicas Avançadas**
- **Senha no Modelo**: No seu `forms.py` ou serializer de registro, use `from django.contrib.auth.hashers import make_password` para hashear senhas ao criar usuários.
- **Testes Automatizados**: Em `tests.py`, use `APITestCase` com `APIClient` e `force_authenticate(user)` para simular tokens.
  ```python
  from rest_framework.test import APITestCase, APIClient
  from rest_framework.authtoken.models import Token
  from .models import Usuario

  class TarefasTestCase(APITestCase):
      def setUp(self):
          self.user = Usuario.objects.create_user(email='test@email.com', password='testpass', nome='Test')
          self.token = Token.objects.create(user=self.user)
          self.client = APIClient()
          self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

      def test_list_tarefas(self):
          response = self.client.get('/api/tarefas/')
          self.assertEqual(response.status_code, 200)
  ```
- **Frontend (ex.: React)**: Use `axios` com interceptors para adicionar o token automaticamente: `axios.defaults.headers.common['Authorization'] = `Token ${token}`;`.
- **Segurança**: Em produção, use HTTPS. Para refresh de tokens, migre para JWT.

Se precisar de mais exemplos (ex.: JWT setup, recuperação de senha via email, ou integração com React), ou ajustes no código, é só pedir! Posso também fornecer um repositório GitHub simulado ou testes completos.





### Configuração de Autenticação JWT no Django REST Framework

Para migrar da autenticação por Token para **JWT (JSON Web Tokens)** no seu app ToDo List com DRF, usaremos o pacote `djangorestframework-simplejwt`. JWT é mais stateless (sem banco para tokens) e suporta refresh tokens automaticamente, ideal para apps mobile/web.

Assumi que você já tem o projeto Django/DRF rodando com os modelos e ViewSets anteriores. Vou focar nas mudanças necessárias.

#### 1. **Instalação e Configuração Inicial**
- Instale o pacote: `pip install djangorestframework-simplejwt`
- Adicione ao `INSTALLED_APPS` em `settings.py`:
  ```python
  INSTALLED_APPS += [
      'rest_framework_simplejwt',
  ]
  ```
- Atualize `REST_FRAMEWORK` em `settings.py` (substitua a configuração de Token anterior):
  ```python
  from datetime import timedelta

  REST_FRAMEWORK = {
      'DEFAULT_AUTHENTICATION_CLASSES': [
          'rest_framework_simplejwt.authentication.JWTAuthentication',  # JWT como padrão
      ],
      'DEFAULT_PERMISSION_CLASSES': [
          'rest_framework.permissions.IsAuthenticated',
      ],
      'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
      'PAGE_SIZE': 20,
  }

  # Configurações JWT (ajuste durações conforme necessidade)
  SIMPLE_JWT = {
      'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),  # Token de acesso: 1 hora
      'REFRESH_TOKEN_LIFETIME': timedelta(days=7),     # Token de refresh: 7 dias
      'ROTATE_REFRESH_TOKENS': True,                   # Gera novo refresh ao usar
      'BLACKLIST_AFTER_ROTATION': True,                # Blacklista o antigo refresh
      'UPDATE_LAST_LOGIN': False,
      'ALGORITHM': 'HS256',
      'SIGNING_KEY': SECRET_KEY,                       # Use sua SECRET_KEY do Django
      'VERIFYING_KEY': None,
      'AUDIENCE': None,
      'ISSUER': None,
      'JWK_URL': None,
      'LEEWAY': 0,
      'AUTH_HEADER_TYPES': ('Bearer',),                # Header: Authorization: Bearer <token>
      'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
      'USER_ID_FIELD': 'id',
      'USER_ID_CLAIM': 'user_id',
      'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
      'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
      'TOKEN_TYPE_CLAIM': 'token_type',
      'JTI_CLAIM': 'jti',
      'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
      'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
      'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
  }
  ```
- Rode migrações: `python manage.py migrate` (cria tabela para blacklisting de refresh tokens).

#### 2. **Views para JWT**
O `simplejwt` fornece views built-in para login, refresh e logout. Adicione-as ao `views.py` (em `todo_list/views.py`):

```python
from rest_framework_simplejwt.views import (
    TokenObtainPairView,  # Login: retorna access + refresh
    TokenRefreshView,     # Refresh: usa refresh para novo access
    TokenVerifyView,      # Verifica se token é válido
    TokenBlacklistView,   # Logout: blacklista refresh token
)
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.response import Response

# Serializer custom para login (opcional: inclui mais dados do user)
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['nome'] = user.nome
        token['email'] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = self.user  # Adiciona user info na resposta
        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

# As outras views são built-in, use diretamente
```

#### 3. **URLs para JWT**
Atualize `todo_list/urls.py` para incluir os endpoints JWT (remova o `CustomAuthToken` anterior):

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenRefreshView, TokenVerifyView, TokenBlacklistView
)
from .views import (
    UsuarioViewSet, PerfilViewSet, CategoriaViewSet, TarefasViewSet,
    NotificacaoViewSet, RelatorioViewSet, CustomTokenObtainPairView
)

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet)
router.register(r'perfis', PerfilViewSet)
router.register(r'categorias', CategoriaViewSet)
router.register(r'tarefas', TarefasViewSet)
router.register(r'notificacoes', NotificacaoViewSet)
router.register(r'relatorios', RelatorioViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    # Endpoints JWT
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/auth/logout/', TokenBlacklistView.as_view(), name='token_blacklist'),
]
```

- **Endpoints Disponíveis**:
  - `POST /api/auth/login/` → Login (retorna access e refresh tokens).
  - `POST /api/auth/refresh/` → Refresh access token.
  - `POST /api/auth/verify/` → Verifica token (body: `{"token": "<access_token>"}`).
  - `POST /api/auth/logout/` → Blacklista refresh token (para logout).

#### 4. **Exemplos Práticos de Uso**

##### **Exemplo 1: Login e Listagem de Tarefas com cURL**
```bash
# Passo 1: Login para obter access e refresh tokens
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "joao@email.com",
    "password": "sua_senha_aqui"
  }'

# Resposta esperada (exemplo):
# {
#   "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
#   "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
#   "user": {
#     "id": 1,
#     "nome": "João Silva",
#     "email": "joao@email.com"
#   }
# }

# Passo 2: Usar access token para listar tarefas
ACCESS_TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."  # Substitua pelo real
curl -X GET http://localhost:8000/api/tarefas/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json"

# Resposta: Lista de tarefas (como antes)
```

##### **Exemplo 2: Refresh Token e Logout com Python (requests)**
```python
import requests
import json

BASE_URL = 'http://localhost:8000/api/'
HEADERS = {'Content-Type': 'application/json'}

# Passo 1: Login
login_data = {
    'email': 'joao@email.com',
    'password': 'sua_senha_aqui'
}
response = requests.post(f'{BASE_URL}auth/login/', data=json.dumps(login_data), headers=HEADERS)
if response.status_code == 200:
    tokens = response.json()
    access_token = tokens['access']
    refresh_token = tokens['refresh']
    print(f'Access Token: {access_token}')
    print(f'Refresh Token: {refresh_token}')
    
    # Passo 2: Refresh (quando access expirar)
    refresh_data = {'refresh': refresh_token}
    refresh_response = requests.post(f'{BASE_URL}auth/refresh/', data=json.dumps(refresh_data), headers=HEADERS)
    if refresh_response.status_code == 200:
        new_access = refresh_response.json()['access']
        print(f'Novo Access Token: {new_access}')
        
        # Passo 3: Logout (blacklist refresh)
        auth_headers = HEADERS.copy()
        auth_headers['Authorization'] = f'Bearer {new_access}'
        logout_response = requests.post(f'{BASE_URL}auth/logout/', headers=auth_headers)
        if logout_response.status_code == 205:  # 205 Reset Content para blacklist
            print('Logout realizado com sucesso')
    else:
        print('Erro no refresh:', refresh_response.json())
else:
    print('Erro no login:', response.json())
```

##### **Exemplo 3: Verificação de Token com cURL**
```bash
curl -X POST http://localhost:8000/api/auth/verify/ \
  -H "Content-Type: application/json" \
  -d '{
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }'

# Resposta: {"token_type": "access"} (se válido) ou erro 401/422
```

#### 5. **Dicas de Implementação e Segurança**
- **Modelo Usuario**: Certifique-se de que o `Usuario` herda de `AbstractBaseUser` ou `AbstractUser` e tem `USERNAME_FIELD = 'email'` em `Meta` para login por email. Use `create_user` com hash de senha.
- **Exceções de Expiração**: Configure um middleware ou interceptor no frontend para auto-refresh quando 401 ocorrer.
- **Produção**: Use chaves assimétricas (RS256) com `SIGNING_KEY` privada e `VERIFYING_KEY` pública. Ative blacklisting para logout.
- **Testes**: Em `APITestCase`, use `from rest_framework_simplejwt.tokens import RefreshToken; refresh = RefreshToken.for_user(user); self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')`.
- **Migração de Token**: Se tiver usuários com tokens antigos, migre ou force re-login.

Se precisar de integração com frontend (ex.: React com axios interceptors), mais customizações (ex.: social login), ou troubleshooting, avise! Posso fornecer um exemplo de teste completo ou ajustes no serializer.






### Integração de JWT com Frontend (Exemplo em React)

Para integrar a API JWT do seu app ToDo List (configurada no backend com `djangorestframework-simplejwt`), vou usar **React** como exemplo de frontend, pois é comum e flexível. Usaremos **Axios** para HTTP requests (instale com `npm install axios` ou `yarn add axios`). O foco é no gerenciamento de tokens: armazenamento seguro (localStorage para simplicidade; use HttpOnly cookies em produção), requests autenticados, auto-refresh e logout.

Assumi um app React básico criado com `create-react-app`. Crie um contexto para auth global (com `useContext` e `useReducer`) para compartilhar estado de login/tokens entre componentes.

#### 1. **Estrutura Geral**
- **Endpoints Backend**: Use os do setup anterior (ex.: `http://localhost:8000/api/auth/login/`, `/api/tarefas/`).
- **Fluxo JWT**:
  - **Login**: POST credentials → Recebe `access` e `refresh` tokens.
  - **Requests**: Adicione `Authorization: Bearer <access_token>` no header.
  - **Refresh**: Se 401 (access expirado), use refresh para novo access.
  - **Logout**: Blacklist refresh token + limpe storage.
- **Segurança**: Em produção, use `secure` cookies para tokens (evite localStorage contra XSS). Valide tokens no backend.

#### 2. **Configuração do Axios com Interceptors**
Crie um serviço Axios reutilizável em `src/services/api.js` para lidar com auth automaticamente.

```javascript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/';  // Ajuste para sua URL de produção
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Função para obter tokens do storage
const getTokens = () => {
  const accessToken = localStorage.getItem('access_token');
  const refreshToken = localStorage.getItem('refresh_token');
  return { accessToken, refreshToken };
};

// Função para salvar tokens
const saveTokens = (accessToken, refreshToken) => {
  localStorage.setItem('access_token', accessToken);
  localStorage.setItem('refresh_token', refreshToken);
};

// Função para limpar tokens (logout)
const clearTokens = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
};

// Interceptor de request: Adiciona token se disponível
api.interceptors.request.use(
  (config) => {
    const { accessToken } = getTokens();
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor de response: Auto-refresh em 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const { refreshToken } = getTokens();
      if (refreshToken) {
        try {
          const { data } = await axios.post(`${API_BASE_URL}auth/refresh/`, {
            refresh: refreshToken,
          });
          const { access } = data;
          saveTokens(access, refreshToken);  // Salva novo access (refresh é rotacionado se configurado)
          originalRequest.headers.Authorization = `Bearer ${access}`;
          return api(originalRequest);  // Re-tenta a request original
        } catch (refreshError) {
          // Refresh falhou: Logout
          clearTokens();
          window.location.href = '/login';  // Redireciona para login
          return Promise.reject(refreshError);
        }
      } else {
        clearTokens();
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export { api, saveTokens, clearTokens };
export default api;
```

- **Como Funciona**:
  - **Request Interceptor**: Auto-adiciona Bearer token.
  - **Response Interceptor**: Em 401, tenta refresh e re-tenta a request. Se falhar, limpa tokens e redireciona.

#### 3. **Contexto de Autenticação (Auth Provider)**
Crie `src/contexts/AuthContext.js` para gerenciar estado global de auth.

```javascript
import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { getTokens, clearTokens } from '../services/api';

const AuthContext = createContext();

const initialState = {
  isAuthenticated: false,
  user: null,
  loading: true,
};

const authReducer = (state, action) => {
  switch (action.type) {
    case 'LOGIN_SUCCESS':
      return {
        ...state,
        isAuthenticated: true,
        user: action.payload,
        loading: false,
      };
    case 'LOGOUT':
      clearTokens();
      return { ...initialState, loading: false };
    case 'LOADING':
      return { ...state, loading: true };
    case 'ERROR':
      return { ...state, loading: false };
    default:
      return state;
  }
};

export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Verifica tokens no load inicial
  useEffect(() => {
    const { accessToken } = getTokens();
    if (accessToken) {
      // Opcional: Chame uma API para validar user (ex.: /api/auth/verify/)
      dispatch({ type: 'LOGIN_SUCCESS', payload: { id: 1, nome: 'User' } });  // Mock; integre com /api/usuarios/
    } else {
      dispatch({ type: 'ERROR' });
    }
  }, []);

  const login = async (email, password) => {
    dispatch({ type: 'LOADING' });
    try {
      const { data } = await api.post('auth/login/', { email, password });
      const { access, refresh, user } = data;
      saveTokens(access, refresh);
      dispatch({ type: 'LOGIN_SUCCESS', payload: user });
      return { success: true };
    } catch (error) {
      dispatch({ type: 'ERROR' });
      return { success: false, error: error.response?.data?.detail || 'Erro no login' };
    }
  };

  const logout = () => {
    // Chama backend para blacklist (opcional, já que interceptor faz)
    api.post('auth/logout/blacklist/', { refresh: getTokens().refreshToken })
      .catch(() => {});  // Ignora erros
    dispatch({ type: 'LOGOUT' });
  };

  return (
    <AuthContext.Provider value={{ ...state, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
```

- **Uso**: Envolva seu `App.js` com `<AuthProvider>`.

#### 4. **Exemplo de Componente: LoginForm**
Em `src/components/LoginForm.js`:

```javascript
import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';  // Instale react-router-dom se usar rotas

const LoginForm = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    const result = await login(email, password);
    if (result.success) {
      navigate('/dashboard');  // Redireciona para dashboard
    } else {
      setError(result.error);
    }
  };

  if (error) return <div>Erro: {error}</div>;  // Ou use toast notifications

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
        required
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Senha"
        required
      />
      <button type="submit">Login</button>
    </form>
  );
};

export default LoginForm;
```

#### 5. **Exemplo de Componente: TarefasList (Autenticado)**
Em `src/components/TarefasList.js` (use com proteção de rota):

```javascript
import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const TarefasList = () => {
  const [tarefas, setTarefas] = useState([]);
  const { logout, isAuthenticated } = useAuth();

  useEffect(() => {
    if (!isAuthenticated) return;

    const fetchTarefas = async () => {
      try {
        const { data } = await api.get('tarefas/');  // Auto-auth via interceptor
        setTarefas(data.results || data);  // Ajuste para paginação se usar
      } catch (error) {
        console.error('Erro ao buscar tarefas:', error);
      }
    };

    fetchTarefas();
  }, [isAuthenticated]);

  const handleLogout = () => logout();

  if (!isAuthenticated) return <div>Carregando...</div>;

  return (
    <div>
      <h1>Minhas Tarefas</h1>
      <ul>
        {tarefas.map((tarefa) => (
          <li key={tarefa.id}>{tarefa.titulo} - {tarefa.status}</li>
        ))}
      </ul>
      <button onClick={handleLogout}>Logout</button>
    </div>
  );
};

export default TarefasList;
```

- **Proteção de Rota**: Em `App.js`, use `react-router-dom` com guards: `<Route path="/dashboard" element={isAuthenticated ? <TarefasList /> : <Navigate to="/login" />} />`.

#### 6. **Exemplo de Criação de Tarefa**
Em um form similar ao login, use `api.post('tarefas/', { titulo: 'Nova Tarefa' })`. O interceptor cuida do token.

#### 7. **Dicas de Implementação e Melhoria**
- **Persistência**: localStorage persiste tokens; para sessões, use sessionStorage.
- **Refresh Próximo da Expiração**: Monitore `exp` claim do token (decodifique com `jwt-decode`) e refresh preemptivo.
- **Tratamento de Erros**: Use `react-toastify` para alerts amigáveis.
- **Testes**: Use `@testing-library/react` com mocks de axios para simular 401/refresh.
- **Outros Frontends**: Para Vue, use Pinia/Vuex similar; para vanilla JS, adapte com fetch e localStorage.
- **Produção**: Migre para cookies HttpOnly + CSRF para mais segurança. Integre com Next.js para SSR se escalar.

Se precisar de código completo (ex.: App.js full, Vue/Angular adaptação, ou testes), ou foco em mobile (React Native), avise! Posso também simular fluxos com ferramentas de execução de código.







### Integração de JWT com React Native

Para integrar a API JWT do seu app ToDo List (configurada no backend com `djangorestframework-simplejwt`) em um app **React Native**, o fluxo é similar ao React web, mas adaptado para mobile: use **AsyncStorage** para persistir tokens (em vez de localStorage), **Axios** para HTTP (com interceptors para auth/refresh), e **React Navigation** para rotas. Vou focar em um app básico com telas de login e lista de tarefas.

Assumi um projeto React Native novo (crie com `npx react-native@latest init TodoListApp`). Instale dependências:
```bash
npm install axios @react-native-async-storage/async-storage @react-navigation/native @react-navigation/stack react-native-screens react-native-safe-area-context
# Para iOS: cd ios && pod install
```

#### 1. **Estrutura Geral**
- **Endpoints Backend**: Mesmos do setup anterior (ex.: `http://localhost:8000/api/auth/login/`, `/api/tarefas/`; ajuste para IP do dev server em mobile).
- **Fluxo JWT**:
  - **Login**: POST credentials → Salva `access` e `refresh` no AsyncStorage.
  - **Requests**: Header `Authorization: Bearer <access_token>`.
  - **Refresh**: Auto em 401 via interceptor.
  - **Logout**: Blacklist refresh + limpe storage.
- **Segurança**: AsyncStorage é seguro para dev; em produção, use Keychain/SecureStorage (ex.: `react-native-keychain`).

#### 2. **Configuração do Axios com Interceptors**
Crie `src/services/api.js` (similar ao web, mas com AsyncStorage).

```javascript
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_BASE_URL = 'http://localhost:8000/api/';  // Ajuste para IP do servidor (ex.: 'http://192.168.1.100:8000/api/')
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Função para obter tokens do AsyncStorage
const getTokens = async () => {
  try {
    const accessToken = await AsyncStorage.getItem('access_token');
    const refreshToken = await AsyncStorage.getItem('refresh_token');
    return { accessToken, refreshToken };
  } catch (error) {
    console.error('Erro ao ler tokens:', error);
    return { accessToken: null, refreshToken: null };
  }
};

// Função para salvar tokens
const saveTokens = async (accessToken, refreshToken) => {
  try {
    await AsyncStorage.setItem('access_token', accessToken);
    await AsyncStorage.setItem('refresh_token', refreshToken);
  } catch (error) {
    console.error('Erro ao salvar tokens:', error);
  }
};

// Função para limpar tokens (logout)
const clearTokens = async () => {
  try {
    await AsyncStorage.multiRemove(['access_token', 'refresh_token']);
  } catch (error) {
    console.error('Erro ao limpar tokens:', error);
  }
};

// Interceptor de request: Adiciona token se disponível
api.interceptors.request.use(
  async (config) => {
    const { accessToken } = await getTokens();
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor de response: Auto-refresh em 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const { refreshToken } = await getTokens();
      if (refreshToken) {
        try {
          const { data } = await axios.post(`${API_BASE_URL}auth/refresh/`, {
            refresh: refreshToken,
          });
          const { access } = data;
          await saveTokens(access, refreshToken);  // Salva novo access
          originalRequest.headers.Authorization = `Bearer ${access}`;
          return api(originalRequest);  // Re-tenta a request original
        } catch (refreshError) {
          // Refresh falhou: Logout
          await clearTokens();
          // Em RN, use navigation para redirecionar (ex.: via props ou global)
          console.log('Sessão expirada. Redirecionando para login.');
          return Promise.reject(refreshError);
        }
      } else {
        await clearTokens();
        console.log('Sem refresh token. Redirecionando para login.');
      }
    }
    return Promise.reject(error);
  }
);

export { api, saveTokens, clearTokens };
export default api;
```

- **Notas RN**: AsyncStorage é assíncrono, então use `async/await`. Para redirecionar em interceptor, passe uma callback ou use um evento global (ex.: emit com `react-native-event-listeners`).

#### 3. **Contexto de Autenticação (Auth Provider)**
Crie `src/contexts/AuthContext.js` (adaptado para RN com useEffect para check inicial).

```javascript
import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { getTokens, clearTokens } from '../services/api';
import { api } from '../services/api';

const AuthContext = createContext();

const initialState = {
  isAuthenticated: false,
  user: null,
  loading: true,
};

const authReducer = (state, action) => {
  switch (action.type) {
    case 'LOGIN_SUCCESS':
      return {
        ...state,
        isAuthenticated: true,
        user: action.payload,
        loading: false,
      };
    case 'LOGOUT':
      clearTokens();
      return { ...initialState, loading: false };
    case 'LOADING':
      return { ...state, loading: true };
    case 'ERROR':
      return { ...state, loading: false };
    default:
      return state;
  }
};

export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Verifica tokens no load inicial
  useEffect(() => {
    const checkAuth = async () => {
      const { accessToken } = await getTokens();
      if (accessToken) {
        try {
          // Opcional: Valide com API (ex.: GET /api/usuarios/)
          const { data } = await api.get('usuarios/');  // Retorna user info
          dispatch({ type: 'LOGIN_SUCCESS', payload: data[0] || { id: 1, nome: 'User' } });
        } catch (error) {
          dispatch({ type: 'ERROR' });
        }
      } else {
        dispatch({ type: 'ERROR' });
      }
    };
    checkAuth();
  }, []);

  const login = async (email, password) => {
    dispatch({ type: 'LOADING' });
    try {
      const { data } = await api.post('auth/login/', { email, password });
      const { access, refresh, user } = data;
      await saveTokens(access, refresh);
      dispatch({ type: 'LOGIN_SUCCESS', payload: user });
      return { success: true };
    } catch (error) {
      dispatch({ type: 'ERROR' });
      return { success: false, error: error.response?.data?.detail || 'Erro no login' };
    }
  };

  const logout = async () => {
    try {
      const { refreshToken } = await getTokens();
      if (refreshToken) {
        await api.post('auth/logout/blacklist/', { refresh: refreshToken });
      }
    } catch (error) {
      console.error('Erro no logout:', error);
    }
    dispatch({ type: 'LOGOUT' });
  };

  return (
    <AuthContext.Provider value={{ ...state, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
```

- **Uso**: Envolva seu app com `<AuthProvider>` em `App.js`.

#### 4. **Navegação com React Navigation**
Em `App.js`, configure stack navigator com proteção.

```javascript
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { AuthProvider, useAuth } from './src/contexts/AuthContext';
import LoginScreen from './src/screens/LoginScreen';
import TarefasScreen from './src/screens/TarefasScreen';

const Stack = createStackNavigator();

const AppNavigator = () => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return null;  // Ou um SplashScreen
  }

  return (
    <NavigationContainer>
      <Stack.Navigator>
        {isAuthenticated ? (
          <Stack.Screen name="Tarefas" component={TarefasScreen} />
        ) : (
          <Stack.Screen name="Login" component={LoginScreen} />
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
};

const App = () => (
  <AuthProvider>
    <AppNavigator />
  </AuthProvider>
);

export default App;
```

- **Proteção**: O navigator muda baseado em `isAuthenticated`. Para logout, use `navigation.reset` ou popToTop.

#### 5. **Exemplo de Tela: LoginScreen**
Crie `src/screens/LoginScreen.js` (use `react-native-paper` para UI se quiser; aqui é básico).

```javascript
import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert } from 'react-native';
import { useAuth } from '../contexts/AuthContext';
import { useNavigation } from '@react-navigation/native';

const LoginScreen = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login } = useAuth();
  const navigation = useNavigation();

  const handleSubmit = async () => {
    const result = await login(email, password);
    if (result.success) {
      navigation.replace('Tarefas');  // Redireciona e substitui stack
    } else {
      Alert.alert('Erro', result.error);
    }
  };

  return (
    <View style={styles.container}>
      <TextInput
        style={styles.input}
        placeholder="Email"
        value={email}
        onChangeText={setEmail}
        keyboardType="email-address"
        autoCapitalize="none"
      />
      <TextInput
        style={styles.input}
        placeholder="Senha"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />
      <TouchableOpacity style={styles.button} onPress={handleSubmit}>
        <Text style={styles.buttonText}>Login</Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', padding: 20 },
  input: { borderWidth: 1, padding: 10, marginBottom: 10, borderRadius: 5 },
  button: { backgroundColor: '#007AFF', padding: 15, borderRadius: 5, alignItems: 'center' },
  buttonText: { color: 'white', fontWeight: 'bold' },
});

export default LoginScreen;
```

#### 6. **Exemplo de Tela: TarefasScreen**
Crie `src/screens/TarefasScreen.js`.

```javascript
import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, TouchableOpacity, StyleSheet, Alert } from 'react-native';
import { api } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { useNavigation } from '@react-navigation/native';

const TarefasScreen = () => {
  const [tarefas, setTarefas] = useState([]);
  const { logout, isAuthenticated } = useAuth();
  const navigation = useNavigation();

  useEffect(() => {
    if (!isAuthenticated) return;

    const fetchTarefas = async () => {
      try {
        const { data } = await api.get('tarefas/');
        setTarefas(data.results || data);
      } catch (error) {
        Alert.alert('Erro', 'Falha ao carregar tarefas');
      }
    };

    fetchTarefas();
  }, [isAuthenticated]);

  const handleLogout = async () => {
    await logout();
    navigation.replace('Login');
  };

  const renderTarefa = ({ item }) => (
    <View style={styles.item}>
      <Text>{item.titulo} - {item.status}</Text>
    </View>
  );

  if (!isAuthenticated) return <Text>Carregando...</Text>;

  return (
    <View style={styles.container}>
      <FlatList
        data={tarefas}
        keyExtractor={(item) => item.id.toString()}
        renderItem={renderTarefa}
      />
      <TouchableOpacity style={styles.button} onPress={handleLogout}>
        <Text style={styles.buttonText}>Logout</Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20 },
  item: { padding: 15, borderBottomWidth: 1, borderBottomColor: '#ccc' },
  button: { backgroundColor: '#FF3B30', padding: 15, borderRadius: 5, alignItems: 'center', marginTop: 20 },
  buttonText: { color: 'white', fontWeight: 'bold' },
});

export default TarefasScreen;
```

#### 7. **Dicas de Implementação e Melhoria**
- **Dev Tools**: Use Flipper ou React Native Debugger para inspecionar network/storage.
- **Refresh em Background**: Para apps em background, use `react-native-background-fetch` para validar tokens periodicamente.
- **UI/UX**: Integre `react-native-paper` ou `native-base` para componentes nativos. Adicione pull-to-refresh com `RefreshControl` no FlatList.
- **Erros de Rede**: Em mobile, trate offline com `NetInfo` (instale `npm install @react-native-community/netinfo`).
- **Testes**: Use `jest` + `@testing-library/react-native` para mockar Axios e AsyncStorage.
- **Produção**: Build com Expo ou bare workflow; configure ProGuard para ofuscação. Para iOS/Android, use biometria com `react-native-biometrics`.
- **Expansão**: Adicione tela de criação de tarefa com `api.post('tarefas/', { titulo: 'Nova' })`.

Se precisar de código full (ex.: git repo simulado), integração com Redux, ou foco em Expo/Flutter, avise! Posso também adaptar para criação de tarefas ou notificações push.




### Adicionando Push Notifications ao App ToDo List (React Native + Django)

Para adicionar **push notifications** ao seu app ToDo List, usaremos **Firebase Cloud Messaging (FCM)**, que é o padrão para Android/iOS em React Native. Isso permite enviar notificações do backend Django (ex.: lembretes de tarefas vencidas) para o dispositivo do usuário.

**Fluxo Geral**:
- **Frontend (RN)**: Registra o token FCM do dispositivo, envia para o backend (via API), e lida com recebimento de notificações (foreground/background).
- **Backend (Django)**: Armazena tokens por usuário (nova tabela/campo), usa `firebase-admin` para enviar notificações baseadas em eventos (ex.: tarefa vencida).
- **Gatilhos**: Use signals ou Celery para enviar notificações automáticas (ex.: via `notificacao` model).

Assumi que você tem um projeto Firebase configurado (crie em [console.firebase.google.com](https://console.firebase.google.com)). Baixe `google-services.json` (Android) e `GoogleService-Info.plist` (iOS), e adicione-os ao projeto RN.

#### 1. **Configuração no Firebase**
- Crie um projeto Firebase.
- Ative FCM (Cloud Messaging).
- Para o backend: Gere uma chave de serviço (`serviceAccountKey.json`) em Project Settings > Service Accounts > Generate New Private Key. Salve em `/path/to/your/django/project/firebase_credentials.json` (adicione ao `.gitignore`).

#### 2. **Integração no Backend (Django)**
Instale dependências: `pip install firebase-admin celery[redis]` (para jobs assíncronos; use Redis como broker).

##### **Atualize models.py** (Adicione campo para FCM token no Usuario ou nova tabela)
```python
# Em todo_list/models.py (adicione ao Usuario ou crie DeviceToken)
from django.db import models

class DeviceToken(models.Model):
    """
    Armazena FCM tokens por dispositivo/usuário.
    """
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='device_tokens')
    token = models.CharField(max_length=500, unique=True)
    plataforma = models.CharField(max_length=10, choices=[('android', 'Android'), ('ios', 'iOS')], default='android')
    data_criacao = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        db_table = 'device_token'

    def __str__(self):
        return f'Token para {self.usuario.nome} ({self.plataforma})'
```

Rode `makemigrations` e `migrate`.

##### **firebase_config.py** (Novo arquivo em todo_list/)
```python
import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings

# Inicializa Firebase (rode uma vez, ex.: em __init__.py do app)
if not firebase_admin._apps:
    cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)  # Caminho para firebase_credentials.json
    firebase_admin.initialize_app(cred)
```

##### **views.py** (Adicione endpoints para registrar token e enviar notificação)
```python
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import DeviceToken, Notificacao
from .serializers import DeviceTokenSerializer  # Crie um serializer simples
from firebase_config import messaging  # Importa do arquivo acima

class UsuarioViewSet(viewsets.ReadOnlyModelViewSet):
    # ... (código anterior)
    
    @action(detail=False, methods=['post'])
    def registrar_token(self, request):
        """
        Registra FCM token do dispositivo.
        Body: {"token": "fcm_token_aqui", "plataforma": "android"}
        """
        serializer = DeviceTokenSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(usuario=request.user)
            return Response({'status': 'Token registrado'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def enviar_push_notificacao(usuario_id, titulo, corpo, data=None):
    """
    Função helper para enviar push via FCM.
    """
    usuario = Usuario.objects.get(id=usuario_id)
    tokens = usuario.device_tokens.filter(ativo=True).values_list('token', flat=True)
    
    if not tokens:
        return {'status': 'Sem tokens registrados'}
    
    message = messaging.MulticastMessage(
        notification=messaging.Notification(title=titulo, body=corpo),
        tokens=list(tokens),
        data=data or {}  # Dados custom (ex.: {'tarefa_id': 123})
    )
    
    response = messaging.send_multicast(message)
    success_count = response.success_count
    failure_count = response.failure_count
    
    # Log falhas (opcional)
    if failure_count > 0:
        for idx, resp in enumerate(response.responses):
            if not resp.success:
                print(f'Falha no token {tokens[idx]}: {resp.exception()}')
    
    return {'success': success_count, 'failure': failure_count}

# Exemplo: Envie notificação ao criar Notificacao (use signal ou Celery)
@receiver(post_save, sender=Notificacao)
def trigger_push(sender, instance, created, **kwargs):
    if created and instance.tipo == 'LEMBRETE':
        enviar_push_notificacao(
            instance.usuario_id,
            'Lembrete de Tarefa',
            instance.mensagem
        )
```

##### **settings.py** (Adicione)
```python
import os

FIREBASE_CREDENTIALS_PATH = os.path.join(BASE_DIR, 'firebase_credentials.json')

# Para Celery (opcional, para envios assíncronos)
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
```

- **Serializer para DeviceToken** (em serializers.py):
  ```python
  class DeviceTokenSerializer(serializers.ModelSerializer):
      class Meta:
          model = DeviceToken
          fields = ['token', 'plataforma']
  ```

- **Uso**: No RN, chame POST `/api/usuarios/registrar_token/` após login.

#### 3. **Integração no Frontend (React Native)**
Instale dependências: `npm install @react-native-firebase/app @react-native-firebase/messaging` (e configure nativos per [docs](https://rnfirebase.io/)).

##### **App.js** (Atualize para inicializar FCM)
```javascript
import React, { useEffect } from 'react';
import { AuthProvider } from './src/contexts/AuthContext';
import AppNavigator from './src/navigation/AppNavigator';  // Seu navigator anterior
import messaging from '@react-native-firebase/messaging';
import { api } from './src/services/api';
import { useAuth } from './src/contexts/AuthContext';

const App = () => {
  const { user } = useAuth();  // user do context

  useEffect(() => {
    // Solicita permissão para notificações
    const requestPermission = async () => {
      const authStatus = await messaging().requestPermission();
      const enabled =
        authStatus === messaging.AuthorizationStatus.AUTHORIZED ||
        authStatus === messaging.AuthorizationStatus.PROVISIONAL;

      if (enabled) {
        console.log('Permissão concedida');
        await registrarFCMToken(user?.id);
      }
    };

    if (user) {
      requestPermission();
    }

    // Listener para notificações em foreground
    const unsubscribe = messaging().onMessage(async remoteMessage => {
      Alert.alert('Nova Notificação!', `${remoteMessage.notification.title}: ${remoteMessage.notification.body}`);
    });

    // Listener para background/quit state
    messaging().setBackgroundMessageHandler(async remoteMessage => {
      console.log('Mensagem em background:', remoteMessage);
    });

    return unsubscribe;
  }, [user]);

  const registrarFCMToken = async (userId) => {
    const token = await messaging().getToken();
    await api.post('usuarios/registrar_token/', {
      token,
      plataforma: Platform.OS,  // 'android' ou 'ios'
    });
    console.log('FCM Token registrado:', token);
  };

  return (
    <AuthProvider>
      <AppNavigator />
    </AuthProvider>
  );
};

export default App;
```

- **Permissões**: No Android, adicione `<uses-permission android:name="android.permission.POST_NOTIFICATIONS" />` em `AndroidManifest.xml` (para API 33+). No iOS, configure em `Info.plist`.

##### **Exemplo de Envio Automático no Backend**
Para lembretes diários (use Celery task):
```python
# tasks.py (novo arquivo)
from celery import shared_task
from datetime import datetime, timedelta
from .views import enviar_push_notificacao
from .models import Tarefas

@shared_task
def enviar_lembretes_diarios():
    hoje = datetime.now().date()
    tarefas_vencidas = Tarefas.objects.filter(
        data_vencimento=hoje,
        status='PENDENTE',
        usuario__device_tokens__isnull=False
    ).distinct()
    
    for tarefa in tarefas_vencidas:
        enviar_push_notificacao(
            tarefa.usuario_id,
            'Tarefa Vencendo!',
            f'{tarefa.titulo} vence hoje! Prioridade: {tarefa.prioridade}.'
        )
```

- Rode Celery: `celery -A seu_projeto worker -l info` e agende com `celery beat`.

#### 4. **Testando Push Notifications**
- **Backend**: Use Postman para POST token, então chame uma view custom para testar envio.
- **RN**: Rode o app (`npx react-native run-android` ou iOS), conceda permissão, e simule envio via Firebase Console (Cloud Messaging > Compose).
- **Debug**: Use `adb logcat` (Android) ou Console.app (iOS) para logs FCM.

#### 5. **Dicas e Considerações**
- **Produção**: Use APNs para iOS (FCM lida internamente). Armazene tokens com expiração (FCM tokens mudam).
- **Celery para Escala**: Para envios em massa, evite bloquear views.
- **Dados Custom**: Envie `data` payload para deep links (ex.: abrir tarefa específica).
- **Expansão**: Integre com `notificacao` model para histórico. Para web push, use Web Push API.
- **Docs Atualizadas (2025)**: Baseado em FCM v10+; verifique [rnfirebase.io](https://rnfirebase.io/messaging/usage) para mudanças.

Se precisar de Celery setup completo, iOS-specific code, ou integração com relatórios, avise! Posso também fornecer um exemplo de deep linking.




### Local Notifications in React Native for the ToDo List App

Local notifications in React Native allow your app to schedule and display alerts directly on the device (e.g., reminders for task deadlines), without needing a server or internet connection. This is perfect for the ToDo List app: when a user creates a task with a `data_vencimento`, we can schedule a local notification to remind them offline. Unlike push notifications (which we added with FCM), local ones are device-managed and work in all app states (foreground, background, killed).

As of November 2025, the recommended library for bare React Native (non-Expo) is **`@notifee/react-native`**. It's actively maintained, cross-platform (Android/iOS), and supports advanced features like channels, actions, and custom styles. It replaces older options like `react-native-push-notification` for better performance and API consistency.

#### 1. **Installation and Setup**
Install the library and link it:
```bash
npm install @notifee/react-native
# For iOS: cd ios && pod install
# For Android: No extra steps needed, but ensure minSdkVersion 21+ in android/build.gradle
```

**Android Configuration** (`android/app/src/main/AndroidManifest.xml`):
Add permissions inside `<manifest>`:
```xml
<uses-permission android:name="android.permission.VIBRATE" />
<uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" />
<uses-permission android:name="android.permission.POST_NOTIFICATIONS" />  <!-- For Android 13+ -->
```

**iOS Configuration** (`ios/YourApp/Info.plist`):
Add these keys:
```xml
<key>UIBackgroundModes</key>
<array>
    <string>background-processing</string>
    <string>fetch</string>
</array>
<key>NSUserNotificationsUsageDescription</key>
<string>This app uses notifications to remind you of tasks.</string>
```

Initialize Notifee in your app's entry point (e.g., `index.js` or `App.js`):
```javascript
import notifee, { AndroidImportance } from '@notifee/react-native';
import { Platform } from 'react-native';

// Request permission on app start
async function requestPermission() {
  const settings = await notifee.requestPermission({
    badge: true,
    sound: true,
    alert: true,
    provisional: false,  // iOS: Ask for full permission
  });
  if (settings.authorizationStatus >= 1) {
    console.log('Permission granted');
    await createChannel();
  } else {
    console.log('Permission denied');
  }
}

// Create Android channel (required for Android 8+)
async function createChannel() {
  if (Platform.OS === 'android') {
    await notifee.createChannel({
      id: 'todo-reminders',
      name: 'ToDo Reminders',
      importance: AndroidImportance.HIGH,  // Ensures sound/vibration
      vibration: true,
      sound: 'default',
    });
  }
}

// Call on app launch
requestPermission();
```

#### 2. **Scheduling Local Notifications**
Integrate this into your ToDo app. When creating/updating a task (e.g., in a form), schedule a notification 5 minutes before the due date (or at due date).

**Example: Schedule Notification for a Task** (in `src/services/notifications.js` or directly in `TarefasScreen.js`):
```javascript
import notifee, { AndroidImportance, TriggerType } from '@notifee/react-native';
import { Platform } from 'react-native';

// Function to schedule a task reminder
export const scheduleTaskNotification = async (task) => {
  if (!task.data_vencimento) return;  // No due date, no notification

  const dueDate = new Date(task.data_vencimento);
  const triggerDate = new Date(dueDate.getTime() - 5 * 60 * 1000);  // 5 min before

  if (triggerDate <= new Date()) return;  // Already past due

  const trigger = {
    type: TriggerType.TIMESTAMP,
    timestamp: triggerDate.getTime(),
  };

  const notificationId = await notifee.createTriggerNotification(
    {
      title: 'ToDo Reminder',
      body: `${task.titulo} is due soon! Priority: ${task.prioridade}`,
      android: {
        channelId: 'todo-reminders',
        smallIcon: 'ic_notification',  // Add to android/app/src/main/res/drawable
        pressAction: {
          id: `task-${task.id}`,  // Unique ID for handling press
        },
      },
      ios: {
        sound: 'default',
        badge: 1,  // Update app icon badge
      },
      data: { taskId: task.id.toString() },  // Custom data for handling
    },
    trigger
  );

  console.log(`Notification scheduled for task ${task.id} with ID: ${notificationId}`);
  return notificationId;  // Store this in AsyncStorage or sync to backend
};

// Cancel a notification (e.g., when task is completed)
export const cancelTaskNotification = async (taskId) => {
  await notifee.cancelNotificationByTag(`task-${taskId}`);
};
```

**Integration in TarefasScreen.js** (Update when creating/updating task):
```javascript
// In your create/update task logic (after API call)
const createTask = async (newTaskData) => {
  try {
    const response = await api.post('tarefas/', newTaskData);
    const task = response.data;
    
    // Schedule local notification
    await scheduleTaskNotification(task);
    
    // Refresh list
    fetchTarefas();
  } catch (error) {
    Alert.alert('Error', 'Failed to create task');
  }
};

// When marking as complete
const completeTask = async (taskId) => {
  // Update via API...
  await cancelTaskNotification(taskId);  // Cancel reminder
};
```

#### 3. **Handling Notification Events**
Listen for presses to open the app/task details, even if the app is closed.

In `App.js` (or a global listener file):
```javascript
import notifee from '@notifee/react-native';
import { useEffect } from 'react';
import { useNavigation } from '@react-navigation/native';

export const NotificationListener = () => {
  const navigation = useNavigation();

  useEffect(() => {
    // Foreground events (app open)
    return notifee.onForegroundEvent(({ type, detail }) => {
      if (type === notifee.EventType.PRESS) {
        const taskId = detail.notification.data?.taskId;
        if (taskId) {
          navigation.navigate('TarefaDetails', { taskId: parseInt(taskId) });
        }
      }
    });
  }, []);

  // Background/killed state (use getInitialNotification for launch)
  useEffect(() => {
    notifee.getInitialNotification()
      .then((initialNotification) => {
        if (initialNotification) {
          const taskId = initialNotification.notification.data?.taskId;
          if (taskId && navigation.isReady()) {
            navigation.navigate('TarefaDetails', { taskId: parseInt(taskId) });
          }
        }
      });
  }, [navigation]);

  // For background events, add to your main component or use a service
  return null;
};

// Add <NotificationListener /> to your AppNavigator
```

#### 4. **Best Practices**
- **Permissions First**: Always check/request permissions before scheduling. Handle denials gracefully (e.g., show a settings prompt).
- **Unique IDs/Tags**: Use task IDs in notification tags (`notifee.cancelNotificationByTag`) for easy cancellation/updates.
- **Testing**: 
  - Use physical devices (simulators don't support notifications fully).
  - Test app states: Foreground (shows inline), background (banner), killed (launch app).
  - Schedule short delays (e.g., 10s) for quick testing.
- **Customization**: 
  - Android: Use channels for categorization (e.g., high-priority for 'ALTA').
  - iOS: Leverage critical alerts if needed (requires entitlement).
  - Styles: Add big text/pictures for rich tasks (e.g., attach task description).
- **Offline Sync**: When online, sync scheduled notifications to backend (e.g., store IDs in `tarefas` model extension).
- **Edge Cases**: Handle timezones (use UTC for `timestamp`), repeating notifications (e.g., daily check-ins with `TriggerType.DAILY`), and battery optimization (prompt users to disable on Android).
- **Alternatives**: For Expo apps, use `expo-notifications` (simpler but less flexible). Avoid deprecated libs like `react-native-push-notification`.

This setup ensures reliable reminders for tasks, enhancing user engagement. For example, a task due Nov 20, 2025, at 9 AM will notify at 8:55 AM. If you need iOS-specific tweaks, repeating notifications, or integration with the Django backend for hybrid push/local, let me know!






### Integração com Celery, Testes Unitários para API e OAuth2 Social Login no App ToDo List

Vou estender o app ToDo List (Django backend + React Native frontend) com as funcionalidades solicitadas. Assumi a estrutura anterior (modelos, ViewSets, JWT auth). Para **Celery**, focarei em tarefas assíncronas como geração de relatórios e envio de notificações. Para **testes unitários**, usarei `APITestCase` do DRF para endpoints chave. Para **OAuth2 Social Login**, usarei `dj-rest-auth` + `django-allauth` para backend (Google/GitHub), com integração frontend em RN via `react-native-app-auth` ou webviews.

#### 1. **Integração com Celery Tasks**
Celery gerencia tarefas assíncronas (ex.: relatórios semanais, lembretes push). Use Redis como broker (instale: `pip install celery redis`). Rode Celery com `celery -A todo_list worker -l info` e Beat para agendamento: `celery -A todo_list beat -l info`.

##### **settings.py** (Adições)
```python
# Celery
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# Para Beat (agendamento)
CELERY_BEAT_SCHEDULE = {
    'gerar-relatorios-semanais': {
        'task': 'todo_list.tasks.gerar_relatorios_semanais',
        'schedule': 86400.0,  # Diário (em segundos); ajuste para semanal
    },
    'enviar-lembretes-diarios': {
        'task': 'todo_list.tasks.enviar_lembretes_diarios',
        'schedule': 3600.0,  # Hora em hora
    },
}
```

##### **tasks.py** (Novo arquivo em `todo_list/tasks.py`)
```python
import json
from celery import shared_task
from datetime import date, timedelta
from django.utils import timezone
from .models import Relatorio, Tarefas, Usuario, Notificacao
from .views import enviar_push_notificacao  # Do setup anterior de push

@shared_task
def gerar_relatorios_semanais():
    """
    Gera relatório semanal para todos usuários ativos.
    """
    fim = date.today()
    inicio = fim - timedelta(days=7)
    usuarios = Usuario.objects.filter(ativo=True)
    
    for usuario in usuarios:
        tarefas = Tarefas.objects.filter(
            usuario=usuario,
            data_criacao__range=[inicio, fim]
        )
        total = tarefas.count()
        concluidas = tarefas.filter(status='CONCLUIDA').count()
        produtividade = (concluidas / total * 100) if total > 0 else 0
        
        Relatorio.objects.create(
            usuario=usuario,
            periodo_inicio=inicio,
            periodo_fim=fim,
            total_tarefas=total,
            tarefas_concluidas=concluidas,
            produtividade=round(produtividade, 2),
            resumo=json.dumps({
                'categorias': [t.categoria.nome for t in tarefas if t.categoria],
                'insights': f'Produtividade: {produtividade:.2f}%'
            })
        )
    print(f'Relatórios gerados para {usuarios.count()} usuários')

@shared_task
def enviar_lembretes_diarios():
    """
    Envia lembretes para tarefas pendentes vencendo amanhã.
    Integra com push notifications.
    """
    amanha = date.today() + timedelta(days=1)
    tarefas = Tarefas.objects.filter(
        data_vencimento=amanha,
        status='PENDENTE'
    )
    
    for tarefa in tarefas:
        # Cria notificação no banco
        Notificacao.objects.create(
            usuario=tarefa.usuario,
            tarefa=tarefa,
            mensagem=f'Lembrete: {tarefa.titulo} vence amanhã!',
            tipo='LEMBRETE'
        )
        
        # Envia push (do setup anterior)
        enviar_push_notificacao(
            tarefa.usuario_id,
            'Lembrete de Tarefa',
            f'{tarefa.titulo} vence em 24h. Prioridade: {tarefa.prioridade}'
        )
    print(f'Lembretes enviados para {tarefas.count()} tarefas')

# Exemplo de uso síncrono em views (para testes)
def trigger_relatorio_manual(usuario_id):
    gerar_relatorios_semanais.delay()  # Assíncrono
```

- **Integração em Views**: No `RelatorioViewSet`, chame `gerar_relatorios_semanais.delay()` no `@action(detail=False, methods=['post']) def gerar_manual(self, request):`.
- **Frontend (RN)**: Para disparar manual, adicione botão que chama API endpoint para task.

#### 2. **Unit Tests para API**
Use `pytest` ou Django's `TestCase`. Instale `pytest-django` (`pip install pytest-django`). Rode com `pytest`.

##### **tests/test_api.py** (Novo arquivo em `todo_list/tests/`)
```python
import pytest
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import Tarefas, Usuario, Relatorio
from unittest.mock import patch, MagicMock

Usuario = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user():
    return Usuario.objects.create_user(email='test@example.com', password='testpass123', nome='Test User')

@pytest.fixture
def user_client(user, api_client):
    # Simula JWT login (use force_authenticate para tests)
    api_client.force_authenticate(user=user)
    return api_client

class TestTarefasAPIViewSet(APITestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(email='user@example.com', password='pass', nome='User')
        self.client.force_authenticate(user=self.user)
        self.url = reverse('tarefa-list')  # Ajuste para seu router: /api/tarefas/

    def test_list_tarefas_authenticated(self):
        Tarefas.objects.create(titulo='Test Task', usuario=self.user, status='PENDENTE')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_tarefa(self):
        data = {'titulo': 'New Task', 'prioridade': 'ALTA', 'data_vencimento': '2025-11-20'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Tarefas.objects.count(), 1)
        self.assertEqual(Tarefas.objects.first().titulo, 'New Task')

    def test_unauthenticated_access(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class TestRelatorioAPIViewSet(APITestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(email='report@example.com', password='pass', nome='Report User')
        self.client.force_authenticate(user=self.user)
        self.url = reverse('relatorio-list')

    @patch('todo_list.tasks.gerar_relatorios_semanais.delay')  # Mock Celery task
    def test_gerar_relatorio_manual(self, mock_task):
        response = self.client.post(self.url + 'gerar/')  # Seu @action
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_task.assert_called_once()

class TestNotificacaoAPIViewSet(APITestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(email='notif@example.com', password='pass', nome='Notif User')
        self.tarefa = Tarefas.objects.create(titulo='Notif Task', usuario=self.user)
        self.client.force_authenticate(user=self.user)
        self.url = reverse('notificacao-list')

    def test_create_notificacao(self):
        data = {'tarefa': self.tarefa.id, 'mensagem': 'Test Msg', 'tipo': 'LEMBRETE'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Notificacao.objects.count(), 1)
```

- **Rodar Testes**: `pytest todo_list/tests/test_api.py -v`. Cubra 80%+ com coverage (`pip install pytest-cov`; `pytest --cov`).
- **Mocking**: Use `@patch` para Celery e Firebase para isolar testes.

#### 3. **OAuth2 Social Login**
Use `dj-rest-auth` + `django-allauth` para backend (OAuth2 providers como Google). Instale: `pip install dj-rest-auth django-allauth social-auth-app-django`.

##### **settings.py** (Adições)
```python
INSTALLED_APPS += [
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',  # + 'github' para GitHub
    'dj_rest_auth',
    'dj_rest_auth.registration',
]

# Allauth
SITE_ID = 1
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': 'your-google-client-id',
            'secret': 'your-google-secret',
            'key': ''
        },
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
    },
    # Similar para GitHub
}

# dj-rest-auth
REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] += ['dj_rest_auth.jwt_auth.JWTCookieAuthentication']
# Ou mantenha JWT header
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
```

##### **urls.py** (Atualize raiz e app)
Em `projeto/urls.py`:
```python
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client

urlpatterns += [
    path('dj-rest-auth/', include('dj_rest_auth.urls')),
    path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),
    path('dj-rest-auth/google/', SocialLoginView.adapter_view(GoogleOAuth2Adapter),
         name='google_login'),
         {'client_class': OAuth2Client}),
]
```

- **Configuração Provider**: No Google Console, crie OAuth2 app com redirect URI `http://localhost:8000/dj-rest-auth/google/callback/`. Similar para GitHub.

##### **Frontend (React Native) Integração**
Use `react-native-app-auth` para OAuth flow (`npm install react-native-app-auth expo-auth-session` se Expo). Exemplo em `LoginScreen.js`:
```javascript
import { authorize } from 'react-native-app-auth';

const googleConfig = {
  issuer: 'https://accounts.google.com',
  scopes: ['openid', 'profile', 'email'],
  clientId: 'your-google-client-id',
  redirectUrl: 'com.yourapp:/oauthredirect',  // Configure em RN
  serviceConfiguration: {
    authorizationEndpoint: 'https://accounts.google.com/o/oauth2/v2/auth',
    tokenEndpoint: 'https://oauth2.googleapis.com/token',
  },
};

const handleGoogleLogin = async () => {
  try {
    const result = await authorize(googleConfig);
    // Envie result.accessToken para backend: POST /dj-rest-auth/google/ com token
    const { data } = await api.post('dj-rest-auth/google/', {
      access_token: result.accessToken,
    });
    // Salve JWT de data (access/refresh)
    await saveTokens(data.access, data.refresh);
    navigation.replace('Tarefas');
  } catch (error) {
    Alert.alert('Erro', 'Falha no login Google');
  }
};

// Adicione botão <TouchableOpacity onPress={handleGoogleLogin}><Text>Login com Google</Text></TouchableOpacity>
```

- **iOS/Android Setup**: Configure URL schemes em `Info.plist` e `AndroidManifest.xml` para redirect.
- **Segurança**: Use PKCE para mobile OAuth.

Essas adições tornam o app escalável e seguro. Para deploy (ex.: Heroku com Redis), ou mais providers/testes, avise!




### Deploying Your Django ToDo List App to Heroku

Heroku is an excellent PaaS for deploying Django apps, offering easy scaling, managed Postgres, and add-ons like Redis for Celery. This guide assumes your ToDo List project (with DRF, JWT, Celery, Firebase for push notifications, and social auth) is ready in a Git repo. We'll use the latest Heroku CLI (v8+ as of Nov 2025) and best practices for Django 5.x.

#### Prerequisites
1. **Install Heroku CLI**: Download from [devcenter.heroku.com/articles/heroku-cli](https://devcenter.heroku.com/articles/heroku-cli). Verify: `heroku --version`.
2. **Git Repo**: Ensure your project is in Git (`git init` if not). Commit all code: `git add . && git commit -m "Initial commit"`.
3. **Heroku Account**: Sign up at [heroku.com](https://heroku.com) and login: `heroku login`.
4. **Free Tier Limits**: Hobby dynos are free but sleep after 30min inactivity; upgrade for production ($7/mo). Add-ons like Postgres are free for basics.

#### Step 1: Prepare Your Django Project
Heroku runs your app as a Python web dyno. Update these files:

##### **runtime.txt** (Root of repo)
Specify Python version (use 3.12 for compatibility with your libs):
```
python-3.12.7
```

##### **requirements.txt** (Root of repo)
Generate with `pip freeze > requirements.txt`, but curate for production (remove dev deps like pytest). Example for your app:
```
Django==5.1.2
djangorestframework==3.15.2
djangorestframework-simplejwt==5.3.1
dj-rest-auth==6.0.0
django-allauth==65.0.1
celery==5.4.0
redis==5.1.1
psycopg2-binary==2.9.9  # For Postgres
firebase-admin==6.5.0
gunicorn==22.0.0  # WSGI server for Heroku
whitenoise==6.7.0  # Static files serving
python-decouple==3.8  # For env vars
```

##### **Procfile** (Root of repo, no extension)
Defines dynos:
```
web: gunicorn todo_list.wsgi:application --log-file -
worker: celery -A todo_list worker -l info  # For Celery tasks
beat: celery -A todo_list beat -l info  # For scheduled tasks (scale separately)
release: python manage.py migrate --noinput && python manage.py collectstatic --noinput  # Run migrations/static on deploy
```

##### **todo_list/wsgi.py** (Update if needed)
Ensure it uses `os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'todo_list.settings')`:
```python
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'todo_list.settings')
application = get_wsgi_application()
```

##### **settings.py** (Production Adjustments)
Use `python-decouple` for secrets. Add:
```python
from decouple import config
import django_heroku  # pip install django-heroku (add to requirements.txt)

# Security
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = ['*']  # Tighten in prod

# Database (Heroku Postgres)
DATABASES = {
    'default': config('DATABASE_URL', cast='uri', default='sqlite:///db.sqlite3')
}  # Heroku injects DATABASE_URL

# Static/Media Files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Celery (use Heroku Redis add-on)
CELERY_BROKER_URL = config('REDIS_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = CELERY_BROKER_URL

# JWT/Firestore Secrets
SIMPLE_JWT['SIGNING_KEY'] = config('SECRET_KEY')  # Use Heroku config var
FIREBASE_CREDENTIALS_PATH = config('FIREBASE_CREDENTIALS_PATH')  # Upload JSON as config var or file

# Social Auth (Google keys as config vars)
SOCIALACCOUNT_PROVIDERS['google']['APP']['client_id'] = config('GOOGLE_CLIENT_ID')
SOCIALACCOUNT_PROVIDERS['google']['APP']['secret'] = config('GOOGLE_CLIENT_SECRET')

# WhiteNoise for static files
MIDDLEWARE = ['whitenoise.middleware.WhiteNoiseMiddleware', ...]  # Add after SecurityMiddleware
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Heroku Config
django_heroku.settings(locals())
```

- **.gitignore**: Add `staticfiles/`, `media/`, `*.sqlite3`, and your Firebase JSON.

#### Step 2: Add Heroku Add-ons
- **Postgres**: `heroku addons:create heroku-postgresql:hobby-dev -a your-app-name` (injects `DATABASE_URL`).
- **Redis** (for Celery): `heroku addons:create heroku-redis:hobby-dev -a your-app-name` (sets `REDIS_URL`).

#### Step 3: Environment Variables
Set secrets via CLI (never commit them):
```
heroku config:set SECRET_KEY=your-django-secret-key -a your-app-name
heroku config:set DEBUG=False -a your-app-name
heroku config:set GOOGLE_CLIENT_ID=your-google-id -a your-app-name
heroku config:set GOOGLE_CLIENT_SECRET=your-google-secret -a your-app-name
heroku config:set FIREBASE_CREDENTIALS_PATH=your-firebase-json-content  # Base64 or multiline
# For Firebase, upload the JSON content as a string var and load in firebase_config.py
```

For multiline (Firebase JSON): Use `heroku config:set FIREBASE_CREDENTIALS='{"type":"service_account",...}' -a your-app-name`.

#### Step 4: Deploy to Heroku
1. Create app: `heroku create your-app-name` (e.g., `todolist-xai-2025`).
2. Push code: `git push heroku main` (runs release phase: migrate + collectstatic).
3. Scale dynos: `heroku ps:scale web=1 worker=1 beat=1 -a your-app-name`.
4. Open: `heroku open` (visits https://your-app-name.herokuapp.com).
5. Logs: `heroku logs --tail` for debugging.

- **API Base**: Your endpoints will be at `https://your-app-name.herokuapp.com/api/tarefas/`, etc.

#### Step 5: Handling Static/Media Files
- **Collectstatic**: Already in release phase.
- **Media Uploads**: For user avatars (perfil model), use Heroku's ephemeral storage or add AWS S3 (via `django-storages` + add-on).
- **Frontend (RN)**: Deploy separately (e.g., Expo EAS or App Store); it consumes the API URL via env var.

#### Step 6: Celery on Heroku
- Workers/Beat dynos handle tasks like `gerar_relatorios_semanais`.
- Scale: `heroku ps:scale worker=0:1 beat=0:1` (dyno indexing for multiple).
- Redis add-on auto-scales; monitor with `heroku redis:info`.

#### Step 7: Verification and Monitoring
- **Run Migrations**: `heroku run python manage.py migrate -a your-app-name`.
- **Create Superuser**: `heroku run python manage.py createsuperuser -a your-app-name`.
- **Test API**: Use Postman with `https://your-app-name.herokuapp.com/api/auth/login/`.
- **Push Notifications**: Ensure Firebase project is linked; tokens register via API.
- **Monitoring**: Add New Relic/Sentry add-ons: `heroku addons:create newrelic:stairway -a your-app-name`.
- **Custom Domain**: `heroku domains:add www.yourdomain.com` + DNS setup.

#### Common Issues & Tips
- **Gunicorn Errors**: Ensure `gunicorn` in requirements; check logs for port binding.
- **Static 404s**: Verify WhiteNoise middleware order.
- **Celery Fails**: Confirm Redis URL; test locally with `docker run -p 6379:6379 redis`.
- **Sleepy Dynos**: Upgrade to Basic ($7/mo) for always-on.
- **Costs**: Free tier: 550-1000 dyno hours/mo; Postgres/Redis free for dev.
- **CI/CD**: Integrate GitHub Actions: On push, `git push heroku main`.
- **2025 Updates**: Heroku deprecated free dynos in 2022 but offers credits; use Vercel/Netlify for static if scaling frontend.

Your ToDo app should now be live! For RN integration, update `API_BASE_URL` to the Heroku domain in `api.js`. If issues (e.g., social auth callback), share logs. Need AWS S3 for media or full CI script? Let me know!






### Deploying Your Django App to Railway

Railway is a modern, GitHub-integrated PaaS that simplifies deploying Django apps with built-in support for PostgreSQL, Redis (for Celery), and automatic builds. It's free for hobby projects (up to $5/mo credit) and scales easily. This guide is based on the official Railway docs and recent tutorials (as of November 2025). It assumes a standard Django project (e.g., with DRF, JWT, or Celery like in our ToDo List example). No major updates to the process in 2025—Railway still auto-detects Django via `manage.py`.

#### Prerequisites
1. **Accounts and Tools**:
   - Sign up at [railway.app](https://railway.app) (GitHub login recommended).
   - Install Railway CLI: `npm install -g @railway/cli` (or via Homebrew: `brew install railway`).
   - Git repo: Push your Django project to GitHub (private/public OK).
   - Python 3.10+ and Django installed locally for testing.

2. **Project Readiness**:
   - Test locally: `python manage.py runserver` and `python manage.py migrate`.
   - Virtual env: Use one and generate `requirements.txt` with `pip freeze > requirements.txt`.

#### Step 1: Prepare Your Django Project
Railway uses Nixpacks for builds (auto-detects Python/Django), but add these for production.

##### **requirements.txt** (Root of repo)
Include essentials (curate from `pip freeze`):
```
Django==5.1.2  # Or your version
gunicorn==22.0.0  # WSGI server
whitenoise==6.7.0  # Static files
psycopg[binary]==3.2.1  # Postgres adapter
# Add others: djangorestframework, celery, redis, etc.
```

##### **Procfile** (Root of repo, no extension)
Defines start commands (Railway uses this for dynos):
```
web: gunicorn your_project.wsgi:application --bind 0.0.0.0:$PORT
# For Celery (if using): worker: celery -A your_project worker -l info
# For Beat: beat: celery -A your_project beat -l info
```

##### **your_project/settings.py** (Production config)
Update for Railway's env vars (e.g., for Postgres):
```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Security
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
ALLOWED_HOSTS = ['*']  # Or ['your-railway-app.up.railway.app']

# Database (Railway injects via service vars)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('PGDATABASE', 'postgres'),
        'USER': os.getenv('PGUSER', 'postgres'),
        'PASSWORD': os.getenv('PGPASSWORD', ''),
        'HOST': os.getenv('PGHOST', 'postgres.railway.internal'),  # Internal service
        'PORT': os.getenv('PGPORT', '5432'),
        'OPTIONS': {'sslmode': 'require'},  # Secure connection
    }
}

# Static/Media Files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# WhiteNoise for static serving
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add here
    # ... other middleware
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Celery (if using)
CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = CELERY_BROKER_URL

# JWT/Secrets: Use Railway vars
# SIMPLE_JWT['SIGNING_KEY'] = os.getenv('SECRET_KEY')
# Social auth keys: os.getenv('GOOGLE_CLIENT_ID'), etc.

# Run collectstatic in release (optional, Railway handles)
```

- **.gitignore**: Exclude `db.sqlite3`, `__pycache__`, `staticfiles/`, `media/`, and secrets.
- **Local Testing**: Set env vars locally (e.g., via `.env` with `python-decouple`) and run `python manage.py collectstatic`.

#### Step 2: Add Services (Database, Redis)
Railway uses "services" for DBs—link them to your app via vars.

1. **Postgres**:
   - In Railway dashboard: New Project > Deploy from GitHub repo > Add Service > Database > PostgreSQL.
   - Railway auto-generates vars like `PGDATABASE`, `PGHOST` (use `${{Postgres.PGDATABASE}}` in app vars).

2. **Redis** (for Celery):
   - Add Service > Database > Redis.
   - Set `REDIS_URL = ${{Redis.REDIS_URL}}` in app vars.

#### Step 3: Deploy to Railway
Three methods—pick one.

##### **Method 1: GitHub Integration (Easiest, Recommended)**
1. Log in to Railway dashboard: `railway login`.
2. New Project > Deploy from GitHub Repo > Select your repo/branch.
3. Railway detects Django, builds, and deploys (logs in dashboard).
4. Add Postgres/Redis services (as Step 2).
5. Set vars: In app settings > Variables, add `SECRET_KEY=your-secret`, `DEBUG=False`, `GOOGLE_CLIENT_ID=...`, etc. Reference DB vars like `DATABASE_URL=${{Postgres.DATABASE_URL}}` (Railway auto-parses for Django).
6. Trigger deploy: Push to GitHub (auto-deploys) or manual "Deploy" button.
7. Domain: Settings > Networking > Generate Public Domain (e.g., `your-app.up.railway.app`).

##### **Method 2: CLI Deployment**
1. `railway login` and `railway init` (links to new/existing project).
2. `railway link` to connect repo.
3. Add DB: `railway add postgres` (or `railway add redis`).
4. Set vars: `railway variables set SECRET_KEY=your-secret DEBUG=False`.
5. Deploy: `railway up` (uploads changes; use Git for ongoing).
6. Run migrations: `railway run python manage.py migrate`.
7. Collect static: `railway run python manage.py collectstatic --noinput`.

##### **Method 3: One-Click Template**
- Go to Railway templates: Search "Django" > Deploy template (includes Postgres).
- Fork to GitHub, customize, and deploy as Method 1.

#### Step 4: Post-Deployment
- **Migrations/Static**: Railway runs builds, but manual: `railway run python manage.py migrate` and `collectstatic`.
- **Superuser**: `railway run python manage.py createsuperuser`.
- **Logs/Monitoring**: Dashboard > Logs tab (real-time). Add variables like `LOG_LEVEL=INFO`.
- **Custom Domain**: Networking > Add Domain (free SSL).
- **Scaling**: Services > Scale (CPU/RAM); free tier: 512MB RAM, 0.5 vCPU.
- **Celery**: Add worker/beat services with Procfile commands; link to Redis/Postgres.
- **API Testing**: Use Postman on `https://your-app.up.railway.app/api/tarefas/` with JWT.

#### Common Issues & Tips (2025)
- **Build Fails**: Ensure `runtime.txt` with `python-3.12.7` if needed; check logs for missing deps.
- **DB Connection**: Use internal host (`postgres.railway.internal`) for services; external for local dev.
- **Static Files 404**: Confirm WhiteNoise and `collectstatic` in build (add to `railway.json` if custom: `{ "build": { "command": "python manage.py collectstatic --noinput" } }`).
- **Costs**: $5/mo credit; Postgres/Redis ~$5/mo each beyond free tier.
- **CI/CD**: Auto-deploys on GitHub push; integrate GitHub Actions for tests.
- **Firebase/Social**: Set JSON/content as vars (multiline OK); update redirect URIs to Railway domain.
- **Security**: `DEBUG=False`; use Railway's env vars for all secrets. Scan with `railway run python manage.py check --deploy`.

Your app deploys in ~5 mins! For our ToDo List, update RN `API_BASE_URL` to the Railway domain. If stuck (e.g., Celery setup), share error logs. Need Railway vs. Heroku comparison or Vercel for frontend? Ask!    





### Deploying Django with Celery on Railway (Updated for 2025)

Railway remains one of the best platforms for deploying Django apps with Celery in 2025, thanks to its seamless GitHub integration, built-in Redis/Postgres services, and one-click templates for full stacks including Celery workers and Beat schedulers. It's cost-effective ($5/mo credit for hobbyists) and auto-scales. This guide builds on the previous Django deployment steps, focusing on Celery integration (e.g., for your ToDo List tasks like report generation and notifications). Based on Railway's official docs and recent templates (e.g., Django/Celery/Redis/Postgres stack), here's how to do it.

#### Prerequisites
- Django project with Celery configured (e.g., `tasks.py`, `CELERY_BROKER_URL` in `settings.py`).
- GitHub repo with your code (including `Procfile`, `requirements.txt` from previous guide).
- Railway account (sign up via GitHub at [railway.app](https://railway.app)).
- Install Railway CLI: `npm install -g @railway/cli` (or `brew install railway`).

#### Step 1: Prepare Your Project for Celery
Ensure your setup supports multiple processes (web server + workers).

##### **Procfile** (Root of repo)
Railway uses this for service commands. Define separate services for web, worker, and beat:
```
web: gunicorn your_project.wsgi:application --bind 0.0.0.0:$PORT
worker: celery -A your_project worker --loglevel=info --concurrency=2  # Adjust concurrency
beat: celery -A your_project beat --loglevel=info  # For scheduled tasks like crontabs
release: python manage.py migrate --noinput && python manage.py collectstatic --noinput
```

##### **requirements.txt**
Add Celery/Redis deps:
```
Django==5.1.2
gunicorn==22.0.0
whitenoise==6.7.0
psycopg[binary]==3.2.1
celery==5.4.0
redis==5.1.1
# Your other deps (DRF, simplejwt, etc.)
```

##### **settings.py** (Celery Config)
Use Railway env vars for broker/backend:
```python
import os

# Celery
CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# Beat Schedule (if using periodic tasks)
from celery.schedules import crontab
CELERY_BEAT_SCHEDULE = {
    'gerar-relatorios-semanais': {
        'task': 'your_app.tasks.gerar_relatorios_semanais',
        'schedule': crontab(hour=0, minute=0, day_of_week='monday'),  # Weekly
    },
}

# Other settings from previous guide (DB, static files, etc.)
```

- **Test Locally**: Run `celery -A your_project worker -l info` and `celery -A your_project beat -l info` in separate terminals. Trigger a task (e.g., via Django shell: `from your_app.tasks import my_task; my_task.delay()`).

#### Step 2: Use Railway's One-Click Template (Recommended for Quick Start)
Railway provides pre-built templates for Django + Celery stacks, saving setup time.

1. Go to [Railway Templates](https://railway.app/templates) in your dashboard.
2. Search for "Django Celery" or use direct links:
   - [Django, Celery, Redis & Postgres](https://railway.app/template/NBR_V3) (full stack with tasks demo).
   - [Django with Celery](https://railway.app/template/a6vvTu) (basic structure).
3. Click **Deploy Template** > Select your GitHub repo (fork the template if customizing).
4. Railway auto-detects Django, installs deps, and provisions services:
   - **Web Service**: For your Django app.
   - **Worker Service**: Runs Celery workers (scaled independently).
   - **Beat Service**: For schedulers (optional; enable if using periodic tasks).
   - **Redis**: Broker for queues.
   - **Postgres**: DB.

5. In the project dashboard:
   - **Variables**: Set `SECRET_KEY`, `DEBUG=False`, `REDIS_URL=${{Redis.REDIS_URL}}`, `DATABASE_URL=${{Postgres.DATABASE_URL}}` (Railway auto-links services).
   - For Firebase/social auth: Add as vars (e.g., `GOOGLE_CLIENT_ID=...`).

#### Step 3: Manual Deployment via CLI or Dashboard (If Not Using Template)
1. **Link Repo**: `railway login` > `railway init` > Select/create project > Link GitHub repo.
2. **Add Services**:
   - Postgres: Dashboard > New > Database > PostgreSQL (or CLI: `railway add postgres`).
   - Redis: Dashboard > New > Database > Redis (CLI: `railway add redis`).
3. **Set Vars**:
   ```
   railway variables set SECRET_KEY=your-secret DEBUG=False
   railway variables set REDIS_URL=${{Redis.REDIS_URL}}  # References service
   railway variables set DATABASE_URL=${{Postgres.DATABASE_URL}}
   ```
4. **Deploy**:
   - Push to GitHub (auto-deploys).
   - Or CLI: `railway up`.
5. **Run One-Off Commands**:
   ```
   railway run python manage.py migrate
   railway run python manage.py createsuperuser
   railway run python manage.py collectstatic --noinput
   ```

#### Step 4: Configure and Scale Services
- **Services Tab** (Dashboard):
  - **Web**: Default; expose port 8000 (Railway auto-binds `$PORT`).
  - **Worker**: Scale to 1+ instances (e.g., for high-volume tasks like notifications).
  - **Beat**: Deploy as a separate service if using schedules; scale to 1 (single instance to avoid duplicates).
- **Health Checks**: Add to `Procfile` or dashboard (e.g., `/health/` endpoint returning 200).
- **Networking**: Services communicate via internal URLs (e.g., `redis.railway.internal:6379`).

#### Step 5: Verify and Monitor
- **Domain**: Settings > Generate Public Domain (e.g., `your-app.up.railway.app`). API at `/api/tarefas/`.
- **Test Celery**:
  - Trigger a task via API/shell: `railway run python manage.py shell` > `from your_app.tasks import my_task; my_task.delay()`.
  - Check logs: Dashboard > Logs > Select service (web/worker/beat).
- **Monitoring**: Built-in metrics (CPU/RAM); integrate Sentry/New Relic via vars.
- **Costs (2025)**: $5/mo credit covers basics; Redis/Postgres ~$5/mo each. Scale workers dynamically.

#### Best Practices for Django + Celery in 2025
From recent guides (e.g., Docker-focused deployments and scalable arch):
- **Dockerize for Consistency**: Use multi-stage Dockerfile (build + runtime) for prod:
  ```
  FROM python:3.12-slim as builder
  WORKDIR /app
  COPY requirements.txt .
  RUN pip install --user -r requirements.txt

  FROM python:3.12-slim
  WORKDIR /app
  COPY --from=builder /root/.local /root/.local
  COPY . .
  ENV PATH=/root/.local/bin:$PATH
  CMD ["gunicorn", "your_project.wsgi:application", "--bind", "0.0.0.0:$PORT"]
  ```
  Add to Railway via `railway.json`: `{ "build": { "builder": "NIXPACKS" } }`.
- **Env Vars Everywhere**: Use `python-decouple` for all configs; never hardcode.
- **Task Reliability**: Use `CELERY_TASK_ACKS_LATE=True` for retries; monitor queues with Flower (`pip install flower`; add `flower: celery -A your_project flower` to Procfile).
- **Security**: `DEBUG=False`; scan with `railway run python manage.py check --deploy`.
- **CI/CD**: GitHub Actions for tests/deploy: On push, run pytest + `railway up`.
- **Scaling**: Start with 1 worker; monitor with Railway metrics. For high load, use separate queues (e.g., `CELERY_TASK_DEFAULT_QUEUE='default'`).

This deploys a robust, production-ready setup in ~10 mins. For your ToDo List, tasks like `enviar_lembretes_diarios` will run reliably. If preferring Docker/Heroku/AWS, or troubleshooting (e.g., worker logs), provide details!