[app]

# (str) Title of your application
title = Pro Fit Tracker

# (str) Package name
package.name = profittracker

# (str) Package domain (needed for android packaging)
package.domain = org.antonio

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,jpeg,kv,atlas,db

# (str) Application versioning
version = 1.0.0

# (str) Icon of the application (Asegúrate de tener logo_gym.png en tu carpeta)
icon.filename = %(source.dir)s/logo_gym.png

# (str) Supported orientations (landscape, portrait or all)
orientation = portrait

# ============================================
# DEPENDENCIAS Y LIBRERÍAS REVISADAS (CORREGIDO)
# ============================================
# Se removió 'sqlite3' de los requerimientos ya que Android lo incluye de forma nativa.
requirements = python3, hostpython3, kivy==2.3.0, kivymd==1.2.0, pillow

# (list) Permissions for saving and reading progress photos
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, INTERNET

# (int) Target Android API
android.api = 33

# (int) Minimum API your APK will support
android.minapi = 21

# (str) Android NDK version to use (Estable para Kivy 2.3.0)
android.ndk = 25b

# (str) Bootstrap to use for android build
android.bootstrap = sdl2

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
