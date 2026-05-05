import bcrypt
from database import execute_query

nome = "Administrador"
email = "admin@mbusinessvision.com.br"
senha = "Milton#BI_2026"

senha_hash = bcrypt.hashpw(
    senha.encode("utf-8"),
    bcrypt.gensalt()
).decode("utf-8")

execute_query(
    """
    INSERT INTO usuarios (nome, email, senha_hash, perfil, ativo)
    VALUES (:nome, :email, :senha_hash, 'admin', TRUE)
    ON CONFLICT (email) DO UPDATE
    SET senha_hash = EXCLUDED.senha_hash,
        ativo = TRUE
    """,
    {
        "nome": nome,
        "email": email,
        "senha_hash": senha_hash,
    }
)

print("Usuário criado com sucesso.")
print("Email:", email)
print("Senha:", senha)