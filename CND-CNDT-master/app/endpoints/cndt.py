import asyncio
from fastapi import APIRouter, HTTPException, status
from app.models import CndtRequest, CndtResponse, ErrorResponse
from app.core import CONCURRENCY_LIMITER, logger
from app.services.cndt_service import gerar_certidao_cndt_sync, CndtError

router = APIRouter()

@router.post(
    "/consulta/cndt",
    response_model=CndtResponse,
    summary="Consulta e extrai texto de uma certidão CNDT",
    tags=["CNDT"],
    responses={
        500: {"model": ErrorResponse, "description": "Falha no processo de consulta"},
        503: {"model": ErrorResponse, "description": "Serviço indisponível (muitas requisições)"}
    }
)
async def consultar_cndt(request_data: CndtRequest):
    """
    Orquestra a consulta de CNDT de forma assíncrona, controlando a
    concorrência de execuções do Selenium.
    """
    try:
        async with CONCURRENCY_LIMITER:
            logger.info(f"Iniciando consulta CNDT para o CNPJ: {request_data.cnpj}")
            texto_pdf = await asyncio.to_thread(
                gerar_certidao_cndt_sync,
                cnpj=request_data.cnpj,
                file_id=request_data.file_id
            )
            return CndtResponse(texto_pdf=texto_pdf)
    except CndtError as e:
        logger.error(f"Erro de negócio ao gerar CNDT: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        logger.error(f"Erro inesperado no endpoint CNDT: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno inesperado.")