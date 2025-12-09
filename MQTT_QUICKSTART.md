# CozyTime Bridge - Quick MQTT Reference

## ✅ Изменения внесены

### 1. Обновленные файлы:
- ✅ `secrets.yaml` - добавлены MQTT креденшалы
- ✅ `cozytime_bridge.yaml` - добавлена MQTT интеграция
- ✅ `.gitignore` - обновлен для безопасности

### 2. Новые файлы:
- ✅ `secrets.yaml.example` - шаблон для других разработчиков
- ✅ `MQTT_SETUP.md` - полная документация по MQTT

## 🚀 Быстрый старт

### Прошивка ESP32:
```bash
# OTA (через WiFi)
esphome run cozytime_bridge.yaml

# USB (первая прошивка)
esphome run cozytime_bridge.yaml --device /dev/cu.usbserial-XXXXX
```

### Проверка работы MQTT:
```bash
# Подписка на все топики (используйте данные из secrets.yaml)
mosquitto_sub -h BROKER_IP -p 1883 -u YOUR_USERNAME -P "YOUR_PASSWORD" -t "cozytime_bridge/#" -v

# Статус ESP32
mosquitto_sub -h BROKER_IP -p 1883 -u YOUR_USERNAME -P "YOUR_PASSWORD" -t "cozytime_bridge/status"
```

## 📊 MQTT Топики

| Топик | Данные | Частота |
|-------|--------|---------|
| `cozytime_bridge/status` | `online`/`offline` | При подключении/отключении |
| `cozytime_bridge/temperature` | `79.8` (°F) | Каждые 5 сек |
| `cozytime_bridge/humidity` | `37` (%) | Каждые 5 сек |
| `cozytime_bridge/rssi` | `-65` (dBm) | Каждые 5 сек |
| `cozytime_bridge/battery` | `96` (%) | Каждые 5 сек |

## 🔐 Безопасность

Все секреты в `secrets.yaml` (защищен `.gitignore`):
- MQTT broker IP
- MQTT порт
- MQTT username
- MQTT password
- API encryption key

## 📚 Документация

- `README.md` - основная документация проекта
- `MQTT_SETUP.md` - детальная настройка MQTT
- `PROTOCOL_ANALYSIS.md` - анализ BLE протокола

---
**Версия:** 2.1 (MQTT enabled)
**Дата:** 9 декабря 2025
