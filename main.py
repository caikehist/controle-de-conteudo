from fastapi import FastAPI, Request, UploadFile, File, HTTPException, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base
from pydantic import BaseModel
from typing import Optional, List
from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware
import pandas as pd
import io
import os
import secrets
from datetime import datetime, timedelta
from jose import JWTError, jwt

# Configurações de Autenticação
SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configuração do Google OAuth (variáveis de ambiente)
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "seu-client-id-aqui")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "seu-client-secret-aqui")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")

# Configuração do Banco de Dados SQLite
DATABASE_URL = "sqlite:///./conteudos.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo de Usuário
class UsuarioDB(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    nome = Column(String, nullable=True)
    foto_url = Column(String, nullable=True)
    ativo = Column(Boolean, default=True)
    criado_em = Column(String, default=lambda: datetime.now().isoformat())

# Modelo do Banco de Dados de Conteúdos
class ConteudoDB(Base):
    __tablename__ = "conteudos"
    
    id = Column(Integer, primary_key=True, index=True)
    usuario_email = Column(String, nullable=True)  # Vincula ao usuário que criou
    trimestre = Column(String, nullable=True)
    bimestre = Column(String, nullable=True)
    data = Column(String, nullable=True)
    turma = Column(String, nullable=True)
    turno = Column(String, nullable=True)
    componente_curricular = Column(String, nullable=True)
    conteudo = Column(String, nullable=True)
    registrado = Column(String, default="NAO")
    professor = Column(String, nullable=True)
    escola = Column(String, nullable=True)

# Criar tabelas
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sistema de Gestão de Conteúdos")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
templates = Jinja2Templates(directory=".")

# Configuração OAuth
oauth = OAuth()
oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

# Pydantic Schema
class ConteudoSchema(BaseModel):
    id: Optional[int] = None
    usuario_email: Optional[str] = None
    trimestre: Optional[str] = None
    bimestre: Optional[str] = None
    data: Optional[str] = None
    turma: Optional[str] = None
    turno: Optional[str] = None
    componente_curricular: Optional[str] = None
    conteudo: Optional[str] = None
    registrado: Optional[str] = "NAO"
    professor: Optional[str] = None
    escola: Optional[str] = None
    
    class Config:
        from_attributes = True

class UsuarioSchema(BaseModel):
    email: str
    nome: Optional[str] = None
    foto_url: Optional[str] = None

# Funções de autenticação
def get_current_user(request: Request):
    user = request.session.get('user')
    if not user:
        return None
    return user

def login_required(request: Request):
    user = get_current_user(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": "/login"}
        )
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Rotas de Autenticação
@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/auth/google")
async def auth_google(request: Request):
    redirect_uri = GOOGLE_REDIRECT_URI
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/auth/google/callback")
async def auth_google_callback(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
        
        if not user_info:
            raise HTTPException(status_code=400, detail="Erro ao obter informações do usuário")
        
        email = user_info.get('email')
        nome = user_info.get('name')
        foto_url = user_info.get('picture')
        
        # Salvar ou atualizar usuário no banco
        db = SessionLocal()
        try:
            usuario = db.query(UsuarioDB).filter(UsuarioDB.email == email).first()
            if not usuario:
                usuario = UsuarioDB(email=email, nome=nome, foto_url=foto_url)
                db.add(usuario)
            else:
                usuario.nome = nome
                usuario.foto_url = foto_url
            db.commit()
        finally:
            db.close()
        
        # Salvar na sessão
        request.session['user'] = {
            'email': email,
            'nome': nome,
            'foto_url': foto_url
        }
        
        return RedirectResponse(url="/", status_code=302)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na autenticação: {str(e)}")

@app.get("/logout")
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url="/", status_code=302)

# Rotas da Aplicação
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    user = get_current_user(request)
    db = SessionLocal()
    try:
        # Se usuário logado, mostrar apenas seus conteúdos
        if user:
            conteudos = db.query(ConteudoDB).filter(ConteudoDB.usuario_email == user['email']).all()
        else:
            conteudos = db.query(ConteudoDB).all()
        
        return templates.TemplateResponse("template.html", {
            "request": request,
            "conteudos": conteudos,
            "user": user
        })
    finally:
        db.close()

@app.post("/import-csv")
async def import_csv(file: UploadFile = File(...), request: Request = None):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Usuário deve estar logado para importar CSV")
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Arquivo deve ser CSV")
    
    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents), encoding='utf-8')
        
        colunas_esperadas = ['trimestre', 'bimestre', 'data', 'turma', 'turno', 
                           'componente curricular', 'conteudo', 'registrado', 
                           'professor', 'escola']
        
        for col in colunas_esperadas:
            if col not in df.columns:
                raise HTTPException(status_code=400, detail=f"Coluna '{col}' não encontrada no CSV")
        
        db = SessionLocal()
        try:
            count = 0
            for _, row in df.iterrows():
                conteudo = ConteudoDB(
                    usuario_email=user['email'],
                    trimestre=str(row['trimestre']) if pd.notna(row['trimestre']) else None,
                    bimestre=str(row['bimestre']) if pd.notna(row['bimestre']) else None,
                    data=str(row['data']) if pd.notna(row['data']) else None,
                    turma=str(row['turma']) if pd.notna(row['turma']) else None,
                    turno=str(row['turno']) if pd.notna(row['turno']) else None,
                    componente_curricular=str(row['componente curricular']) if pd.notna(row['componente curricular']) else None,
                    conteudo=str(row['conteudo']) if pd.notna(row['conteudo']) else None,
                    registrado=str(row['registrado']) if pd.notna(row['registrado']) else "NAO",
                    professor=str(row['professor']) if pd.notna(row['professor']) else None,
                    escola=str(row['escola']) if pd.notna(row['escola']) else None
                )
                db.add(conteudo)
                count += 1
            db.commit()
            return {"message": f"{count} registros importados com sucesso!"}
        finally:
            db.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar CSV: {str(e)}")

@app.post("/conteudos/")
async def create_conteudo(conteudo: ConteudoSchema, request: Request):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Usuário deve estar logado para criar conteúdo")
    
    db = SessionLocal()
    try:
        db_conteudo = ConteudoDB(
            usuario_email=user['email'],
            **conteudo.model_dump(exclude={'id', 'usuario_email'})
        )
        db.add(db_conteudo)
        db.commit()
        db.refresh(db_conteudo)
        return db_conteudo
    finally:
        db.close()

@app.get("/api/conteudos/", response_model=List[ConteudoSchema])
async def read_conteudos(request: Request):
    user = get_current_user(request)
    db = SessionLocal()
    try:
        if user:
            return db.query(ConteudoDB).filter(ConteudoDB.usuario_email == user['email']).all()
        else:
            return []
    finally:
        db.close()

@app.put("/conteudos/{conteudo_id}")
async def update_conteudo(conteudo_id: int, conteudo: ConteudoSchema, request: Request):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Usuário deve estar logado para editar conteúdo")
    
    db = SessionLocal()
    try:
        db_conteudo = db.query(ConteudoDB).filter(ConteudoDB.id == conteudo_id).first()
        if db_conteudo is None:
            raise HTTPException(status_code=404, detail="Conteúdo não encontrado")
        
        # Verificar se o usuário é dono do conteúdo
        if db_conteudo.usuario_email != user['email']:
            raise HTTPException(status_code=403, detail="Não autorizado a editar este conteúdo")
        
        update_data = conteudo.model_dump(exclude={'id', 'usuario_email'}, exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_conteudo, key, value)
        
        db.commit()
        db.refresh(db_conteudo)
        return db_conteudo
    finally:
        db.close()

@app.delete("/conteudos/{conteudo_id}")
async def delete_conteudo(conteudo_id: int, request: Request):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Usuário deve estar logado para excluir conteúdo")
    
    db = SessionLocal()
    try:
        db_conteudo = db.query(ConteudoDB).filter(ConteudoDB.id == conteudo_id).first()
        if db_conteudo is None:
            raise HTTPException(status_code=404, detail="Conteúdo não encontrado")
        
        # Verificar se o usuário é dono do conteúdo
        if db_conteudo.usuario_email != user['email']:
            raise HTTPException(status_code=403, detail="Não autorizado a excluir este conteúdo")
        
        db.delete(db_conteudo)
        db.commit()
        return {"message": "Conteúdo excluído com sucesso!"}
    finally:
        db.close()

@app.post("/conteudos/{conteudo_id}/registrar")
async def registrar_conteudo(conteudo_id: int, request: Request):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Usuário deve estar logado")
    
    db = SessionLocal()
    try:
        db_conteudo = db.query(ConteudoDB).filter(ConteudoDB.id == conteudo_id).first()
        if db_conteudo is None:
            raise HTTPException(status_code=404, detail="Conteúdo não encontrado")
        
        # Verificar se o usuário é dono do conteúdo
        if db_conteudo.usuario_email != user['email']:
            raise HTTPException(status_code=403, detail="Não autorizado a registrar este conteúdo")
        
        db_conteudo.registrado = "SIM"
        db.commit()
        db.refresh(db_conteudo)
        return db_conteudo
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
