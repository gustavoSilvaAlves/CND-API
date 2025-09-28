import os
import time
import fitz
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import tempfile
import shutil
from app.core import settings, logger


class CndtError(Exception): pass


class CaptchaError(CndtError): pass


class PdfDownloadError(CndtError): pass


def _configurar_driver_sync(download_directory: str):
    logger.info(f"Configurando driver. Diretório de download: {download_directory}")
    os.makedirs(download_directory, exist_ok=True)
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    prefs = {
        "download.default_directory": download_directory,
        "download.prompt_for_download": False,
        "plugins.always_open_pdf_externally": True
    }
    options.add_experimental_option("prefs", prefs)
    return uc.Chrome(options=options)


def _resolver_captcha_sync(driver) -> str:
    logger.info("Resolvendo captcha de imagem...")
    try:
        wait = WebDriverWait(driver, 10)
        captcha_img = wait.until(
            EC.presence_of_element_located((By.XPATH, "//img[@id='idImgBase64' and contains(@src, 'base64')]"))
        )
        captcha_base64 = captcha_img.get_attribute('src').split(',')[1]

        response = requests.post('http://2captcha.com/in.php', data={
            'key': settings.captcha_api_key, 'method': 'base64',
            'body': captcha_base64, 'json': 1
        }, timeout=20)
        captcha_id = response.json().get('request')

        if not captcha_id:
            raise CaptchaError("2Captcha não retornou um ID de requisição.")

        time.sleep(15)
        url_result = f"http://2captcha.com/res.php?key={settings.captcha_api_key}&action=get&id={captcha_id}&json=1"

        for _ in range(10):
            result_response = requests.get(url_result, timeout=10)
            result = result_response.json()
            if result.get('status') == 1:
                logger.info("Captcha resolvido com sucesso.")
                return result.get('request')
            if result.get('request') != 'CAPCHA_NOT_READY':
                raise CaptchaError(f"Erro no 2Captcha: {result.get('request')}")
            time.sleep(5)

        raise CaptchaError("Tempo esgotado para resolver o CAPTCHA.")
    except Exception as e:
        raise CaptchaError(f"Falha inesperada ao resolver o CAPTCHA: {e}")


def gerar_certidao_cndt_sync(cnpj: str, file_id: str) -> str:
    # --- MUDANÇA 1: Criar um diretório temporário único para esta requisição ---
    temp_dir = tempfile.mkdtemp()
    logger.info(f"Diretório temporário criado para a requisição: {temp_dir}")
    # --------------------------------------------------------------------------

    driver = None
    try:
        # Passa o diretório temporário para a configuração do driver
        driver = _configurar_driver_sync(temp_dir)
        driver.get('https://cndt-certidao.tst.jus.br/gerarCertidao.faces')
        wait = WebDriverWait(driver, 20)

        captcha_text = _resolver_captcha_sync(driver)

        wait.until(EC.presence_of_element_located((By.ID, 'gerarCertidaoForm:cpfCnpj'))).send_keys(cnpj)
        driver.find_element(By.ID, 'idCampoResposta').send_keys(captcha_text)
        driver.find_element(By.ID, 'gerarCertidaoForm:btnEmitirCertidao').click()
        logger.info("Formulário enviado. Aguardando download do PDF...")

        # A lógica de espera agora é segura, pois olha apenas dentro da pasta temporária
        caminho_pdf_final = os.path.join(temp_dir, f"{file_id}.pdf")
        timeout = 60
        arquivo_baixado_path = None
        for _ in range(timeout):
            files = [f for f in os.listdir(temp_dir) if f.endswith('.pdf')]
            if files:
                arquivo_baixado_path = os.path.join(temp_dir, files[0])
                break
            time.sleep(1)

        if not arquivo_baixado_path:
            raise PdfDownloadError("PDF não foi baixado a tempo.")

        logger.info(f"PDF baixado. Renomeando para {caminho_pdf_final}")
        os.rename(arquivo_baixado_path, caminho_pdf_final)

        with fitz.open(caminho_pdf_final) as doc:
            texto_extraido = "".join(page.get_text() for page in doc)

        logger.info("Texto extraído com sucesso.")
        return texto_extraido

    finally:
        if driver:
            driver.quit()
        # --- MUDANÇA 2: Limpar o diretório temporário e todo o seu conteúdo ---
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            logger.info(f"Diretório temporário {temp_dir} removido.")