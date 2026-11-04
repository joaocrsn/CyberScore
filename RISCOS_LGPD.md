# CyberScore: riscos jurídicos e de privacidade

Levantamento feito em 04/11/2026 para o projeto acadêmico. **Não é parecer jurídico**: revise com o orientador
e, se possível, com alguém da área de Direito da UDF antes de abrir o app ao público.

Legenda de gravidade: 🔴 alta · 🟠 média · 🟡 baixa

| # | Risco | Gravidade | O que já foi feito | O que ainda depende de você |
|---|---|---|---|---|
| 1 | **Pesquisa com seres humanos sem aprovação ética.** Coletar respostas de pessoas para análise acadêmica pode exigir submissão ao Comitê de Ética em Pesquisa (CEP/Plataforma Brasil), conforme a Resolução CNS nº 510/2016. | 🔴 | Todas as respostas são guardadas de forma anônima, com aviso claro e aceite antes de começar; só médias no painel. | **Perguntar ao orientador** se o projeto precisa passar pelo CEP e se o aviso atual basta como Termo de Consentimento (TCLE), antes de divulgar o link para coleta real. Até lá, use só para demonstração. |
| 2 | **Usuário digitar dados pessoais (dele ou de terceiros) na Consultoria**, que são enviados à IA nos EUA. | 🔴 | Aviso destacado antes do campo; bloqueio automático de CPF, cartão, e-mail e telefone; o relato não é gravado no banco. | Nada obrigatório. O filtro não pega nomes ou endereços: o aviso continua essencial. |
| 3 | **Transferência internacional de dados** (Groq, Streamlit/Snowflake e Supabase nos EUA; Google Fonts). | 🟠 | Informada na política com base no consentimento específico (art. 33, VIII); banco recomendado na região São Paulo. | Escolher **São Paulo** ao criar o Supabase. Opcional: hospedar as fontes no próprio app para eliminar o Google Fonts. |
| 4 | **Controlador pessoa física.** Como estudante, você responde pessoalmente pelo tratamento dos dados. | 🟠 | Política identifica o controlador e o caráter acadêmico, sem fins lucrativos. | Preencher um **e-mail de contato real** em `legal.py` e responder pedidos em até 15 dias. Agentes de pequeno porte podem dispensar o encarregado (Resolução CD/ANPD nº 2/2022), mas o canal de contato é obrigatório. |
| 5 | **Dados pseudonimizados continuam sendo dados pessoais.** O hash do código liga várias avaliações à mesma pessoa. | 🟠 | Código nunca é gravado (HMAC com chave secreta); nenhum dado de contato é pedido; histórico só é criado por escolha do usuário. | Guardar a `PIMENTA_CODIGO` em segredo e nunca publicá-la. |
| 6 | **Anonimização contestável.** Todo diagnóstico é guardado sem identificador e tratado como dado anônimo (art. 12), mas setor + área + data/hora, em amostras pequenas, podem permitir reconhecer alguém. Se isso acontecer, o dado volta a ser pessoal e exigiria uma base legal. | 🟠 | Nenhum dado de contato é pedido; setor e área são opcionais; aviso e aceite antes de começar; o painel esconde grupos com menos de 3 pessoas e não mostra respostas individuais. | Não exportar nem publicar respostas individuais no artigo; usar só agregados. Ao analisar no Supabase, não cruzar com informações externas sobre quem respondeu. |
| 7 | **Acesso administrativo aos dados brutos** (senha de admin, painel do Supabase). | 🟠 | Área admin só apaga dados (não exibe); comparação de senha resistente a ataques de tempo; sem senha configurada, a área fica desativada. | Usar senhas fortes e únicas no Supabase, GitHub e `SENHA_ADMIN`, com verificação em duas etapas nessas contas. |
| 8 | **Retenção além do necessário.** | 🟡 | Política define prazo: até o usuário apagar ou até o fim do projeto. | **Apagar o banco** (ou o projeto no Supabase) na data de `FIM_DO_PROJETO`. Coloque um lembrete na agenda. |
| 9 | **Menores de idade** usando o app. | 🟡 | Termos e aceite exigem 18 anos ou mais; não há coleta de dados de identificação. | Nada obrigatório: não há verificação de idade (autodeclaração). |
| 10 | **Orientação errada gerada por IA** levar a prejuízo. | 🟡 | Termos deixam claro o caráter educativo; protocolos fixos e cartilhas oficiais aparecem antes da IA; prompt proíbe links e marcas. | Nada obrigatório. |
| 11 | **Cookies da plataforma** não previstos na política. | 🟡 | Estatísticas de uso do Streamlit desativadas (`gatherUsageStats = false`); só cookies técnicos declarados. | Conferir os cookies reais depois do deploy (checklist no `DEPLOY.md`) e ajustar a aba Cookies se aparecer algo novo. |
| 12 | **Incidente de segurança** (vazamento do banco ou das chaves). | 🟡 | Coleta mínima reduz o impacto; chaves fora do código e fora do GitHub (`.gitignore`). | Se acontecer: trocar todas as chaves, avaliar o risco e, se relevante, comunicar a ANPD e os usuários (art. 48 da LGPD; prazo de 3 dias úteis pela Resolução CD/ANPD nº 15/2024). |
| 13 | **Uso de nomes de instituições** (CERT.br, Febraban, Governo Federal). | 🟡 | Aparecem só como links para materiais públicos, sem sugerir parceria. | Não usar logotipos dessas instituições no app. |
| 14 | **Adivinhação de códigos de acesso.** | 🟡 | Código com ~79 bits de aleatoriedade (inviável de adivinhar) e limite de 5 tentativas por sessão. | Nada obrigatório. |

## O que mudou no app por causa da LGPD

- Todo diagnóstico é gravado **de forma anônima** para estatísticas, com aviso claro antes de começar;
  só o **histórico** (opcional) liga resultados a um código.
- Setor e área viraram **opcionais**; nenhum dado de identificação é pedido.
- Aceite obrigatório da Política de Privacidade e dos Termos, com declaração de 18+.
- Página **Privacidade e Termos** com política completa, termos e política de cookies.
- Aviso de cookies na primeira visita; estatísticas do Streamlit desativadas.
- **Meu Histórico**: o titular vê e apaga os próprios dados sem precisar pedir a ninguém (art. 18).
- Alerta permanente no menu lateral para não digitar dados sensíveis; bloqueio automático na Consultoria.
