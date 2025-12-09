#!/usr/bin/env python3
"""
Анализ timestamp в BLE пакетах CozyTime
"""

import csv
from datetime import datetime

def parse_packet(hex_str):
    """Парсит BLE пакет и возвращает все компоненты"""
    if not hex_str or hex_str == 'unavailable':
        return None

    bytes_list = hex_str.strip().split()
    if len(bytes_list) < 14:
        return None

    try:
        return {
            'prefix': bytes_list[0:4],
            'byte4': int(bytes_list[4], 16),
            'temp_raw': (int(bytes_list[6], 16) << 8) | int(bytes_list[5], 16),
            'humidity': int(bytes_list[7], 16),
            'battery': int(bytes_list[8], 16),
            'ts_byte9': int(bytes_list[9], 16),
            'ts_month': int(bytes_list[10], 16),
            'ts_day': int(bytes_list[11], 16),
            'ts_hour': int(bytes_list[12], 16),
            'ts_minute': int(bytes_list[13], 16),
        }
    except (ValueError, IndexError):
        return None

print("=" * 100)
print("АНАЛИЗ TIMESTAMP В BLE ПАКЕТАХ COZYTIME")
print("=" * 100)

# Читаем history (1).csv
data_points = []
with open('history (1).csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['state'] and row['state'] != 'unavailable':
            packet = parse_packet(row['state'])
            if packet:
                ha_time = datetime.fromisoformat(row['last_changed'].replace('Z', '+00:00'))
                data_points.append({
                    'ha_time': ha_time,
                    'packet': packet,
                    'raw': row['state']
                })

print(f"\nНайдено {len(data_points)} валидных пакетов\n")

# Анализируем первые 20 записей
print(f"{'#':>3} | {'HA Timestamp':>19} | BLE Timestamp [10][11][12][13] | Diff")
print("-" * 100)

for i, dp in enumerate(data_points[:30], 1):
    ha_time = dp['ha_time']
    p = dp['packet']

    # Форматируем BLE timestamp как дату
    ble_month = p['ts_month']
    ble_day = p['ts_day']
    ble_hour = p['ts_hour']
    ble_min = p['ts_minute']

    # Вычисляем разницу во времени
    # Предполагаем что год 2025
    try:
        ble_datetime = datetime(2025, ble_month, ble_day, ble_hour, ble_min, tzinfo=ha_time.tzinfo)
        time_diff = (ha_time - ble_datetime).total_seconds()
        diff_str = f"{time_diff:+6.0f}s"
    except ValueError:
        ble_datetime = None
        diff_str = "invalid"

    ble_str = f"{ble_month:02d}-{ble_day:02d} {ble_hour:02d}:{ble_min:02d}"
    ha_str = ha_time.strftime("%m-%d %H:%M:%S")

    print(f"{i:3d} | {ha_str:>19} | {ble_str:>22} | {diff_str:>8}")

# Статистика по байту [9]
print("\n" + "=" * 100)
print("СТАТИСТИКА БАЙТА [9]:")
byte9_values = [dp['packet']['ts_byte9'] for dp in data_points]
unique_byte9 = set(byte9_values)
print(f"  Уникальные значения: {sorted(unique_byte9)}")
print(f"  Всего уникальных: {len(unique_byte9)}")
if len(unique_byte9) == 1:
    print(f"  ✓ Байт [9] всегда константа: 0x{list(unique_byte9)[0]:02X}")

# Проверяем монотонность timestamp
print("\n" + "=" * 100)
print("ПРОВЕРКА МОНОТОННОСТИ BLE TIMESTAMP:")
monotonic = True
prev_ts = None
for i, dp in enumerate(data_points[:100], 1):
    p = dp['packet']
    current_ts = (p['ts_month'], p['ts_day'], p['ts_hour'], p['ts_minute'])
    if prev_ts and current_ts < prev_ts:
        print(f"  ✗ Немонотонность на записи {i}: {prev_ts} -> {current_ts}")
        monotonic = False
    prev_ts = current_ts

if monotonic:
    print(f"  ✓ BLE timestamp монотонно возрастает во всех {min(100, len(data_points))} записях")

# Разница между BLE и HA timestamp
print("\n" + "=" * 100)
print("РАЗНИЦА МЕЖДУ BLE И HOME ASSISTANT TIMESTAMP:")
differences = []
for dp in data_points[:100]:
    p = dp['packet']
    ha_time = dp['ha_time']
    try:
        ble_datetime = datetime(2025, p['ts_month'], p['ts_day'], p['ts_hour'], p['ts_minute'],
                               tzinfo=ha_time.tzinfo)
        diff = (ha_time - ble_datetime).total_seconds()
        differences.append(diff)
    except ValueError:
        pass

if differences:
    avg_diff = sum(differences) / len(differences)
    min_diff = min(differences)
    max_diff = max(differences)
    print(f"  Средняя разница: {avg_diff:+7.1f} секунд")
    print(f"  Минимум:         {min_diff:+7.1f} секунд")
    print(f"  Максимум:        {max_diff:+7.1f} секунд")

    if abs(avg_diff) < 60:
        print(f"  ✓ Разница минимальна - BLE timestamp показывает время последнего измерения датчика")
    else:
        print(f"  ⚠ Значительная разница - возможно timezone offset")

print("=" * 100)
