# ==============================================================================
# Dockerfile para Servicio Frontend (Nginx Alpine / SPA ES Modules)
# ==============================================================================

FROM nginx:1.27-alpine

# Instalar curl para healthchecks del contenedor
RUN apk add --no-cache curl

# Copiar configuración personalizada de Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copiar archivos estáticos de la aplicación frontend
COPY index.html /usr/share/nginx/html/
COPY src/ /usr/share/nginx/html/src/

EXPOSE 80

# Healthcheck interno del contenedor
HEALTHCHECK --interval=10s --timeout=3s --retries=3 \
  CMD curl -f http://localhost/healthz || exit 1

CMD ["nginx", "-g", "daemon off;"]
