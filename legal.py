"""Textos de Política de Privacidade, Termos de Uso e Cookies do CyberScore.

ANTES DE PUBLICAR: troque EMAIL_CONTATO por um e-mail pessoal seu (não use o da empresa) e
confira as datas. Estes textos são um modelo para projeto acadêmico, não substituem
a revisão por um profissional de Direito.
"""

CONTROLADOR = "João Victor Bezerra Cursino"
EMAIL_CONTATO = "joao.cursino@undf.edu.br"
DATA_ATUALIZACAO = "09/11/2026"
FIM_DO_PROJETO = "31/12/2027"

AVISO_COOKIES = (
    "🍪 **Cookies:** este site usa apenas cookies técnicos, necessários para ele funcionar com segurança. "
    "Não usamos cookies de publicidade nem de rastreamento. Detalhes na Política de Cookies."
)
AVISO_COOKIES_HTML = (
    '<span aria-hidden="true">🍪</span><span><b>Cookies:</b> este site usa apenas cookies técnicos, '
    "necessários para ele funcionar com segurança. Não usamos cookies de publicidade nem de rastreamento.</span>"
)

RESUMO_PRIVACIDADE = f"""
- **Não pedimos** nome, e-mail, CPF nem telefone.
- **Todas as respostas são guardadas de forma anônima** para estatísticas e para a pesquisa acadêmica
  do projeto, sem nada que identifique você.
- Se você escolher **guardar no histórico**, recebe um código anônimo para rever os próprios resultados.
- O código de acesso não é armazenado: guardamos apenas uma versão embaralhada (hash) dele.
- Você pode ver e apagar seu histórico a qualquer momento em **Meu Histórico**.
- Os relatos da **Consultoria** são enviados a um serviço de IA externo (Groq, nos EUA) e não são guardados por nós.
- Responsável: {CONTROLADOR}, projeto acadêmico da UnDF. Contato: {EMAIL_CONTATO}.
"""

POLITICA_PRIVACIDADE = f"""
### 1. Quem é o responsável pelos seus dados
O CyberScore é um projeto acadêmico, sem fins lucrativos, desenvolvido por **{CONTROLADOR}**,
estudante do curso de Gestão da Tecnologia da Informação da Universidade do Distrito Federal (UnDF),
que atua como **controlador** dos dados, nos termos da Lei Geral de Proteção de Dados (Lei nº 13.709/2018, LGPD).

Contato para qualquer assunto sobre seus dados: **{EMAIL_CONTATO}**.

### 2. Quais dados tratamos
Coletamos **apenas o necessário** para cada funcionalidade:

| Funcionalidade | Dados | Quando |
|---|---|---|
| Diagnóstico de Risco e estatísticas | Respostas às perguntas, score e data, **sem nenhum identificador** | Sempre que você conclui um diagnóstico |
| Perfil (opcional) | Setor de atuação e área | Só se você preencher |
| Meu Histórico (opcional) | Os mesmos resultados, ligados a um **hash** do seu código de acesso | Só se você escolher guardar no histórico |
| Consultoria de Incidentes | O texto que você digitar | Enviado à IA no momento da análise; **não é guardado por nós** |

**Não coletamos** nome, e-mail, CPF, telefone, endereço, localização nem dados sensíveis
(como saúde, religião ou biometria). **Não peça nem informe** esse tipo de dado nos campos de texto.

O código de acesso funciona como uma senha: **nós não o armazenamos**. Guardamos apenas um
resumo criptográfico (HMAC-SHA256) que não permite descobrir o código original. Por isso,
se você perder o código, não conseguimos recuperá-lo.

### 3. Para que usamos e com qual base legal
Antes de usar qualquer parte do site, você lê um resumo desta política na **tela de acesso** e
declara que aceita estes termos e que tem 18 anos ou mais. Você pode reler os textos completos a qualquer
momento pelo botão **Privacidade e Termos**, no menu lateral.

- **Guardar e mostrar seu histórico**: com base no seu **consentimento** (art. 7º, I, da LGPD),
  dado ao escolher "Guardar no meu histórico".
- **Estatísticas e pesquisa acadêmica**: os resultados sem histórico são guardados **sem nenhum
  identificador** (não pedimos nome, e-mail, CPF ou telefone, e eles não são ligados a código nenhum),
  o que os torna dados anonimizados, fora do alcance da LGPD (art. 12). Mesmo assim, você é informado
  antes de começar. Os resultados aparecem apenas em médias, e grupos com menos de 3 pessoas ficam ocultos.
  Se você também guardar no histórico, esse uso estatístico ocorre com base no seu consentimento (art. 7º, I).
- **Análise da Consultoria por IA**: com base no seu **consentimento**, dado ao clicar em "Analisar Ameaça"
  depois de ler o aviso exibido na página.

Não usamos seus dados para publicidade, criação de perfil comercial ou decisões automatizadas
que produzam efeitos jurídicos sobre você. O score é apenas educativo.

### 4. Com quem compartilhamos
Usamos serviços de terceiros, que tratam dados em nosso nome (operadores):

- **Streamlit Community Cloud (Snowflake Inc., EUA)**: hospedagem do site.
- **Supabase (EUA, com servidor na região escolhida pelo projeto)**: armazenamento do banco de dados.
- **Groq Inc. (EUA)**: análise dos relatos da Consultoria por inteligência artificial.
- **Google Fonts (Google LLC, EUA)**: fontes do site; o navegador informa ao Google o seu endereço IP ao carregá-las.

Alguns desses serviços ficam fora do Brasil. Essa **transferência internacional** ocorre com base
no seu consentimento específico (art. 33, VIII, da LGPD) e nas garantias contratuais oferecidas por esses
fornecedores. **Não vendemos nem cedemos** seus dados a ninguém.

### 5. Por quanto tempo guardamos
- **Histórico**: até você apagá-lo em "Meu Histórico" ou até o fim do projeto (previsto para {FIM_DO_PROJETO}),
  o que ocorrer primeiro.
- **Dados da pesquisa**: até o fim do projeto. Depois disso, mantemos apenas estatísticas agregadas,
  que não identificam ninguém.
- **Relatos da Consultoria**: não são guardados por nós. O fornecedor da IA pode retê-los por um período
  limitado, conforme a política dele.

### 6. Seus direitos
Pelo art. 18 da LGPD, você pode, a qualquer momento: confirmar se tratamos seus dados, acessá-los,
corrigi-los, pedir a anonimização ou eliminação, pedir a portabilidade, saber com quem compartilhamos
e **revogar o consentimento**.

- **Ver e apagar** seu histórico: diretamente em **Meu Histórico**, com o seu código.
- **Outros pedidos**: escreva para **{EMAIL_CONTATO}**. Respondemos em até 15 dias.

Resultados guardados **sem código** são anônimos desde a origem: como não há como saber de quem são,
não é possível localizá-los para exclusão individual. Se quiser poder apagar seus resultados depois,
escolha **guardar no histórico** antes de começar. Ao apagar o histórico, os resultados saem também
das estatísticas.

Você também pode apresentar reclamação à **Autoridade Nacional de Proteção de Dados (ANPD)**.

### 7. Segurança
Adotamos medidas como conexão criptografada (HTTPS), armazenamento do código apenas em forma de hash,
isolamento por código (cada pessoa só acessa os próprios dados), coleta mínima e exibição apenas de
médias no painel de administração, restrito por senha. Nenhum sistema é 100% seguro; em caso de incidente que possa trazer
risco relevante, comunicaremos os usuários e a ANPD, conforme o art. 48 da LGPD.

### 8. Crianças e adolescentes
O CyberScore é destinado a **maiores de 18 anos**. Não coletamos conscientemente dados de menores de idade.

### 9. Alterações
Podemos atualizar esta política. A data da última atualização fica sempre no topo desta página.
"""

TERMOS_USO = f"""
### 1. Sobre o serviço
O CyberScore é uma ferramenta **educativa e gratuita**, parte de um projeto acadêmico da UnDF,
que ajuda você a identificar hábitos digitais de risco e a reagir a incidentes de segurança.
Ao usar o site, você concorda com estes termos.

### 2. Não é consultoria profissional
O score, as dicas e as respostas da IA são **orientações gerais**, não substituem a ajuda de
profissionais de segurança, do seu banco, da polícia ou de um advogado. Em caso de fraude,
procure sempre os **canais oficiais**.

### 3. Respostas geradas por inteligência artificial
As respostas da Consultoria são geradas automaticamente e **podem conter erros**. Confira as
orientações importantes nas cartilhas oficiais indicadas e com as instituições envolvidas.

### 4. O que você não deve fazer
- Inserir dados pessoais seus ou de terceiros (senhas, CPF, cartões, nomes, documentos).
- Tentar acessar dados de outras pessoas, adivinhar códigos de acesso ou atacar o sistema.
- Usar robôs ou automações para enviar respostas em massa.
- Usar o site para qualquer finalidade ilegal.

### 5. Seu código de acesso
O código é a única forma de acessar seu histórico. **Guarde-o com cuidado e não compartilhe.**
Quem tiver o código poderá ver e apagar os resultados associados a ele. Não temos como recuperar
códigos perdidos.

### 6. Disponibilidade
O site é oferecido "como está", em infraestrutura gratuita, e pode ficar fora do ar, ser alterado
ou encerrado ao fim do projeto, sem aviso prévio.

### 7. Links externos
Indicamos cartilhas e sites de terceiros (CERT.br, Governo Federal, Febraban e outros).
Não somos responsáveis pelo conteúdo nem pelas práticas de privacidade desses sites.

### 8. Limitação de responsabilidade
Na máxima extensão permitida pela lei, o projeto não se responsabiliza por decisões tomadas
com base nas orientações do site nem por prejuízos causados por terceiros.

### 9. Lei aplicável
Estes termos seguem a legislação brasileira. Fica eleito o foro de Brasília/DF,
ressalvado o direito do consumidor de propor ação no seu domicílio.

Dúvidas: **{EMAIL_CONTATO}**.
"""

POLITICA_COOKIES = """
### O que são cookies
Cookies são pequenos arquivos que o site guarda no seu navegador.

### Quais usamos
Usamos **apenas cookies estritamente necessários**, criados pela plataforma Streamlit para o site funcionar
com segurança (por exemplo, proteção contra falsificação de requisições, o cookie `_streamlit_xsrf`).
Eles não identificam você e não servem para publicidade. Por serem essenciais, dispensam consentimento.

### O que não usamos
- Cookies de publicidade ou de redes sociais.
- Ferramentas de análise de comportamento (como Google Analytics). A coleta de estatísticas de uso
  do próprio Streamlit está **desativada** neste site.

### Observações
- O seu código de acesso fica **só na memória desta aba**: ao fechar o site, você precisará digitá-lo de novo.
- Se você estiver conectado a uma conta em streamlit.io, a própria plataforma pode usar cookies dela,
  sob a política de privacidade da Snowflake.
- As fontes do site vêm do Google Fonts, que não grava cookies, mas recebe o seu endereço IP.

Você pode apagar ou bloquear cookies nas configurações do navegador; o site pode deixar de funcionar
corretamente se os cookies essenciais forem bloqueados.
"""
