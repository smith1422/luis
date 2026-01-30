import os
os.system("pg_restore --no-owner --dbname=$DATABASE_URL migraciones/sistema_administrativo.backup")
