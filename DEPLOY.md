# Como colocar o CyberScore no ar

Caminho escolhido: **Streamlit Community Cloud** (site) + **Supabase** (banco), ambos gratuitos.
O endereço final será algo como `https://cyberscore-udf.streamlit.app`.

> Você cria as contas e digita as senhas. Nunca envie senhas ou chaves por chat, e-mail ou print.

---

## 0. Antes de tudo (5 min)

1. Abra `legal.py` e troque `EMAIL_CONTATO = "[preencha-seu-email-pessoal]"` por um **e-mail pessoal**
   (não use o da empresa). É o canal oficial de privacidade exigido pela LGPD.
2. Confira `FIM_DO_PROJETO` (data em que os dados serão apagados) e ajuste se precisar.

## 1. Banco de dados no Supabase (10 min)

1. Entre em **supabase.com** → *Start your project* → entre com o GitHub (crie a conta do GitHub antes, passo 2.1).
2. *New project*:
   - **Name:** `cyberscore`
   - **Database Password:** clique em *Generate a password* e **guarde num gerenciador de senhas**.
   - **Region:** `South America (São Paulo)`: os dados ficam no Brasil (bom para a LGPD).
3. Com o projeto criado, clique em **Connect** (topo da página) → aba **Connection String** →
   **Type: URI** → **Method: Session pooler**. Copie o endereço. Ele é parecido com:
   `postgresql://postgres.abcd:[YOUR-PASSWORD]@aws-0-sa-east-1.pooler.supabase.com:5432/postgres`
4. Monte a sua `DATABASE_URL`:
   - troque `postgresql://` por `postgresql+psycopg2://`
   - troque `[YOUR-PASSWORD]` pela senha do passo 2 (se a senha tiver `@`, `#` ou `/`, gere outra sem esses símbolos).

As tabelas são criadas sozinhas na primeira vez que o app abrir.

> No plano gratuito, o Supabase **pausa o projeto após 7 dias sem uso**. Se o app mostrar erro de banco,
> entre no painel do Supabase e clique em *Restore project*.

## 2. Código no GitHub (10 min)

1. Crie uma conta em **github.com** (pode usar e-mail pessoal).
2. Clique em **+** → *New repository* → nome `cyberscore` → marque **Private** → *Create repository*.
3. Na página do repositório, clique em *uploading an existing file* e arraste **somente** estes arquivos
   e a pasta `.streamlit` (que só pode conter os arquivos abaixo):
   - `app.py`, `repositorio.py`, `legal.py`, `requirements.txt`, `.gitignore`
   - `.streamlit/config.toml` e `.streamlit/secrets.toml.example`
4. **NÃO envie** `.streamlit/secrets.toml` (tem sua chave e senhas) nem `dados_seguranca.db`.
   Se enviar por engano: apague o arquivo no GitHub **e troque todas as chaves e senhas** que estavam nele.
5. *Commit changes*.

## 3. Publicar no Streamlit Community Cloud (10 min)

1. Entre em **share.streamlit.io** → *Continue with GitHub* → autorize o acesso ao repositório.
2. *Create app* → *Deploy a public app from GitHub*:
   - **Repository:** `seu-usuario/cyberscore` · **Branch:** `main` · **Main file path:** `app.py`
   - **App URL:** escolha um nome, ex.: `cyberscore-udf`
3. Abra **Advanced settings**:
   - **Python version:** 3.13
   - **Secrets:** cole o conteúdo abaixo, preenchido:
     ```toml
     GROQ_API_KEY = "gsk_..."
     SENHA_ADMIN = "uma-senha-forte-diferente-da-local"
     PIMENTA_CODIGO = "copie a mesma do seu secrets.toml local ou gere uma nova"
     DATABASE_URL = "postgresql+psycopg2://postgres.abcd:SENHA@aws-0-sa-east-1.pooler.supabase.com:5432/postgres"
     ```
     Para gerar uma `PIMENTA_CODIGO` nova: `python -c "import secrets; print(secrets.token_urlsafe(32))"`.
     **Depois de publicar, nunca mais troque a PIMENTA_CODIGO**: todos os códigos de histórico deixariam de funcionar.
4. *Deploy*. A primeira vez leva uns 3 minutos.

> O app "dorme" depois de algumas horas sem visitas. Quem abrir verá um botão para acordá-lo (leva ~1 minuto).
> Antes da apresentação, abra o link uns minutos antes.

## 4. Conferir depois de publicar

- [ ] A **tela de acesso** aparece primeiro, sem menu, e só libera o site depois das duas caixas marcadas.
- [ ] Diagnóstico com **Guardar no histórico** mostra o código; **Meu Histórico** abre com ele.
- [ ] Em outra aba anônima, um código inventado **não** abre histórico nenhum.
- [ ] **Consultoria** responde com a IA; um relato com CPF é bloqueado.
- [ ] O endereço do site com `?admin` no final abre o **Painel de Administração**, que pede a senha
      e mostra os registros, os dashboards e os botões de exportação (Excel, CSV e HTML).
- [ ] O botão **Privacidade e Termos** do menu mostra o seu e-mail de contato.
- [ ] No navegador: F12 → *Application* → *Cookies*: anote os cookies que aparecem e confira se batem
      com a aba **Cookies** da política (a plataforma pode adicionar algum próprio).

Para atualizar o app depois: envie o arquivo alterado para o GitHub (*Add file → Upload files*).
O Streamlit Cloud atualiza sozinho em ~1 minuto.

---

## 5. Domínio próprio (quando quiser)

O Streamlit Community Cloud gratuito **não aceita domínio próprio**. Quando tiver um domínio, há dois caminhos:

**A) Redirecionar (mais simples, grátis além do domínio)**
1. Registre o domínio no **registro.br** (ex.: `cyberscore.com.br`, cerca de R$ 40/ano). Precisa de CPF e
   é feito por você no site.
2. Crie uma conta gratuita na **Cloudflare**, adicione o domínio e troque os servidores DNS no Registro.br
   pelos que a Cloudflare indicar.
3. Na Cloudflare: *Rules → Redirect Rules* → redirecionar `cyberscore.com.br/*` para
   `https://cyberscore-udf.streamlit.app`. Quem digitar o domínio cai no app (a barra de endereço mostrará
   o endereço do Streamlit).

**B) Domínio de verdade no endereço (mais trabalho)**
Mudar a hospedagem para o **Render** (aceita domínio próprio no plano gratuito), mantendo o Supabase.
O código já está pronto para isso; quando chegar a hora, peça e eu preparo os arquivos e o passo a passo.
