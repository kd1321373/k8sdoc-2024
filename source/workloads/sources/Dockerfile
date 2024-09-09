# Dockerfile(hostbotディレクトリと同じ場所に置く)

FROM python:slim
WORKDIR /app
RUN --mount=type=bind,source=./hostbot,target=/app pip install -r /app/requirements.txt
COPY hostbot/serve.py /app/
EXPOSE 80
CMD ["python", "/app/serve.py"]

