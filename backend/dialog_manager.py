"""
dialog_manager.py
-------------------
Gerenciador de diálogo do assistente. Equivale aos "dialog nodes" do
Watson Assistant: decide o que responder com base na intenção
detectada, nas entidades extraídas e no estado da conversa (contexto).

Mantém um pequeno estado por sessão (session_id), assim como o Watson
mantém "contexto" entre mensagens de uma mesma conversa.
"""

import random
from entities import extrair_entidades
from nlu_engine import MotorNLU

SINTOMAS = {"sintoma_dor_peito", "sintoma_falta_ar", "sintoma_palpitacao", "sintoma_tontura"}

NOMES_SINTOMAS = {
    "sintoma_dor_peito": "dor no peito",
    "sintoma_falta_ar": "falta de ar",
    "sintoma_palpitacao": "palpitação",
    "sintoma_tontura": "tontura",
}

AVISO_LEGAL = (
    " (Lembrando: sou um assistente educacional simulado do projeto CardioIA "
    "e não substituo uma avaliação médica real.)"
)

MAX_TENTATIVAS_FALLBACK = 2


class GerenciadorDialogo:
    def __init__(self):
        self.nlu = MotorNLU()
        self.sessoes = {}  # session_id -> estado da conversa

    def _get_sessao(self, session_id: str):
        if session_id not in self.sessoes:
            self.sessoes[session_id] = {
                "estado": "inicio",
                "sintoma_atual": None,
                "intensidade": None,
                "duracao": None,
                "tentativas_fallback": 0,
            }
        return self.sessoes[session_id]

    def processar(self, session_id: str, texto: str) -> str:
        sessao = self._get_sessao(session_id)
        entidades = extrair_entidades(texto)

        # Se estamos no meio de uma triagem de sintoma, o dialog node
        # "aguardando_detalhes" tem prioridade sobre uma nova classificação de intent.
        if sessao["estado"] == "aguardando_intensidade":
            return self._tratar_intensidade(sessao, texto, entidades)

        if sessao["estado"] == "aguardando_duracao":
            return self._tratar_duracao(sessao, texto, entidades)

        intent, confianca = self.nlu.prever(texto)

        if intent == "desconhecido":
            return self._tratar_fallback(sessao)

        sessao["tentativas_fallback"] = 0

        if intent == "emergencia":
            return self._resposta_estatica("emergencia")

        if intent in SINTOMAS:
            return self._iniciar_triagem_sintoma(sessao, intent)

        # intents "simples" (saudação, despedida, dúvidas, fora de escopo, etc.)
        return self._resposta_estatica(intent)

    def _resposta_estatica(self, tag: str) -> str:
        info = self.nlu.get_intent_info(tag)
        if not info or "respostas" not in info:
            return self._tratar_fallback(None)
        return random.choice(info["respostas"])

    def _iniciar_triagem_sintoma(self, sessao, intent: str) -> str:
        sessao["sintoma_atual"] = intent
        sessao["estado"] = "aguardando_intensidade"
        nome = NOMES_SINTOMAS[intent]
        return (
            f"Entendi, você está sentindo {nome}. Em uma escala, essa sensação está "
            f"leve, moderada, forte ou insuportável?"
        )

    def _tratar_intensidade(self, sessao, texto, entidades) -> str:
        intensidade = entidades["intensidade"]
        if not intensidade:
            return (
                "Não consegui identificar a intensidade. Pode responder com uma "
                "palavra: leve, moderada, forte ou insuportável?"
            )

        sessao["intensidade"] = intensidade

        # Regra de segurança: sintoma forte/insuportável já escala para emergência,
        # sem precisar perguntar mais nada.
        if intensidade in ("forte", "insuportavel"):
            self._reiniciar_sessao(sessao)
            return self._resposta_estatica("emergencia")

        sessao["estado"] = "aguardando_duracao"
        return "Há quanto tempo você sente isso? (ex.: 'há 2 dias', 'hoje', 'agora')"

    def _tratar_duracao(self, sessao, texto, entidades) -> str:
        duracao = entidades["duracao"] or texto  # aceita texto livre se não bater no regex
        sessao["duracao"] = duracao
        nome = NOMES_SINTOMAS.get(sessao["sintoma_atual"], "esse sintoma")
        intensidade = sessao["intensidade"]

        resposta = (
            f"Obrigado por detalhar. Resumindo: {nome}, intensidade {intensidade}, "
            f"começou {duracao}. Para sintomas cardíacos, mesmo leves ou moderados, "
            f"o recomendado é agendar uma avaliação com um cardiologista o quanto antes, "
            f"principalmente se o sintoma persistir ou piorar."
            f"{AVISO_LEGAL}"
        )

        self._reiniciar_sessao(sessao)
        return resposta

    def _tratar_fallback(self, sessao) -> str:
        if sessao is not None:
            sessao["tentativas_fallback"] += 1
            if sessao["tentativas_fallback"] > MAX_TENTATIVAS_FALLBACK:
                sessao["tentativas_fallback"] = 0
                return (
                    "Ainda não consegui entender. Para garantir sua segurança, "
                    "recomendo falar diretamente com um profissional de saúde ou, "
                    "em caso de urgência, ligar para o SAMU (192)."
                )
        return (
            "Desculpe, não entendi. Pode me contar com outras palavras o que "
            "você está sentindo ou perguntando?"
        )

    def _reiniciar_sessao(self, sessao):
        sessao["estado"] = "inicio"
        sessao["sintoma_atual"] = None
        sessao["intensidade"] = None
        sessao["duracao"] = None
