# Sistema de Gestão de Conteúdos com Login Google

Aplicação web completa para gestão de conteúdos educacionais com autenticação via Google OAuth e persistência em banco de dados SQLite.

## ✨ Funcionalidades

- 🔐 **Login com Google** - Autenticação segura via OAuth 2.0
- 📋 **CRUD Completo** - Crie, edite e exclua conteúdos
- 📁 **Importação CSV** - Carregue dados em massa via arquivo CSV
- 📊 **Gestão por Usuário** - Cada usuário vê apenas seus próprios conteúdos
- ✅ **Registro de Conteúdo** - Marque conteúdos como registrados com clique na linha
- 📋 **Cópia Automática** - Clique na linha copia o conteúdo para área de transferência
- 💾 **Persistência SQLite** - Dados salvos localmente

## 🚀 Instalação

### 1. Instale as dependências

```bash
pip install -r requirements.txt
```

### 2. Configure o Google OAuth

1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto ou selecione um existente
3. Ative a **Google+ API**
4. Vá em **APIs & Services > Credentials**
5. Clique em **Create Credentials > OAuth client ID**
6. Configure a tela de consentimento OAuth (preencha os dados necessários)
7. Crie uma credencial do tipo **Web application**
8. Adicione em **Authorized redirect URIs**: `http://localhost:8000/auth/google/callback`
9. Copie o **Client ID** e **Client Secret**

### 3. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto (ou use variáveis de ambiente):

```bash
GOOGLE_CLIENT_ID=seu-client-id-aqui
GOOGLE_CLIENT_SECRET=seu-client-secret-aqui
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
```

Ou exporte no terminal:

```bash
export GOOGLE_CLIENT_ID="seu-client-id-aqui"
export GOOGLE_CLIENT_SECRET="seu-client-secret-aqui"
export GOOGLE_REDIRECT_URI="http://localhost:8000/auth/google/callback"
```

### 4. Execute a aplicação

```bash
uvicorn main:app --reload
```

### 5. Acesse no navegador

👉 http://localhost:8000

## 📖 Uso

### Primeiro Acesso
1. Ao acessar a aplicação, clique em **🔐 Login**
2. Faça login com sua conta Google
3. Após autenticado, você será redirecionado para a página principal

### Cadastro Manual
1. Clique em **➕ Novo Conteúdo**
2. Preencha o formulário com os dados:
   - Trimestre, Bimestre, Data
   - Turma, Turno
   - Componente Curricular
   - Conteúdo (obrigatório)
   - Professor, Escola
3. Clique em **💾 Salvar Conteúdo**

### Importação via CSV
1. Clique em **📁 Importar CSV**
2. Arraste o arquivo CSV ou clique para selecionar
3. O CSV deve conter as colunas:
   - trimestre, bimestre, data, turma, turno
   - componente curricular, conteudo, registrado
   - professor, escola

### Marcar como Registrado
1. Na lista de conteúdos, clique em qualquer linha
2. O campo **conteúdo** será copiado automaticamente para a área de transferência
3. Um alert perguntará: "O conteúdo foi registrado?"
4. Se confirmar **OK**, a linha ficará verde e o campo "registrado" será preenchido com "SIM"

### Edição/Exclusão
1. Clique no botão **✏️ Editar** na linha desejada
2. Altere os dados no modal que abrir
3. Clique em **💾 Salvar Alterações** ou **🗑️ Excluir**

## 📁 Estrutura do Projeto

```
/workspace
├── main.py              # Backend FastAPI + Rotas
├── template.html        # Frontend principal
├── login.html           # Página de login
├── requirements.txt     # Dependências Python
├── .env.example         # Exemplo de variáveis de ambiente
├── README.md            # Esta documentação
└── conteudos.db         # Banco de dados SQLite (criado automaticamente)
```

## 🔒 Segurança

- Autenticação via Google OAuth 2.0
- Sessões seguras com secret key aleatória
- Isolamento de dados por usuário
- Validação de propriedade nas operações de edição/exclusão

## 🛠️ Tecnologias

- **Backend**: FastAPI, SQLAlchemy, Authlib
- **Frontend**: HTML5, CSS3, JavaScript
- **Banco de Dados**: SQLite
- **Autenticação**: Google OAuth 2.0
- **Servidor**: Uvicorn (ASGI)

## 📝 Observações

- Os dados são persistidos no arquivo `conteudos.db`
- Cada usuário só pode editar/excluir seus próprios conteúdos
- O CSV é apenas para importação inicial - depois os dados ficam no banco
- A sessão expira após 30 minutos de inatividade

## 🐛 Troubleshooting

### Erro "TemplateNotFound"
Certifique-se de que os arquivos `template.html` e `login.html` estão na mesma pasta que `main.py`.

### Erro de autenticação Google
Verifique se:
- As credenciais estão corretas
- O redirect URI está configurado corretamente no Google Cloud Console
- A Google+ API está ativada

### Dados não aparecem
Verifique se você está logado com a mesma conta Google usada para criar os registros.

## 📄 Licença

Uso livre para fins educacionais e comerciais.
