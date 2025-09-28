from fastapi import APIRouter, HTTPException, status, Query
from app.models import CndResponse, ErrorResponse
from app.services.cnd_service import consultar_cnd_async, CndNaoEncontradaError, CndServicoIndisponivelError

router = APIRouter()


@router.get(
    "/consulta/cnd",
    response_model=CndResponse,
    summary="Consulta uma Certidão Negativa de Débitos (CND)",
    tags=["CND"],
    responses={
        404: {"model": ErrorResponse, "description": "Certidão não encontrada"},
        503: {"model": ErrorResponse, "description": "Serviço da Dataprev indisponível"}
    }
)
async def consultar_cnd(
        cnpj: str = Query(
            ...,
            min_length=14,
            max_length=14,
            regex="^[0-9]{14}$",
            description="CNPJ a ser consultado, contendo apenas números."
        )
):
    """
    Consulta a CND de um estabelecimento diretamente no site da Dataprev.
    Esta operação é puramente assíncrona e não utiliza Selenium.
    """
    try:
        # Note que NÃO usamos semáforo aqui. A operação é leve.
        conteudo_certidao = await consultar_cnd_async(cnpj)
        return CndResponse(cnpj=cnpj, conteudo_certidao=conteudo_certidao)

    except CndNaoEncontradaError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except CndServicoIndisponivelError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro interno inesperado: {e}")