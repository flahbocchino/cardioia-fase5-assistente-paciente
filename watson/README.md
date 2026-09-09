Sobre esta pasta
O enunciado original da Fase 5 pedia o uso do IBM watsonx Assistant como
plataforma base do assistente conversacional.
Durante a tentativa de criação da conta no IBM Cloud, o processo de
cadastro apresentou uma falha recorrente e documentada publicamente na
comunidade de usuários da IBM (erro `REG-PAYGO-UPGRADE-...`, referente à
autorização do cartão de crédito usado apenas para verificação de
identidade, sem geração de cobrança). Após múltiplas tentativas — incluindo
troca de cartão e verificação de rede — o problema persistiu.
Diante disso, o professor da disciplina foi consultado e autorizou o uso
de uma alternativa técnica, mantendo o mesmo objetivo pedagógico da
atividade: um assistente conversacional baseado nos conceitos de NLP
(intents, entities e dialog nodes).
Solução adotada
Em vez do watsonx Assistant, foi desenvolvido um motor de NLU e diálogo
próprio, em Python, com a mesma lógica conceitual:
Conceito do Watson Assistant	Implementação equivalente
Intents	`backend/training_data.json` (frases de exemplo por intenção) + `backend/nlu_engine.py` (classificador TF-IDF + Regressão Logística)
Entities	`backend/entities.py` (extração de intensidade, duração e confirmação sim/não)
Dialog nodes / contexto	`backend/dialog_manager.py` (máquina de estados por sessão)
API do assistente	`backend/app.py` (API Flask que expõe o motor conversacional)
Essa abordagem preserva o objetivo da atividade — aplicar processamento de
linguagem natural para interpretar mensagens do paciente e conduzir um
fluxo de atendimento inicial em saúde — sem depender de uma plataforma
externa que se mostrou inacessível por motivos fora do nosso controle.
Os arquivos do backend estão na pasta `../backend`.
