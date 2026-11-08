FROM python:3.14-slim
WORKDIR /api
COPY api/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY api ./
EXPOSE 5000
RUN useradd api
USER api
CMD ["gunicorn", "api:app", "--bind", "0.0.0.0:5000"]
