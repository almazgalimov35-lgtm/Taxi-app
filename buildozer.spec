[app]
title = Taxi
package.name = taxiapp
package.domain = org.taxi

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0

requirements = hostpython3==3.11.5,python3==3.11.5,kivy==2.3.0

orientation = portrait
fullscreen = 0

p4a.branch = master
android.ndk = 25b

android.permissions = INTERNET
android.accept_sdk_license = True

android.archs = arm64-v8a

android.api = 30
android.minapi = 21

log_level = 2
