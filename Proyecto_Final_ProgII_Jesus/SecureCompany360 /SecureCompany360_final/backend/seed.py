"""
Script de inicialización: crea los roles base y un usuario Administrador
para poder empezar a probar el sistema.

Uso:
    cd backend
    python seed.py
"""
from app.database import SessionLocal, Base, engine
from app import models
from app.security.auth import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()

ROLES = ["Administrador", "RRHH", "Soporte", "Analista", "Usuario"]

for nombre in ROLES:
    if not db.query(models.Rol).filter(models.Rol.nombre == nombre).first():
        db.add(models.Rol(nombre=nombre))
db.commit()

if not db.query(models.Empleado).filter(models.Empleado.cedula == "8-000-0001").first():
    admin_emp = models.Empleado(
        nombre_completo="Administrador del Sistema",
        cedula="8-000-0001",
        cargo="Administrador TI",
        departamento="Tecnología",
    )
    db.add(admin_emp)
    db.commit()
    db.refresh(admin_emp)

    rol_admin = db.query(models.Rol).filter(models.Rol.nombre == "Administrador").first()
    admin_user = models.Usuario(
        empleado_id=admin_emp.id,
        username="admin",
        password_hash=hash_password("Admin2026!"),
        rol_id=rol_admin.id,
    )
    db.add(admin_user)
    db.commit()
    print("Usuario admin creado -> username: admin / password: Admin2026!")
else:
    print("El usuario admin ya existía, no se creó de nuevo.")

db.close()
print("Roles y datos base listos.")
