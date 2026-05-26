import os
import sqlite3
from datetime import datetime

# Detectar plataforma para NO romper la pantalla en Android
from kivy.utils import platform
if platform not in ('android', 'ios'):
    from kivy.config import Config
    Config.set('graphics', 'width', '420')
    Config.set('graphics', 'height', '780')

from kivymd.app import MDApp
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFillRoundFlatButton
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.card import MDCard
from kivy.uix.image import Image
from kivy.uix.spinner import Spinner

class ProFitTrackerApp(MDApp):
    def build(self):
        self.title = "PRO FIT - Premium Tracker"
        # Configurar paleta de colores Material Design (Oscuro + Turquesa Eléctrico)
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.primary_hue = "A700"
        
        # Inicializar Base de Datos
        self.init_database()
        
        # Contenedor Principal (Navegación Inferior Moderna)
        nav_bar = MDBottomNavigation(panel_color=(0.1, 0.1, 0.1, 1))
        
        # --- PESTAÑA 1: RUTINAS ---
        tab_rutinas = MDBottomNavigationItem(name='rutinas', text='Rutinas', icon='weight-lifter')
        tab_rutinas.add_widget(self.build_ui_rutinas())
        
        # --- PESTAÑA 2: DIETA ---
        tab_dieta = MDBottomNavigationItem(name='dieta', text='Dieta', icon='food-apple')
        tab_dieta.add_widget(self.build_ui_dieta())
        
        # --- PESTAÑA 3: PERFIL ---
        tab_perfil = MDBottomNavigationItem(name='perfil', text='Progreso', icon='account-circle')
        tab_perfil.add_widget(self.build_ui_perfil())
        
        nav_bar.add_widget(tab_rutinas)
        nav_bar.add_widget(tab_dieta)
        nav_bar.add_widget(tab_perfil)
        
        # Cargar datos iniciales
        self.cargar_perfil()
        
        return nav_bar

    def init_database(self):
        self.conn = sqlite3.connect("rutinas_gym.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS ejercicios (id INTEGER PRIMARY KEY AUTOINCREMENT, dia TEXT, nombre TEXT, series_reps TEXT, notas TEXT, foto_path TEXT)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS dieta (dia TEXT PRIMARY KEY, desayuno TEXT, almuerzo TEXT, cena TEXT, meriendas_suplementos TEXT)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS perfil (id INTEGER PRIMARY KEY DEFAULT 1, nombre TEXT, apellido TEXT, peso_inicial REAL, estatura REAL, foto_antes_path TEXT, foto_despues_path TEXT)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS historial_peso (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, peso REAL)")
        self.conn.commit()

    # ================= UI: RUTINAS =================
    def build_ui_rutinas(self):
        layout = BoxLayout(orientation='vertical', padding=15, spacing=12)
        
        # Cabecera
        layout.add_widget(MDLabel(text="ENTRENAMIENTO DIARIO", font_style="headline6", bold=True, theme_text_color="Primary", size_hint_y=None, height=30))
        
        # Spinner estilizado
        self.spin_dias = Spinner(text='Lunes', values=('Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'), size_hint_y=None, height=40, background_color=(0, 0.5, 0.5, 1), color=(1,1,1,1))
        self.spin_dias.bind(text=self.actualizar_ejercicios_lista)
        layout.add_widget(self.spin_dias)
        
        # Campos de Texto Material Design
        self.input_ej_nombre = MDTextField(hint_text="Nombre del Ejercicio", mode="round")
        self.input_ej_series = MDTextField(hint_text="Series y Repeticiones (Ej: 4x10)", mode="round")
        self.input_ej_notas = MDTextField(hint_text="Notas o Recordatorio técnico", mode="round", multiline=True)
        self.input_ej_foto = MDTextField(hint_text="Ruta de imagen/guía (Opcional)", mode="round")
        
        layout.add_widget(self.input_ej_nombre)
        layout.add_widget(self.input_ej_series)
        layout.add_widget(self.input_ej_notas)
        layout.add_widget(self.input_ej_foto)
        
        # Botón Guardar Redondeado
        btn_guardar = MDFillRoundFlatButton(text="AÑADIR A LA RUTINA", md_bg_color=self.theme_cls.primary_color, font_size="16sp", pos_hint={"center_x": 0.5}, size_hint_x=0.8)
        btn_guardar.bind(on_press=self.guardar_ejercicio)
        layout.add_widget(btn_guardar)
        
        # Tarjeta de visualización del último ejercicio
        card_info = MDCard(orientation='vertical', padding=12, radius=15, md_bg_color=(0.15, 0.15, 0.15, 1), size_hint_y=None, height=130)
        self.lbl_info_ejercicios = MDLabel(text="Selecciona un día para ver tus ejercicios.", theme_text_color="Secondary", font_style="body2")
        card_info.add_widget(self.lbl_info_ejercicios)
        layout.add_widget(card_info)
        
        self.img_ejercicio = Image(source='', size_hint_y=1)
        layout.add_widget(self.img_ejercicio)
        
        return layout

    # ================= UI: DIETA =================
    def build_ui_dieta(self):
        scroll = ScrollView()
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        
        layout.add_widget(MDLabel(text="PLAN DE ALIMENTACIÓN", font_style="headline6", bold=True, theme_text_color="Primary", size_hint_y=None, height=30))
        
        self.spin_dias_dieta = Spinner(text='Lunes', values=('Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'), size_hint_y=None, height=40, background_color=(0, 0.5, 0.5, 1), color=(1,1,1,1))
        self.spin_dias_dieta.bind(text=self.cargar_dieta_del_dia)
        layout.add_widget(self.spin_dias_dieta)
        
        self.txt_desayuno = MDTextField(hint_text="🍳 Desayuno", mode="rectangle", multiline=True)
        self.txt_almuerzo = MDTextField(hint_text="🍗 Almuerzo", mode="rectangle", multiline=True)
        self.txt_cena = MDTextField(hint_text="🐟 Cena", mode="rectangle", multiline=True)
        self.txt_meriendas = MDTextField(hint_text="🥤 Suplementos y Meriendas", mode="rectangle", multiline=True)
        
        layout.add_widget(self.txt_desayuno)
        layout.add_widget(self.txt_almuerzo)
        layout.add_widget(self.txt_cena)
        layout.add_widget(self.txt_meriendas)
        
        btn_diet = MDFillRoundFlatButton(text="GUARDAR MENÚ DIARIO", md_bg_color=self.theme_cls.primary_color, pos_hint={"center_x": 0.5}, size_hint_x=0.8)
        btn_diet.bind(on_press=self.guardar_dieta)
        layout.add_widget(btn_diet)
        
        scroll.add_widget(layout)
        return scroll

    # ================= UI: PERFIL Y FOTOS =================
    def build_ui_perfil(self):
        scroll = ScrollView()
        layout = BoxLayout(orientation='vertical', padding=15, spacing=12, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        
        layout.add_widget(MDLabel(text="MÉTRICAS Y EVOLUCIÓN", font_style="headline6", bold=True, theme_text_color="Primary", size_hint_y=None, height=30))
        
        # Campos de perfil
        self.input_perf_nombre = MDTextField(hint_text="Nombre", mode="round")
        self.input_perf_apellido = MDTextField(hint_text="Apellido", mode="round")
        self.input_perf_estatura = MDTextField(hint_text="Estatura (Metros. Ej: 1.75)", mode="round")
        self.input_perf_peso_i = MDTextField(hint_text="Peso Inicial (kg)", mode="round")
        
        layout.add_widget(self.input_perf_nombre)
        layout.add_widget(self.input_perf_apellido)
        layout.add_widget(self.input_perf_estatura)
        layout.add_widget(self.input_perf_peso_i)
        
        # Campos de rutas de fotos
        self.input_foto_antes = MDTextField(hint_text="Ruta Foto Inicial (Antes)", mode="round")
        self.input_foto_despues = MDTextField(hint_text="Ruta Foto Actual (Después)", mode="round")
        layout.add_widget(self.input_foto_antes)
        layout.add_widget(self.input_foto_despues)
        
        btn_u_perfil = MDRaisedButton(text="ACTUALIZAR DATOS", pos_hint={"center_x": 0.5})
        btn_u_perfil.bind(on_press=self.guardar_perfil)
        layout.add_widget(btn_u_perfil)
        
        # Tarjeta de visualización IMC
        card_imc = MDCard(orientation='vertical', padding=15, radius=15, md_bg_color=(0.11, 0.11, 0.11, 1), size_hint_y=None, height=100)
        self.lbl_imc_kivy = MDLabel(text="Ingresa datos para calcular el IMC estatus.", halign="center", font_style="body2")
        card_imc.add_widget(self.lbl_imc_kivy)
        layout.add_widget(card_imc)
        
        # Control de Peso Diario
        layout.add_widget(MDLabel(text="REGISTRO DE PESO DIARIO", font_style="subtitle1", bold=True, theme_text_color="Primary"))
        self.input_nuevo_peso = MDTextField(hint_text="Peso de hoy (kg)", mode="round")
        layout.add_widget(self.input_nuevo_peso)
        
        btn_add_peso = MDFillRoundFlatButton(text="AÑADIR PESO", md_bg_color=(0.1, 0.6, 0.3, 1), pos_hint={"center_x": 0.5})
        btn_add_peso.bind(on_press=self.registrar_nuevo_peso)
        layout.add_widget(btn_add_peso)
        
        # Historial de Pesos
        self.lbl_historial_pesos = MDLabel(text="Sin registros previos.", halign="center", theme_text_color="Secondary", font_style="caption")
        layout.add_widget(self.lbl_historial_pesos)
        
        # --- SECCIÓN PREMIUM ANTES Y DESPUÉS ---
        layout.add_widget(MDLabel(text="ESTADO DE CAMBIO VISUAL", font_style="subtitle1", bold=True, halign="center"))
        
        grid_fotos = GridLayout(cols=2, size_hint_y=None, height=180, spacing=10)
        
        card_antes = MDCard(radius=10, md_bg_color=(0.15,0.15,0.15,1))
        self.img_antes = Image(source='')
        card_antes.add_widget(self.img_antes)
        
        card_despues = MDCard(radius=10, md_bg_color=(0.15,0.15,0.15,1))
        self.img_despues = Image(source='')
        card_despues.add_widget(self.img_despues)
        
        grid_fotos.add_widget(card_antes)
        grid_fotos.add_widget(card_despues)
        layout.add_widget(grid_fotos)
        
        scroll.add_widget(layout)
        return scroll

    # ================= CONTROLADORES DE DATOS =================
    def guardar_ejercicio(self, instance):
        dia = self.spin_dias.text
        nombre = self.input_ej_nombre.text.strip()
        series = self.input_ej_series.text.strip()
        notas = self.input_ej_notas.text.strip()
        foto = self.input_ej_foto.text.strip()
        if not nombre: return
        self.cursor.execute("INSERT INTO ejercicios (dia, nombre, series_reps, notas, foto_path) VALUES (?, ?, ?, ?, ?)", (dia, nombre, series, notas, foto))
        self.conn.commit()
        self.input_ej_nombre.text = ""
        self.input_ej_series.text = ""
        self.input_ej_notas.text = ""
        self.input_ej_foto.text = ""
        self.actualizar_ejercicios_lista()

    def actualizar_ejercicios_lista(self, *args):
        dia = self.spin_dias.text
        self.cursor.execute("SELECT nombre, series_reps, notas, foto_path FROM ejercicios WHERE dia = ? ORDER BY id DESC LIMIT 1", (dia,))
        res = self.cursor.fetchone()
        if res:
            self.lbl_info_ejercicios.text = f"🔥 ÚLTIMO EJERCICIO:\n\n🏋️ {res[0]}\n🔢 Series/Reps: {res[1]}\n📝 Notas: {res[2]}"
            if res[3] and os.path.exists(res[3]): self.img_ejercicio.source = res[3]
            else: self.img_ejercicio.source = ''
        else:
            self.lbl_info_ejercicios.text = "No hay entrenamientos agendados hoy."
            self.img_ejercicio.source = ''

    def cargar_dieta_del_dia(self, *args):
        dia = self.spin_dias_dieta.text
        self.cursor.execute("SELECT desayuno, almuerzo, cena, meriendas_suplementos FROM dieta WHERE dia = ?", (dia,))
        res = self.cursor.fetchone()
        if res:
            self.txt_desayuno.text, self.txt_almuerzo.text, self.txt_cena.text, self.txt_meriendas.text = res[0], res[1], res[2], res[3]
        else:
            self.txt_desayuno.text = self.txt_almuerzo.text = self.txt_cena.text = self.txt_meriendas.text = ""

    def guardar_dieta(self, instance):
        dia = self.spin_dias_dieta.text
        self.cursor.execute("INSERT OR REPLACE INTO dieta (dia, desayuno, almuerzo, cena, meriendas_suplementos) VALUES (?, ?, ?, ?, ?)",
                            (dia, self.txt_desayuno.text, self.txt_almuerzo.text, self.txt_cena.text, self.txt_meriendas.text))
        self.conn.commit()

    def cargar_perfil(self):
        self.cursor.execute("SELECT nombre, apellido, peso_inicial, estatura, foto_antes_path, foto_despues_path FROM perfil WHERE id = 1")
        res = self.cursor.fetchone()
        if res:
            self.input_perf_nombre.text = res[0] if res[0] else ""
            self.input_perf_apellido.text = res[1] if res[1] else ""
            self.input_perf_estatura.text = str(res[3]) if res[3] else ""
            self.input_perf_peso_i.text = str(res[2]) if res[2] else ""
            self.input_foto_antes.text = res[4] if res[4] else ""
            self.input_foto_despues.text = res[5] if res[5] else ""
            self.calcular_imc()
            self.actualizar_historial_peso()

    def guardar_perfil(self, instance):
        try:
            estatura = float(self.input_perf_estatura.text) if self.input_perf_estatura.text else 0.0
            peso_i = float(self.input_perf_peso_i.text) if self.input_perf_peso_i.text else 0.0
        except ValueError: return
        self.cursor.execute("INSERT OR REPLACE INTO perfil (id, nombre, apellido, peso_inicial, estatura, foto_antes_path, foto_despues_path) VALUES (1, ?, ?, ?, ?, ?, ?)",
                            (self.input_perf_nombre.text, self.input_perf_apellido.text, peso_i, estatura, self.input_foto_antes.text, self.input_foto_despues.text))
        self.conn.commit()
        self.calcular_imc()

    def registrar_nuevo_peso(self, instance):
        try: peso = float(self.input_nuevo_peso.text)
        except ValueError: return
        fecha = datetime.now().strftime("%d/%m %H:%M")
        self.cursor.execute("INSERT INTO historial_peso (fecha, peso) VALUES (?, ?)", (fecha, peso))
        self.conn.commit()
        self.input_nuevo_peso.text = ""
        self.actualizar_historial_peso()
        self.calcular_imc()

    def actualizar_historial_peso(self):
        self.cursor.execute("SELECT fecha, peso FROM historial_peso ORDER BY id DESC LIMIT 3")
        res = self.cursor.fetchall()
        if res:
            self.lbl_historial_pesos.text = "📊 CRONOLOGÍA DE PESOS:\n" + "  |  ".join([f"{r[0]} -> {r[1]}kg" for r in res])

    def calcular_imc(self):
        try:
            estatura = float(self.input_perf_estatura.text)
            self.cursor.execute("SELECT peso FROM historial_peso ORDER BY id DESC LIMIT 1")
            ultimo = self.cursor.fetchone()
            peso = ultimo[0] if ultimo else float(self.input_perf_peso_i.text)
            if estatura > 0 and peso > 0:
                imc = peso / (estatura ** 2)
                est = "Saludable 🦾" if imc < 25 else "Sobrepeso ⚠️"
                if imc < 18.5: est = "Bajo Peso 🥦"
                self.lbl_imc_kivy.text = f"PESO ACTUAL: {peso} kg   |   IMC: {imc:.2f}\nESTADO: {est}"
                if os.path.exists(self.input_foto_antes.text): self.img_antes.source = self.input_foto_antes.text
                if os.path.exists(self.input_foto_despues.text): self.img_despues.source = self.input_foto_despues.text
        except: pass

    def on_stop(self):
        self.conn.close()

if __name__ == '__main__':
    ProFitTrackerApp().run()
