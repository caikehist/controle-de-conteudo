# Gerenciador de Conteúdo CSV

Aplicação web desenvolvida com **FastAPI** (backend Python) e interface moderna em HTML/CSS/JavaScript para gerenciamento de registros de conteúdo educacional.

## Funcionalidades

- ✅ Upload de arquivos CSV com drag-and-drop ou seleção de arquivo
- ✅ Visualização dos dados em tabela interativa
- ✅ **Clique em qualquer linha**: 
  - Copia automaticamente o campo "conteúdo" para a área de transferência
  - Exibe alerta perguntando se o conteúdo foi registrado
  - Se responder "SIM": a linha fica verde e o campo "registrado" é atualizado
- ✅ Edição posterior do status de registro
- ✅ Interface responsiva e moderna com gradientes e animações
- ✅ Notificações toast para feedback ao usuário

## Requisitos

- Python 3.8+
- FastAPI
- Uvicorn
- Pandas
- Python-multipart

## Instalação

```bash
pip install fastapi uvicorn pandas python-multipart
```

## Execução

```bash
python main.py
```

A aplicação estará disponível em: **http://localhost:8000**

## Formato do Arquivo CSV

O arquivo CSV deve conter as seguintes colunas:

| Coluna | Descrição |
|--------|-----------|
| trimestre | Trimestre letivo (ex: 1º, 2º, 3º) |
| bimestre | Bimestre letivo (ex: 1º, 2º, 3º, 4º) |
| data | Data do registro (ex: 2024-02-15) |
| turma | Turma (ex: 9ºA, 8ºB) |
| turno | Turno (ex: Matutino, Vespertino) |
| componente curricular | Nome da disciplina |
| conteudo | Conteúdo ministrado |
| registrado | Status (SIM/NÃO) |
| professor | Nome do professor |
| escola | Nome da escola |

### Exemplo de CSV

```csv
trimestre,bimestre,data,turma,turno,componente curricular,conteudo,registrado,professor,escola
1º,1º,2024-02-15,9ºA,Matutino,História,Revolução Francesa,NÃO,João Silva,Escola Central
```

## Como Usar

1. **Carregar arquivo**: Arraste e solte seu arquivo CSV na área indicada ou clique em "Selecionar Arquivo"
2. **Visualizar dados**: Os dados serão exibidos em uma tabela organizada
3. **Copiar conteúdo**: Clique em qualquer linha para copiar o conteúdo para a área de transferência
4. **Registrar conteúdo**: Após clicar, confirme no alerta se o conteúdo foi registrado
   - Se "SIM": A linha ficará verde e o status será atualizado
   - Se "NÃO": Nada acontece, você pode tentar novamente depois
5. **Editar posteriormente**: Clique novamente em uma linha já registrada para alterar o status

## API Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Página principal da aplicação |
| POST | `/upload` | Upload de arquivo CSV |
| PUT | `/update/{row_id}` | Atualizar registro de uma linha |
| GET | `/data` | Obter todos os dados carregados |

## Tecnologias Utilizadas

- **Backend**: FastAPI (Python)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Processamento de dados**: Pandas
- **Servidor**: Uvicorn (ASGI)

## Design UI/UX

A interface foi projetada com foco em:
- **Usabilidade**: Interações claras e feedback imediato
- **Acessibilidade**: Cores contrastantes e textos legíveis
- **Estética**: Gradientes modernos, sombras suaves e animações fluidas
- **Responsividade**: Funciona bem em diferentes tamanhos de tela

## Autor

Desenvolvido como solução para gerenciamento de conteúdos educacionais.
