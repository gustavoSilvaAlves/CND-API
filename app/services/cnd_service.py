import re
import httpx

class CndError(Exception): pass


class CndNaoEncontradaError(CndError): pass


class CndServicoIndisponivelError(CndError): pass


async def _buscar_numero_certidao(cnpj: str, client: httpx.AsyncClient) -> str:
    """Passo 1: Busca o número interno da certidão."""
    url = "http://cnd.dataprev.gov.br/CWS/BIN/cws_mv2.asp"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "cnd.dataprev.gov.br",
        "Origin": "http://cnd.dataprev.gov.br",
        "Referer": "http://cnd.dataprev.gov.br/CWS/BIN/cws_mv2.asp?CONTEXTO/CND/ACNT1004",
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
        raise CndServicoIndisponivelError(f"Erro de comunicação com a Dataprev: {exc}")

    cnd_doc_line = ''
    for line in response.text.splitlines():
        if "NAO HA CND EMITIDA PARA O ESTABELECIMENTO" in line:
            raise CndNaoEncontradaError(f"Não há CND emitida para o CNPJ: {cnpj}")
        if "DETALHES[0]" in line:
            cnd_doc_line = line
            break

    if not cnd_doc_line:
        raise CndNaoEncontradaError(f"Não foi possível extrair a linha de detalhes para o CNPJ: {cnpj}")

    campos = re.findall(r'"(.*?)"', cnd_doc_line)
    if len(campos) < 5:
        raise CndNaoEncontradaError("Formato de detalhes inesperado na resposta da Dataprev.")

    return campos[3] + campos[4].replace("/", "")


async def consultar_cnd_async(cnpj: str) -> str:
    """Função principal do serviço que orquestra a consulta CND."""
    async with httpx.AsyncClient() as client:
        numero_certidao = await _buscar_numero_certidao(cnpj, client)

        url_detalhes = f"http://cnd.dataprev.gov.br/CWS/BIN/cws_mv2.asp?COMS_BIN/SIW_Contexto=CND/SIW_Transacao_Web=CONSULTA2/{numero_certidao}"
        headers = {
            "Host": "cnd.dataprev.gov.br",
            "Referer": "http://cnd.dataprev.gov.br/CWS/BIN/cws_mv2.asp",  # <--- Crucial
            "User-Agent": "Mozilla/5.0"
        }

        try:
            response = await client.get(url_detalhes, headers=headers, timeout=10.0)
            response.raise_for_status()
        except httpx.RequestError as exc:
            raise CndServicoIndisponivelError(f"Erro ao buscar detalhes da certidão: {exc}")

        regex = r'new detalhe\("([^"]+)"\)'
        texto_linhas = [
            match.group(1).strip()
            for match in re.finditer(regex, response.text)
            if match.group(1).strip()
        ]

        if not texto_linhas:
            raise CndNaoEncontradaError("Não foi possível extrair o conteúdo da certidão.")

        return "\n".join(texto_linhas)