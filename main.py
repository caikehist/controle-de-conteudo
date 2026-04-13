import pandas as pd
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import uuid
import os

app = FastAPI(title="CSV Content Manager")

# Armazenamento em memória para os dados
data_store = {}

class RowData(BaseModel):
    id: str
    trimestre: Optional[str] = None
    bimestre: Optional[str] = None
    data: Optional[str] = None
    turma: Optional[str] = None
    turno: Optional[str] = None
    componente_curricular: Optional[str] = None
    conteudo: Optional[str] = None
    registrado: Optional[str] = None
    professor: Optional[str] = None
    escola: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
async def root():
    html_content = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gerenciador de Conteúdo CSV</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2em;
            margin-bottom: 10px;
        }
        
        .upload-section {
            padding: 30px;
            background: #f8f9fa;
            border-bottom: 2px solid #e9ecef;
        }
        
        .upload-area {
            border: 3px dashed #667eea;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            background: white;
        }
        
        .upload-area:hover {
            border-color: #764ba2;
            background: #f0f0ff;
        }
        
        .upload-area.dragover {
            border-color: #764ba2;
            background: #e8e8ff;
        }
        
        #fileInput {
            display: none;
        }
        
        .upload-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            margin-top: 15px;
            transition: transform 0.2s ease;
        }
        
        .upload-btn:hover {
            transform: scale(1.05);
        }
        
        .table-container {
            padding: 30px;
            overflow-x: auto;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 10px;
            overflow: hidden;
        }
        
        thead {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        th, td {
            padding: 15px 12px;
            text-align: left;
            border-bottom: 1px solid #e9ecef;
        }
        
        th {
            font-weight: 600;
            text-transform: uppercase;
            font-size: 12px;
            letter-spacing: 0.5px;
        }
        
        tbody tr {
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        tbody tr:hover {
            background: #f0f0ff;
            transform: scale(1.01);
        }
        
        tbody tr.registrado {
            background: #d4edda !important;
            color: #155724;
        }
        
        tbody tr.registrado:hover {
            background: #c3e6cb !important;
        }
        
        .status-badge {
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }
        
        .status-sim {
            background: #28a745;
            color: white;
        }
        
        .status-nao {
            background: #dc3545;
            color: white;
        }
        
        .info-text {
            color: #6c757d;
            margin-top: 15px;
            font-size: 14px;
        }
        
        .toast {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: #333;
            color: white;
            padding: 15px 25px;
            border-radius: 8px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            opacity: 0;
            transform: translateY(20px);
            transition: all 0.3s ease;
            z-index: 1000;
        }
        
        .toast.show {
            opacity: 1;
            transform: translateY(0);
        }
        
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #6c757d;
        }
        
        .empty-state i {
            font-size: 48px;
            margin-bottom: 20px;
            display: block;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 Gerenciador de Conteúdo</h1>
            <p>Carregue seu arquivo CSV e gerencie os registros de conteúdo</p>
        </div>
        
        <div class="upload-section">
            <div class="upload-area" id="uploadArea">
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#667eea" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                    <polyline points="17 8 12 3 7 8"></polyline>
                    <line x1="12" y1="3" x2="12" y2="15"></line>
                </svg>
                <h3 style="margin: 20px 0 10px;">Arraste e solte seu arquivo CSV aqui</h3>
                <p style="color: #6c757d;">ou clique para selecionar</p>
                <input type="file" id="fileInput" accept=".csv">
                <button class="upload-btn" onclick="document.getElementById('fileInput').click()">
                    Selecionar Arquivo
                </button>
                <p class="info-text">O arquivo deve conter as colunas: trimestre, bimestre, data, turma, turno, componente curricular, conteudo, registrado, professor, escola</p>
            </div>
        </div>
        
        <div class="table-container">
            <div id="emptyState" class="empty-state">
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#6c757d" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                    <line x1="16" y1="13" x2="8" y2="13"></line>
                    <line x1="16" y1="17" x2="8" y2="17"></line>
                    <polyline points="10 9 9 9 8 9"></polyline>
                </svg>
                <h3 style="margin: 20px 0 10px;">Nenhum arquivo carregado</h3>
                <p>Faça upload de um arquivo CSV para visualizar os dados</p>
            </div>
            
            <table id="dataTable" style="display: none;">
                <thead>
                    <tr>
                        <th>Trimestre</th>
                        <th>Bimestre</th>
                        <th>Data</th>
                        <th>Turma</th>
                        <th>Turno</th>
                        <th>Componente Curricular</th>
                        <th>Conteúdo</th>
                        <th>Registrado</th>
                        <th>Professor</th>
                        <th>Escola</th>
                    </tr>
                </thead>
                <tbody id="tableBody">
                </tbody>
            </table>
        </div>
    </div>
    
    <div class="toast" id="toast"></div>
    
    <script>
        let currentData = [];
        
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const dataTable = document.getElementById('dataTable');
        const tableBody = document.getElementById('tableBody');
        const emptyState = document.getElementById('emptyState');
        const toast = document.getElementById('toast');
        
        // Drag and drop handlers
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0 && files[0].name.endsWith('.csv')) {
                handleFile(files[0]);
            } else {
                showToast('Por favor, selecione um arquivo CSV válido');
            }
        });
        
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFile(e.target.files[0]);
            }
        });
        
        async function handleFile(file) {
            const formData = new FormData();
            formData.append('file', file);
            
            try {
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    const data = await response.json();
                    currentData = data.data;
                    renderTable();
                    showToast('Arquivo carregado com sucesso!');
                } else {
                    showToast('Erro ao carregar o arquivo');
                }
            } catch (error) {
                showToast('Erro de conexão: ' + error.message);
            }
        }
        
        function renderTable() {
            if (currentData.length === 0) {
                emptyState.style.display = 'block';
                dataTable.style.display = 'none';
                return;
            }
            
            emptyState.style.display = 'none';
            dataTable.style.display = 'table';
            
            tableBody.innerHTML = currentData.map(row => `
                <tr data-id="${row.id}" class="${row.registrado === 'SIM' ? 'registrado' : ''}" onclick="handleRowClick('${row.id}')">
                    <td>${escapeHtml(row.trimestre || '')}</td>
                    <td>${escapeHtml(row.bimestre || '')}</td>
                    <td>${escapeHtml(row.data || '')}</td>
                    <td>${escapeHtml(row.turma || '')}</td>
                    <td>${escapeHtml(row.turno || '')}</td>
                    <td>${escapeHtml(row.componente_curricular || '')}</td>
                    <td><strong>${escapeHtml(row.conteudo || '')}</strong></td>
                    <td>
                        <span class="status-badge ${row.registrado === 'SIM' ? 'status-sim' : 'status-nao'}">
                            ${row.registrado || 'NÃO'}
                        </span>
                    </td>
                    <td>${escapeHtml(row.professor || '')}</td>
                    <td>${escapeHtml(row.escola || '')}</td>
                </tr>
            `).join('');
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        async function handleRowClick(rowId) {
            const row = currentData.find(r => r.id === rowId);
            if (!row) return;
            
            // Copiar conteúdo para a área de transferência
            if (row.conteudo) {
                try {
                    await navigator.clipboard.writeText(row.conteudo);
                    showToast('Conteúdo copiado para a área de transferência!');
                } catch (err) {
                    // Fallback para navegadores mais antigos
                    const textArea = document.createElement('textarea');
                    textArea.value = row.conteudo;
                    document.body.appendChild(textArea);
                    textArea.select();
                    document.execCommand('copy');
                    document.body.removeChild(textArea);
                    showToast('Conteúdo copiado para a área de transferência!');
                }
            }
            
            // Perguntar se o conteúdo foi registrado
            setTimeout(() => {
                if (confirm('O conteúdo foi registrado?')) {
                    updateRegistro(rowId, 'SIM');
                }
            }, 300);
        }
        
        async function updateRegistro(rowId, valor) {
            try {
                const response = await fetch(`/update/${rowId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ registrado: valor })
                });
                
                if (response.ok) {
                    const updatedRow = await response.json();
                    const index = currentData.findIndex(r => r.id === rowId);
                    if (index !== -1) {
                        currentData[index] = updatedRow;
                        renderTable();
                        showToast('Registro atualizado com sucesso!');
                    }
                } else {
                    showToast('Erro ao atualizar registro');
                }
            } catch (error) {
                showToast('Erro de conexão: ' + error.message);
            }
        }
        
        function showToast(message) {
            toast.textContent = message;
            toast.classList.add('show');
            setTimeout(() => {
                toast.classList.remove('show');
            }, 3000);
        }
    </script>
</body>
</html>
    """
    return html_content

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Ler o arquivo CSV
        df = pd.read_csv(file.file)
        
        # Normalizar nomes das colunas (substituir espaços por underscores e lowercase)
        df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]
        
        # Validar colunas necessárias
        required_columns = ['trimestre', 'bimestre', 'data', 'turma', 'turno', 
                          'componente_curricular', 'conteudo', 'registrado', 
                          'professor', 'escola']
        
        for col in required_columns:
            if col not in df.columns:
                raise HTTPException(status_code=400, detail=f"Coluna '{col}' não encontrada no CSV. Colunas encontradas: {list(df.columns)}")
        
        # Converter para lista de dicionários com ID único
        data = []
        for index, row in df.iterrows():
            row_data = {
                'id': str(uuid.uuid4()),
                'trimestre': str(row['trimestre']) if pd.notna(row['trimestre']) else '',
                'bimestre': str(row['bimestre']) if pd.notna(row['bimestre']) else '',
                'data': str(row['data']) if pd.notna(row['data']) else '',
                'turma': str(row['turma']) if pd.notna(row['turma']) else '',
                'turno': str(row['turno']) if pd.notna(row['turno']) else '',
                'componente_curricular': str(row['componente_curricular']) if pd.notna(row['componente_curricular']) else '',
                'conteudo': str(row['conteudo']) if pd.notna(row['conteudo']) else '',
                'registrado': str(row['registrado']) if pd.notna(row['registrado']) else '',
                'professor': str(row['professor']) if pd.notna(row['professor']) else '',
                'escola': str(row['escola']) if pd.notna(row['escola']) else ''
            }
            data.append(row_data)
        
        # Armazenar em memória
        data_store['current'] = data
        
        return {"message": "Arquivo processado com sucesso", "data": data}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/update/{row_id}")
async def update_row(row_id: str, row_data: RowData):
    if 'current' not in data_store:
        raise HTTPException(status_code=400, detail="Nenhum dado carregado")
    
    # Encontrar e atualizar a linha
    for i, row in enumerate(data_store['current']):
        if row['id'] == row_id:
            # Atualizar apenas o campo 'registrado'
            if row_data.registrado is not None:
                data_store['current'][i]['registrado'] = row_data.registrado
            return data_store['current'][i]
    
    raise HTTPException(status_code=404, detail="Linha não encontrada")

@app.get("/data")
async def get_data():
    if 'current' not in data_store:
        return {"data": []}
    return {"data": data_store['current']}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
