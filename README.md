# CardioIA — Fase 5: Assistente Cardiológico Inteligente

Assistente conversacional para orientação inicial sobre saúde cardiovascular, desenvolvido para a Fase 5 do curso de Inteligência Artificial da FIAP (disciplina de Processamento de Linguagem Natural, Chatbots & Virtual Agents).

O assistente interpreta mensagens escritas por pacientes, reconhece sintomas cardiovasculares, conduz uma triagem simples em múltiplas etapas, identifica possíveis emergências e orienta o usuário a procurar atendimento médico quando necessário.

> ⚠️ **Este sistema é educacional.** Não fornece diagnóstico, prescrição ou tratamento médico, e não substitui avaliação por um profissional de saúde.

---

## 🔗 Links

| | |
|---|---|
| 💬 Interface do assistente | https://flahbocchino.github.io/cardioia-fase5-assistente-paciente/ |
| ⚙️ API backend | https://cardioia-fase5-assistente-paciente.onrender.com |
| 🎥 Vídeo de demonstração | https://youtube.com/shorts/TIFEblU6CCA |

> Nota: o backend roda em um plano gratuito do Render e "dorme" após um tempo sem uso — a primeira mensagem pode demorar de 20 a 30 segundos para responder.

---

## 🏗️ Arquitetura

```
Usuário digita no chat (frontend)
        │  POST /mensagem
        ▼
Backend Flask recupera/cria o estado da sessão
        │
        ▼
Existe triagem em andamento?
   │ sim                    │ não
   ▼                        ▼
Gerenciador de diálogo    Classificador de intenção (NLU)
interpreta a resposta     (TF-IDF + Regressão Logística)
conforme a etapa atual            │
        │                         ▼
        └──────────────► Extração de entidades
                          (intensidade, duração)
                                │
                                ▼
                    Decide resposta: direta, início
                    de triagem, pergunta adicional,
                    emergência ou fallback
                                │
                                ▼
                      Resposta em JSON → chat
```

O projeto adota uma implementação própria em Python (classificador de intenções, extrator de entidades e gerenciador de diálogo) em vez do IBM watsonx Assistant previsto originalmente no enunciado. A substituição foi autorizada pelo professor após uma falha recorrente e documentada no processo de cadastro do IBM Cloud (erro `REG-PAYGO-UPGRADE-...`). A implementação reproduz conceitualmente os mesmos componentes (intents, entities, dialog nodes). Justificativa completa em [`watson/README.md`](watson/README.md).

---

## 📁 Estrutura do repositório

```
cardioia-fase5-assistente-paciente/
├── backend/                 # API Flask, NLU, entidades e gerenciador de diálogo
│   ├── app.py
│   ├── dialog_manager.py
│   ├── entities.py
│   ├── nlu_engine.py
│   ├── requirements.txt
│   └── training_data.json
├── frontend/                # Interface web (HTML/CSS/JS puro)
│   └── index.html
├── docs/                     # Cópia da interface publicada via GitHub Pages
│   ├── index.html
│   └── relatorio_fluxo_conversacional.pdf
├── watson/                   # Justificativa da substituição do IBM watsonx Assistant
│   └── README.md
├── ir_alem/                  # Componentes extras (ver seção abaixo)
│   ├── ir_alem_1_extracao_clinica.ipynb
│   ├── resultados_extracao_clinica.json
│   ├── relatorio_ir_alem_1_extracao_clinica.pdf
│   ├── ir_alem_2_rpa_ia_dados.ipynb
│   └── relatorio_ir_alem_2_rpa_ia_dados.pdf
├── prints/                    # Capturas de tela do projeto
└── README.md
```

---

## ▶️ Como rodar o backend localmente

```bash
cd backend
pip install -r requirements.txt
python app.py
```

O servidor sobe em `http://localhost:5000`. Para testar a interface localmente, abra `frontend/index.html` e altere a URL da API no JavaScript de `https://cardioia-fase5-assistente-paciente.onrender.com` para `http://localhost:5000`.

Em produção, o backend é iniciado via Gunicorn (`gunicorn app:app`) no Render.

---

## 🧠 Como o assistente funciona

- **Reconhecimento de intenções:** classificador supervisionado (TF-IDF + Regressão Logística) treinado sobre 12 intenções e cerca de 70 frases de exemplo (`backend/training_data.json`).
- **Extração de entidades:** identifica intensidade (leve, moderada, forte, insuportável) e duração do sintoma a partir do texto livre, usando dicionários de palavras e expressões regulares.
- **Gerenciamento de diálogo:** máquina de estados por sessão, que conduz uma triagem em etapas (sintoma → intensidade → duração → resumo e recomendação).
- **Emergência:** se a intenção classificada for `emergencia`, ou se a intensidade relatada durante a triagem for `forte`/`insuportável`, o sistema interrompe o fluxo e orienta a ligar para o SAMU (192) ou procurar o pronto-socorro mais próximo.
- **Fallback progressivo:** mensagens não compreendidas (confiança abaixo de 0.18) pedem reformulação; após duas tentativas sem sucesso, o sistema recomenda diretamente falar com um profissional de saúde.

---

## 🚀 Ir Além

### Ir Além 1 — IA Generativa e Extração de Informações Clínicas
Uso do Gemini (IA Generativa) para interpretar textos clínicos em linguagem livre e extrair informações estruturadas em JSON (sintomas, sinais vitais, tabagismo, comorbidades, nível de urgência sugerido).
📓 Notebook: [`ir_alem/ir_alem_1_extracao_clinica.ipynb`](ir_alem/ir_alem_1_extracao_clinica.ipynb)
📄 Relatório: [`ir_alem/relatorio_ir_alem_1_extracao_clinica.pdf`](ir_alem/relatorio_ir_alem_1_extracao_clinica.pdf)

### Ir Além 2 — Automação Inteligente com RPA, IA e Dados Híbridos
Simulação de um robô (RPA) que lê periodicamente sinais vitais de pacientes (SQLite), aplica regras clínicas e um modelo de IA (`IsolationForest`) para detectar anomalias, e registra logs e alertas de forma rastreável em um banco não relacional (MongoDB Atlas).
📓 Notebook: [`ir_alem/ir_alem_2_rpa_ia_dados.ipynb`](ir_alem/ir_alem_2_rpa_ia_dados.ipynb)
📄 Relatório: [`ir_alem/relatorio_ir_alem_2_rpa_ia_dados.pdf`](ir_alem/relatorio_ir_alem_2_rpa_ia_dados.pdf)

---

## ⚠️ Limitações conhecidas

- Conjunto de treinamento pequeno (~70 frases); limiar de confiança baixo (0.18) por causa disso.
- Sessões de conversa ficam apenas em memória — são perdidas ao reiniciar o servidor e não são compartilhadas entre múltiplos workers do Gunicorn.
- Sem autenticação, rate limiting, testes automatizados ou observabilidade estruturada.
- Protótipo acadêmico — não deve ser tratado como dispositivo médico ou sistema clínico real.

---

## 👩‍💻 Autoria

Flávia Nunes Bocchino — FIAP, Inteligência Artificial, 2026.
