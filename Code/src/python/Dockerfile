# ==============================================================================
# Dockerfile para Servicio Python (FastAPI / Uvicorn / ML Analytics)
# ==============================================================================

FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias para compilar paquetes C/C++ y herramientas
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de requerimientos primero para aprovechar la caché de Docker
COPY requirements.services.txt ./

# Instalar PyTorch versión CPU (liviana) y demás dependencias del servicio
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.services.txt

# Copiar el código fuente de la aplicación
COPY . ./

# Establecer PYTHONPATH apuntando al directorio raíz del código Python
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PORT=8000

EXPOSE 8000

# Punto de entrada: Iniciar el servicio analítico FastAPI con Uvicorn
CMD ["uvicorn", "domain.services.main:app", "--host", "0.0.0.0", "--port", "8000"]
