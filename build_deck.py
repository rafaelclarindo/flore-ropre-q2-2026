import base64
import csv
import html as html_lib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"


def image_uri(filename):
    data = base64.b64encode((ASSETS / filename).read_bytes()).decode("ascii")
    return f"data:image/png;base64,{data}"


COLLI_RED = image_uri("colli-red.png")
COLLI_WHITE = image_uri("colli-white.png")
CLIENT_NAME = "Florestec"
CLIENT_LOGO = image_uri("client-logo.png") if (ASSETS / "client-logo.png").exists() else None
CLIENT_LOGO_HTML = (
    f'<img class="client-logo-img" src="{CLIENT_LOGO}" alt="{CLIENT_NAME}">'
    if CLIENT_LOGO
    else f'<span class="client-mark">{CLIENT_NAME}</span>'
)


def optional_image_uri(filename):
    path = ASSETS / filename
    return image_uri(filename) if path.exists() else None


def media_asset_src(filename):
    return f"assets/{filename}" if (ASSETS / filename).exists() else None


def channel_logo_html(filename, alt):
    src = optional_image_uri(filename)
    if not src:
        return ""
    return f'<img class="channel-logo" src="{src}" alt="{alt}">'


def pct_number(value):
    clean = value.replace("%", "").replace(".", "").replace(",", ".").strip()
    try:
        return float(clean)
    except ValueError:
        return None


def projection_diff_class(metric, diff):
    value = pct_number(diff)
    if value is None:
        return ""
    lower_better = any(token in metric.lower() for token in ("cpm", "cpc", "custo", "cac"))
    if lower_better:
        return "good" if value <= 100 else "bad"
    if value >= 100:
        return "good"
    return "warn" if value >= 70 else "bad"


def projection_table_from_csv(filename, month_keyword):
    path = ASSETS / filename
    if not path.exists():
        return '<div class="projection-empty">CSV de projeção pendente.</div>'
    rows = list(csv.reader(path.open(encoding="utf-8-sig", newline="")))
    if len(rows) < 3:
        return '<div class="projection-empty">CSV de projeção sem linhas suficientes.</div>'

    month_positions = [(index, value.strip()) for index, value in enumerate(rows[0]) if value.strip()]
    selected = month_positions[-1]
    for item in month_positions:
        if month_keyword.lower() in item[1].lower():
            selected = item
            break
    start, title = selected
    title = title.replace("PROJEÇÃO - ", "").title()
    cols = [start, start + 1, start + 2, start + 3]

    body = []
    for row in rows[2:]:
        if len(row) <= start or not row[start].strip():
            continue
        values = [row[col].strip() if len(row) > col else "" for col in cols]
        cells = "".join(
            f"<td>{html_lib.escape(value)}</td>" for value in values
        )
        body.append(f"<tr>{cells}</tr>")

    return f"""
      <div class="projection-title-card">
        <span>Cenário</span>
        <strong>{html_lib.escape(title)}</strong>
      </div>
      <div class="projection-table-wrap">
        <table class="projection-table">
          <thead>
            <tr>
              <th>Base</th>
              <th>Pessimista</th>
              <th>Realista</th>
              <th>Otimista</th>
            </tr>
          </thead>
          <tbody>
            {''.join(body)}
          </tbody>
        </table>
      </div>
    """


def projection_slide(filename, month_keyword="JUNHO", quarter_label="Q3"):
    return f"""
    <section class="slide dark projection-slide">
      <div class="slide-head">
        <div>
          <span class="eyebrow">Objetivos | Próximo quarter</span>
          <h1>Projeção {html_lib.escape(quarter_label)}</h1>
        </div>
      </div>
      {projection_table_from_csv(filename, month_keyword)}
    </section>
    """


def stair_gauge(value, rotation):
    return f"""
      <div class="stair-gauge">
        <span class="step-gauge-tag">ROI</span>
        <svg viewBox="0 0 120 78" aria-hidden="true">
          <path class="gauge-red" d="M18 58 A42 42 0 0 1 43 22"></path>
          <path class="gauge-yellow" d="M43 22 A42 42 0 0 1 77 22"></path>
          <path class="gauge-green" d="M77 22 A42 42 0 0 1 102 58"></path>
          <line class="gauge-needle" x1="60" y1="58" x2="60" y2="24" transform="rotate({rotation} 60 58)"></line>
          <circle cx="60" cy="58" r="5"></circle>
        </svg>
        <span class="step-gauge-value">{value}</span>
      </div>
    """


def step_stair(step_label, phase_label, gauge_value, rotation, current):
    current_cls = " current" if current else ""
    current_tag = f"""
      <div class="stair-current-tag">
        <span class="label">Estamos aqui</span>
        <span class="arrow"></span>
      </div>
    """ if current else ""
    gauge_html = stair_gauge(gauge_value, rotation) if gauge_value else ""
    return f"""
      <div class="stair{current_cls}">
        {current_tag}
        {gauge_html}
        <div class="stair-card">{step_label}</div>
        <div class="stair-bar"></div>
        <div class="stair-phase">{phase_label}</div>
      </div>
    """


def creative_media(filename, headline, badge):
    path = ASSETS / filename
    if path.exists() and path.suffix.lower() in {".mp4", ".mov", ".webm"}:
        src = media_asset_src(filename)
        poster = ASSETS / f"{path.stem}-poster.jpg"
        poster_attr = f' poster="assets/{poster.name}"' if poster.exists() else ""
        title = html_lib.escape(headline, quote=True)
        return f"""
          <div class="creative-video-shell">
            <video class="creative-video" src="{src}" title="{title}" muted loop playsinline preload="auto"{poster_attr}></video>
            <button class="creative-play-button" type="button" aria-label="Reproduzir vídeo"><span class="play-dot"></span></button>
            <a class="creative-open-video" href="{src}" target="_blank" rel="noopener" title="Abrir vídeo em nova aba">
              <span class="play-dot"></span><span>Abrir vídeo</span>
            </a>
          </div>
        """
    if path.exists():
        return f'<img class="creative-img" src="{image_uri(filename)}" alt="{headline}">'
    return f"""
      <div class="creative-placeholder">
        <div class="creative-badge">{badge}</div>
        <div class="creative-art-title">{headline}</div>
        <div class="creative-cta">Slot do criativo</div>
      </div>
    """


def creative_rank(rank, title, filename, badge, thesis, metric_label, metric_value, cpl, leads, cpmql, mqls):
    return f"""
      <article class="creative-rank-card">
        <div class="creative-media-wrap">
          {creative_media(filename, title, badge)}
        </div>
        <div class="creative-info">
          <div class="creative-rank-head">
            <span>{rank}</span>
            <strong>{title}</strong>
          </div>
          <p>{thesis}</p>
          <div class="creative-metrics">
            <div><span>{metric_label}</span><strong>{metric_value}</strong></div>
            <div><span>CPL</span><strong>{cpl}</strong></div>
            <div><span>Leads</span><strong>{leads}</strong></div>
            <div><span>CPMQL</span><strong>{cpmql}</strong></div>
            <div><span>MQLs</span><strong>{mqls}</strong></div>
          </div>
        </div>
      </article>
    """


def section_menu_slide(active, title, subtitle, bg="dark"):
    def row(num, name, subs=None):
        active_class = " active" if num == active else ""
        sub_html = ""
        if subs:
            sub_html = "<div class=\"sub\">" + "".join(f"<span>{item}</span>" for item in subs) + "</div>"
        return f"""
        <div class="menu-row{active_class}">
          <div class="menu-num">{num}</div>
          <div class="menu-card"><strong>{name}</strong>{sub_html}</div>
        </div>
        """
    return f"""
    <section class="slide {bg} section-menu-slide">
      <h1 class="visually-hidden">ROPRE {title}</h1>
      <div class="summary-bg"></div>
      <div class="summary-title">
        <div class="small">ROPRE</div>
        <div class="big">{title}</div>
        <div class="big" style="font-size:60px;margin-top:14px">{subtitle}</div>
      </div>
      <div class="summary-menu">
        {row("01", "Resultados", ["Gerais", "Funil", "Canais", "Gargalos", "Lições"])}
        {row("02", "Objetivos", ["Quarter fechado", "Próximo quarter", "Projeção"])}
        {row("03", "Premissas e riscos")}
        {row("04", "Entregas", ["Realizadas", "Previstas", "Revisão do backlog"])}
        {row("05", "Próximos passos")}
      </div>
    </section>
    """


def stage(rate_label, rate_real, rate_proj, name, real, proj, cost_label, cost_real, cost_proj, attain, note=""):
    tone = "good" if attain >= 100 else "warn" if attain >= 70 else "bad"
    width = max(5, min(attain, 100))
    return f"""
    <div class="funnel-row">
      <div class="side side-left">
        <span>{rate_label}</span>
        <strong>{rate_real}</strong>
        <small>Marco {rate_proj}</small>
      </div>
      <div class="funnel-center">
        <div class="funnel-bar">
          <div class="funnel-fill {tone}" style="width:{width}%"></div>
          <div class="funnel-text">
            <strong>{name}</strong>
            <span>{real} <em>Marco {proj}</em></span>
          </div>
        </div>
        <div class="funnel-note">{attain}% do marco{note}</div>
      </div>
      <div class="side side-right">
        <span>{cost_label}</span>
        <strong>{cost_real}</strong>
        <small>Marco {cost_proj}</small>
      </div>
    </div>
    """


def funnel_slide(kind, title, invest_real, invest_proj, stages, restriction=None, bg="dark", logo=None, logo_alt=""):
    restriction_html = ""
    label_html = f'<div class="section-label">{kind}</div>' if kind else ""
    logo_html = channel_logo_html(logo, logo_alt) if logo else ""
    if restriction:
        restriction_html = f"""
        <div class="restriction">
          <span>Gargalo</span>
          <strong>{restriction}</strong>
        </div>
        """
    return f"""
    <section class="slide {bg}">
      {label_html}
      <div class="slide-head">
        <h1>{title}</h1>
        {logo_html}
      </div>
      <div class="investment">
        <div class="investment-item"><span>Verba Q2</span><strong>{invest_real}</strong></div>
        <div class="investment-item"><span>Verba Q1 | referência</span><strong>{invest_proj}</strong></div>
      </div>
      <div class="funnel-header">
        <span>Taxa de passagem</span>
        <span>Volume | Q2 vs marco</span>
        <span>Custo por etapa</span>
      </div>
      <div class="funnel">
        {''.join(stages)}
      </div>
      {restriction_html}
    </section>
    """


def mini_stage(rate_label, rate, label, value, cost_label, cost):
    return f"""
      <div class="mini-stage">
        <div class="mini-tax"><span>{rate_label}</span><strong>{rate}</strong></div>
        <div class="mini-main"><span>{label}</span><strong>{value}</strong></div>
        <div class="mini-cost"><span>{cost_label}</span><strong>{cost}</strong></div>
      </div>
    """


def mini_funnel(period, investment, stages):
    return f"""
      <div class="mini-funnel-card">
        <div class="mini-title"><span>{period}</span><strong>{investment}</strong></div>
        <div class="mini-head"><span>Taxa</span><span>Volume</span><span>Custo</span></div>
        <div class="mini-funnel">
          {''.join(stages)}
        </div>
      </div>
    """


def action_slide(number, title, score, why, what, how, who, when, dependency, evidence, bg="white"):
    dependency_html = ""
    if dependency:
        dependency_html = f'<div class="card detail-card dependency"><span class="kicker">Trava do cliente</span><h3>Para rodar</h3><p>{dependency}</p></div>'
    return f"""
    <section class="slide {bg} action-detail-slide">
      <span class="eyebrow">Plano de ação | 5W1H</span>
      <div class="action-title-row">
        <div class="action-number">{number}</div>
        <div>
          <h1>{title}</h1>
          <div class="score-pill">Prioridade {number} | Score {score}</div>
        </div>
      </div>
      <div class="action-detail-grid">
        <div class="card why-card">
          <span class="kicker">Why</span>
          <h3>Por que executar</h3>
          <p>{why}</p>
          <div class="evidence-box"><span>Evidência</span><strong>{evidence}</strong></div>
        </div>
        <div class="detail-stack">
          <div class="card detail-card"><span class="kicker">What</span><h3>O que será feito</h3><p>{what}</p></div>
          <div class="card detail-card"><span class="kicker">How</span><h3>Como será executado</h3><p>{how}</p></div>
        </div>
        <div class="detail-stack">
          <div class="card detail-card"><span class="kicker">Who</span><h3>Responsável</h3><p>{who}</p></div>
          <div class="card detail-card"><span class="kicker">When</span><h3>Quando</h3><p>{when}</p></div>
          {dependency_html}
        </div>
      </div>
    </section>
    """


action_slides = [
    action_slide(
        "01",
        "SLA alerta SDR IA",
        "1,67",
        "No Q2, 104 de 145 leads da SDR IA (72%) ficaram travados em Ativado IA, com só 1 em Qualificação. O cliente relatou que não chegam os leads que necessita.",
        "Nunca operar SDR IA sem SLA de avanço e alerta de fila travada quando mais de 30% dos leads pararem por 7 dias.",
        "Produto SDR e Coord definem alerta, dashboard de fila e dono de destravamento; validar em todo cliente Kommo+SDR IA.",
        "Produto SDR + Coord",
        "Até 30/09/2026",
        "Acesso ao Kommo e regra de estágio padronizada.",
        "145 leads SDR IA; 104 (72%) em Ativado IA; 1 em Qualificação.",
        "white",
    ),
    action_slide(
        "02",
        "Rankear por SQL e venda",
        "1,67",
        "PMax GERAL teve o melhor CPL (R$ 21,71) e zero vendas, enquanto SEARCH CORE vendeu R$ 13.441 e PMax 05/06 vendeu R$ 13.221. Otimizar só por CPL esconde o funil.",
        "Rankear mídia por SQL e venda, não só por CPL, no checklist de growth.",
        "Dashboard de campanha com venda/SQL; pausar ou cortar vencedores de CPL sem venda; priorizar Search Core e criativos com receita.",
        "Paid + PM",
        "Imediato (padrão Invictus)",
        "",
        "PMax GERAL CPL R$ 21,71 e 0 vendas; Search Core e PMax 05/06 com receita.",
        "",
    ),
    action_slide(
        "03",
        "Tracking no onboarding",
        "1,25",
        "Tracking GTM e conversões só entraram em 22/06, 24 dias após o pedido de churn em 28/05. Sem rastreio cedo, o diagnóstico chega tarde demais.",
        "Tracking GTM/CRM no onboarding, antes do mês 2, nunca só no churn.",
        "Checklist de onboarding com GTM, conversões e funil Kommo validados na abertura do projeto.",
        "Coord + Tech",
        "Até 30/09/2026 (padrão)",
        "",
        "37 entregas reais; tracking/GTM concentrados em 22/06 pós-churn.",
        "white",
    ),
    action_slide(
        "04",
        "1 AM por quarter",
        "1,00",
        "Houve 3 AMs em sequência no Q2 (Isabela, Melissa, Gabriela). Troca sem handoff formal quebra contexto, CSAT e ritmo comercial.",
        "Congelar troca de AM: handoff formal ou 1 dono por quarter.",
        "Coord define titular único por quarter e protocolo de handoff escrito quando a troca for inevitável.",
        "Coord",
        "Imediato (padrão Invictus)",
        "",
        "Execução real Q2: Isabela (abr), Melissa (abr-jun), Gabriela (desde 11/06).",
        "",
    ),
    action_slide(
        "05",
        "Alinhar meta com BE",
        "1,00",
        "A meta V4 de faturamento (R$ 40k/mês) ficou desalinhada do BE citado pelo cliente (R$ 75k/mês). Expectativa errada na proposta vira crise de percepção.",
        "Alinhar meta de faturamento com o BE do cliente já na proposta.",
        "Comercial V4 e PM documentam BE do cliente no kickoff e batem meta cockpit contra esse número.",
        "Comercial V4 + PM",
        "Em toda nova proposta",
        "",
        "Meta cockpit R$ 40k/mês vs BE cliente R$ 75k/mês (call 05/06); BE competência R$ 52.500.",
        "white",
    ),
    action_slide(
        "06",
        "QA criativo vs produto",
        "0,83",
        "CSAT Campanhas ficou em 1 de 5. Criativos de IA foram rejeitados pela cliente por não bater com o produto real (foto e especificação).",
        "Banir criativo de IA sem QA de produto real (foto e especificação).",
        "Design e AM validam criativo contra catálogo/NR-31 antes de veicular; rejeição vira bloqueio de publicação.",
        "Design + AM",
        "Imediato (padrão Invictus)",
        "",
        "CSAT Campanhas 1/5; rejeições de criativo IA em 28/05 e 05/06.",
        "",
    ),
]



q1_compact = [
    mini_stage("n/a", "n/a", "Invest. Meta", "R$ 2.494", "Mix Q", "30%"),
    mini_stage("n/a", "n/a", "Leads", "87", "CPL", "R$ 28,66"),
    mini_stage("Lead -> MQL", "11,5%", "MQLs", "10", "Custo/MQL", "R$ 249,37"),
    mini_stage("MQL -> SQL", "10,0%", "SQLs", "1", "Custo/SQL", "R$ 2.494"),
    mini_stage("SQL -> venda", "100%", "Vendas", "1", "Receita", "R$ 11,6k"),
]

q2_compact = [
    mini_stage("n/a", "n/a", "Invest. Google", "R$ 5.907", "Mix Q", "70%"),
    mini_stage("n/a", "n/a", "Conversões", "124", "CPL", "R$ 47,64"),
    mini_stage("Lead -> MQL", "15,3%", "MQLs", "19", "Custo/MQL", "R$ 310,90"),
    mini_stage("MQL -> SQL", "31,6%", "SQLs", "6", "Custo/SQL", "R$ 984,51"),
    mini_stage("SQL -> venda", "16,7%", "Vendas", "1", "Receita", "R$ 13,4k"),
]


q2_stages = [
    stage("n/a", "n/a", "n/a", "Leads", "213", "n/a", "Invest.", "R$ 8.401", "R$ 9.000", 93),
    stage("Lead -> MQL", "24,4%", "30%", "MQLs", "52", "64", "Custo/MQL", "R$ 161,55", "n/a", 81),
    stage("MQL -> SQL", "44,2%", "50%", "SQLs", "23", "32", "Custo/SQL", "R$ 365,25", "n/a", 72),
    stage("SQL -> venda", "13,0%", "40%", "Vendas", "3", "9", "Custo/venda", "R$ 2.800", "n/a", 33),
    stage("Ticket", "R$ 12.738", "n/a", "Receita", "R$ 38,2k", "R$ 120k", "Pacing", "32%", "100%", 32),
]




html = f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="asset-colli-red" content="assets/colli-red.png">
  <meta name="asset-colli-white" content="assets/colli-white.png">
  <title>ROPRE Quarter | Florestec</title>
  <style>
    :root {{
      --red: #ed1c24;
      --red-dark: #5f080b;
      --ink: #191919;
      --muted: #767171;
      --cream: #f6f2ec;
      --line: rgba(25,25,25,.10);
      --good: #059669;
      --warn: #d97706;
      --bad: #ef4444;
      --scale: 1;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; min-height: 100vh; background: #111; font-family: "Inter", "Segoe UI", Arial, sans-serif; color: var(--ink); overflow: hidden; }}
    #deck {{
      position: absolute;
      left: 50%;
      top: 50%;
      width: 1600px;
      height: 900px;
      transform: translate(-50%, -50%) scale(var(--scale));
      transform-origin: center;
      background: var(--cream);
      overflow: hidden;
      box-shadow: 0 40px 120px rgba(0,0,0,.45);
    }}
    .slide {{
      position: absolute;
      inset: 0;
      padding: 72px 96px 108px;
      opacity: 0;
      visibility: hidden;
      pointer-events: none;
      transform: translateX(24px);
      transition: opacity .24s ease, transform .24s ease;
      background: radial-gradient(circle at 88% 6%, rgba(237,28,36,.07), transparent 27%), #f7f4ef;
      overflow: hidden;
    }}
    .slide.active {{ opacity: 1; visibility: visible; pointer-events: auto; transform: translateX(0); }}
    .slide.red {{ color: white; background: linear-gradient(135deg, #ed1c24 0%, #7a060b 100%); }}
    .slide.dark {{ color: white; background: radial-gradient(circle at 72% 12%, rgba(237,28,36,.50), transparent 32%), linear-gradient(145deg, #260204 0%, #100001 100%); }}
    .slide.white {{ background: white; }}
    .cover-client {{ position: absolute; left: 96px; top: 78px; min-width: 260px; min-height: 70px; display: inline-flex; align-items: center; gap: 14px; color: white; }}
    .client-mark {{ display: inline-flex; align-items: center; justify-content: center; min-width: 210px; height: 64px; padding: 0 22px; border: 1px solid rgba(255,255,255,.34); border-radius: 13px; background: rgba(255,255,255,.10); font: 800 20px/1.05 "Inter"; }}
    .client-logo-img {{ display: block; max-width: 280px; max-height: 82px; object-fit: contain; object-position: left center; }}
    .cover-title {{ position: absolute; left: 96px; bottom: 138px; max-width: 960px; }}
    .cover-title h1 {{ margin: 0; font-size: 92px; line-height: .94; letter-spacing: -.04em; }}
    .cover-title p {{ margin: 28px 0 0; color: rgba(255,255,255,.72); font-size: 28px; }}
    .orb {{ position: absolute; border-radius: 50%; background: rgba(255,255,255,.10); filter: blur(.2px); }}
    h1, h2, h3, p {{ margin-top: 0; }}
    h1 {{ font-size: 68px; line-height: .96; letter-spacing: -.04em; margin-bottom: 18px; }}
    h2 {{ font-size: 58px; line-height: 1; letter-spacing: -.035em; margin-bottom: 22px; }}
    h3 {{ font-size: 30px; line-height: 1.1; margin-bottom: 12px; }}
    .eyebrow, .section-label {{ display: inline-flex; align-items: center; height: 34px; padding: 0 14px; border-radius: 999px; background: rgba(237,28,36,.10); color: var(--red); font: 800 12px/1 "IBM Plex Mono", monospace; letter-spacing: .08em; text-transform: uppercase; }}
    .dark .eyebrow, .dark .section-label, .red .eyebrow {{ color: white; background: rgba(255,255,255,.13); }}
    .red .section-label {{ color: white; background: rgba(255,255,255,.13); }}
    .visually-hidden {{ position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; border: 0; }}
    .summary-bg {{ position: absolute; inset: 0; background: radial-gradient(circle at 16% 58%, rgba(255,255,255,.20), transparent 22%), radial-gradient(circle at 70% 20%, rgba(237,28,36,.45), transparent 36%), linear-gradient(120deg, #08080b 0%, #300709 66%, #070304 100%); }}
    .section-menu-slide.red {{ background: #160103; }}
    .section-menu-slide.red .summary-bg {{ background: radial-gradient(circle at 16% 58%, rgba(255,255,255,.16), transparent 22%), radial-gradient(circle at 70% 20%, rgba(237,28,36,.48), transparent 34%), linear-gradient(120deg, #08080b 0%, #3a080a 66%, #070304 100%); }}
    .summary-title {{ position: absolute; left: 96px; bottom: 238px; color: white; }}
    .summary-title .small {{ font-size: 34px; margin-bottom: 10px; }}
    .summary-title .big {{ font-size: 82px; font-weight: 800; line-height: .9; letter-spacing: -.04em; }}
    .summary-menu {{ position: absolute; right: 144px; top: 72px; width: 480px; display: grid; gap: 13px; }}
    .menu-row {{ display: grid; grid-template-columns: 76px 1fr; gap: 14px; align-items: stretch; }}
    .menu-num {{ display: flex; align-items: center; justify-content: center; border-radius: 8px; background: rgba(11,11,13,.72); border: 1px solid rgba(255,255,255,.20); color: rgba(255,255,255,.55); font: 800 24px/1 "IBM Plex Mono", monospace; }}
    .menu-card {{ min-height: 88px; padding: 20px 26px; border: 1px solid rgba(255,255,255,.22); border-radius: 8px; background: rgba(10,10,12,.62); color: rgba(255,255,255,.55); }}
    .menu-row.active .menu-num, .menu-row.active .menu-card {{ background: var(--red); color: white; border-color: var(--red); }}
    .section-menu-slide.red .menu-row.active .menu-num, .section-menu-slide.red .menu-row.active .menu-card {{ background: var(--red); color: white; border-color: var(--red); }}
    .menu-card strong {{ display: block; font-size: 25px; line-height: 1; margin-bottom: 10px; }}
    .menu-card .sub {{ display: grid; gap: 5px; font-size: 14px; line-height: 1.1; }}
    .menu-card .sub span {{ display: grid; grid-template-columns: 13px 1fr; align-items: baseline; }}
    .menu-card .sub span::before {{ content: "•"; opacity: .92; }}
    .slide-head {{ display: flex; justify-content: space-between; align-items: flex-start; gap: 40px; }}
    .channel-logo {{ width: 92px; height: 58px; object-fit: contain; margin-top: 2px; filter: drop-shadow(0 10px 24px rgba(0,0,0,.18)); }}
    .cards {{ display: grid; gap: 18px; }}
    .grid-4 {{ grid-template-columns: repeat(4, 1fr); }}
    .grid-3 {{ grid-template-columns: repeat(3, 1fr); }}
    .grid-2 {{ grid-template-columns: repeat(2, 1fr); }}
    .card {{ border: 1px solid var(--line); border-radius: 18px; background: rgba(255,255,255,.76); padding: 26px; }}
    .dark .card {{ border-color: rgba(255,255,255,.14); background: rgba(255,255,255,.07); }}
    .metric {{ min-height: 152px; }}
    .label {{ color: var(--muted); font-size: 16px; line-height: 1.2; }}
    .dark .label {{ color: rgba(255,255,255,.68); }}
    .value {{ margin-top: 16px; color: var(--red); font-size: 50px; line-height: .92; letter-spacing: -.04em; font-weight: 800; }}
    .dark .value {{ color: #fff3e0; }}
    .sub {{ margin-top: 9px; color: var(--muted); font: 700 13px/1.2 "IBM Plex Mono", monospace; }}
    .dark .sub {{ color: rgba(255,255,255,.62); }}
    .table {{ width: 100%; border-collapse: collapse; font-size: 16px; margin-top: 26px; overflow: hidden; border-radius: 16px; background: white; }}
    .table th, .table td {{ padding: 13px 15px; border-bottom: 1px solid rgba(25,25,25,.08); text-align: left; }}
    .table th {{ color: var(--muted); background: rgba(237,28,36,.05); font: 800 12px/1 "IBM Plex Mono", monospace; text-transform: uppercase; letter-spacing: .04em; }}
    .table .num {{ text-align: right; font-family: "IBM Plex Mono", monospace; white-space: nowrap; }}
    .constraint-layout {{ display: grid; grid-template-columns: 1.35fr 1fr 1fr 1fr; gap: 18px; margin-top: 30px; align-items: stretch; }}
    .constraint-main {{ color: white; background: linear-gradient(135deg, #ed1c24 0%, #9d080d 62%, #3b0305 100%); border-color: rgba(237,28,36,.52); box-shadow: 0 24px 60px rgba(237,28,36,.20); }}
    .constraint-main .label, .constraint-main .sub {{ color: rgba(255,255,255,.82); }}
    .constraint-value {{ margin-top: 14px; color: white; font-size: 48px; line-height: .92; letter-spacing: -.04em; font-weight: 900; }}
    .constraint-main p {{ margin: 20px 0 0; color: rgba(255,255,255,.78); font-size: 17px; line-height: 1.2; }}
    .quarter-slide h1 {{ font-size: 58px; margin-bottom: 10px; }}
    .quarter-layout {{ display: grid; grid-template-columns: 1fr 1fr 310px; gap: 18px; margin-top: 22px; align-items: stretch; }}
    .mini-funnel-card {{ border: 1px solid var(--line); border-radius: 18px; background: rgba(255,255,255,.80); padding: 18px; min-height: 602px; }}
    .mini-title {{ display: flex; justify-content: space-between; align-items: baseline; padding-bottom: 13px; border-bottom: 1px solid rgba(25,25,25,.08); }}
    .mini-title span {{ color: var(--red); font: 900 22px/1 "IBM Plex Mono", monospace; }}
    .mini-title strong {{ font: 900 22px/1 "IBM Plex Mono", monospace; }}
    .mini-head {{ display: grid; grid-template-columns: 34% 36% 30%; gap: 8px; padding: 12px 0 6px; color: var(--muted); font: 800 10px/1 "IBM Plex Mono", monospace; text-transform: uppercase; letter-spacing: .04em; }}
    .mini-stage {{ display: grid; grid-template-columns: 34% 36% 30%; gap: 8px; align-items: stretch; min-height: 58px; margin-bottom: 7px; }}
    .mini-stage > div {{ border-radius: 12px; background: rgba(237,28,36,.055); padding: 9px 10px; overflow: hidden; }}
    .mini-stage span {{ display: block; color: var(--muted); font-size: 11px; line-height: 1.05; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
    .mini-stage strong {{ display: block; margin-top: 6px; font: 900 17px/1 "IBM Plex Mono", monospace; color: var(--ink); white-space: nowrap; }}
    .mini-main strong {{ color: var(--red); }}
    .reading-panel {{ border: 1px solid var(--line); border-radius: 18px; background: white; padding: 20px; min-height: 602px; display: flex; flex-direction: column; justify-content: space-between; }}
    .reading-block {{ display: grid; gap: 12px; }}
    .reading-item {{ border-radius: 14px; padding: 15px; background: rgba(25,25,25,.035); }}
    .reading-item.good {{ background: rgba(5,150,105,.08); }}
    .reading-item.bad {{ background: rgba(239,68,68,.08); }}
    .reading-item span {{ display: block; color: var(--muted); font: 800 10px/1 "IBM Plex Mono", monospace; text-transform: uppercase; margin-bottom: 7px; }}
    .reading-item strong {{ display: block; color: var(--ink); font-size: 18px; line-height: 1.1; }}
    .reading-item.good strong {{ color: var(--good); }}
    .reading-item.bad strong {{ color: var(--bad); }}
    .reading-item p {{ margin: 7px 0 0; color: var(--muted); font-size: 13px; line-height: 1.18; }}
    .investment {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); align-items: center; gap: 18px; margin: 10px 0 12px; padding: 14px 20px; border: 1px solid rgba(255,255,255,.16); border-radius: 16px; background: rgba(255,255,255,.06); }}
    .investment-item {{ display: flex; align-items: center; gap: 18px; min-height: 38px; }}
    .investment span {{ color: rgba(255,255,255,.84); font-weight: 800; font-size: 18px; line-height: 1; }}
    .investment strong {{ color: white; font-size: 34px; line-height: .95; }}
    .funnel-header {{ display: grid; grid-template-columns: 185px 1fr 185px; gap: 14px; margin: 12px 0 8px; color: rgba(255,255,255,.52); font: 800 11px/1 "IBM Plex Mono", monospace; text-transform: uppercase; letter-spacing: .05em; }}
    .funnel-header span:first-child {{ text-align: right; }}
    .funnel-row {{ display: grid; grid-template-columns: 185px 1fr 185px; gap: 14px; align-items: center; min-height: 56px; margin-bottom: 6px; }}
    .side {{ display: grid; gap: 3px; }}
    .side-left {{ text-align: right; }}
    .side span {{ color: rgba(255,255,255,.52); font-size: 12px; }}
    .side strong {{ font: 800 17px/1 "IBM Plex Mono", monospace; color: white; }}
    .side small {{ color: rgba(255,255,255,.48); font-size: 10px; }}
    .funnel-bar {{ position: relative; height: 42px; border-radius: 10px; overflow: hidden; background: rgba(255,255,255,.07); border: 1px solid rgba(255,255,255,.10); }}
    .funnel-fill {{ position: absolute; inset: 0 auto 0 0; border-radius: 10px; background: linear-gradient(90deg, #7f1d1d, var(--bad)); }}
    .funnel-fill.warn {{ background: linear-gradient(90deg, #7f1d1d, var(--warn)); }}
    .funnel-fill.good {{ background: linear-gradient(90deg, #7f1d1d, var(--good)); }}
    .funnel-text {{ position: relative; z-index: 2; height: 100%; display: flex; align-items: center; justify-content: space-between; padding: 0 18px; }}
    .funnel-text strong {{ font-size: 17px; }}
    .funnel-text span {{ font: 800 15px/1 "IBM Plex Mono", monospace; }}
    .funnel-text em {{ color: rgba(255,255,255,.58); font-style: normal; margin-left: 10px; font-size: 12px; }}
    .funnel-note {{ margin-top: 3px; color: rgba(255,255,255,.44); font-size: 10px; }}
    .restriction {{ margin-left: 199px; margin-top: 18px; border-radius: 18px; border: 1px solid rgba(255,138,128,.44); background: linear-gradient(135deg, rgba(255,138,128,.18), rgba(74,6,3,.42)); padding: 18px 22px; }}
    .restriction span {{ display: block; color: rgba(255,255,255,.62); font: 800 11px/1 "IBM Plex Mono", monospace; text-transform: uppercase; margin-bottom: 8px; }}
    .restriction strong {{ font-size: 22px; }}
    .action-grid {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 16px; margin-top: 34px; }}
    .action {{ min-height: 418px; display: flex; flex-direction: column; justify-content: space-between; }}
    .rank {{ color: var(--red); font: 800 30px/1 "IBM Plex Mono", monospace; }}
    .action-detail-slide h1 {{ margin: 0; font-size: 56px; }}
    .action-detail-slide .eyebrow {{ padding: 12px 20px; min-height: 42px; font-size: 14px; color: white; background: var(--red); box-shadow: 0 10px 24px rgba(237,28,36,.18); }}
    .action-title-row {{ display: grid; grid-template-columns: 96px 1fr; gap: 24px; align-items: center; margin-top: 20px; }}
    .action-number {{ width: 96px; height: 96px; border-radius: 18px; display: flex; align-items: center; justify-content: center; color: white; background: var(--red); font: 900 36px/1 "IBM Plex Mono", monospace; }}
    .score-pill {{ display: inline-flex; margin-top: 14px; padding: 9px 14px; border-radius: 999px; background: rgba(237,28,36,.08); color: var(--red); font: 900 12px/1 "IBM Plex Mono", monospace; text-transform: uppercase; }}
    .action-detail-grid {{ display: grid; grid-template-columns: 1.05fr 1fr 1fr; gap: 20px; margin-top: 28px; min-height: 505px; }}
    .why-card {{ display: flex; flex-direction: column; justify-content: space-between; background: linear-gradient(145deg, rgba(237,28,36,.10), white); }}
    .why-card p, .detail-card p {{ color: var(--muted); font-size: 18px; line-height: 1.28; margin: 0; }}
    .kicker {{ display: inline-flex; margin-bottom: 14px; color: var(--red); font: 900 12px/1 "IBM Plex Mono", monospace; text-transform: uppercase; letter-spacing: .05em; }}
    .evidence-box {{ margin-top: 28px; padding: 20px; border-radius: 16px; background: rgba(25,25,25,.055); }}
    .evidence-box span {{ display: block; color: var(--muted); font: 900 11px/1 "IBM Plex Mono", monospace; text-transform: uppercase; margin-bottom: 10px; }}
    .evidence-box strong {{ display: block; color: var(--ink); font-size: 22px; line-height: 1.12; }}
    .detail-stack {{ display: grid; gap: 18px; }}
    .detail-card {{ min-height: 154px; }}
    .detail-card h3 {{ margin-bottom: 10px; }}
    .detail-card.dependency {{ border-color: rgba(237,28,36,.24); background: rgba(237,28,36,.055); }}
    .creative-ranking-slide h1 {{ text-align: center; font-size: 50px; margin-bottom: 22px; }}
    .creative-rank-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; }}
    .creative-rank-card {{ border: 1px solid rgba(255,255,255,.18); border-radius: 20px; overflow: hidden; background: rgba(255,255,255,.07); display: grid; grid-template-rows: 270px 1fr; }}
    .creative-media-wrap {{ position: relative; background: rgba(0,0,0,.30); overflow: hidden; display: flex; align-items: center; justify-content: center; }}
    .creative-img, .creative-video {{ width: 100%; height: 100%; display: block; object-fit: contain; }}
    .creative-video-shell {{ position: relative; width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; background: #070707; }}
    .creative-video {{ background: #070707; cursor: pointer; }}
    .creative-video::-webkit-media-controls-panel {{ background: rgba(0,0,0,.70); }}
    .creative-play-button {{ position: absolute; left: 50%; top: 50%; z-index: 2; width: 58px; height: 58px; border: 1px solid rgba(255,255,255,.28); border-radius: 999px; display: flex; align-items: center; justify-content: center; transform: translate(-50%, -50%); background: rgba(237,28,36,.92); box-shadow: 0 16px 42px rgba(0,0,0,.36); cursor: pointer; }}
    .creative-video-shell.is-playing .creative-play-button {{ opacity: 0; pointer-events: none; }}
    .creative-open-video {{ position: absolute; right: 14px; top: 14px; z-index: 3; display: inline-flex; align-items: center; gap: 8px; height: 32px; padding: 0 12px; border-radius: 999px; color: white; text-decoration: none; background: rgba(237,28,36,.92); border: 1px solid rgba(255,255,255,.24); font: 900 10px/1 "IBM Plex Mono", monospace; text-transform: uppercase; box-shadow: 0 12px 28px rgba(0,0,0,.28); }}
    .creative-open-video:hover {{ background: #ff2630; }}
    .play-dot {{ width: 0; height: 0; border-top: 6px solid transparent; border-bottom: 6px solid transparent; border-left: 9px solid white; }}
    .creative-placeholder {{ height: 100%; padding: 28px; display: flex; flex-direction: column; justify-content: space-between; background: radial-gradient(circle at 80% 20%, rgba(163,230,53,.58), transparent 28%), linear-gradient(135deg, #006b2d, #0b3b23 58%, #061f16); color: white; }}
    .creative-badge {{ align-self: flex-start; padding: 8px 12px; border-radius: 999px; background: rgba(255,255,255,.16); font: 900 11px/1 "IBM Plex Mono", monospace; text-transform: uppercase; }}
    .creative-art-title {{ max-width: 310px; font-size: 31px; line-height: 1.02; font-weight: 900; }}
    .creative-cta {{ align-self: flex-start; padding: 10px 14px; border-radius: 10px; background: #7bd800; color: #06350f; font: 900 13px/1 "IBM Plex Mono", monospace; text-transform: uppercase; }}
    .creative-info {{ padding: 22px; display: flex; flex-direction: column; gap: 14px; }}
    .creative-rank-head {{ display: grid; grid-template-columns: 52px 1fr; gap: 14px; align-items: start; }}
    .creative-rank-head span {{ color: var(--red); font: 900 32px/1 "IBM Plex Mono", monospace; }}
    .creative-rank-head strong {{ color: white; font-size: 23px; line-height: 1.08; }}
    .creative-info p {{ color: rgba(255,255,255,.68); font-size: 15px; line-height: 1.22; margin: 0; }}
    .creative-metrics {{ margin-top: auto; display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }}
    .creative-metrics div {{ border-radius: 12px; padding: 11px; background: rgba(255,255,255,.08); }}
    .creative-metrics span {{ display: block; color: rgba(255,255,255,.58); font: 900 10px/1 "IBM Plex Mono", monospace; text-transform: uppercase; margin-bottom: 7px; }}
    .creative-metrics strong {{ display: block; color: white; font: 900 17px/1 "IBM Plex Mono", monospace; }}
    .step-slide h1 {{ font-size: 54px; margin-top: 12px; }}
    .step-canvas {{ position: relative; height: 640px; margin-top: 8px; padding: 118px 70px 90px 100px; border-radius: 24px; overflow: hidden; background: radial-gradient(circle at 17% 69%, rgba(237,28,36,.32), transparent 28%), radial-gradient(circle at 79% 20%, rgba(237,28,36,.18), transparent 35%), linear-gradient(135deg, rgba(237,28,36,.12), rgba(255,255,255,.04)); border: 1px solid rgba(255,255,255,.14); }}
    .step-midline {{ position: absolute; left: 0; right: 0; top: 48%; height: 2px; background: rgba(255,255,255,.24); }}
    .step-axis-x {{ position: absolute; left: 60px; right: 40px; bottom: 90px; height: 2px; background: var(--red); }}
    .step-axis-y {{ position: absolute; left: 60px; top: 40px; bottom: 90px; width: 2px; background: var(--red); }}
    .step-axis-x::after {{ content: ""; position: absolute; right: -8px; top: -6px; border-left: 11px solid var(--red); border-top: 7px solid transparent; border-bottom: 7px solid transparent; }}
    .step-axis-y::after {{ content: "Dinheiro+"; position: absolute; left: -46px; top: 50%; color: var(--red); font-weight: 900; white-space: nowrap; transform: translateY(-50%) rotate(-90deg); transform-origin: center; }}
    .step-tempo-label {{ position: absolute; right: 40px; bottom: 36px; color: #ed1c24; font: 700 13px/1.1 "IBM Plex Sans"; font-weight: 900; }}
    .step-stairs {{ position: relative; height: 100%; display: flex; align-items: flex-end; gap: 34px; }}
    .stair {{ flex: 1; display: flex; flex-direction: column; align-items: center; position: relative; }}
    .stair-current-tag {{ display: flex; flex-direction: column; align-items: center; gap: 10px; margin-bottom: 16px; }}
    .stair-current-tag .label {{ padding: 12px 18px; border: 3px solid rgba(255,255,255,.34); color: white; font: 900 15px/1 "IBM Plex Mono", monospace; white-space: nowrap; }}
    .stair-current-tag .arrow {{ position: relative; width: 2px; height: 36px; background: white; }}
    .stair-current-tag .arrow::after {{ content: ""; position: absolute; left: -6px; bottom: -1px; border-left: 7px solid transparent; border-right: 7px solid transparent; border-top: 10px solid white; }}
    .stair-card {{ margin-bottom: 16px; min-width: 118px; padding: 13px 18px; border: 2px solid var(--red); border-radius: 9px; background: rgba(20,0,0,.58); color: white; text-align: center; font: 900 15px/1 "IBM Plex Mono", monospace; box-shadow: inset 0 0 18px rgba(237,28,36,.18); }}
    .stair.current .stair-card {{ background: white; color: var(--ink); border-color: white; box-shadow: 0 0 0 8px rgba(255,255,255,.12), inset 0 0 0 1px rgba(237,28,36,.12); }}
    .stair-bar {{ width: 100%; border-radius: 16px 16px 0 0; background: linear-gradient(180deg, rgba(237,28,36,.60), rgba(237,28,36,.14)); border: 1px solid rgba(255,255,255,.20); border-bottom: none; box-shadow: inset 0 0 30px rgba(0,0,0,.22); }}
    .stair.current .stair-bar {{ background: linear-gradient(180deg, rgba(255,255,255,.45), rgba(237,28,36,.22)); }}
    .stair:nth-child(1) .stair-bar {{ height: 40px; }}
    .stair:nth-child(2) .stair-bar {{ height: 130px; }}
    .stair:nth-child(3) .stair-bar {{ height: 210px; }}
    .stair:nth-child(4) .stair-bar {{ height: 280px; }}
    .stair-phase {{ margin-top: 14px; height: 34px; display: flex; align-items: center; justify-content: center; text-align: center; color: rgba(255,255,255,.72); font: 700 13px/1.15 "IBM Plex Sans"; }}
    .stair-gauge {{ margin-bottom: 12px; text-align: center; }}
    .step-gauge-tag {{ display: block; margin-bottom: 2px; color: rgba(255,255,255,.62); font: 900 10px/1 "IBM Plex Mono", monospace; text-transform: uppercase; letter-spacing: .1em; }}
    .stair-gauge svg {{ display: block; width: 96px; height: 62px; margin: 0 auto; overflow: visible; }}
    .stair-gauge path {{ fill: none; stroke-width: 11; stroke-linecap: round; }}
    .stair-gauge .gauge-red {{ stroke: #ef4444; }}
    .stair-gauge .gauge-yellow {{ stroke: #f59e0b; }}
    .stair-gauge .gauge-green {{ stroke: #84cc16; }}
    .stair-gauge .gauge-needle {{ stroke: white; stroke-width: 4; stroke-linecap: round; }}
    .stair-gauge circle {{ fill: white; }}
    .step-gauge-value {{ display: inline-block; margin-top: -12px; padding: 3px 14px; border-radius: 999px; background: rgba(12,10,10,.86); border: 1px solid rgba(255,255,255,.26); color: white; font: 900 10px/1 "IBM Plex Mono", monospace; text-transform: uppercase; letter-spacing: .05em; }}
    .projection-slide .slide-head {{ align-items: start; margin-bottom: 12px; }}
    .projection-slide h1 {{ font-size: 52px; margin-top: 12px; }}
    .projection-title-card {{ position: absolute; left: 96px; top: 215px; width: 230px; padding: 20px 22px; border-radius: 18px; background: rgba(255,255,255,.08); border: 1px solid rgba(255,255,255,.15); }}
    .projection-title-card span {{ display: block; color: rgba(255,255,255,.62); font: 900 11px/1 "IBM Plex Mono", monospace; text-transform: uppercase; margin-bottom: 10px; }}
    .projection-title-card strong {{ display: block; font-size: 28px; line-height: 1.02; }}
    .projection-table-wrap {{ position: absolute; left: 360px; top: 205px; width: 1010px; max-height: 650px; overflow: hidden; border-radius: 16px; border: 1px solid rgba(255,255,255,.22); background: rgba(0,0,0,.28); box-shadow: 0 24px 70px rgba(0,0,0,.24); }}
    .projection-table {{ width: 100%; border-collapse: collapse; table-layout: fixed; font: 800 11px/1.08 "IBM Plex Mono", monospace; color: white; }}
    .projection-table th, .projection-table td {{ border: 1px solid rgba(255,255,255,.30); padding: 5px 8px; text-align: center; height: 24px; }}
    .projection-table th {{ background: var(--red); text-transform: uppercase; font-size: 11px; }}
    .projection-table th:first-child, .projection-table td:first-child {{ width: 190px; text-align: left; background: rgba(255,255,255,.12); }}
    .projection-table tr:nth-child(even) td {{ background-color: rgba(255,255,255,.07); }}
    .projection-table td.good {{ background: #15803d !important; color: white; }}
    .projection-table td.warn {{ background: #d97706 !important; color: white; }}
    .projection-table td.bad {{ background: #dc2626 !important; color: white; }}
    .projection-empty {{ margin-top: 60px; padding: 34px; border-radius: 20px; border: 1px solid rgba(255,255,255,.20); background: rgba(255,255,255,.08); }}
    .objective-grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-top: 28px; }}
    .objective-card {{ min-height: 420px; display: flex; flex-direction: column; justify-content: space-between; }}
    .objective-card .value {{ font-size: 58px; }}
    .smart-card {{ margin-top: 24px; padding: 24px 28px; border-radius: 18px; border: 1px solid rgba(237,28,36,.14); background: rgba(237,28,36,.055); }}
    .smart-card h3 {{ margin-bottom: 8px; }}
    .smart-card p {{ margin: 0; color: var(--muted); font-size: 18px; line-height: 1.28; }}
    .risk-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; margin-top: 28px; }}
    .risk-grid .card {{ min-height: 160px; }}
    .risk-table-slide h1 {{ text-align: center; font-size: 54px; margin-bottom: 42px; }}
    .risk-table-wrap {{ width: 1110px; margin: 0 auto; border: 1px solid rgba(255,255,255,.72); background: linear-gradient(135deg, rgba(237,28,36,.18), rgba(41,0,0,.32)); box-shadow: 0 30px 80px rgba(0,0,0,.28); }}
    .risk-table {{ width: 100%; border-collapse: collapse; table-layout: fixed; color: white; }}
    .risk-table th, .risk-table td {{ border: 1px solid rgba(255,255,255,.72); vertical-align: top; text-align: left; }}
    .risk-table th {{ padding: 8px 10px; font-size: 20px; line-height: 1; font-style: italic; font-weight: 900; }}
    .risk-table td {{ padding: 9px 10px; font-size: 16px; line-height: 1.22; font-weight: 650; }}
    .risk-table .risk-item {{ width: 140px; color: white; font-style: italic; font-weight: 900; }}
    .risk-table .risk-premise {{ width: 390px; }}
    .risk-table .risk-risk {{ width: 335px; }}
    .risk-table .risk-impact {{ width: 240px; color: #fff2c9; font-size: 14px; line-height: 1.24; }}
    .risk-table tbody tr:last-child .risk-impact {{ color: #ffd166; }}
    .next-steps-slide h1 {{ font-size: 64px; margin-bottom: 30px; }}
    .next-steps-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; margin-top: 26px; }}
    .next-step-card {{ min-height: 430px; display: flex; flex-direction: column; justify-content: space-between; }}
    .next-step-card .rank {{ color: var(--red); font-size: 34px; }}
    .next-step-card p {{ color: var(--muted); font-size: 19px; line-height: 1.28; }}
    .next-owner {{ display: inline-flex; align-items: center; min-height: 36px; padding: 0 13px; border-radius: 999px; background: rgba(237,28,36,.08); color: var(--red); font: 900 12px/1 "IBM Plex Mono", monospace; text-transform: uppercase; }}
    .closing-slide {{ color: white; background: radial-gradient(circle at 78% 8%, rgba(237,28,36,.72), transparent 34%), linear-gradient(135deg, #090001 0%, #4c0608 68%, #ed1c24 100%); }}
    .closing-glass {{ position: absolute; right: -110px; top: 105px; width: 590px; height: 520px; border-radius: 120px; transform: rotate(-27deg); border: 2px solid rgba(255,255,255,.34); background: linear-gradient(135deg, rgba(255,255,255,.30), rgba(255,255,255,.04)); box-shadow: inset 0 0 70px rgba(255,255,255,.20), 0 30px 90px rgba(0,0,0,.30); }}
    .closing-content {{ position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; }}
    .closing-logo {{ width: 180px; height: 54px; object-fit: contain; margin-bottom: 36px; }}
    .closing-content h1 {{ font-size: 92px; line-height: .92; margin: 0 0 34px; }}
    .csat-pill {{ min-width: 390px; min-height: 72px; padding: 0 34px; border-radius: 999px; display: inline-flex; align-items: center; justify-content: center; gap: 18px; background: rgba(237,28,36,.72); color: white; font-size: 16px; }}
    .bars {{ display: grid; gap: 13px; }}
    .bar-row {{ display: grid; grid-template-columns: 96px 1fr 54px; gap: 12px; align-items: center; font-size: 15px; font-weight: 700; }}
    .track {{ height: 16px; border-radius: 999px; background: rgba(25,25,25,.10); overflow: hidden; }}
    .fill {{ height: 100%; border-radius: 999px; background: linear-gradient(90deg, var(--red), #ff481f); }}
    .footer-logo {{ position: absolute; left: 96px; bottom: 38px; z-index: 8; width: 190px; height: 50px; display: flex; align-items: center; }}
    .footer-logo img {{ max-width: 190px; max-height: 50px; object-fit: contain; }}
    .nav {{ position: absolute; right: 70px; bottom: 34px; z-index: 20; display: flex; gap: 12px; }}
    .nav button {{ width: 48px; height: 48px; border: none; border-radius: 999px; background: rgba(255,255,255,.92); color: #111; font-size: 30px; cursor: pointer; }}
    .nav button:disabled {{ opacity: .35; cursor: default; }}
    .counter {{ position: absolute; right: 240px; bottom: 52px; z-index: 20; color: rgba(25,25,25,.48); font: 800 12px/1 "IBM Plex Mono", monospace; }}
    .dark ~ .counter, .red ~ .counter {{ color: rgba(255,255,255,.55); }}
    .progress {{ position: absolute; left: 0; bottom: 0; height: 7px; width: 100%; background: rgba(255,255,255,.22); z-index: 18; }}
    .progress span {{ display: block; height: 100%; width: 0; background: linear-gradient(90deg, var(--red), #ff481f); }}
    @media (prefers-reduced-motion: reduce) {{
      *, *::before, *::after {{ animation-duration: .01ms !important; animation-iteration-count: 1 !important; scroll-behavior: auto !important; transition-duration: .01ms !important; }}
    }}
  </style>
</head>
<body>
  <div id="deck">
    <section class="slide red">
      <div class="cover-client">{CLIENT_LOGO_HTML}</div>
      <div class="cover-title">
        <h1>Diagnóstico de saída</h1>
        <p>{CLIENT_NAME} | Q2 2026</p>
      </div>
      <div class="orb" style="width:420px;height:420px;right:-70px;top:-120px"></div>
      <div class="orb" style="width:260px;height:260px;right:300px;top:100px"></div>
    </section>

    <section class="slide dark">
      <h1 class="visually-hidden">ROPRE Resultados Performance</h1>
      <div class="summary-bg"></div>
      <div class="summary-title">
        <div class="small">ROPRE</div>
        <div class="big">Resultados</div>
        <div class="big" style="font-size:60px;margin-top:14px">Performance</div>
      </div>
      <div class="summary-menu">
        <div class="menu-row active"><div class="menu-num">01</div><div class="menu-card"><strong>Resultados</strong><div class="sub"><span>Gerais</span><span>Funil</span><span>Canais</span><span>Gargalos</span><span>Lições</span></div></div></div>
        <div class="menu-row"><div class="menu-num">02</div><div class="menu-card"><strong>Objetivos</strong><div class="sub"><span>Quarter fechado</span><span>Próximo quarter</span><span>Projeção Q3</span></div></div></div>
        <div class="menu-row"><div class="menu-num">03</div><div class="menu-card"><strong>Premissas e riscos</strong></div></div>
        <div class="menu-row"><div class="menu-num">04</div><div class="menu-card"><strong>Entregas</strong><div class="sub"><span>Realizadas</span><span>Previstas</span><span>Revisão do backlog</span></div></div></div>
        <div class="menu-row"><div class="menu-num">05</div><div class="menu-card"><strong>Próximos passos</strong></div></div>
      </div>
    </section>

    {funnel_slide("Q2 vs marco", "Q2 | Funil versus Marcos", "R$ 8.400,76", "R$ 9.000,00", q2_stages, restriction="SDR IA + SQL para Venda + gestão")}

    <section class="slide">
      <span class="eyebrow">Resultados | Funil mês a mês</span>
      <h1>Q2 2026 mês a mês</h1>
      <table class="table">
        <thead><tr><th>Mês</th><th class="num">Invest. (GP)</th><th class="num">Leads</th><th class="num">MQL</th><th class="num">SQL</th><th class="num">Vendas</th><th class="num">Receita</th></tr></thead>
        <tbody>
          <tr><td>Abril</td><td class="num">R$ 2.803,03</td><td class="num">55</td><td class="num">10</td><td class="num">5</td><td class="num">2</td><td class="num">R$ 24.992</td></tr>
          <tr><td>Maio</td><td class="num">R$ 1.978,66</td><td class="num">69</td><td class="num">7</td><td class="num">6</td><td class="num">0</td><td class="num">R$ 0</td></tr>
          <tr><td>Junho</td><td class="num">R$ 3.619,07</td><td class="num">89</td><td class="num">35</td><td class="num">12</td><td class="num">1</td><td class="num">R$ 13.221</td></tr>
          <tr><td><strong>Total Q2</strong></td><td class="num"><strong>R$ 8.400,76</strong></td><td class="num"><strong>213</strong></td><td class="num"><strong>52</strong></td><td class="num"><strong>23</strong></td><td class="num"><strong>3</strong></td><td class="num"><strong>R$ 38.213</strong></td></tr>
        </tbody>
      </table>
      <div class="cards grid-3" style="margin-top:22px">
        <div class="card"><h3>Abril carregou a receita</h3><p class="label">2 vendas e R$ 24.992; maio zerou vendas mesmo com 69 leads e CPL Google saudável.</p></div>
        <div class="card"><h3>Junho subiu MQL</h3><p class="label">Lead para MQL foi a 39,3% e SQL a 12, mas SQL para Venda ficou em 8,3%.</p></div>
        <div class="card"><h3>Investimento em 93%</h3><p class="label">R$ 8.401 de R$ 9.000 projetados: mídia não faltou; o funil morreu na qualificação e no fechamento.</p></div>
      </div>
    </section>

    <section class="slide quarter-slide">
      <span class="eyebrow">Resultados gerais</span>
      <h1>Meta versus Google</h1>
      <div class="quarter-layout">
        {mini_funnel("Meta Q2", "R$ 2.494", q1_compact)}
        {mini_funnel("Google Q2", "R$ 5.907", q2_compact)}
        <aside class="reading-panel">
          <div>
            <h3>O que mudou</h3>
            <div class="reading-block">
              <div class="reading-item good"><span>Volume</span><strong>Mídia entregou</strong><p>211 leads/conv reais nos canais; pacing de invest. em 93% do marco de R$ 9k.</p></div>
              <div class="reading-item bad"><span>Piorou</span><strong>CPL sem venda</strong><p>PMax GERAL CPL R$ 21,71 e zero vendas; Search Core e PMax 05/06 venderam.</p></div>
              <div class="reading-item bad"><span>Travou</span><strong>SDR IA e fechamento</strong><p>72% dos leads IA parados; SQL para Venda em 13% no quarter (maio 0%).</p></div>
            </div>
          </div>
          <div class="sub">Observação: gap Total GP vs soma de canais (+23 MQL, +16 SQL, +1 venda) por mês de atingimento diferente do mês de entrada.</div>
        </aside>
      </div>
    </section>

    <section class="slide white">
      <span class="eyebrow">Resultados | Meta Ads</span>
      <h1>Meta Ads | Campanhas do Q2</h1>
      <table class="table">
        <thead><tr><th>Campanha</th><th class="num">Invest.</th><th class="num">Leads</th><th class="num">CPL</th><th>Leitura</th></tr></thead>
        <tbody>
          <tr><td>TESTE ABO TF</td><td class="num">R$ 336,36</td><td class="num">22</td><td class="num">R$ 15,29</td><td>1 venda | R$ 6.619</td></tr>
          <tr><td>TESTE ABO</td><td class="num">R$ 287,57</td><td class="num">15</td><td class="num">R$ 19,17</td><td>Sem venda</td></tr>
          <tr><td>ABO Vivência 03</td><td class="num">R$ 992,39</td><td class="num">37</td><td class="num">R$ 26,82</td><td>Maior volume Meta</td></tr>
          <tr><td>ABO Vivência 02 LKL</td><td class="num">R$ 877,37</td><td class="num">12</td><td class="num">R$ 73,11</td><td>Pior CPL relevante</td></tr>
          <tr><td><strong>Total Meta Q2</strong></td><td class="num"><strong>R$ 2.493,69</strong></td><td class="num"><strong>87</strong></td><td class="num"><strong>R$ 28,66</strong></td><td></td></tr>
        </tbody>
      </table>
      <p class="label" style="margin-top:14px">CPL Meta caiu de R$ 36,78 em abril para R$ 24,33 em junho. Canal barato em lead, fraco em SQL (MQL para SQL 10%).</p>
    </section>

    <section class="slide">
      <span class="eyebrow">Resultados | Google Ads</span>
      <h1>Google Ads | Campanhas do Q2</h1>
      <table class="table">
        <thead><tr><th>Campanha</th><th class="num">Invest.</th><th class="num">Conv.</th><th class="num">CPL</th><th>Venda / Receita</th></tr></thead>
        <tbody>
          <tr><td>PMAX GERAL LP 01/04</td><td class="num">R$ 1.475,95</td><td class="num">68</td><td class="num">R$ 21,71</td><td>0 | R$ 0</td></tr>
          <tr><td>PMAX 05/06</td><td class="num">R$ 1.242,86</td><td class="num">34</td><td class="num">R$ 36,55</td><td>1 | R$ 13.221</td></tr>
          <tr><td>SEARCH LEADS LP1 CORE</td><td class="num">R$ 1.824,21</td><td class="num">17</td><td class="num">R$ 107,31</td><td>1 | R$ 13.441</td></tr>
          <tr><td><strong>Total Google Q2</strong></td><td class="num"><strong>R$ 5.907,07</strong></td><td class="num"><strong>124</strong></td><td class="num"><strong>R$ 47,64</strong></td><td></td></tr>
        </tbody>
      </table>
      <p class="label" style="margin-top:16px">PMax concentrou 82% das conversões. Melhor CPL do quarter (PMax GERAL) não vendeu; keyword área de vivência nr 31 fechou R$ 13.441 no Search Core.</p>
    </section>

    <section class="slide white">
      <span class="eyebrow">Resultados | Eficiência e sentimento</span>
      <h1>Eficiência, BE e CSAT</h1>
      <div class="cards grid-4" style="margin-top:24px">
        <div class="card metric"><div class="label">Google Q | CPL</div><div class="value">R$ 47,64</div><div class="sub">R$ 5.907 | 124 conv</div></div>
        <div class="card metric"><div class="label">Meta Q | CPL</div><div class="value">R$ 28,66</div><div class="sub">R$ 2.494 | 87 leads</div></div>
        <div class="card metric"><div class="label">SQL -> Venda</div><div class="value">13%</div><div class="sub">maio 0% | restrição</div></div>
        <div class="card metric"><div class="label">SDR IA travada</div><div class="value">72%</div><div class="sub">104 de 145 leads</div></div>
      </div>
      <div class="cards grid-4" style="margin-top:24px">
        <div class="card metric"><div class="label">Resultado BE</div><div class="value">-R$ 83k</div><div class="sub">BE no mês 35</div></div>
        <div class="card metric"><div class="label">BE / mês</div><div class="value">R$ 52,5k</div><div class="sub">competência</div></div>
        <div class="card metric"><div class="label">NPS</div><div class="value">5</div><div class="sub">MHS Indiferente</div></div>
        <div class="card metric"><div class="label">CSAT Campanhas</div><div class="value">1/5</div><div class="sub">criativos IA rejeitados</div></div>
      </div>
      <p class="label" style="margin-top:22px">Churn pedido em 28/05 e concluído em 09/07. Este deck é lição organizacional Invictus, não plano de retenção da Florestec.</p>
    </section>

    <section class="slide">
      <span class="eyebrow">Análise</span>
      <h1>Gargalos identificados</h1>
      <div class="constraint-layout">
        <div class="card metric constraint-main">
          <div class="label">Restrição principal</div>
          <div class="constraint-value">SDR IA + SQL-Venda</div>
          <div class="sub">72% travados | 13% fecha</div>
          <p>Mídia gerou volume; o funil morreu na SDR IA, no fechamento e na gestão (troca de AM, tracking tardio, otimização por CPL sem venda).</p>
        </div>
        <div class="card metric"><div class="label">SQL -> Venda</div><div class="value">13%</div><div class="sub">3 vendas em 23 SQLs</div></div>
        <div class="card metric"><div class="label">PMax melhor CPL</div><div class="value">0</div><div class="sub">vendas | CPL R$ 21,71</div></div>
        <div class="card metric"><div class="label">Invest. pacing</div><div class="value">93%</div><div class="sub">não é falta de lead</div></div>
      </div>
      <div class="cards grid-3" style="margin-top:22px">
        <div class="card"><h3>Causa provável</h3><p class="label">Fila IA sem SLA, ranking por CPL sem SQL/venda, tracking só pós-churn e expectativa R$ 40k vs BE cliente R$ 75k.</p></div>
        <div class="card"><h3>O que não é gargalo</h3><p class="label">Volume de mídia (213 leads GP), Google estável com PMax e tendência de CPL Meta de R$ 36 para R$ 24.</p></div>
        <div class="card"><h3>Leitura</h3><p class="label">Diagnóstico de saída: padronizar SDR IA, ranking por venda, tracking no onboarding e 1 AM por quarter na Invictus.</p></div>
      </div>
    </section>

    {''.join(action_slides)}

    {section_menu_slide("02", "Objetivos", "Lições Invictus", "red")}

    <section class="slide">
      <span class="eyebrow">Objetivos | Quarter fechado</span>
      <h1>O que Q2 bateu e o que ficou devendo</h1>
      <div class="objective-grid">
        <div class="card objective-card">
          <div><h3>Bateu</h3><p class="label">Pacing de mídia em 93%, Google com Search Core e PMax 05/06 gerando receita, e CPL Meta em queda ao longo do quarter.</p></div>
          <div><div class="value">213</div><div class="sub">leads no Growth Pack</div></div>
        </div>
        <div class="card objective-card">
          <div><h3>Ficou devendo</h3><p class="label">Só 3 vendas, SQL para Venda em 13%, BE em -R$ 83k (mês 35), NPS 5 e CSAT Campanhas 1/5.</p></div>
          <div><div class="value">Churn</div><div class="sub">28/05 para 09/07</div></div>
        </div>
        <div class="card objective-card">
          <div><h3>Alinhamento</h3><p class="label">Plano = lições Invictus (SDR, ranking, tracking, AM, meta/BE, QA criativo), não KRs de retenção do cliente.</p></div>
          <div><div class="value">Org</div><div class="sub">restrição sistêmica</div></div>
        </div>
      </div>
    </section>

    <section class="slide">
      <span class="eyebrow">Objetivos</span>
      <h1>Objetivos do próximo quarter (Invictus)</h1>
      <div class="smart-card">
        <h3>Objetivo SMART</h3>
        <p>Até 30/09/2026, todo projeto Invictus com Kommo e SDR IA terá: (a) alerta se mais de 30% dos leads pararem em Ativado IA por 7 dias; (b) dashboard de campanha com venda e SQL; (c) GTM e conversões no onboarding; (d) 1 AM titular por quarter.</p>
      </div>
      <div class="cards grid-4" style="margin-top:24px">
        <div class="card metric"><div class="label">Alerta SDR IA</div><div class="value">30%</div><div class="sub">fila parada | 7 dias</div></div>
        <div class="card metric"><div class="label">Ranking mídia</div><div class="value">SQL/venda</div><div class="sub">não só CPL</div></div>
        <div class="card metric"><div class="label">Tracking</div><div class="value">Onboarding</div><div class="sub">antes do mês 2</div></div>
        <div class="card metric"><div class="label">AM titular</div><div class="value">1</div><div class="sub">por quarter</div></div>
      </div>
      <div class="cards grid-3" style="margin-top:28px">
        <div class="card"><h3>KR 1</h3><p class="label">Alerta de fila SDR IA ativo em 100% dos projetos Kommo+SDR IA.</p></div>
        <div class="card"><h3>KR 2</h3><p class="label">Dashboard campanha com SQL e venda no checklist de growth.</p></div>
        <div class="card"><h3>KR 3</h3><p class="label">GTM e conversões validados no onboarding, antes do mês 2.</p></div>
        <div class="card"><h3>KR 4</h3><p class="label">1 AM titular por quarter, com handoff formal se houver troca.</p></div>
        <div class="card"><h3>KR 5</h3><p class="label">Meta de fat. alinhada ao BE do cliente documentado na proposta.</p></div>
        <div class="card"><h3>KR 6</h3><p class="label">QA de criativo vs produto real obrigatório antes de veicular.</p></div>
      </div>
    </section>

    {projection_slide("cenarios-breakeven.csv", "CENÁRIOS", "Q2 | Cenários do breakeven (saída)")}

    {section_menu_slide("03", "Premissas", "e riscos", "dark")}

    <section class="slide red risk-table-slide">
      <h1>Premissas e Riscos</h1>
      <div class="risk-table-wrap">
        <table class="risk-table">
          <thead>
            <tr><th>Item</th><th>Premissa</th><th>Risco</th><th>Impacto</th></tr>
          </thead>
          <tbody>
            <tr>
              <td class="risk-item">1 | Narrativa</td>
              <td class="risk-premise">Diagnóstico interno assume SDR IA e gestão como causa, não só mídia.</td>
              <td class="risk-risk">Narrativa distorcida ("mídia não performa") se espalha sem o funil.</td>
              <td class="risk-impact">Alto | Lição errada vira padrão em outros B2B.</td>
            </tr>
            <tr>
              <td class="risk-item">2 | SDR IA</td>
              <td class="risk-premise">SLA e alerta de fila travada implantados até 30/09/2026.</td>
              <td class="risk-risk">Outros clientes repetem 70%+ de leads parados em Ativado IA.</td>
              <td class="risk-impact">Alto | Volume de mídia queima sem SQL.</td>
            </tr>
            <tr>
              <td class="risk-item">3 | Ranking</td>
              <td class="risk-premise">Campanhas ranqueadas por SQL/venda, não só CPL.</td>
              <td class="risk-risk">Vencedores de CPL sem venda continuam recebendo verba.</td>
              <td class="risk-impact">Alto | Mesmo padrão PMax GERAL (CPL baixo, 0 venda).</td>
            </tr>
            <tr>
              <td class="risk-item">4 | Tracking</td>
              <td class="risk-premise">GTM e CRM no onboarding, nunca só no churn.</td>
              <td class="risk-risk">Diagnóstico chega 20+ dias depois da ruptura.</td>
              <td class="risk-impact">Médio / Alto | Decisão cega e CSAT baixo.</td>
            </tr>
            <tr>
              <td class="risk-item">5 | Expectativa</td>
              <td class="risk-premise">BE do cliente documentado no kickoff e meta alinhada.</td>
              <td class="risk-risk">Meta V4 (R$ 40k) vs BE cliente (R$ 75k) gera crise de percepção.</td>
              <td class="risk-impact">Alto | Churn por desalinhamento, não só por CPL.</td>
            </tr>
            <tr>
              <td class="risk-item">6 | Criativo</td>
              <td class="risk-premise">QA de produto real obrigatório antes de veicular IA.</td>
              <td class="risk-risk">CSAT Campanhas 1/5 se repete com rejeição de criativo.</td>
              <td class="risk-impact">Médio | Relacionamento e confiança no time criativo.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    {section_menu_slide("04", "Entregas", "Execução")}

    <section class="slide">
      <span class="eyebrow">Entregas</span>
      <h1>37 entregas reais no Q2</h1>
      <div class="cards grid-2" style="margin-top:28px">
        <div class="card">
          <h3>Pontos de atenção</h3>
          <div class="bars">
            <div class="bar-row"><span>Entregas reais</span><div class="track"><div class="fill" style="width:44%"></div></div><span>37/84</span></div>
            <div class="bar-row"><span>Tracking/GTM</span><div class="track"><div class="fill" style="width:100%"></div></div><span>22/06</span></div>
            <div class="bar-row"><span>Abril (reais)</span><div class="track"><div class="fill" style="width:14%"></div></div><span>5</span></div>
            <div class="bar-row"><span>Board</span><div class="track"><div class="fill" style="width:40%"></div></div><span>Atrasado</span></div>
            <div class="bar-row"><span>Score V4</span><div class="track"><div class="fill" style="width:60%"></div></div><span>3/5</span></div>
          </div>
        </div>
        <div class="card">
          <h3>Equipe e sentimento</h3>
          <div class="bars">
            <div class="bar-row"><span>AMs no Q2</span><div class="track"><div class="fill" style="width:100%"></div></div><span>3</span></div>
            <div class="bar-row"><span>NPS</span><div class="track"><div class="fill" style="width:50%"></div></div><span>5</span></div>
            <div class="bar-row"><span>CSAT Campanhas</span><div class="track"><div class="fill" style="width:20%"></div></div><span>1/5</span></div>
            <div class="bar-row"><span>MHS</span><div class="track"><div class="fill" style="width:40%"></div></div><span>Indiferente</span></div>
            <div class="bar-row"><span>WA</span><div class="track"><div class="fill" style="width:50%"></div></div><span>Cuidado</span></div>
          </div>
        </div>
      </div>
      <table class="table">
        <thead><tr><th>Ponto de atenção</th><th>Evidência</th><th>Fonte</th></tr></thead>
        <tbody>
          <tr><td>Tracking só pós-churn</td><td>GTM e conversões concentrados em 22/06 (churn pedido 28/05)</td><td>Ekyte</td></tr>
          <tr><td>Troca de AM sem estabilidade</td><td>Isabela, Melissa e Gabriela no mesmo quarter</td><td>Operação</td></tr>
          <tr><td>Criativos rejeitados</td><td>CSAT Campanhas 1/5; IA sem QA de produto real</td><td>CSAT + WA</td></tr>
        </tbody>
      </table>
    </section>

    {section_menu_slide("05", "Próximos", "Passos", "dark")}

    <section class="slide next-steps-slide">
      <span class="eyebrow">Próximos passos</span>
      <h1>Lições para a Invictus</h1>
      <div class="next-steps-grid">
        <div class="card next-step-card">
          <div>
            <div class="rank">01</div>
            <h3>Alerta SDR IA</h3>
            <p>Implantar SLA e alerta de fila travada em todos os projetos Kommo com SDR IA.</p>
          </div>
          <span class="next-owner">Dono | Produto SDR + Coord</span>
        </div>
        <div class="card next-step-card">
          <div>
            <div class="rank">02</div>
            <h3>Ranking por venda</h3>
            <p>Dashboard de campanha com SQL/venda no checklist; banir otimização só por CPL.</p>
          </div>
          <span class="next-owner">Dono | Paid + PM</span>
        </div>
        <div class="card next-step-card">
          <div>
            <div class="rank">03</div>
            <h3>Onboarding e AM</h3>
            <p>Tracking no onboarding, 1 AM por quarter e meta alinhada ao BE do cliente na proposta.</p>
          </div>
          <span class="next-owner">Dono | Coord + Comercial V4</span>
        </div>
      </div>
    </section>

    <section class="slide closing-slide no-footer">
      <div class="closing-glass"></div>
      <div class="closing-content">
        <img class="closing-logo" src="{COLLI_WHITE}" alt="Colli&Co">
        <h1>Obrigado!</h1>
        <div class="csat-pill">Avalie este check-in em nosso CSAT</div>
      </div>
    </section>

    <div class="footer-logo"><img id="footerLogo" src="{COLLI_RED}" alt="Colli&Co"></div>
    <div class="counter" id="counter">01 / 13</div>
    <div class="nav"><button id="prevBtn" data-testid="prev-slide" aria-label="Anterior">‹</button><button id="nextBtn" data-testid="next-slide" aria-label="Próximo">›</button></div>
    <div class="progress"><span id="progress" class="progress-fill"></span></div>
  </div>
  <script>
    const deck = document.getElementById("deck");
    const slides = Array.from(document.querySelectorAll(".slide"));
    const prevBtn = document.getElementById("prevBtn");
    const nextBtn = document.getElementById("nextBtn");
    const counter = document.getElementById("counter");
    const progress = document.getElementById("progress");
    const footerLogo = document.getElementById("footerLogo");
    const colliRed = "{COLLI_RED}";
    const colliWhite = "{COLLI_WHITE}";
    let current = 0;
    const creativeVideos = Array.from(document.querySelectorAll(".creative-video"));
    document.querySelectorAll(".creative-video-shell").forEach((shell) => {{
      const video = shell.querySelector("video");
      const syncState = () => shell.classList.toggle("is-playing", video && !video.paused);
      shell.addEventListener("click", (event) => {{
        if (!video || event.target.closest(".creative-open-video")) return;
        event.preventDefault();
        if (video.paused) {{
          creativeVideos.forEach((other) => {{ if (other !== video) other.pause(); }});
          video.play().catch(() => {{}});
        }} else {{
          video.pause();
        }}
        syncState();
      }});
      video?.addEventListener("play", syncState);
      video?.addEventListener("pause", syncState);
      video?.addEventListener("ended", syncState);
    }});
    function fitDeck() {{
      const vw = window.visualViewport?.width || document.documentElement.clientWidth || window.innerWidth;
      const vh = window.visualViewport?.height || document.documentElement.clientHeight || window.innerHeight;
      const scale = Math.max(.1, Math.min((vw - 16) / 1600, (vh - 16) / 900, 1));
      deck.style.setProperty("--scale", scale);
    }}
    function show(index) {{
      current = Math.max(0, Math.min(index, slides.length - 1));
      slides.forEach((slide, i) => slide.classList.toggle("active", i === current));
      document.querySelectorAll(".slide:not(.active) video").forEach((video) => video.pause());
      counter.textContent = String(current + 1).padStart(2, "0") + " / " + String(slides.length).padStart(2, "0");
      progress.style.width = ((current + 1) / slides.length * 100) + "%";
      prevBtn.disabled = current === 0;
      nextBtn.disabled = current === slides.length - 1;
      const dark = slides[current].classList.contains("dark") || slides[current].classList.contains("red");
      footerLogo.src = dark ? colliWhite : colliRed;
      footerLogo.parentElement.style.opacity = slides[current].classList.contains("no-footer") ? "0" : "1";
      counter.style.color = dark ? "rgba(255,255,255,.55)" : "rgba(25,25,25,.48)";
    }}
    prevBtn.addEventListener("click", () => show(current - 1));
    nextBtn.addEventListener("click", () => show(current + 1));
    window.addEventListener("keydown", (event) => {{
      if (event.key === "ArrowRight") show(current + 1);
      if (event.key === "ArrowLeft") show(current - 1);
    }});
    window.addEventListener("resize", fitDeck);
    fitDeck();
    show(0);
  </script>
</body>
</html>
"""

(ROOT / "index.html").write_text(html, encoding="utf-8")
print(ROOT / "index.html")
