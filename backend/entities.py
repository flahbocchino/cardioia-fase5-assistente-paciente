"""
entities.py
------------
Extração simples de entidades a partir do texto do paciente.
Equivale às "entities" do Watson Assistant, só que implementadas
por palavras-chave e expressões regulares em vez de uma interface visual.

Entidades reconhecidas:
- intensidade: leve / moderada / forte / insuportável
- duracao: referências de tempo ("há 2 dias", "hoje", "ontem", "agora")
- sim_nao: confirmação ou negação numa resposta curta
"""

import re

PALAVRAS_INTENSIDADE = {
    "leve": "leve",
    "fraca": "leve",
    "moderada": "moderada",
    "media": "moderada",
    "média": "moderada",
    "forte": "forte",
    "intensa": "forte",
    "insuportavel": "insuportavel",
    "insuportável": "insuportavel",
}

PALAVRAS_SIM = {"sim", "s", "isso", "exato", "correto", "com certeza", "positivo"}
PALAVRAS_NAO = {"não", "nao", "n", "negativo", "de jeito nenhum"}

PADRAO_DURACAO = re.compile(
    r"(h[áa]\s+\d+\s+(minuto|hora|dia|semana)s?)"
    r"|(\bhoje\b)|(\bontem\b)|(\bagora\b)|(\bnesse momento\b)",
    re.IGNORECASE,
)


def extrair_intensidade(texto: str):
    texto_lower = texto.lower()
    for palavra, valor in PALAVRAS_INTENSIDADE.items():
        if palavra in texto_lower:
            return valor
    return None


def extrair_duracao(texto: str):
    encontrado = PADRAO_DURACAO.search(texto)
    return encontrado.group(0) if encontrado else None


def extrair_sim_nao(texto: str):
    texto_lower = texto.lower().strip()
    if texto_lower in PALAVRAS_SIM:
        return "sim"
    if texto_lower in PALAVRAS_NAO:
        return "nao"
    return None


def extrair_entidades(texto: str) -> dict:
    """Retorna um dicionário com todas as entidades encontradas na frase."""
    return {
        "intensidade": extrair_intensidade(texto),
        "duracao": extrair_duracao(texto),
        "sim_nao": extrair_sim_nao(texto),
    }
