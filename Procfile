web: gunicorn app:app
worker: celery -A tasks.celery_app worker --loglevel=info --pool=solo