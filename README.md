# 📚 Sistema de Gestão de Conteúdos

Aplicação web completa para gestão de conteúdos educacionais com persistência em banco de dados SQLite.

## ✨ Funcionalidades

- **📁 Importação via CSV**: Carregue arquivos CSV com todos os campos necessários
- **➕ Cadastro Manual**: Formulário completo para cadastro direto na aplicação
- **✏️ Edição**: Modal de edição para alterar qualquer registro
- **🗑️ Exclusão**: Remova registros indesejados
- **📋 Listagem**: Tabela interativa com todos os registros
- **📝 Registro de Conteúdo**: Clique em uma linha para copiar o conteúdo e marcar como registrado
- **💾 Persistência**: Dados salvos em banco de dados SQLite

## 🚀 Instalação e Execução

### 1. Instale as dependências

```bash
pip install -r requirements.txt
```

### 2. Execute a aplicação

```bash
uvicorn main:app --reload
```

### 3. Acesse no navegador

```
http://127.0.0.1:8000
```

## 📊 Estrutura do CSV

O arquivo CSV deve conter as seguintes colunas:

```
trimestre, bimestre, data, turma, turno, componente curricular, conteudo, registrado, professor, escola
```

### Exemplo de CSV:

```csv
trimestre,bimestre,data,turma,turno,componente curricular,conteudo,registrado,professor,escola
1º Trimestre,1º Bimestre,2024-03-15,9º Ano A,Matutino,Matemática,Equações do segundo grau,NAO,João Silva,Escola Municipal
2º Trimestre,2º Bimestre,2024-06-20,8º Ano B,Vespertino,História,Revolução Industrial,NAO,Maria Santos,Colégio Estadual
```

## 🎯 Como Usar

### Importar CSV
1. Clique no menu "📁 Importar CSV"
2. Arraste o arquivo ou clique para selecionar
3. Os dados serão importados para o banco de dados

### Cadastrar Manualmente
1. Clique no menu "➕ Novo"
2. Preencha todos os campos do formulário
3. Clique em "💾 Salvar"

### Visualizar e Registrar
1. Na lista, clique em qualquer linha
2. O conteúdo será copiado automaticamente para a área de transferência
3. Um alert perguntará se o conteúdo foi registrado
4. Se confirmar "OK", a linha ficará verde e o campo "registrado" será "SIM"

### Editar Registro
1. Na lista, clique no botão "✏️" da linha desejada
2. Altere os campos no modal que abrirá
3. Clique em "💾 Salvar Alterações"

### Excluir Registro
1. Na lista, clique no botão "🗑️" da linha desejada
2. Confirme a exclusão

## 🗄️ Banco de Dados

Os dados são persistidos no arquivo `conteudos.db` (SQLite), criado automaticamente na primeira execução.

## 📁 Arquivos do Projeto

- `main.py` - Backend FastAPI com rotas e modelo do banco de dados
- `template.html` - Frontend completo com HTML, CSS e JavaScript
- `requirements.txt` - Dependências do projeto
- `exemplo.csv` - Arquivo de exemplo para testes
- `conteudos.db` - Banco de dados SQLite (criado automaticamente)

## 🔧 Tecnologias Utilizadas

- **Backend**: FastAPI, SQLAlchemy, Pandas
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Banco de Dados**: SQLite
- **Servidor**: Uvicorn

## 📝 API Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Página principal |
| POST | `/import-csv` | Importar arquivo CSV |
| GET | `/api/conteudos/` | Listar todos os conteúdos |
| POST | `/conteudos/` | Criar novo conteúdo |
| PUT | `/conteudos/{id}` | Atualizar conteúdo |
| DELETE | `/conteudos/{id}` | Excluir conteúdo |
| POST | `/conteudos/{id}/registrar` | Marcar como registrado |
