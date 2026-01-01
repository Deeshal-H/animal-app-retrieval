FROM python:3.14.2-slim
WORKDIR /app
COPY --exclude=./job_worker / .
RUN pip install -r requirements.txt
EXPOSE 5000
ENV FLASK_APP=app.py
ENTRYPOINT [ "flask", "run", "-h", "0.0.0.0" ]