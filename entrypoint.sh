## Проверяем, существует ли БД
#if [ ! -f /app/data/app.db ]; then
#  echo 'Initializing database...'
#  alembic upgrade head
#fi

uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
