#!/usr/bin/env python3
"""
Детальный анализ timestamp с учетом секунд
"""

import csv
from datetime import datetime

def parse_packet(hex_str):
    """Парсит BLE пакет"""
    if not hex_str or hex_str == 'unavailable':
        return None

    bytes_list = hex_str.strip().split()
    if len(bytes_list) < 14:
        return None

    try:
        return {
            'temp_raw': (int(bytes_list[6], 16) << 8) | int(bytes_list[5], 16),
            'humidity': int(bytes_list[7], 16),
            'battery': int(bytes_list[8], 16),
            'ts_flag': int(bytes_list[9], 16),
            'ts_month': int(bytes_list[10], 16),
            'ts_day': int(bytes_list[11], 16),
            'ts_hour': int(bytes_list[12], 16),
            'ts_minute': int(bytes_list[13], 16),
            'raw': hex_str
        }
    except (ValueError, IndexError):
        return None

print("=" * 100)
print("ДЕТАЛЬНЫЙ АНАЛИЗ TIMESTAMP")
print("=" * 100)

# Читаем данные
data_points = []
with open('history (1).csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['state'] and row['state'] != 'unavailable':
            packet = parse_packet(row['state'])
            if packet and packet['ts_month'] > 0:  # Пропускаем невалидные (00 00 00:00)
                ha_time = datetime.fromisoformat(row['last_changed'].replace('Z', '+00:00'))
                data_points.append({
                    'ha_time': ha_time,
                    'packet': packet
                })

print(f"\nПервые 20 записей с анализом разницы:\n")
print(f"{'#':>3} | {'HA Time':>19} | {'BLE Time':>12} | {'Diff':>8} | Temp | Hum | Batt")
print("-" * 100)

prev_ble_min = None
ble_update_times = []

for i, dp in enumerate(data_points[:50], 1):
    ha_time = dp['ha_time']
    p = dp['packet']

    ble_month = p['ts_month']
    ble_day = p['ts_day']
    ble_hour = p['ts_hour']
    ble_min = p['ts_minute']

    # Проверяем, когда датчик обновил timestamp
    ble_time_tuple = (ble_month, ble_day, ble_hour, ble_min)
    if prev_ble_min is not None and ble_time_tuple != prev_ble_min:
        ble_update_times.append(ha_time)
    prev_ble_min = ble_time_tuple

    try:
        ble_datetime = datetime(2025, ble_month, ble_day, ble_hour, ble_min, tzinfo=ha_time.tzinfo)
        diff_sec = (ha_time - ble_datetime).total_seconds()
        diff_str = f"{diff_sec:+6.0f}s"
    except ValueError:
        diff_str = "invalid"

    temp = 0.179987 * p['temp_raw'] - 40.02

    ble_str = f"{ble_hour:02d}:{ble_min:02d}"
    ha_str = ha_time.strftime("%H:%M:%S")

    marker = "📍" if i > 1 and ble_time_tuple != prev_ble_min else "  "

    print(f"{i:3d} | {ha_str:>19} | {ble_str:>12} | {diff_str:>8} | {temp:4.1f} | {p['humidity']:3d} | {p['battery']:3d} {marker}")

# Анализ интервалов обновления BLE timestamp
if len(ble_update_times) > 1:
    print("\n" + "=" * 100)
    print("ИНТЕРВАЛЫ ОБНОВЛЕНИЯ BLE TIMESTAMP:")
    intervals = []
    for i in range(1, len(ble_update_times)):
        interval = (ble_update_times[i] - ble_update_times[i-1]).total_seconds()
        intervals.append(interval)
        if i <= 10:  # Показываем первые 10
            print(f"  Обновление {i}: через {interval:.0f} секунд")

    if intervals:
        avg_interval = sum(intervals) / len(intervals)
        print(f"\n  Средний интервал обновления: {avg_interval:.1f} секунд")
        print(f"  Минимум: {min(intervals):.0f}s, Максимум: {max(intervals):.0f}s")

print("\n" + "=" * 100)
print("ВЫВОДЫ:")
print("-" * 100)
print("  • Байт [9] = 0x01 (константа, возможно флаг)")
print("  • Байты [10-13] = [месяц][день][час][минута]")
print("  • BLE timestamp монотонно возрастает")
print("  • Разница HA - BLE ≈ 7 минут")
print("  • Возможно:")
print("    - Датчик обновляет timestamp раз в минуту")
print("    - Разница ~7 мин = задержка обновления датчика")
print("    - Или BLE timestamp = время ИЗМЕРЕНИЯ, HA timestamp = время ПОЛУЧЕНИЯ")
print("=" * 100)
