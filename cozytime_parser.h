#pragma once

#include "esphome/core/component.h"
#include "esphome/components/esp32_ble_tracker/esp32_ble_tracker.h"
#include <esp_gap_ble_api.h>

namespace esphome {

class CozytimeParser : public Component, public esp32_ble_tracker::ESPBTDeviceListener {
 public:
  void setup() override {
    ESP_LOGI("cozytime_parser", "CozyTime BLE Parser initialized");
    esp32_ble_tracker::global_esp32_ble_tracker->register_listener(this);
  }

  void dump_config() override {
    ESP_LOGCONFIG("cozytime_parser", "CozyTime BLE Temperature/Humidity Sensor Parser");
  }

  // Вызывается при каждом BLE объявлении
  bool parse_device(const esp32_ble_tracker::ESPBTDevice &device) override {
    // Ищем manufacturer data с нашим ID (0x51C9)
    for (auto &mfg_data : device.get_manufacturer_datas()) {
      if (mfg_data.uuid == esp32_ble_tracker::ESPBTUUID::from_uint16(0x51C9)) {
        // Нашли CozyTime!
        return parse_cozytime_data(mfg_data.data, device.get_rssi());
      }
    }
    return false;
  }

  // Публичные методы для доступа к последним значениям
  float get_temperature() const { return this->temperature_; }
  float get_humidity() const { return this->humidity_; }
  int8_t get_rssi() const { return this->rssi_; }
  bool has_valid_data() const { return this->valid_data_; }

 private:
  float temperature_ = NAN;
  float humidity_ = NAN;
  int8_t rssi_ = 0;
  bool valid_data_ = false;

  // Парсер протокола CozyTime
  bool parse_cozytime_data(const std::vector<uint8_t> &data, int8_t rssi) {
    // Ожидаем как минимум 12 байт:
    // [0-1]: manufacturer ID (0xC9 0x51 в little endian)
    // [2-5]: device prefix (CECD6CCE)
    // [6-15]: variable data (10 байт)

    if (data.size() < 16) {
      ESP_LOGV("cozytime_parser", "Data too short: %d bytes", data.size());
      return false;
    }

    // Проверяем manufacturer ID
    uint16_t mfg_id = data[0] | (data[1] << 8);
    if (mfg_id != 0x51C9) {
      ESP_LOGV("cozytime_parser", "Wrong manufacturer ID: 0x%04X", mfg_id);
      return false;
    }

    // Проверяем фиксированный префикс (CECD6CCE)
    const uint8_t expected_prefix[] = {0xCE, 0xCD, 0x6C, 0xCE};
    if (memcmp(&data[2], expected_prefix, 4) != 0) {
      ESP_LOGV("cozytime_parser", "Wrong device prefix");
      return false;
    }

    // Переменные данные начинаются с индекса 6
    // Структура (от индекса 6):
    // [0]: reserved
    // [1]: packet counter (шум)
    // [2]: fixed (0x02)
    // [3]: temperature byte
    // [4]: humidity byte
    // [5]: fixed (0x00)
    // [6-9]: unknown/checksum

    if (data.size() < 16) {
      ESP_LOGV("cozytime_parser", "Insufficient variable data");
      return false;
    }

    uint8_t temp_byte = data[6 + 3];  // byte[3] переменной части
    uint8_t humid_byte = data[6 + 4]; // byte[4] переменной части

    // Вычисляем значения по найденной формуле
    float temperature = (temp_byte + 42) / 10.0f;
    float humidity = humid_byte - 6;

    // Логируем для отладки
    ESP_LOGD("cozytime_parser",
             "CozyTime: T_byte=0x%02X (dec %d), H_byte=0x%02X (dec %d) → "
             "T=%.1f°C, H=%.0f%%, RSSI=%d dBm",
             temp_byte, temp_byte, humid_byte, humid_byte,
             temperature, humidity, rssi);

    // Сохраняем значения
    this->temperature_ = temperature;
    this->humidity_ = humidity;
    this->rssi_ = rssi;
    this->valid_data_ = true;

    return true;
  }
};

}  // namespace esphome
