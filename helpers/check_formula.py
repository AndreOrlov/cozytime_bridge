#!/usr/bin/env python3
"""
Проверка формулы калибровки температуры CozyTime на новых данных
"""

import csv
import math

# Текущая формула
CURRENT_SLOPE = 0.180123
CURRENT_INTERCEPT = -40.11

def parse_hex_packet(hex_str):
    """Извлекает temp_value из hex строки пакета"""
    if not hex_str or hex_str == 'unavailable':
        return None

    bytes_list = hex_str.strip().split()
    if len(bytes_list) < 7:
        return None

    try:
        byte5 = int(bytes_list[5], 16)
        byte6 = int(bytes_list[6], 16)
        temp_value = (byte6 << 8) | byte5  # Big-endian
        return temp_value
    except (ValueError, IndexError):
        return None

def current_formula(temp_value):
    """Текущая формула T(°F) = 0.180123 × temp_value - 40.11"""
    return CURRENT_SLOPE * temp_value + CURRENT_INTERCEPT

def linear_regression(X, y):
    """Простая линейная регрессия без numpy"""
    n = len(X)
    sum_x = sum(X)
    sum_y = sum(y)
    sum_xx = sum(x*x for x in X)
    sum_xy = sum(X[i]*y[i] for i in range(n))

    # slope = (n*sum_xy - sum_x*sum_y) / (n*sum_xx - sum_x*sum_x)
    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x)
    intercept = (sum_y - slope * sum_x) / n

    # R²
    y_mean = sum_y / n
    ss_tot = sum((y[i] - y_mean)**2 for i in range(n))
    ss_res = sum((y[i] - (slope * X[i] + intercept))**2 for i in range(n))
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

    return slope, intercept, r_squared

# Загружаем данные из data.csv
print("=" * 70)
print("ПРОВЕРКА КАЛИБРОВКИ НА ДАННЫХ ИЗ data.csv")
print("=" * 70)

data_points = []
with open('data.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if not row.get('Row data', '').strip():
            continue
        temp_value = parse_hex_packet(row['Row data'])
        if temp_value is not None and row.get('T F from app'):
            app_temp = float(row['T F from app'])
            place = row.get('Place', '').strip()
            data_points.append((temp_value, app_temp, place))

print(f"\nНайдено {len(data_points)} калибровочных точек:\n")
print(f"{'temp_value':>11} | {'App Temp':>8} | {'Predicted':>8} | {'Error':>7} | Location")
print("-" * 70)

errors = []
X_data = []
y_data = []

for temp_value, app_temp, place in sorted(data_points):
    predicted = current_formula(temp_value)
    error = predicted - app_temp
    errors.append(error)
    X_data.append(temp_value)
    y_data.append(app_temp)
    print(f"{temp_value:11d} | {app_temp:8.1f} | {predicted:8.2f} | {error:+7.2f} | {place}")

# Статистика ошибок
mean_error = sum(errors) / len(errors)
max_error = max(abs(e) for e in errors)
std_dev = math.sqrt(sum((e - mean_error)**2 for e in errors) / len(errors))
rms_error = math.sqrt(sum(e**2 for e in errors) / len(errors))

print("\n" + "=" * 70)
print("СТАТИСТИКА ОШИБОК (°F):")
print(f"  Mean Error:  {mean_error:+7.3f}°F")
print(f"  Max Error:   {max_error:7.3f}°F")
print(f"  Std Dev:     {std_dev:7.3f}°F")
print(f"  RMS Error:   {rms_error:7.3f}°F")

# Пересчитываем формулу с новыми данными
print("\n" + "=" * 70)
print("ПЕРЕРАСЧЕТ ФОРМУЛЫ С НОВЫМИ ДАННЫМИ")
print("=" * 70)

new_slope, new_intercept, r_squared = linear_regression(X_data, y_data)

print(f"\nТекущая формула: T(°F) = {CURRENT_SLOPE:.6f} × temp_value + {CURRENT_INTERCEPT:.2f}")
print(f"Новая формула:   T(°F) = {new_slope:.6f} × temp_value + {new_intercept:.2f}")
print(f"R² = {r_squared:.6f}")

# Проверяем новую формулу
print("\n" + "=" * 70)
print("ПРОВЕРКА НОВОЙ ФОРМУЛЫ:")
print("=" * 70)
print(f"{'temp_value':>11} | {'App Temp':>8} | {'New Pred':>8} | {'Error':>7}")
print("-" * 70)

new_errors = []
for temp_value, app_temp, place in sorted(data_points):
    new_predicted = new_slope * temp_value + new_intercept
    new_error = new_predicted - app_temp
    new_errors.append(new_error)
    print(f"{temp_value:11d} | {app_temp:8.1f} | {new_predicted:8.2f} | {new_error:+7.2f}")

new_mean_error = sum(new_errors) / len(new_errors)
new_max_error = max(abs(e) for e in new_errors)
new_std_dev = math.sqrt(sum((e - new_mean_error)**2 for e in new_errors) / len(new_errors))
new_rms_error = math.sqrt(sum(e**2 for e in new_errors) / len(new_errors))

print("\nНОВАЯ СТАТИСТИКА ОШИБОК (°F):")
print(f"  Mean Error:  {new_mean_error:+7.3f}°F")
print(f"  Max Error:   {new_max_error:7.3f}°F")
print(f"  Std Dev:     {new_std_dev:7.3f}°F")
print(f"  RMS Error:   {new_rms_error:7.3f}°F")

# Сравнение изменений
print("\n" + "=" * 70)
if new_rms_error < rms_error:
    improvement = rms_error - new_rms_error
    print(f"✓ УЛУЧШЕНИЕ: RMS ошибка уменьшилась на {improvement:.3f}°F")
    print(f"✓ РЕКОМЕНДУЕТСЯ обновить формулу")
    print(f"\nОбновите в cozytime_bridge.yaml:")
    print(f"  float temperature = {new_slope:.6f} * temp_value + {new_intercept:.2f};")
else:
    print(f"✗ Текущая формула работает лучше или одинаково")

print("=" * 70)

# Проверяем диапазон температур
print("\nДИАПАЗОН ТЕМПЕРАТУР:")
min_temp = min(y_data)
max_temp = max(y_data)
print(f"  Минимум: {min_temp:.1f}°F ({(min_temp - 32) * 5/9:.1f}°C)")
print(f"  Максимум: {max_temp:.1f}°F ({(max_temp - 32) * 5/9:.1f}°C)")
print(f"  Диапазон: {max_temp - min_temp:.1f}°F ({(max_temp - min_temp) * 5/9:.1f}°C)")
print("=" * 70)
