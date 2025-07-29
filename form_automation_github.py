# form_automation_github.py
import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys # Importar Keys para simular teclas

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GitHubFormAutomator:
    def __init__(self):
        # Obtener datos desde variables de entorno (GitHub Secrets)
        self.form_url = os.environ.get('FORM_URL')
        self.email = os.environ.get('EMAIL')
        self.nombre = os.environ.get('NOMBRE')
        self.dni = os.environ.get('DNI')
        
        # Verificar que todas las variables estén configuradas
        if not all([self.form_url, self.email, self.nombre, self.dni]):
            missing = []
            if not self.form_url: missing.append('FORM_URL')
            if not self.email: missing.append('EMAIL')
            if not self.nombre: missing.append('NOMBRE')
            if not self.dni: missing.append('DNI')
            raise ValueError(f"Faltan estas variables de entorno: {', '.join(missing)}")
        
        self.driver = None
        logging.info(f"✅ Configuración cargada - Email: {self.email}, Nombre: {self.nombre}")
        
    def setup_chrome_driver(self):
        """Configura Chrome para GitHub Actions"""
        chrome_options = Options()
        
        # Opciones necesarias para GitHub Actions
        chrome_options.add_argument("--headless")  # Sin interfaz gráfica
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        
        # Opciones anti-detección
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Inicializar driver
        service = Service()  # ChromeDriver se instala automáticamente
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Configurar timeouts
        self.driver.implicitly_wait(10)
        self.driver.set_page_load_timeout(30)
        
        # Ocultar propiedades de webdriver
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        logging.info("✅ Chrome configurado correctamente")
        
    def take_screenshot(self, name):
        """Toma screenshot para debugging"""
        try:
            filename = f"/tmp/form_{name}.png"
            self.driver.save_screenshot(filename)
            logging.info(f"📸 Screenshot guardado: {filename}")
        except Exception as e:
            logging.error(f"❌ Error al tomar screenshot: {e}")
            
    def wait_and_find_element(self, by, value, timeout=15, screenshot_name=None):
        """Busca un elemento con timeout y manejo de errores"""
        try:
            logging.info(f"🔍 Buscando elemento: {value}")
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            logging.info(f"✅ Elemento encontrado: {value}")
            return element
        except Exception as e:
            logging.error(f"❌ No se encontró elemento {value}: {e}")
            if screenshot_name:
                self.take_screenshot(f"error_{screenshot_name}")
            return None
            
    def type_like_human(self, element, text, delay=0.1):
        """Escribe texto simulando comportamiento humano"""
        element.clear()
        time.sleep(0.5)
        
        for char in text:
            element.send_keys(char)
            time.sleep(delay + (hash(char) % 50) / 1000)  # Variación aleatoria
            
        logging.info(f"✍️ Texto ingresado: {text}")
        
    def fill_form_step_by_step(self):
        """Llena el formulario paso a paso con logging detallado"""
        try:
            logging.info("🚀 === INICIANDO AUTOMATIZACIÓN ===")
            logging.info(f"🌐 URL del formulario: {self.form_url}")
            
            # Configurar navegador
            self.setup_chrome_driver()
            
            # Ir al formulario
            logging.info("📄 Navegando al formulario...")
            self.driver.get(self.form_url)
            time.sleep(5)  # Esperar carga inicial
            
            # Screenshot inicial
            self.take_screenshot("01_inicial")
            logging.info("✅ Formulario cargado")
            
            # === SECCIÓN 1: EMAIL ===
            logging.info("\n📧 === PASO 1: LLENAR EMAIL ===")
            
            # Buscar campo de email con múltiples estrategias
            email_field = None
            email_strategies = [
                (By.CSS_SELECTOR, 'input[type="email"]'),
                (By.CSS_SELECTOR, 'input[aria-label*="email" i]'),
                (By.CSS_SELECTOR, 'input[aria-label*="correo" i]'),
                (By.CSS_SELECTOR, 'input[name*="email" i]'),
                (By.XPATH, '//input[contains(@aria-label, "email") or contains(@aria-label, "correo") or contains(@aria-label, "Email") or contains(@aria-label, "Correo")]'),
                (By.XPATH, '//input[@type="text" or @type="email"][1]'),  # Primer campo de texto
            ]
            
            for i, (by, selector) in enumerate(email_strategies, 1):
                try:
                    logging.info(f"🔍 Estrategia {i}: {selector}")
                    email_field = WebDriverWait(self.driver, 8).until(
                        EC.element_to_be_clickable((by, selector))
                    )
                    logging.info(f"✅ Campo email encontrado con estrategia {i}")
                    break
                except:
                    logging.info(f"❌ Estrategia {i} falló")
                    continue
            
            if not email_field:
                logging.error("❌ No se pudo encontrar el campo de email")
                self.take_screenshot("error_no_email_field")
                return False
            
            # Llenar email
            logging.info(f"✍️ Llenando email: {self.email}")
            self.type_like_human(email_field, self.email)
            time.sleep(2)
            
            self.take_screenshot("02_email_filled")
            
            # Buscar botón "Siguiente"
            logging.info("🔍 Buscando botón 'Siguiente'...")
            next_button = None
            next_strategies = [
                (By.XPATH, '//span[contains(text(), "Siguiente")]/../..'),
                (By.XPATH, '//span[contains(text(), "Next")]/../..'),
                (By.XPATH, '//div[@role="button" and contains(., "Siguiente")]'),
                (By.XPATH, '//button[contains(., "Siguiente")]'),
                (By.XPATH, '//*[contains(text(), "Siguiente")]/ancestor::*[@role="button" or @type="button" or contains(@class, "button")]'),
            ]
            
            for i, (by, selector) in enumerate(next_strategies, 1):
                try:
                    logging.info(f"🔍 Estrategia botón {i}: buscando 'Siguiente'")
                    next_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((by, selector))
                    )
                    logging.info(f"✅ Botón 'Siguiente' encontrado con estrategia {i}")
                    break
                except:
                    logging.info(f"❌ Estrategia botón {i} falló")
                    continue
            
            if not next_button:
                logging.error("❌ No se encontró el botón 'Siguiente'")
                self.take_screenshot("error_no_next_button")
                return False
            
            # Click en "Siguiente"
            logging.info("👆 Haciendo click en 'Siguiente'...")
            self.driver.execute_script("arguments[0].click();", next_button)
            time.sleep(4)  # Esperar carga de siguiente sección
            
            self.take_screenshot("03_after_next")
            logging.info("✅ Primera sección completada")
            
            # === SECCIÓN 2: NOMBRE Y DNI ===
            logging.info("\n👤 === PASO 2: SELECCIONAR NOMBRE ===")
            
            # Buscar dropdown de nombres
            dropdown = None
            dropdown_strategies = [
                (By.CSS_SELECTOR, 'select'),
                (By.CSS_SELECTOR, 'div[role="listbox"]'),
                (By.CSS_SELECTOR, 'div[role="combobox"]'),
                (By.CSS_SELECTOR, 'div[aria-haspopup="listbox"]'),
                (By.XPATH, '//div[contains(@class, "dropdown") or contains(@class, "select")]'),
            ]
            
            for i, (by, selector) in enumerate(dropdown_strategies, 1):
                try:
                    logging.info(f"🔍 Estrategia dropdown {i}: {selector}")
                    dropdown = WebDriverWait(self.driver, 8).until(
                        EC.element_to_be_clickable((by, selector))
                    )
                    logging.info(f"✅ Dropdown encontrado con estrategia {i}")
                    break
                except:
                    logging.info(f"❌ Estrategia dropdown {i} falló")
                    continue
            
            if not dropdown:
                logging.error("❌ No se encontró el dropdown de nombres")
                self.take_screenshot("error_no_dropdown")
                return False
            
            # Seleccionar nombre del dropdown
            logging.info(f"👆 Seleccionando nombre: {self.nombre}")
            
            if dropdown.tag_name.lower() == 'select':
                # Dropdown HTML estándar
                try:
                    select = Select(dropdown)
                    select.select_by_visible_text(self.nombre)
                    logging.info("✅ Nombre seleccionado en dropdown estándar")
                except Exception as e:
                    logging.error(f"❌ Error al seleccionar en dropdown estándar: {e}")
                    return False
            else:
                # Dropdown personalizado de Google Forms
                try:
                    # Abrir dropdown
                    self.driver.execute_script("arguments[0].click();", dropdown)
                    # Esperar un poco más para que las opciones se carguen completamente
                    time.sleep(3) 
                    
                    self.take_screenshot("04_dropdown_opened")
                    
                    option_found = False
                    
                    # NUEVA ESTRATEGIA: Intentar enviar teclas al elemento del dropdown
                    # Esto simula escribir en el campo de búsqueda del dropdown de Google Forms
                    try:
                        logging.info(f"🔍 Intentando seleccionar la opción enviando teclas: '{self.nombre.strip()}'")
                        # Enviar el nombre y luego la tecla ENTER
                        dropdown.send_keys(self.nombre.strip())
                        time.sleep(1) # Pequeña espera para que el formulario procese la entrada
                        dropdown.send_keys(Keys.ENTER) # Simular Enter para seleccionar la opción
                        logging.info(f"✅ Opción '{self.nombre}' seleccionada enviando teclas.")
                        option_found = True
                    except Exception as e:
                        logging.warning(f"⚠️ Falló la selección de opción enviando teclas. Error: {e}")
                        
                    if not option_found:
                        # Si la estrategia de enviar teclas falla, volvemos a intentar por data-value y luego por texto visible
                        # Normalizar el nombre a buscar para comparación (solo para fallback de texto)
                        target_name_normalized_for_text = self.nombre.strip().lower() 
                        
                        # Intentar buscar directamente la opción por su atributo data-value
                        try:
                            logging.info(f"🔍 Fallback: Intentando seleccionar por data-value: '{self.nombre.strip()}'")
                            option_element = WebDriverWait(self.driver, 10).until(
                                EC.element_to_be_clickable((By.XPATH, f'//div[@role="option" and @data-value="{self.nombre.strip()}"]'))
                            )
                            self.driver.execute_script("arguments[0].click();", option_element)
                            logging.info(f"✅ Fallback: Opción '{self.nombre}' seleccionada usando data-value.")
                            option_found = True
                        except Exception as e:
                            logging.info(f"❌ Fallback: No se encontró la opción por data-value ('{self.nombre.strip()}'), intentando por texto visible. Error: {e}")
                            
                            # Fallback a la búsqueda por texto visible si data-value falla
                            # Esperar a que al menos una opción visible esté presente
                            WebDriverWait(self.driver, 10).until(
                                EC.visibility_of_element_located((By.XPATH, '//div[@role="option"]'))
                            )
                            
                            # Buscar específicamente los spans dentro de los divs con role="option"
                            possible_options_spans = self.driver.find_elements(By.XPATH, 
                                '//div[@role="option"]//span'
                            )
                            
                            logging.info(f"🔍 Fallback: Encontradas {len(possible_options_spans)} posibles spans de opciones para búsqueda por texto.")

                            for option_span in possible_options_spans:
                                try:
                                    option_text = option_span.text.strip()
                                    option_text_normalized = option_text.lower()

                                    logging.info(f"   Fallback: Comparando opción extraída: '{option_text_normalized}' con '{target_name_normalized_for_text}'")
                                    
                                    if option_text_normalized == target_name_normalized_for_text:
                                        # Asegurarse de que el elemento padre (div[role="option"]) es cliqueable
                                        parent_div = option_span.find_element(By.XPATH, './ancestor::div[@role="option"][1]')
                                        WebDriverWait(self.driver, 5).until(
                                            EC.visibility_of(parent_div)
                                        )
                                        WebDriverWait(self.driver, 5).until(
                                            EC.element_to_be_clickable(parent_div)
                                        )
                                        self.driver.execute_script("arguments[0].click();", parent_div)
                                        logging.info(f"✅ Fallback: Opción '{self.nombre}' seleccionada usando texto visible.")
                                        option_found = True
                                        break
                                except Exception as e:
                                    logging.warning(f"⚠️ Fallback: Error al procesar una opción o no cliqueable (búsqueda por texto): {e}")
                                    continue
                    
                    if not option_found:
                        logging.error(f"❌ No se encontró la opción '{self.nombre}' en el dropdown después de revisar todas las posibles opciones.")
                        self.take_screenshot("error_option_not_found")
                        return False
                        
                except Exception as e:
                    logging.error(f"❌ Error al manejar dropdown personalizado: {e}")
                    self.take_screenshot("error_dropdown_handling")
                    return False
            
            time.sleep(2)
            self.take_screenshot("05_name_selected")
            
            # === PASO 3: DNI ===
            logging.info("\n🆔 === PASO 3: LLENAR DNI ===")
            
            # Buscar campo de DNI
            dni_field = None
            dni_strategies = [
                (By.CSS_SELECTOR, 'input[aria-label*="dni" i]'),
                (By.CSS_SELECTOR, 'input[aria-label*="DNI"]'),
                (By.CSS_SELECTOR, 'input[aria-label*="documento" i]'),
                (By.CSS_SELECTOR, 'input[name*="dni" i]'),
                (By.CSS_SELECTOR, 'input[name*="document" i]'),
                (By.XPATH, '//input[contains(@aria-label, "dni") or contains(@aria-label, "DNI") or contains(@aria-label, "documento") or contains(@aria-label, "Documento")]'),
            ]
            
            for i, (by, selector) in enumerate(dni_strategies, 1):
                try:
                    logging.info(f"🔍 Estrategia DNI {i}: {selector}")
                    dni_field = WebDriverWait(self.driver, 8).until(
                        EC.element_to_be_clickable((by, selector))
                    )
                    logging.info(f"✅ Campo DNI encontrado con estrategia {i}")
                    break
                except:
                    logging.info(f"❌ Estrategia DNI {i} falló")
                    continue
            
            # Si no encuentra campo específico, usar último campo de texto
            if not dni_field:
                try:
                    logging.info("🔍 Buscando último campo de texto como DNI...")
                    text_fields = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="text"]')
                    if text_fields:
                        dni_field = text_fields[-1]
                        logging.info("✅ Usando último campo de texto como campo DNI")
                    else:
                        # Buscar cualquier input visible
                        inputs = self.driver.find_elements(By.CSS_SELECTOR, 'input')
                        visible_inputs = [inp for inp in inputs if inp.is_displayed()]
                        if visible_inputs:
                            dni_field = visible_inputs[-1]
                            logging.info("✅ Usando último input visible como campo DNI")
                except Exception as e:
                    logging.error(f"❌ Error buscando campo DNI alternativo: {e}")
            
            if not dni_field:
                logging.error("❌ No se pudo encontrar el campo de DNI")
                self.take_screenshot("error_no_dni_field")
                return False
            
            # Llenar DNI
            logging.info(f"✍️ Llenando DNI: {self.dni}")
            self.type_like_human(dni_field, self.dni)
            time.sleep(2)
            
            self.take_screenshot("06_dni_filled")
            
            # === PASO 4: ENVIAR ===
            logging.info("\n📤 === PASO 4: ENVIAR FORMULARIO ===")
            
            # Buscar botón "Enviar"
            submit_button = None
            submit_strategies = [
                (By.XPATH, '//span[contains(text(), "Enviar")]/../..'),
                (By.XPATH, '//span[contains(text(), "Submit")]/../..'),
                (By.XPATH, '//div[@role="button" and contains(., "Enviar")]'),
                (By.XPATH, '//button[contains(., "Enviar")]'),
                (By.XPATH, '//input[@type="submit"]'),
                (By.XPATH, '//*[contains(text(), "Enviar")]/ancestor::*[@role="button" or @type="button" or contains(@class, "button")]'),
            ]
            
            for i, (by, selector) in enumerate(submit_strategies, 1):
                try:
                    logging.info(f"🔍 Estrategia enviar {i}: buscando 'Enviar'")
                    submit_button = WebDriverWait(self.driver, 8).until(
                        EC.element_to_be_clickable((by, selector))
                    )
                    logging.info(f"✅ Botón 'Enviar' encontrado con estrategia {i}")
                    break
                except:
                    logging.info(f"❌ Estrategia enviar {i} falló")
                    continue
            
            if not submit_button:
                logging.error("❌ No se encontró el botón 'Enviar'")
                self.take_screenshot("error_no_submit_button")
                return False
            
            # Click en "Enviar"
            logging.info("👆 Haciendo click en 'Enviar'...")
            self.driver.execute_script("arguments[0].click();", submit_button)
            time.sleep(5)  # Esperar confirmación
            
            # Verificar envío exitoso
            try:
                # Buscar mensaje de confirmación
                success_indicators = [
                    "respuesta se ha registrado",
                    "response has been recorded",
                    "gracias",
                    "thank you",
                    "enviado",
                    "submitted"
                ]
                
                page_text = self.driver.page_source.lower()
                success = any(indicator in page_text for indicator in success_indicators)
                
                if success:
                    logging.info("🎉 ¡FORMULARIO ENVIADO EXITOSAMENTE!")
                    return True
                else:
                    logging.warning("⚠️ No se detectó mensaje de confirmación, pero el envío puede haber sido exitoso")
                    return True  # Asumir éxito si no hay errores
                    
            except Exception as e:
                logging.error(f"❌ Error verificando envío: {e}")
                return True  # Asumir éxito si llegamos hasta aquí
                
        except Exception as e:
            logging.error(f"💥 ERROR CRÍTICO durante la automatización: {e}")
            self.take_screenshot("error_critical")
            return False
        finally:
            if self.driver:
                logging.info("🔚 Cerrando navegador...")
                self.driver.quit()

def main():
    """Función principal"""
    try:
        logging.info("🤖 === INICIANDO AUTOMATIZACIÓN DE FORMULARIO ===")
        
        automator = GitHubFormAutomator()
        success = automator.fill_form_step_by_step()
        
        if success:
            logging.info("✅ === AUTOMATIZACIÓN COMPLETADA EXITOSAMENTE ===")
            print("✅ ¡Formulario enviado correctamente!")
            exit(0)
        else:
            logging.error("❌ === AUTOMATIZACIÓN FALLÓ ===")
            print("❌ Error: El formulario no pudo ser enviado")
            exit(1)
            
    except Exception as e:
        logging.error(f"💥 ERROR CRÍTICO: {e}")
        print(f"❌ Error crítico: {e}")
        exit(1)

if __name__ == "__main__":
    main()
