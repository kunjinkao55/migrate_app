#!/usr/bin/env bash
cd backend
#source venv/bin/activate
#flask init-db            # 只第一次
flask run &              # 后台
flask python -m flask run --host=0.0.0.0 --port=5000 &
#celery -A backend.tasks.celery_app worker --loglevel=info --pool=solo &
cd ../frontend
npm run dev &
#node tus-server.js &