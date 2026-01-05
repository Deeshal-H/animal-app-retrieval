FROM python:3.14.2-alpine
WORKDIR /job_worker
COPY ./job_worker .
COPY ./service ./service
COPY ./helpers ./helpers
COPY config.yaml .
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "-m", "main"]