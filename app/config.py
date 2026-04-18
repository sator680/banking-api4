import os


class Config:
    SECRET_KEY = "banking-secret-2024"

    # En local : utilise l'URL Neon directement
    # Sur Render : utilise la variable d'environnement DATABASE_URL
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql://neondb_owner:npg_B7rUypwQ9MxW@ep-dry-shape-alafmt6l-pooler.c-3.eu-central-1.aws.neon.tech/neondb?sslmode=require"
    ).replace("postgres://", "postgresql://")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }
