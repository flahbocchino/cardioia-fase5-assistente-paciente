"""
nlu_engine.py
--------------
Motor de reconhecimento de intenção (NLU) do assistente.
Equivale ao motor de NLU do Watson Assistant: recebe uma frase do
paciente e decide qual "intent" ela representa.

Técnica: vetorização TF-IDF + Regressão Logística, treinado a partir
de exemplos de frases por intenção (training_data.json).
Isso é o mesmo tipo de abordagem clássica de NLP vista em disciplinas
de Processamento de Linguagem Natural: bag-of-words / TF-IDF + classificador.
"""

import json
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

CAMINHO_DADOS = os.path.join(os.path.dirname(__file__), "training_data.json")

# Com poucas frases de treino por intenção e várias classes, a probabilidade
# "absoluta" do vencedor tende a ficar baixa mesmo quando a previsão está
# correta (a massa de probabilidade se espalha entre as classes). Por isso o
# limiar é mais baixo do que se costuma ver em datasets grandes.
LIMIAR_CONFIANCA = 0.18  # abaixo disso, tratamos como "não entendi"


class MotorNLU:
    def __init__(self, caminho_dados: str = CAMINHO_DADOS):
        with open(caminho_dados, "r", encoding="utf-8") as f:
            self.dados = json.load(f)["intents"]

        # unigramas + bigramas ajudam bastante em frases curtas ("dor no peito"
        # carrega mais sinal como bigrama do que como três unigramas soltos)
        self.vetorizador = TfidfVectorizer(
            ngram_range=(1, 2),
            lowercase=True,
            strip_accents="unicode",
        )
        self.classificador = LogisticRegression(max_iter=1000, C=5.0)
        self.mapa_intents = {intent["tag"]: intent for intent in self.dados}

        self._treinar()

    def _treinar(self):
        frases, rotulos = [], []
        for intent in self.dados:
            for frase in intent["frases"]:
                frases.append(frase)
                rotulos.append(intent["tag"])

        X = self.vetorizador.fit_transform(frases)
        self.classificador.fit(X, rotulos)

    def prever(self, texto: str):
        """Retorna (intent_prevista, confianca)."""
        X = self.vetorizador.transform([texto])
        probabilidades = self.classificador.predict_proba(X)[0]
        classes = self.classificador.classes_

        indice_melhor = probabilidades.argmax()
        intent_prevista = classes[indice_melhor]
        confianca = float(probabilidades[indice_melhor])

        if confianca < LIMIAR_CONFIANCA:
            return "desconhecido", confianca

        return intent_prevista, confianca

    def get_intent_info(self, tag: str):
        return self.mapa_intents.get(tag)
