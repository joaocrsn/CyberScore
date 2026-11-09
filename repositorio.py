"""Camada de dados do CyberScore: a "API" interna entre a tela (app.py) e o banco.

Regras de isolamento, garantidas aqui e não na tela:
- A tela nunca monta SQL nem acessa o banco direto: só chama os métodos desta classe.
- O código de acesso do usuário nunca é gravado: só um HMAC-SHA256 dele (com "pimenta" secreta).
- Todo dado pessoal só é lido ou apagado mediante o código, sempre filtrando pelo hash dele.
- Todo diagnóstico é gravado para estatísticas, mas sem identificação: só quem escolhe o histórico
  tem o hash do código ligado aos resultados.
- O Painel de Administração (restrito por senha) recebe os registros sem o hash: quem tem histórico
  aparece só com um apelido sequencial (H1, H2...).
- estatisticas_pesquisa() devolve só médias e esconde grupos com menos de TAMANHO_MINIMO_GRUPO
  pessoas, para qualquer uso público dos resultados.

Funciona com SQLite (no seu PC) e com Postgres (Supabase, em produção): basta trocar a URL.
"""
import hashlib
import hmac
import json
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import (
    Boolean, Column, DateTime, Integer, MetaData, String, Table, Text, create_engine, delete, func, insert, select,
)

ALFABETO_CODIGO = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"  # sem 0/O, 1/I/L para não confundir na digitação
TAMANHO_CODIGO = 16  # 31^16 ≈ 2^79 combinações: inviável de adivinhar
TAMANHO_MINIMO_GRUPO = 3
FUSO_BRASILIA = timezone(timedelta(hours=-3))

metadados = MetaData()

avaliacoes = Table(
    "avaliacoes", metadados,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("usuario_hash", String(64), index=True),  # vazio = resultado anônimo, só para pesquisa
    Column("pesquisa", Boolean, nullable=False, default=True),  # entra nas estatísticas (hoje, sempre)
    Column("setor", String(40)),  # opcional
    Column("area", String(60)),  # opcional
    Column("score", Integer, nullable=False),
    Column("versao", Integer, nullable=False),
    Column("respostas", Text, nullable=False),  # JSON com índice da pergunta, opção e pontos
    Column("criado_em", DateTime(timezone=True), nullable=False),
)


def gerar_codigo():
    bruto = "".join(secrets.choice(ALFABETO_CODIGO) for _ in range(TAMANHO_CODIGO))
    return "-".join(bruto[i:i + 4] for i in range(0, TAMANHO_CODIGO, 4))


def normalizar_codigo(texto):
    """Aceita o código com ou sem hífens/espaços e em minúsculas. Devolve None se for inválido."""
    limpo = "".join(texto.upper().split()).replace("-", "")
    if len(limpo) != TAMANHO_CODIGO or any(c not in ALFABETO_CODIGO for c in limpo):
        return None
    return "-".join(limpo[i:i + 4] for i in range(0, TAMANHO_CODIGO, 4))


class Repositorio:
    def __init__(self, url_banco, pimenta):
        if not pimenta:
            raise ValueError("Defina PIMENTA_CODIGO no secrets.toml (uma frase longa e secreta).")
        self._pimenta = pimenta.encode()
        self._engine = create_engine(url_banco, pool_pre_ping=True)
        metadados.create_all(self._engine)

    def _hash(self, codigo):
        codigo = normalizar_codigo(codigo or "")
        if codigo is None:
            raise ValueError("Código de acesso inválido.")
        return hmac.new(self._pimenta, codigo.encode(), hashlib.sha256).hexdigest()

    # ---------- Escrita ----------

    def salvar(self, codigo, setor, area, score, versao, respostas):
        """Grava todo resultado para as estatísticas anônimas; com código, ele também entra no histórico."""
        with self._engine.begin() as conexao:
            resultado = conexao.execute(insert(avaliacoes).values(
                usuario_hash=self._hash(codigo) if codigo else None,
                pesquisa=True, setor=setor, area=area, score=score, versao=versao,
                respostas=json.dumps(respostas, ensure_ascii=False),
                criado_em=datetime.now(timezone.utc),
            ))
            return resultado.inserted_primary_key[0]

    # ---------- Dados do próprio usuário (exigem o código) ----------

    def codigo_tem_historico(self, codigo):
        with self._engine.connect() as conexao:
            consulta = select(func.count()).select_from(avaliacoes).where(avaliacoes.c.usuario_hash == self._hash(codigo))
            return conexao.execute(consulta).scalar_one() > 0

    def historico(self, codigo):
        colunas = [avaliacoes.c[n] for n in ("id", "score", "versao", "setor", "area", "pesquisa", "respostas", "criado_em")]
        consulta = (select(*colunas).where(avaliacoes.c.usuario_hash == self._hash(codigo))
                    .order_by(avaliacoes.c.criado_em.desc()))
        with self._engine.connect() as conexao:
            linhas = [dict(linha._mapping) for linha in conexao.execute(consulta)]
        for linha in linhas:
            linha["respostas"] = json.loads(linha["respostas"])
            data = linha["criado_em"]
            if data.tzinfo is None:  # SQLite não guarda fuso
                data = data.replace(tzinfo=timezone.utc)
            linha["criado_em"] = data.astimezone(FUSO_BRASILIA)
        return linhas

    def apagar_avaliacao(self, codigo, id_avaliacao):
        """Apaga uma avaliação; o filtro pelo hash impede apagar a de outra pessoa mesmo sabendo o id."""
        with self._engine.begin() as conexao:
            resultado = conexao.execute(delete(avaliacoes).where(
                avaliacoes.c.id == id_avaliacao, avaliacoes.c.usuario_hash == self._hash(codigo)
            ))
            return resultado.rowcount == 1

    def apagar_historico(self, codigo):
        with self._engine.begin() as conexao:
            return conexao.execute(delete(avaliacoes).where(avaliacoes.c.usuario_hash == self._hash(codigo))).rowcount

    # ---------- Pesquisa (só agregados, nunca linhas individuais) ----------

    def estatisticas_pesquisa(self, versao):
        base = (avaliacoes.c.pesquisa.is_(True), avaliacoes.c.versao == versao)
        with self._engine.connect() as conexao:
            total, media = conexao.execute(select(func.count(), func.avg(avaliacoes.c.score)).where(*base)).one()

            def por(coluna):
                consulta = (select(coluna, func.count(), func.avg(avaliacoes.c.score))
                            .where(*base, coluna.is_not(None)).group_by(coluna))
                grupos = [{"grupo": g, "pessoas": n, "media": float(m)} for g, n, m in conexao.execute(consulta)]
                return [g for g in grupos if g["pessoas"] >= TAMANHO_MINIMO_GRUPO]

            return {
                "total": total,
                "media": float(media) if media is not None else None,
                "por_setor": por(avaliacoes.c.setor),
                "por_area": por(avaliacoes.c.area),
            }

    # ---------- Administração (Painel de Administração, protegido por senha) ----------

    def registros(self):
        """Todos os diagnósticos, um por linha, do mais antigo ao mais recente.

        Nunca devolve o hash do código: quem guardou histórico recebe só um apelido sequencial
        (H1, H2...), que permite ver avaliações da mesma pessoa sem expor nada que a identifique.
        """
        consulta = select(
            avaliacoes.c.id, avaliacoes.c.usuario_hash, avaliacoes.c.setor, avaliacoes.c.area,
            avaliacoes.c.score, avaliacoes.c.versao, avaliacoes.c.respostas, avaliacoes.c.criado_em,
        ).order_by(avaliacoes.c.criado_em, avaliacoes.c.id)
        with self._engine.connect() as conexao:
            linhas = [dict(linha._mapping) for linha in conexao.execute(consulta)]
        apelidos = {}
        for linha in linhas:
            usuario = linha.pop("usuario_hash")
            if usuario:
                apelidos.setdefault(usuario, f"H{len(apelidos) + 1}")
            linha["historico"] = apelidos.get(usuario)
            linha["respostas"] = json.loads(linha["respostas"])
            data = linha["criado_em"]
            if data.tzinfo is None:
                data = data.replace(tzinfo=timezone.utc)
            linha["criado_em"] = data.astimezone(FUSO_BRASILIA)
        return linhas

    def apagar_tudo(self):
        with self._engine.begin() as conexao:
            return conexao.execute(delete(avaliacoes)).rowcount
