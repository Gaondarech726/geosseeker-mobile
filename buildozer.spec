[app]
title = GeoSSeker
package.name = geosseeker
package.domain = org.geosseeker
source.include_exts = py,png,jpg,kv,atlas
source.include_dir = 
version = 1.0
requirements = python3,kivy,pillow,plyer,google-genai,urllib3,certifi,idna,charset-normalizer,requests,pydantic,anyio,sniffio,h11,httpcore,httpx
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.sdk = 30
android.ndk = 25b
android.gradle_dependencies = 
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1