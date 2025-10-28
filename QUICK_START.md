# Quick Start Guide

## 🚀 5-минутен старт

### 1. Копирай .env файла
```bash
cp .env.example .env
```

### 2. Промени паролата (ЗАДЪЛЖИТЕЛНО!)
Редактирай `.env`:
```env
GRAFANA_ADMIN_PASSWORD=твоя-сигурна-парола
```

### 3. Стартирай
```bash
docker-compose up -d
```

### 4. Отвори Grafana
http://localhost:3000

- Username: `admin`
- Password: каквото си задал в `.env`

### 5. Добави хостове чрез UI
1. Отвори **Dashboards → Host Management**
2. Добави първия си хост:
   - Hostname/IP: `8.8.8.8`
   - Display Name: `Google DNS`
   - Group: `internet`
3. Кликни **Add Host**

### 6. Виж метриките
Отвори **Dashboards → Network Latency Monitoring**

## ✅ Gotovo!

Ще видиш:
- 📊 Real-time latency графики
- 📈 Jitter tracking
- 📉 Packet loss monitoring
- 📋 Host status table

## 🔧 Добавяне на повече хостове

### Чрез Web UI (Лесно!) ⭐

1. Grafana → **Dashboards → Host Management**
2. Попълни формата и кликни **Add Host**
3. Готово! Без restart!

### Чрез API

```bash
curl -X POST http://localhost:5000/api/hosts \
  -H "Content-Type: application/json" \
  -d '{"target": "192.168.1.1", "name": "My Router", "group": "network"}'
```

## 📱 Alert нотификации

Редактирай `config/alertmanager/alertmanager.yml` за:
- Slack
- Email
- Telegram
- Discord

Виж примери в файла!

## 🐛 Проблеми?

Виж [README.md](README.md#-troubleshooting) за troubleshooting.

## 📦 Backup

```bash
# Prometheus данни
docker run --rm -v grafana-pinger_prometheus-data:/data -v $(pwd):/backup alpine tar czf /backup/prometheus-backup.tar.gz /data

# Grafana данни
docker run --rm -v grafana-pinger_grafana-data:/data -v $(pwd):/backup alpine tar czf /backup/grafana-backup.tar.gz /data
```

---

**Пълна документация**: [README.md](README.md)
