import json
import os,glob, base64, subprocess
import docker

from datetime import datetime
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.file_detector import LocalFileDetector


class CrawlerCA:

    def getCA(ca: str, force: str = None):
        print(f"iniciando busca pelo CA-{ca}")
        with open('/app/Services/data.json', 'r') as json_file:
            dados_existentes = json.load(json_file)
            cas = dados_existentes.keys() 
            print("CAs = ",cas)
            ca = str(ca)
        if ca in cas:
            print("CA: ",ca)
            validdate = datetime.strptime(dados_existentes[ca]['data_validade'], "%d/%m/%Y %H:%M:%S")
            if((validdate.strftime("%Y/%m/%d") > datetime.today().strftime('%Y/%m/%d')) and force == None):
                print("CA encontrado previamente")
                return dados_existentes[ca]
            elif((validdate.strftime("%Y/%m/%d") < datetime.today().strftime('%Y/%m/%d')) and force == None):
                dados_existentes[ca]['update'] = True
                return dados_existentes[ca]
            
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--charset=UTF-8')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')

        options.add_experimental_option("prefs", {
        "download.default_directory": r"/home/seluser/files",
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": False,
        "plugins.always_open_pdf_externally": True,
        "--enable-managed-downloads": True
        })

        # driver = webdriver.Chrome(options=options)   
        driver = webdriver.Remote(command_executor="http://selenium-chrome-container:4444", options=options)
        
        driver.get("http://caepi.mte.gov.br/internet/ConsultaCAInternet.aspx")
        print("navegando ate o site")
        input_ca = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,"//*[@id='txtNumeroCA']")))
        input_ca.send_keys(ca)
        btn_consultar = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,"//*[@id='btnConsultar']")))
        btn_consultar.click()
        print("consultando")
        sleep(5)
        
        try:
            wait = WebDriverWait(driver, 10)
            btn_image = wait.until(EC.element_to_be_clickable((By.XPATH,"//*[@id='PlaceHolderConteudo_grdListaResultado_btnDetalhar_0']")))
            btn_image.click()
        except Exception as error:
            print("An error occurred:", type(error).__name__, "–", error)
            driver.quit()   
            return []
        
        sleep(5)
        temp_array = {}
        
        items = {
            "numero_ca":"lblNRRegistroCA",
            "data_validade":"lblDTValidade",
            "situacao":"lblSituacao",
            "processo":"lblNRProcesso",
            "cnpj":"lblNRCNPJ",
            "razao_social":"lblNORazaoSocial",
            "natureza":"lblNatureza",
            "equipamento":"lblNOEquipamento",
            "marcacao_ca":"lblDSLocalMarcacaoCA",
            "referencia":"lblDSReferencia",
            "tamanho":"lblDSTamanho",
            "descricao":"lblEquipamentoDSEquipamentoTexto",
            "cor":"lblDSCor",
            "numero_laudo":"grdListaLaudos_lblNrLaudo_0",
            "laudo":"lblDSAprovadoParaLaudo",
            "obs_laudo":"lblOBSAnaliseLaudo",
            "razao_social_laboratorio":"grdListaLaudos_lblNomeLaboratorioLaudo_0",
            "cnpj_laboratorio":"grdListaLaudos_lblNomeLaboratorio_0",
            "norma_tecnica":"grdListaNormas_lblNomeLaboratorioLaudo_0",
            "historico_alteracoes":"grdListaHistoricoAlteracao",
        }
    
        print("recuperando informações do CA")
        for item in items:
            try:
                temp_array[item] = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#PlaceHolderConteudo_"+items[item]))).text
            except:
                pass
        
        nca = driver.find_element(By.ID,"PlaceHolderConteudo_lblNRRegistroCA")
        print(nca.text)
        capdf = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#PlaceHolderConteudo_btnVisualizarCA")))
        capdf.click()
        sleep(5)
        localdir = os.getcwd()
        print("Copiando dados entre containers")
        subprocess.Popen(f"docker cp selenium-chrome-container:/home/seluser/files/ImprimirCAPesquisaInternet.pdf {localdir}/downloads/CA-{ca}.pdf",shell=True)
        with open('/app/Services/data.json', 'r') as json_file:
            dados_existentes = json.load(json_file)
        
        dados_existentes[ca] = temp_array

        # Salvar os dados atualizados
        with open('/app/Services/data.json', 'w') as json_file:
            json.dump(dados_existentes, json_file, indent=4)
            
         # Crie uma instância do cliente Docker
        client = docker.from_env()
        # Nome ou ID do container de origem
        container_name_or_id = "selenium-chrome-container"
        # Caminho para o arquivo dentro do container de origem
        arquivo_no_container = "/home/seluser/files/ImprimirCAPesquisaInternet.pdf"
        # Caminho no sistema de arquivos local onde você deseja copiar o arquivo
        caminho_local_destino = f"downloads/CA-{ca}.pdf"
        # Copie o arquivo do container para o sistema de arquivos local
        try:
            container = client.containers.get(container_name_or_id)
            stream, stat = container.get_archive(arquivo_no_container)
            with open(caminho_local_destino, "wb") as f:
                for chunk in stream:
                    f.write(chunk)
        except docker.errors.NotFound:
            print("Container não encontrado.")
        except Exception as e:
            print(f"Erro: {e}")
        
        driver.quit()
        
        return  temp_array
    