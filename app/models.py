from pydantic import BaseModel, Field

class StatusResponse(BaseModel):
    status: str = Field(..., example="ok", description="Status da API")

class ErrorResponse(BaseModel):
    detail: str

class CndtRequest(BaseModel):
    cnpj: str = Field(..., example="00000000000191", description="CNPJ a ser consultado")
    file_id: str = Field(..., example="certidao_123", description="ID único para nomear o arquivo PDF final")

class CndtResponse(BaseModel):
    texto_pdf: str = Field(..., description="Conteúdo de texto extraído da certidão CNDT em PDF")

class CndResponse(BaseModel):
    cnpj: str
    conteudo_certidao: str