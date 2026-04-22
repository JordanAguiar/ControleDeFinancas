from datetime import datetime
from core.models import Receita
from core.exceptions import ValorInvalidoError, CampoObrigatorioError, DataInvalidaError
import infra


def criar_receita(descricao: str, categoria: str,
                  valor: str, data: str = None) -> Receita:
    if not descricao or not categoria or not valor:
        raise CampoObrigatorioError()
    try:
        valor_float = float(valor.replace(",", "."))
    except ValueError:
        raise ValorInvalidoError("valor")

    if data:
        try:
            datetime.strptime(data, "%d/%m/%Y")
        except ValueError:
            raise DataInvalidaError(data)
    else:
        data = datetime.now().strftime("%d/%m/%Y")

    receita = Receita(descricao=descricao, categoria=categoria,
                      valor=valor_float, data=data)
    infra.salvar_receita(receita)
    return receita


def listar() -> list[Receita]:
    return infra.buscar_receitas()


def deletar(indice: int):
    infra.remover_receita(indice)