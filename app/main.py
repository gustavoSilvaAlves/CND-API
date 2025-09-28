from fastapi import FastAPI
from app.core import settings
from app.endpoints import status, cndt, cnd

app = FastAPI(
    title=settings.app_name,
    description="API para consulta de Certidão Negativa de Débitos(CND) e Certidão Negativa de Débitos Trabalhistas (CNDT).",
    version="1.0.0"
)

# Inclui os routers na aplicação principal
app.include_router(status.router, prefix="/api/v1")
app.include_router(cndt.router, prefix="/api/v1")
app.include_router(cnd.router, prefix="/api/v1")