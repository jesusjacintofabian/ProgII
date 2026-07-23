"""
Configuración central de la app.
Todos los secretos vienen de variables de entorno (.env) -- NUNCA hardcodeados.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # --- Base de datos ---
    # Formato SQL Server con pyodbc, ej:
    # mssql+pyodbc://usuario:password@servidor/SecureCompany360?driver=ODBC+Driver+17+for+SQL+Server
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./secure_company_360.db",  # fallback para desarrollo/pruebas locales
    )

    # --- JWT ---
    SECRET_KEY: str = os.getenv("SECRET_KEY", "CAMBIA_ESTA_LLAVE_EN_PRODUCCION")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # --- Seguridad de login ---
    MAX_INTENTOS_FALLIDOS: int = 5
    BLOQUEO_MINUTOS: int = 10

    # --- CORS ---
    ALLOWED_ORIGINS: list[str] = os.getenv(
        "ALLOWED_ORIGINS", "http://localhost:8080"
    ).split(",")

    # --- Rate limiting ---
    LOGIN_RATE_LIMIT: str = "5/minute"
    DEFAULT_RATE_LIMIT: str = "60/minute"


settings = Settings()
