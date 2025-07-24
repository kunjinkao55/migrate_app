#!/usr/bin/env bash
cd backend
source venv/bin/activate
python -m flask init-db     # 只第一次运行
python -m flask run --host=0.0.0.0 --port=5000 &
cd ../frontend
npm run dev &