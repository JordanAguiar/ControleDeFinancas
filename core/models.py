from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Gasto:
    descricao:  str
    categoria:  str
    valor:      float
    data:       str = field(default_factory=lambda: datetime.now().strftime("%d/%m/%Y"))

    def __post_init__(self):
        self.valor = float(self.valor)


@dataclass
class Receita:
    descricao:  str
    categoria:  str
    valor:      float
    data:       str = field(default_factory=lambda: datetime.now().strftime("%d/%m/%Y"))

    def __post_init__(self):
        self.valor = float(self.valor)


@dataclass
class Divida:
    credor:       str
    descricao:    str
    valor_total:  float
    valor_pago:   float
    vencimento:   str
    status:       str = "Pendente"

    def __post_init__(self):
        self.valor_total = float(self.valor_total)
        self.valor_pago  = float(self.valor_pago)
        restante         = self.valor_total - self.valor_pago
        self.status      = "Quitada" if restante <= 0 else "Pendente"

    @property
    def valor_pendente(self) -> float:
        return max(0.0, self.valor_total - self.valor_pago)


@dataclass
class Investimento:
    descricao:    str
    categoria:    str
    valor:        float
    instituicao:  str
    data:         str = field(default_factory=lambda: datetime.now().strftime("%d/%m/%Y"))

    def __post_init__(self):
        self.valor = float(self.valor)


@dataclass
class GastoFixo:
    descricao:       str
    categoria:       str
    valor:           float
    dia_vencimento:  int
    ativo:           str = "Sim"

    def __post_init__(self):
        self.valor          = float(self.valor)
        self.dia_vencimento = int(self.dia_vencimento)


@dataclass
class Parcela:
    descricao:       str
    categoria:       str
    valor_total:     float
    num_parcelas:    int
    parcelas_pagas:  int
    valor_parcela:   float
    data_inicio:     str
    ativo:           str = "Sim"

    def __post_init__(self):
        self.valor_total   = float(self.valor_total)
        self.num_parcelas  = int(self.num_parcelas)
        self.valor_parcela = float(self.valor_parcela)

    @property
    def parcelas_restantes(self) -> int:
        return max(0, self.num_parcelas - self.parcelas_pagas)

    @property
    def quitada(self) -> bool:
        return self.parcelas_restantes <= 0

    @property
    def status(self) -> str:
        return "Quitado" if self.quitada else f"{self.parcelas_restantes} restantes"


@dataclass
class Resumo:
    total_gastos:       float
    total_receitas:     float
    total_dividas:      float
    dividas_pendentes:  float
    saldo:              float
    qtd_gastos:         int
    qtd_dividas:        int
    qtd_receitas:       int
    qtd_investimentos:  int = 0