# Production Deployment Guide

Ръководство за deploy на мониторинг системата на production сървър.

## Конфигурация за Production Домейн

### 1. Създай `.env` файл

```bash
cp .env.example .env
```

### 2. Редактирай `.env` файла

За домейн `smokeping.fiber.bg`:

```env
# Grafana Admin Credentials - ПРОМЕНИ ПАРОЛАТА!
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=YourSecurePassword123!

# Grafana Root URL - използвай твоя домейн
GRAFANA_ROOT_URL=http://smokeping.fiber.bg

# Server Domain - използвай твоя домейн
SERVER_DOMAIN=smokeping.fiber.bg
```

### 3. Restart Services

```bash
docker-compose down
docker-compose up -d
```

## HTTPS Setup (Препоръчително за Production)

За да добавиш HTTPS с Let's Encrypt:

### Вариант 1: Използвай Traefik (препоръчително)

1. Добави Traefik labels в `docker-compose.yml`
2. Конфигурирай Let's Encrypt автоматично

### Вариант 2: Използвай Nginx с Certbot

1. Инсталирай certbot на хоста:
```bash
apt install certbot python3-certbot-nginx
```

2. Получи SSL сертификат:
```bash
certbot certonly --standalone -d smokeping.fiber.bg
```

3. Обнови `config/nginx/nginx.conf.template`:
```nginx
server {
    listen 443 ssl http2;
    server_name ${SERVER_DOMAIN};

    ssl_certificate /etc/letsencrypt/live/smokeping.fiber.bg/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/smokeping.fiber.bg/privkey.pem;

    # Останалата конфигурация...
}

server {
    listen 80;
    server_name ${SERVER_DOMAIN};
    return 301 https://$server_name$request_uri;
}
```

4. Mount SSL сертификатите в docker-compose.yml:
```yaml
  nginx:
    volumes:
      - /etc/letsencrypt:/etc/letsencrypt:ro
```

5. Обнови `.env`:
```env
GRAFANA_ROOT_URL=https://smokeping.fiber.bg
```

## Firewall Configuration

Отвори необходимите портове:

```bash
# HTTP
ufw allow 80/tcp

# HTTPS (ако използваш SSL)
ufw allow 443/tcp

# За debugging (опционално, може да се затвори след setup)
ufw allow 9090/tcp  # Prometheus
ufw allow 3000/tcp  # Grafana direct access
```

## DNS Configuration

Добави A record за домейна:

```
smokeping.fiber.bg    A    YOUR_SERVER_IP
```

## Проверка на Deployment

1. Провери дали всички контейнери работят:
```bash
docker-compose ps
```

2. Тествай достъп:
```bash
curl http://smokeping.fiber.bg
curl http://smokeping.fiber.bg/host-api/api/health
```

3. Отвори браузър:
```
http://smokeping.fiber.bg
http://smokeping.fiber.bg/host-api/
```

## Security Best Practices

1. **Промени default паролата** за Grafana admin
2. **Използвай HTTPS** в production
3. **Ограничи достъпа** до Prometheus (порт 9090) само от localhost
4. **Настрой firewall** правила
5. **Backup данните** редовно (`prometheus-data`, `grafana-data`)
6. **Следи логовете**:
```bash
docker-compose logs -f
```

## Backup & Restore

### Backup

```bash
# Backup Prometheus data
docker run --rm -v grafana-pinger_prometheus-data:/data -v $(pwd):/backup alpine tar czf /backup/prometheus-backup.tar.gz -C /data .

# Backup Grafana data
docker run --rm -v grafana-pinger_grafana-data:/data -v $(pwd):/backup alpine tar czf /backup/grafana-backup.tar.gz -C /data .

# Backup hosts configuration
cp -r config/ config-backup/
```

### Restore

```bash
# Restore Prometheus data
docker run --rm -v grafana-pinger_prometheus-data:/data -v $(pwd):/backup alpine tar xzf /backup/prometheus-backup.tar.gz -C /data

# Restore Grafana data
docker run --rm -v grafana-pinger_grafana-data:/data -v $(pwd):/backup alpine tar xzf /backup/grafana-backup.tar.gz -C /data
```

## Troubleshooting

### Nginx не се свързва с правилния домейн

Провери дали `SERVER_DOMAIN` е правилно зададен в `.env`:
```bash
docker exec nginx-proxy cat /etc/nginx/nginx.conf | grep server_name
```

### Grafana не се зарежда правилно

Провери `GF_SERVER_ROOT_URL`:
```bash
docker exec grafana env | grep GF_SERVER_ROOT_URL
```

### Host API не работи

Провери логовете:
```bash
docker-compose logs host-api
```
