import os
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from google import genai
from PIL import Image

try:
    from plyer import filechooser
except ImportError:
    filechooser = None

# Твой API-ключ Gemini
GEMINI_API_KEY = "AQ.Ab8RN6LxVi6erBAT5n-LkkPMa3HPGtsg-QFQHOcKVo7lzcxCfA"

class GeoSSekerApp(App):
    def build(self):
        self.title = "GeoSSeker OSINT"
        self.selected_file = ""

        root = BoxLayout(orientation='vertical', padding=15, spacing=12)
        
        # Заголовок
        title_lbl = Label(
            text="[b]GEOSSEKER OSINT VISION[/b]",
            markup=True,
            font_size=20,
            color=(1, 0.2, 0.2, 1),
            size_hint_y=None,
            height=40
        )
        root.add_widget(title_lbl)

        # Кнопка выбора файла
        self.btn_file = Button(
            text="📁 ВЫБРАТЬ ФОТО ИЗ ГАЛЕРЕИ",
            size_hint_y=None,
            height=55,
            background_color=(0.8, 0.1, 0.1, 1),
            color=(1, 1, 1, 1)
        )
        self.btn_file.bind(on_press=self.open_file_chooser)
        root.add_widget(self.btn_file)

        # Кнопка запуска
        self.btn_run = Button(
            text="⚡ ЗАПУСТИТЬ РАЗВЕДКУ",
            size_hint_y=None,
            height=55,
            background_color=(0.2, 0.2, 0.2, 1),
            color=(0.6, 0.6, 0.6, 1),
            disabled=True
        )
        self.btn_run.bind(on_press=self.start_analysis)
        root.add_widget(self.btn_run)

        # Поле для результатов
        scroll = ScrollView(size_hint=(1, 1))
        self.result_lbl = TextInput(
            text="[ Ожидание выбора изображения... ]\nВыберите фотографию, чтобы запустить нейросетевой анализ местности через Gemini Vision.",
            readonly=True,
            background_color=(0.06, 0.06, 0.06, 1),
            foreground_color=(0, 1, 0.8, 1),
            font_size=13,
            multiline=True
        )
        scroll.add_widget(self.result_lbl)
        root.add_widget(scroll)

        return root

    def open_file_chooser(self, instance):
        if filechooser:
            filechooser.open_file(on_selection=self.handle_selection, filters=[("Images", "*.png", "*.jpg", "*.jpeg", "*.webp")])
        else:
            self.result_lbl.text = "[!] Ошибка: plyer filechooser недоступен."

    def handle_selection(self, selection):
        if selection:
            self.selected_file = selection[0]
            filename = os.path.basename(self.selected_file)
            self.btn_file.text = f"📄 {filename}"
            self.btn_run.disabled = False
            self.btn_run.background_color = (1, 0.1, 0.1, 1)
            self.btn_run.color = (1, 1, 1, 1)
            self.result_lbl.text = f"Выбран файл:\n{self.selected_file}\n\nНажмите кнопку 'ЗАПУСТИТЬ РАЗВЕДКУ'."

    def start_analysis(self, instance):
        if not self.selected_file:
            return
        
        self.btn_run.disabled = True
        self.btn_run.text = "АНАЛИЗ..."
        self.result_lbl.text = "[!] Инициализация модуля GeoSSeker Vision...\nОтправка запроса к серверам Gemini..."

        threading.Thread(target=self.run_gemini_task).start()

    def run_gemini_task(self):
        try:
            ai_client = genai.Client(api_key=GEMINI_API_KEY)
            image_pil = Image.open(self.selected_file)

            prompt = (
                "Ты профессиональный OSINT-аналитик и географ. Проанализируй это фото: "
                "обрати внимание на архитектуру зданий, дорожное покрытие, растительность, знаки, язык на вывесках и особенности местности. "
                "Определи наиболее вероятное место съемки (город, улица или достопримечательность). "
                "ОТВЕТЬ СТРОГО В ТАКОМ ФОРМАТЕ:\n"
                "LOCATION: [Название места, город, страна]\n"
                "LAT: [Широта числом, например 50.4501]\n"
                "LON: [Долгота числом, например 30.5234]\n"
                "CONFIDENCE: [Процент уверенности, например 92%]\n"
                "REASON: [Подробное объяснение по деталям на фото]"
            )

            response = None
            for model_name in ['gemini-2.5-flash', 'gemini-1.5-flash', 'gemini-2.0-flash']:
                try:
                    response = ai_client.models.generate_content(
                        model=model_name,
                        contents=[image_pil, prompt]
                    )
                    break
                except Exception:
                    pass

            if not response:
                Clock.schedule_once(lambda dt: self.update_ui("[!] Серверы Google перегружены. Попробуйте еще раз."))
                return

            ai_text = response.text
            loc_name = "Не удалось определить"
            lat, lon = 50.4501, 30.5234
            confidence = "75%"

            for line in ai_text.split('\n'):
                if line.startswith("LOCATION:"):
                    loc_name = line.replace("LOCATION:", "").strip()
                elif line.startswith("LAT:"):
                    try: lat = float(line.replace("LAT:", "").strip())
                    except: pass
                elif line.startswith("LON:"):
                    try: lon = float(line.replace("LON:", "").strip())
                    except: pass
                elif line.startswith("CONFIDENCE:"):
                    confidence = line.replace("CONFIDENCE:", "").strip()

            output = (
                "=== РЕЗУЛЬТАТЫ РАЗВЕДКИ ===\n"
                f"📍 Локация: {loc_name}\n"
                f"🌐 Координаты: {lat}, {lon}\n"
                f"🎯 Уверенность: {confidence}\n\n"
                f"🔍 Анализ ИИ:\n{ai_text}\n\n"
                f"🗺️ Карты: https://www.google.com/maps/search/?api=1&query={lat},{lon}"
            )
            Clock.schedule_once(lambda dt: self.update_ui(output))

        except Exception as e:
            Clock.schedule_once(lambda dt: self.update_ui(f"[!] Ошибка: {e}"))

    def update_ui(self, text):
        self.result_lbl.text = text
        self.btn_run.disabled = False
        self.btn_run.text = "⚡ ЗАПУСТИТЬ РАЗВЕДКУ"

if __name__ == '__main__':
    GeoSSekerApp().run()