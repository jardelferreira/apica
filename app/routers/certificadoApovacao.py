import os
from typing import Annotated

from fastapi import Body, APIRouter
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse

from Services.CAService import CAService
from Services.CrawlerCA import CrawlerCA
from Services.IPGeocoder import IPGeocoder
from Services.CoodinatesGeocoder import CoodinatesGeocoder

from models.exemplosRequest import ExemplosRequest
from models.requestParaExportarArquivo import RequestParaExportarArquivo
from models.requestParaExportarJson import RequestParaExportarJson
from models.infoCADto import InfoCADto
from models.responsesModels import ResponsesModels


router = APIRouter(tags=["Certificado de Aprovação"])
caService = CAService()

@router.get("/certificado/{ca}", tags=["certificados"])
async def getCertificate(ca: str, param: str = None):
    file_location = f"downloads/CA-{ca}.pdf"
    file_name = f"CA-{ca}.pdf"
    if (os.path.isfile(f"downloads/CA-{ca}.pdf")):
        return FileResponse(file_location, media_type='application/octet-stream', filename=file_name)
    elif(param == None):
       return JSONResponse(status_code=303,content={
                            "success": False,
                            "erros": ["Atualize a base de dados de arquivos."]}
                        ) 
    return JSONResponse(status_code=404,content={
                            "success": False,
                            "erros": ["Arquivo não localizado"]}
                        )


@router.get("/geolocationLatLng", tags=["LatLng"])
def geolocationLatLng(lat: str, lng: str):
    if(lat and lng):
        geolocation = CoodinatesGeocoder.geolocation(lat,lng)
        if(geolocation["success"]):
            return JSONResponse(status_code=200,content={
                "success":True,
                "data":geolocation})
        else:
            return JSONResponse(status_code=200,content={
            "success":False,
            "data":geolocation})
    return JSONResponse(status_code=400,content={
            "success":False,
            "data":{"message":"É necessário informar duas coordenadas, lat e lng"}})

@router.get("/geolocationIP/{ip}", tags=["GeoIP"])
def geolocationIP(ip: str):
    if(ip):
        geolocation = IPGeocoder.geolocation(ip)
        if(geolocation["success"]):
            return JSONResponse(status_code=200,content={
                "success":True,
                "data":geolocation})
        else:
            return JSONResponse(status_code=200,content={
            "success":False,
            "data":geolocation})
    return JSONResponse(status_code=400,content={
            "success":False,
            "data":{"message":"É necessário informar um IP"}})


@router.get("/consulta/{ca}/{force}", tags=["crawling"])
def crawlerSeleniumCA(ca: str,force:bool = False):
    print(ca,force)
    dataAPI = CrawlerCA.getCA(ca,force)
    if (dataAPI != []):
        return JSONResponse(status_code=200,content={
            "success":True,
            "data":dataAPI})
    elif(dataAPI == []):
        dataAPI = caService.retornarTodasInfoAtuais(ca)
        if dataAPI != None:
            return dataAPI
    return JSONResponse(status_code=404,content={
                            "success": False,
                            "erros": ["Numero Ca não encontrado!"]}
                        )

@router.get('/CA/{ca}',
            status_code=200,
            summary="Retorna as informações atuais do CA",
            description="Retorna apenas a ultima ocorrencia(dados atuais)",
            responses=ResponsesModels.responsesInfoCA
            )
async def retornarInfoCA(ca: str) -> InfoCADto:
    dadosEPI = caService.retornarTodasInfoAtuais(ca)
    if dadosEPI != None:
        return dadosEPI
    return JSONResponse(status_code=404,content={
                            "success": False,
                            "erros": ["Numero Ca não encontrado!"]}
                        )
    
@router.get('/retornarTodasAtualizacoes/{ca}',
            status_code=200,
            summary="Retorna as todas as atualizações  CA",
            description="Retorna as todas as atualizações  CA",
            responses=ResponsesModels.responsesInfoCA)
async def retornarTodasAtualizacoes(ca: str) -> list[InfoCADto]:
    dadosEPI = caService.retornarTodasAtualizacoes(ca)
    if dadosEPI != None:
        return dadosEPI

    return JSONResponse(404, content={
        "success": False,
        "erros": ["Numero Ca não encontrado!"]})


@router.post('/exportarExcel',
             summary="Gera um arquivo excel com os CAs informados",
             description="Gera um arquivo excel com os CAs informados, caso algum CA não seja encontrado ocorrerá um erro",
             responses=ResponsesModels.responsesExportar)
def post(
    request: Annotated[RequestParaExportarArquivo, Body(
        example=ExemplosRequest.exportarArquivo)]) -> StreamingResponse:
    # Criar uma resposta para o arquivo Excel
    respExportarExcel = caService.exportarExcel(
        request.listaCAs, request.nomeArquivo)
    if len(request.listaCAs) == 0:
        return JSONResponse(status_code=400, content={
            "success": False,
            "erros": "listaCAs não pode estar vazia"})

    if not respExportarExcel['success']:
        return JSONResponse(status_code=404, content={
            "success": False,
            "CAsNaoEncontrados": respExportarExcel['CAsNaoEncontrados']})

    planilha = respExportarExcel['planilha']

    response = StreamingResponse(planilha, media_type='application/vnd.      openxmlformats-officedocument.spreadsheetml.sheet', headers={
        'Content-Disposition': f'attachment; filename={request.nomeArquivo}.xlsx'})

    return response

@router.post('/exportarJSON',
             summary="Retorna um JSON com as informações dos CAs informados",
             responses=ResponsesModels.responsesExportar)
def exportarJSON(request: RequestParaExportarJson) -> list[InfoCADto]:
    if len(request.listaCAs) == 0:
        return JSONResponse(status_code=400, content={
            "success": False,
            "erros": "listaCAs não pode estar vazia"})

    respExportarJson = caService.exportarJson(request.listaCAs)
    if not respExportarJson['success']:
        return JSONResponse(status_code=404,
                            content=respExportarJson
                            )

    return respExportarJson['JSON']
