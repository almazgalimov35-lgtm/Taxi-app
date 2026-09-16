[app]
title = Taxi
package.name = taxiapp
package.domain = org.taxi

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0

# Оставляем версии, которые у вас уже работали
requirements = hostpython3==3.11.5,python3==3.11.5,kivy==2.3.0

orientation = portrait
fullscreen = 0

# --- ПРАВКИ ВАРИАНТА А ---
# Меняем develop на master (может быть стабильнее для Python 3.11)
p4a.branch = master

# NDK пока НЕ удаляем, как рекомендовано ранее
android.ndk = 25b

# --- ОСТАЛЬНЫЕ НАСТРОЙКИ ---
android.permissions = INTERNET
android.accept_sdk_license = True

# Оставляем одну архитектуру для ускорения и упрощения отладки
android.archs = arm64-v8a

android.api = 30
android.minapi = 21

# Уровень логов для отладки (обязательно для диагностики)
log_level = 2
