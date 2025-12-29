from fastapi import FastAPI
from contextlib import asynccontextmanager

from models.database import init_db
from controllers import auth_controller, account_controller, transaction_controller, statement_controller


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database
    await init_db()
    yield
    # Shutdown: Cleanup if needed
    pass


app = FastAPI(
    title="Banking API",
    description="""
    API Bancária Assíncrona com FastAPI
    
    Esta API permite gerenciar operações bancárias de depósitos e saques, vinculadas a contas correntes.
    
    ## Funcionalidades
    
    * **Autenticação**: Registro e login de usuários com JWT
    * **Contas**: Criação e gerenciamento de contas correntes
    * **Transações**: Realização de depósitos e saques com validação
    * **Extratos**: Visualização de extratos bancários completos
    
    ## Autenticação
    
    Para acessar os endpoints protegidos, você precisa:
    1. Registrar um usuário em `/auth/register`
    2. Fazer login em `/auth/login` para obter um token JWT
    3. Incluir o token no header: `Authorization: Bearer <seu_token>`
    """,
    version="1.0.0",
    lifespan=lifespan
)

# Include routers
app.include_router(auth_controller.router)
app.include_router(account_controller.router)
app.include_router(transaction_controller.router)
app.include_router(statement_controller.router)


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - Welcome message
    """
    return {
        "message": "Welcome to Banking API",
        "docs": "/docs",
        "version": "1.0.0"
    }
