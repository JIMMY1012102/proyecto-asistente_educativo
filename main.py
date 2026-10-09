"""
Asistente de Retroalimentación para Simulacros de Admisión (CNI)
Punto de entrada principal de la aplicación FastAPI

Requisitos: 11.1, 10.2
"""

import os
from dotenv import load_dotenv
from fastapi import FastAPI

# Cargar variables de entorno desde .env
load_dotenv()
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Importar middleware y routers
from app.middleware.auth import AuthMiddleware
from app.routers.auth import router as auth_router

# Verificar que las variables de entorno requeridas estén configuradas
REQUIRED_ENV_VARS = ["GEMINI_API_KEY", "JWT_SECRET_KEY"]
missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Variables de entorno requeridas no configuradas: {missing_vars}")

app = FastAPI(
    title="Asistente de Retroalimentación CNI",
    description="Sistema para procesamiento automático y retroalimentación de simulacros de admisión del CNI",
    version="1.0.0",
    docs_url="/docs" if os.getenv("DEBUG", "False") == "True" else None,
    redoc_url="/redoc" if os.getenv("DEBUG", "False") == "True" else None
)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:8000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de autenticación JWT
# Excluir paths que no requieren autenticación
exclude_paths = [
    "/",
    "/health",
    "/docs",
    "/redoc", 
    "/openapi.json",
    "/auth/login",
    "/auth/test/usuarios",
    "/static"
]

app.add_middleware(AuthMiddleware, exclude_paths=exclude_paths)

# Incluir routers
app.include_router(auth_router)

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    """Endpoint raíz que redirige a la aplicación principal"""
    return {"message": "Asistente de Retroalimentación CNI - API activa"}

@app.get("/health")
async def health_check():
    """Endpoint de verificación de salud"""
    return {"status": "healthy", "app": "Asistente CNI"}

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "True") == "True"
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )