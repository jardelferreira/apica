from fastapi import Depends, FastAPI
import uvicorn
from routers import certificadoApovacao
from fastapi.responses import FileResponse

from fastapi.middleware.cors import CORSMiddleware

tag_ca = [
    {
        "name": "Certificado de Aprovação",
        "description": "Consultas e Operações da BaseCAEPI"        
    }
]
app = FastAPI( 
    title="API BaseCAEPI",
    description="""Pesquisar e recuperar informações(por json ou arquivo de excel) sobre os certificados de aprovação emitidos para EPIs.\n
    Codigo fonte: https://github.com/JoaoAugustoMV/API_BaseCAEPI
        """,
        openapi_tags=tag_ca
    )

origins = [
    "http://localhost",
    "https://www.jfwebsystem.com.br",
    "http://www.jfwebsystem.com.br",
    "https://jfwebsystem.com.br",
    "http://jfwebsystem.com.br",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(certificadoApovacao.router)

@app.get("/", tags=["HOME"])
async def index():
    return "Atualizado"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)