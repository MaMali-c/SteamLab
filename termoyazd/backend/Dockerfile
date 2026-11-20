FROM python:3.14-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 \
    TERMOYAZD_ENV=production OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
WORKDIR /app
COPY backend/requirements-production.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN groupadd --system termoyazd && useradd --system --gid termoyazd termoyazd
COPY --chown=termoyazd:termoyazd backend/app ./app
COPY --chown=termoyazd:termoyazd backend/start-production.sh ./start-production.sh
USER termoyazd
EXPOSE 8000
CMD ["sh", "./start-production.sh"]
