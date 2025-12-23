FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

ENV FLASK_APP=app.main
ENV ADMIN_PASSWORD=fancypassword123

EXPOSE 5000

CMD ["python", "-c", "from app.main import socketio, app; socketio.run(app, host='0.0.0.0', port=5000, debug=True)"]
