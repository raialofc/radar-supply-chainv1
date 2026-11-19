#!/usr/bin/env python3
"""
Radar KRL de Supply Chain (demo) - coleta de indicadores do Banco Central.

Atualiza no data.json:
  - fx.usd, fx.eur (PTAX venda, ~90 dias úteis)   -> SGS 1 e 21619
  - fx.usd_mensal (13 meses + mês corrente)       -> SGS 3698
  - indicadores (Selic, IPCA mês, IPCA 12m, IGP-M) -> SGS 432, 433, 13522, 189
  - status de Dólar e Euro (regra: >5% em 30 dias = alerta; >2% = atenção)
Não mexe em notícias, preços de commodities nem nos demais status.

Uso:  python3 coletar_indicadores.py caminho/para/data.json
Agendar em dias úteis, antes das 8h (Agendador de Tarefas do Windows ou cron).
Requer Python 3.9+ e acesso HTTPS de saída a api.bcb.gov.br. Sem dependências externas.

Em caso de falha numa série, mantém o valor anterior e sai com código 1 (para o log/alerta).
"""
import json
import sys
import urllib.request
from datetime import date, datetime, timedelta

BASE = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{}/dados"
UA = {"User-Agent": "Radar-KRL-demo/1.0"}


def sgs(codigo, inicio=None, fim=None, ultimos=None):
    if ultimos:
        url = f"{BASE.format(codigo)}/ultimos/{ultimos}?formato=json"
    else:
        url = f"{BASE.format(codigo)}?formato=json&dataInicial={inicio:%d/%m/%Y}&dataFinal={fim:%d/%m/%Y}"
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        dados = json.load(r)
    return [[d["data"], float(d["valor"])] for d in dados]


def br(v, casas=2):
    return f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def var_30d(serie):
    """Variação % do último valor contra o valor de ~30 dias corridos antes."""
    ult_data = datetime.strptime(serie[-1][0], "%d/%m/%Y")
    alvo = ult_data - timedelta(days=30)
    base = serie[0]
    for d, v in serie:
        if datetime.strptime(d, "%d/%m/%Y") <= alvo:
            base = [d, v]
    return (serie[-1][1] / base[1] - 1) * 100, base[0]


def nivel(var):
    if var > 5:
        return "alerta", "Alerta"
    if var > 2:
        return "atencao", "Atenção"
    return "normal", "Normal"


def main(caminho):
    with open(caminho, encoding="utf-8") as f:
        d = json.load(f)
    hoje = date.today()
    falhas = []

    # Câmbio diário
    for chave, cod in (("usd", 1), ("eur", 21619)):
        try:
            s = sgs(cod, hoje - timedelta(days=130), hoje)
            d["fx"][chave] = s[-90:]
        except Exception as e:  # mantém o anterior
            falhas.append(f"SGS {cod}: {e}")

    # Média mensal do dólar + mês corrente
    try:
        m = sgs(3698, ultimos=13)
        mensal = [[x[0][3:], round(x[1], 4)] for x in m]
        mes = hoje.strftime("%m/%Y")
        do_mes = [v for dt, v in d["fx"]["usd"] if dt[3:] == mes]
        if do_mes and mensal[-1][0] != mes:
            mensal.append([mes + "*", round(sum(do_mes) / len(do_mes), 4)])
        d["fx"]["usd_mensal"] = mensal
    except Exception as e:
        falhas.append(f"SGS 3698: {e}")

    # Indicadores
    mapa = {
        "Selic (meta)": (432, lambda v: f"{br(v)}% a.a."),
        "IPCA 12 meses": (13522, lambda v: f"{br(v)}%"),
        "IPCA mês": (433, lambda v: f"{br(v)}%"),
        "IGP-M mês": (189, lambda v: f"{br(v)}%"),
    }
    for ind in d.get("indicadores", []):
        if ind["nome"] in mapa:
            cod, fmt = mapa[ind["nome"]]
            try:
                dt, v = sgs(cod, ultimos=1)[-1]
                ind["valor"] = fmt(v)
                if cod != 432:  # Selic: referência é a reunião do Copom, mantida manualmente
                    ind["ref"] = dt[3:]
            except Exception as e:
                falhas.append(f"SGS {cod}: {e}")

    # Status de câmbio
    for st in d.get("status", []):
        chave = "usd" if st["cat"].startswith("Dólar") else "eur" if st["cat"].startswith("Euro") else None
        if not chave:
            continue
        s = d["fx"][chave]
        var, desde = var_30d(s)
        st["valor"] = f"R$ {br(s[-1][1], 4)}"
        st["nivel"], st["rotulo"] = nivel(var)
        st["nota"] = f"{'+' if var > 0 else ''}{br(var, 1)}% em 30 dias (desde {desde[:5]})"
        st["data"] = s[-1][0]

    # Manchete e resumo derivados só dos dados coletados (as notícias da demo são estáticas)
    usd = d["fx"]["usd"]
    var_usd, desde = var_30d(usd)
    sinal = "sobe" if var_usd > 0 else "cai"
    d["manchete"] = f"Dólar {sinal} {br(abs(var_usd), 1)}% em 30 dias e fecha a R$ {br(usd[-1][1], 2)}"
    d["resumo"] = (f"O dólar PTAX de {usd[-1][0]} foi R$ {br(usd[-1][1], 4)}, "
                   f"{'alta' if var_usd > 0 else 'queda'} de {br(abs(var_usd), 1)}% desde {desde}. "
                   "Câmbio, juros e inflação são atualizados automaticamente com dados do Banco Central em dias úteis. "
                   "As notícias desta demonstração são exemplos com fonte e data indicadas em cada card.")
    d["edicao"] = f"Edição de {date.today():%d/%m/%Y}"
    d["atualizado"] = datetime.now().astimezone().isoformat(timespec="seconds")
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, separators=(",", ":"))

    if falhas:
        print("Falhas:", *falhas, sep="\n  ")
        sys.exit(1)
    print("Indicadores atualizados.")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data.json")
