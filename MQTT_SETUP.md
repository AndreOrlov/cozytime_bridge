# MQTT Configuration for CozyTime Bridge

## 🔧 Настройка завершена

В проект добавлена интеграция с MQTT брокером Mosquitto.

### 📡 MQTT Broker
- **Host:** хранится в `secrets.yaml`
- **Port:** хранится в `secrets.yaml`
- **Username:** хранится в `secrets.yaml`
- **Password:** хранится в `secrets.yaml`

### 🔐 Безопасность
Все креденшалы хранятся в файле `secrets.yaml`, который исключен из Git через `.gitignore`.

### 📊 MQTT Топики

После прошивки доступны следующие топики:

| Топик | Данные | Описание |
|-------|--------|----------|
| `cozytime_bridge/status` | `online` / `offline` | Статус ESP32 (LWT) |
| `cozytime_bridge/temperature` | `79.8` | Температура в °F |
| `cozytime_bridge/humidity` | `37` | Влажность в % |
| `cozytime_bridge/rssi` | `-65` | Уровень BLE сигнала (dBm) |
| `cozytime_bridge/battery` | `96` | Заряд батареи в % |

### 🏠 Home Assistant Discovery

Включено автоматическое обнаружение (MQTT Discovery):
- **Discovery prefix:** `homeassistant`
- Устройство автоматически появится в Home Assistant после прошивки

### 🧪 Тестирование подключения

#### Подписка на все топики CozyTime:
```bash
mosquitto_sub -h BROKER_IP -p 1883 -u YOUR_USERNAME -P "YOUR_PASSWORD" -t "cozytime_bridge/#" -v
```

#### Проверка статуса ESP32:
```bash
mosquitto_sub -h BROKER_IP -p 1883 -u YOUR_USERNAME -P "YOUR_PASSWORD" -t "cozytime_bridge/status"
```

#### Мониторинг температуры:
```bash
mosquitto_sub -h BROKER_IP -p 1883 -u YOUR_USERNAME -P "YOUR_PASSWORD" -t "cozytime_bridge/temperature"
```

> **Примечание:** Замените `BROKER_IP`, `YOUR_USERNAME` и `YOUR_PASSWORD` на реальные значения из `secrets.yaml`

### 🚀 Прошивка

#### OTA (через WiFi):
```bash
esphome run cozytime_bridge.yaml
```

#### USB (первая прошивка):
```bash
esphome run cozytime_bridge.yaml --device /dev/cu.usbserial-XXXXX
```

### 📝 Логи

Просмотр логов в реальном времени:
```bash
esphome logs cozytime_bridge.yaml
```

Вы должны увидеть:
```
[INFO] MQTT Connected!
```

### 🔄 Что изменилось

1. **secrets.yaml** - добавлены MQTT креденшалы
2. **cozytime_bridge.yaml** - добавлена MQTT конфигурация:
   - Подключение к брокеру
   - Birth/Will messages (LWT)
   - Публикация данных сенсоров
3. **secrets.yaml.example** - шаблон для других разработчиков
4. **.gitignore** - обновлен для исключения артефактов сборки

### ⚡ Особенности

- Данные публикуются каждые **5 секунд** (синхронно с обновлением сенсоров)
- При отключении ESP32 брокер автоматически установит статус `offline` (Last Will Testament)
- При подключении публикуется статус `online` (Birth Message)
- Все операции логируются для отладки

### 🛠️ Troubleshooting

#### MQTT не подключается
1. Проверьте доступность брокера:
   ```bash
   ping BROKER_IP
   ```
2. Проверьте креденшалы в `secrets.yaml`
3. Просмотрите логи ESP32:
   ```bash
   esphome logs cozytime_bridge.yaml
   ```

#### Данные не публикуются
1. Убедитесь, что ESP32 подключен к WiFi
2. Проверьте, что CozyTime датчик в радиусе действия BLE
3. Включите DEBUG логирование временно:
   ```yaml
   logger:
     level: DEBUG
   ```

### 📚 Дополнительные ресурсы

- [ESPHome MQTT Component](https://esphome.io/components/mqtt.html)
- [Home Assistant MQTT Discovery](https://www.home-assistant.io/integrations/mqtt/)
- [Mosquitto Documentation](https://mosquitto.org/documentation/)

---

**Дата обновления:** 9 декабря 2025
**Версия:** 2.1 (добавлен MQTT)
