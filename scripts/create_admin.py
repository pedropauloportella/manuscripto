import argparse
from app.db.session import SessionLocal
from app import models
from app.auth.utils import get_password_hash

def create_admin(email, password):
    db = SessionLocal()
    try:
        user = db.query(models.Usuario).filter(models.Usuario.email == email).first()
        if user:
            print(f"Erro: Usuário com email {email} já existe.")
            return

        admin_user = models.Usuario(
            email=email,
            hashed_password=get_password_hash(password),
            is_active=True,
            is_superuser=True,
            nome_completo="Administrador do Sistema"
        )
        db.add(admin_user)
        db.commit()
        print(f"Usuário administrador {email} criado com sucesso.")
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cria um usuário administrador inicial.")
    parser.add_argument("--email", required=True, help="Email do administrador")
    parser.add_argument("--password", required=True, help="Senha do administrador")
    args = parser.parse_args()
    create_admin(args.email, args.password)