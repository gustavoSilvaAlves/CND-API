import re
import httpx
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel


class CertidaoResponse(BaseModel):
    cnpj: str
    conteudo_certidao: str


app = FastAPI(
    title="API de Consulta de CND",
    description="Uma API assíncrona para consultar a Certidão Negativa de Débitos no site da Dataprev.",
    version="1.0.0"
)


async def buscar_certidao(cnpj: str, client: httpx.AsyncClient) -> str | None:
    """Busca o número da certidão de forma assíncrona."""

    url = "http://cnd.dataprev.gov.br/CWS/BIN/cws_mv2.asp"

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "cnd.dataprev.gov.br",
        "Origin": "http://cnd.dataprev.gov.br",
        "Referer": "http://cnd.dataprev.gov.br/CWS/BIN/cws_mv2.asp?CONTEXTO/CND/ACNT1004",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0"
    }
    payload = {
        "tipo": "1",
        "num": cnpj,
        "SIW_Contexto": "CND",
        "SIW_Transacao_Web": "LISTA",
        "SIW_Layout": "1,14"
    }

    try:
        response = await client.post(url, data=payload, headers=headers, timeout=10.0)
        response.raise_for_status()
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"Erro de comunicação com o serviço da Dataprev: {exc}")

    cnd_doc = ''
    for line in response.text.splitlines():
        if "NAO HA CND EMITIDA PARA O ESTABELECIMENTO" in line:
            return None
        elif "DETALHES[0]" in line:
            cnd_doc = line
            break

    if not cnd_doc:
        return None

    campos = re.findall(r'"(.*?)"', cnd_doc)

    if len(campos) >= 5:
        campo1 = campos[3]
        campo2 = campos[4].replace("/", "")
        resultado_final = campo1 + campo2

        return resultado_final
    else:

        return None


async def detalhar_certidao(cnpj: str, client: httpx.AsyncClient) -> str | None:
    num_cnd = await buscar_certidao(cnpj, client)

    if not num_cnd:
        return None

    url = f"http://cnd.dataprev.gov.br/CWS/BIN/cws_mv2.asp?COMS_BIN/SIW_Contexto=CND/SIW_Transacao_Web=CONSULTA2/{num_cnd}"
    headers = {
        "Host": "cnd.dataprev.gov.br",
        "Referer": "http://cnd.dataprev.gov.br/CWS/BIN/cws_mv2.asp",
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = await client.get(url, headers=headers, timeout=10.0)

        response.raise_for_status()
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"Erro ao buscar detalhes da certidão: {exc}")

    texto = []
    regex = r'new detalhe\("([^"]+)"\)'
    for linha in response.text.splitlines():
        match = re.search(regex, linha)
        if match:
            conteudo = match.group(1).strip()
            if conteudo:
                texto.append(conteudo)

    if not texto:
        return None

    return "\n".join(texto)



@app.get("/CND", response_model=CertidaoResponse)
async def consultar_cnd(
        cnpj: str = Query(
            ...,
            min_length=14,
            max_length=14,
            regex="^[0-9]{14}$",
            description="CNPJ a ser consultado, apenas números."
        )
):
    async with httpx.AsyncClient() as client:
        texto_certidao = await detalhar_certidao(cnpj, client)

    if not texto_certidao:
        raise HTTPException(
            status_code=404,
            detail=f"Não há certidão emitida para o estabelecimento de CNPJ: {cnpj}"
        )
    return CertidaoResponse(
        cnpj=cnpj,
        conteudo_certidao=texto_certidao
    )