import os
import json
import secrets
import string
import jwt
import bcrypt
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

# Carga las variables de entorno desde el archivo .env
load_dotenv()

# ──────────────────────────────────────────────
# Configuración JWT desde variables de entorno
# ──────────────────────────────────────────────

# Clave secreta para firmar y verificar los tokens JWT
JWT_SECRET = os.getenv('JWT_SECRET_KEY')

# Algoritmo de firma (por defecto HS256 si no está definido)
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')

# Tiempo de expiración del token en minutos (por defecto 30)
JWT_EXPIRATION_MINUTES = int(os.getenv('JWT_EXPIRATION_MINUTES', 30))

# Validación crítica: la aplicación no puede arrancar sin la clave secreta
if not JWT_SECRET:
    raise ValueError(
        "JWT_SECRET_KEY no configurado en el archivo .env"
    )

# Ruta absoluta al archivo de usuarios, relativa a este script.
# Garantiza que funcione correctamente sin importar el directorio de ejecución.
USERS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.json")


# ──────────────────────────────────────────────
# Utilidades internas
# ──────────────────────────────────────────────

def _generar_password_temporal(longitud=12):
    """
    Genera una contraseña aleatoria y segura usando el módulo `secrets`.
    Se usa únicamente al crear el usuario admin por primera vez.
    No se almacena en texto plano ni se hardcodea en el código.
    """
    alfabeto = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alfabeto) for _ in range(longitud))


# ──────────────────────────────────────────────
# Gestión de usuarios
# ──────────────────────────────────────────────

def load_users():
    """
    Carga el diccionario de usuarios desde users.json.

    - Si el archivo no existe, crea un usuario 'admin' con una contraseña
      temporal aleatoria, la muestra una sola vez por consola y guarda
      el hash en el archivo.
    - Si el archivo existe pero está corrupto (JSON inválido), lanza un
      ValueError con instrucciones claras.

    Retorna:
        dict: Diccionario con los usuarios y sus hashes de contraseña.
    """
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)

    except FileNotFoundError:
        # Primera ejecución: no existe archivo de usuarios todavía.
        # Se genera una contraseña segura en tiempo de ejecución.
        password_temporal = _generar_password_temporal()

        # Se hashea la contraseña con bcrypt antes de almacenarla
        hashed = bcrypt.hashpw(password_temporal.encode('utf-8'), bcrypt.gensalt())

        default_users = {
            "admin": {
                # Se guarda el hash, nunca la contraseña en texto plano
                "password_hash": hashed.decode('utf-8')
            }
        }

        # Se persiste el usuario admin en el archivo JSON
        with open(USERS_FILE, 'w') as f:
            json.dump(default_users, f, indent=4)

        # Se muestra la contraseña temporal una única vez; no se puede recuperar después
        print("=" * 50)
        print("Usuario 'admin' creado por primera vez.")
        print("Contrasena temporal: " + password_temporal)
        print("Guardela en un lugar seguro; no volvera a mostrarse.")
        print("=" * 50)

        return default_users

    except json.JSONDecodeError:
        # El archivo existe pero su contenido no es JSON válido
        raise ValueError(
            "El archivo users.json esta corrupto o mal formado. "
            "Revise su contenido o elimínelo para regenerarlo."
        )


# ──────────────────────────────────────────────
# Autenticación y tokens
# ──────────────────────────────────────────────

def authenticate_user(username, password):
    """
    Verifica las credenciales del usuario y, si son correctas,
    genera y retorna un token JWT firmado.

    Args:
        username (str): Nombre de usuario.
        password (str): Contraseña en texto plano a verificar.

    Retorna:
        str | None: Token JWT si las credenciales son válidas, None en caso contrario.
    """
    users = load_users()

    # Verifica que el usuario exista en el archivo
    if username not in users:
        return None

    # Obtiene el hash almacenado y lo convierte a bytes para bcrypt
    stored_hash = users[username]['password_hash'].encode('utf-8')

    # Compara la contraseña ingresada contra el hash almacenado
    if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
        ahora = datetime.now(timezone.utc)

        # Payload del token: identidad del usuario, expiración y fecha de emisión
        payload = {
            'sub': username,                                        # Subject: identifica al usuario
            'exp': ahora + timedelta(minutes=JWT_EXPIRATION_MINUTES),  # Expiración del token
            'iat': ahora                                            # Issued at: cuándo fue emitido
        }

        # Firma el token con la clave secreta y el algoritmo configurado
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return token

    # Contraseña incorrecta
    return None


def verify_token(token):
    """
    Decodifica y valida un token JWT.

    Verifica la firma y que el token no haya expirado.

    Args:
        token (str): Token JWT a verificar.

    Retorna:
        dict | None: Payload del token si es válido, None si expiró o es inválido.
    """
    try:
        # Decodifica el token verificando firma y expiración automáticamente
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload

    except jwt.ExpiredSignatureError:
        # El token fue válido pero ya superó su tiempo de expiración
        print("❌ Token expirado.")
        return None

    except jwt.InvalidTokenError:
        # El token está malformado, fue alterado o la firma no coincide
        print("❌ Token inválido.")
        return None