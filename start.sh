#!/bin/bash

# 初始化数据库
python3 -c "
from app import app, db
with app.app_context():
    db.create_all()
"

# 启动Flask应用
flask run --host=0.0.0.0