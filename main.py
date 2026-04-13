from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from pydantic import BaseModel
from typing import Optional, List
import pandas as pd
import io

# Configuração do Banco de Dados SQLite
DATABASE_URL = "sqlite:///./conteudos.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo do Banco de Dados
class ConteudoDB(Base):
    __tablename__ = "conteudos"
    
    id = Column(Integer, primary_key=True, index=True)
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
templates = Jinja2Templates(directory=".")

# Pydantic Schema
class ConteudoSchema(BaseModel):
    id: Optional[int] = None
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

# Rotas
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    db = SessionLocal()
    try:
        conteudos = db.query(ConteudoDB).all()
        return templates.TemplateResponse("template.html", {
            "request": request,
            "conteudos": conteudos
        })
    finally:
        db.close()

@app.post("/import-csv")
async def import_csv(file: UploadFile = File(...)):
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
async def create_conteudo(conteudo: ConteudoSchema):
    db = SessionLocal()
    try:
        db_conteudo = ConteudoDB(**conteudo.model_dump(exclude={'id'}))
        db.add(db_conteudo)
        db.commit()
        db.refresh(db_conteudo)
        return db_conteudo
    finally:
        db.close()

@app.get("/api/conteudos/", response_model=List[ConteudoSchema])
async def read_conteudos():
    db = SessionLocal()
    try:
        return db.query(ConteudoDB).all()
    finally:
        db.close()

@app.put("/conteudos/{conteudo_id}")
async def update_conteudo(conteudo_id: int, conteudo: ConteudoSchema):
    db = SessionLocal()
    try:
        db_conteudo = db.query(ConteudoDB).filter(ConteudoDB.id == conteudo_id).first()
        if db_conteudo is None:
            raise HTTPException(status_code=404, detail="Conteúdo não encontrado")
        
        update_data = conteudo.model_dump(exclude={'id'}, exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_conteudo, key, value)
        
        db.commit()
        db.refresh(db_conteudo)
        return db_conteudo
    finally:
        db.close()

@app.delete("/conteudos/{conteudo_id}")
async def delete_conteudo(conteudo_id: int):
    db = SessionLocal()
    try:
        db_conteudo = db.query(ConteudoDB).filter(ConteudoDB.id == conteudo_id).first()
        if db_conteudo is None:
            raise HTTPException(status_code=404, detail="Conteúdo não encontrado")
        
        db.delete(db_conteudo)
        db.commit()
        return {"message": "Conteúdo excluído com sucesso!"}
    finally:
        db.close()

@app.post("/conteudos/{conteudo_id}/registrar")
async def registrar_conteudo(conteudo_id: int):
    db = SessionLocal()
    try:
        db_conteudo = db.query(ConteudoDB).filter(ConteudoDB.id == conteudo_id).first()
        if db_conteudo is None:
            raise HTTPException(status_code=404, detail="Conteúdo não encontrado")
        
        db_conteudo.registrado = "SIM"
        db.commit()
        db.refresh(db_conteudo)
        return db_conteudo
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
