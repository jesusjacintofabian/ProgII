import logging

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database import Base, engine, SessionLocal
from app.routers import auth, rrhh, inventario, mesa_ayuda, admin, seguridad
from app.security.rate_limit import limiter
from app import models

# --- Logging (auditoría técnica adicional a la tabla LogAuditoria) ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    filename="secure_company_360.log",
)
logger = logging.getLogger("secure_company_360")

# En producción: docs_url=None, redoc_url=None para reducir superficie de reconocimiento
app = FastAPI(
    title="Secure Company 360 - API",
    description="Grupo 1 (RRHH + Inventario) y Grupo 2 (Mesa de Ayuda + Admin)",
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- CORS restrictivo (whitelist, no "*") ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


# --- Bloqueo real de IPs (Respuesta Automática - Grupo 3) ---
# Cualquier IP marcada como bloqueada en la tabla IPBloqueada queda rechazada
# de verdad, no solo listada en el dashboard.
@app.middleware("http")
async def bloquear_ips_maliciosas(request: Request, call_next):
    if request.url.path in ("/health", "/docs", "/openapi.json"):
        return await call_next(request)

    ip_cliente = request.client.host if request.client else None
    # Nunca bloqueamos localhost/loopback: si el propio servidor (o el admin
    # probando desde la misma máquina) quedara bloqueado, nadie podría volver
    # a entrar ni siquiera para desbloquearlo. En producción, detrás de un
    # proxy real, el tráfico externo nunca llega como 127.0.0.1 de todas formas.
    if ip_cliente and ip_cliente not in ("127.0.0.1", "::1", "localhost"):
        db = SessionLocal()
        try:
            bloqueada = db.query(models.IPBloqueada).filter(
                models.IPBloqueada.direccion_ip == ip_cliente,
                models.IPBloqueada.activo == True,
            ).first()
        finally:
            db.close()
        if bloqueada:
            logger.warning(f"IP_BLOQUEADA_RECHAZADA | {ip_cliente} intentó acceder a {request.url.path}")
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "Acceso denegado: esta dirección IP está bloqueada por el sistema de seguridad."},
            )
    return await call_next(request)


# --- Cabeceras de seguridad en cada respuesta ---
@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


# --- Manejo de errores: nunca exponer detalles internos al cliente ---
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"Error no controlado en {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Ocurrió un error interno. Intenta más tarde."},
    )


# --- Routers ---
app.include_router(auth.router)
app.include_router(rrhh.router)
app.include_router(inventario.router)
app.include_router(mesa_ayuda.router)
app.include_router(admin.router)
app.include_router(seguridad.router)


@app.get("/health", tags=["Sistema"])
def health_check():
    return {"status": "ok", "sistema": "Secure Company 360"}


@app.on_event("startup")
def startup():
    # Crea las tablas si no existen (útil en desarrollo; en producción usar
    # database/schema.sql directamente en SQL Server).
    Base.metadata.create_all(bind=engine)
    logger.info("Secure Company 360 API iniciada")
