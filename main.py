import time
import io
import pytesseract
from PIL import Image, ImageOps, ImageEnhance
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# --- KULLANICI BİLGİLERİ ---
USER_NAME = "WqAzer"
USER_PASS = "biro2121"
TARGET_URL = "https://www.ticarisk.com.tr"

def resmi_isleme_sok(img_bytes):
    """Görseldeki gürültüyü (çizgileri) siler ve rakamları netleştirir."""
    img = Image.open(io.BytesIO(img_bytes))
    img = img.convert('L')  # Gri tonlama
    img = ImageOps.invert(img)  # Renkleri ters çevir (Siyah yazı, beyaz arka plan)
    
    # Kontrastı ve Keskinliği artır (Arkadaki ince çizgileri yok eder)
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(5.0)
    
    sharpness = ImageEnhance.Sharpness(img)
    img = sharpness.enhance(2.0)
    
    # Eşikleme (Thresholding): Sadece tam siyah ve tam beyaz bırak
    img = img.point(lambda x: 0 if x < 145 else 255) 
    return img

def botu_baslat():
    # Render/Bulut sunucu ayarları (Headless mod şarttır)
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--headless') 
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        print(f"🔗 {TARGET_URL} adresine bağlanılıyor...")
        driver.get(TARGET_URL)
        time.sleep(4)

        # 1. OTOMATİK GİRİŞ
        print(f"🔑 Giriş yapılıyor: {USER_NAME}")
        
        # Giriş alanlarını bul ve verileri gir
        driver.find_element(By.NAME, "username").send_keys(USER_NAME)
        driver.find_element(By.NAME, "password").send_keys(USER_PASS)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        time.sleep(5) # Girişin tamamlanıp oyunun yüklenmesi için bekle
        print("✅ Giriş başarılı! Sorular çözülmeye başlıyor...")

        # 2. SONSUZ DÖNGÜ: ÇÖZ VE KAZAN
        while True:
            try:
                # Captcha resmini bul (img src içinde 'captcha' geçen elementi arar)
                captcha_img = driver.find_element(By.CSS_SELECTOR, "img[src*='captcha']")
                img_data = captcha_img.screenshot_as_png
                
                # Resmi temizle ve metne çevir
                islenmis_img = resmi_isleme_sok(img_data)
                # Tesseract'a sadece rakam ve matematik sembollerini okumasını söyle
                custom_config = r'--psm 7 -c tessedit_char_whitelist=0123456789+-x*/'
                soru = pytesseract.image_to_string(islenmis_img, config=custom_config).strip()
                
                if soru:
                    # 'x' karakterini Python'un anlayacağı '*' karakterine çevir
                    temiz_soru = soru.replace('x', '*')
                    cevap = eval(temiz_soru)
                    
                    # Cevabı yaz ve gönder
                    cevap_alani = driver.find_element(By.CSS_SELECTOR, "input[placeholder*='Cevabınızı']")
                    cevap_alani.clear()
                    cevap_alani.send_keys(str(cevap))
                    cevap_alani.send_keys(Keys.ENTER)
                    
                    print(f"💰 İşlem: {temiz_soru} = {cevap} | Bakiye artıyor!")
                    
                    # Dakikada 60 soru hedefi için 1 saniye bekle
                    time.sleep(1) 
                
            except Exception:
                # Yeni soru henüz yüklenmediyse kısa süre bekle
                time.sleep(0.5)

    except Exception as e:
        print(f"❌ Bir hata oluştu: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    botu_baslat()
      
