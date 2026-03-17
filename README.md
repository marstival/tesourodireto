# tesourodireto

Histórico interativo de preços e taxas do Tesouro Direto.

Visualize a **taxa de compra** (% a.a.) e o **preço unitário** (PU, R$) para qualquer título e vencimento disponível desde 2004.

**Fonte:** [Tesouro Transparente](https://www.tesourotransparente.gov.br/ckan/dataset/taxas-dos-titulos-ofertados-pelo-tesouro-direto/) — atualizado diariamente pelo Tesouro Nacional.

---

## Opção 1 — GitHub Pages (sem instalação)

Acesse diretamente no browser, sem precisar rodar nada:

**[https://marstival.github.io/tesourodireto/](https://marstival.github.io/tesourodireto/)**

Os dados são atualizados automaticamente todo dia útil via GitHub Actions.

> **Para ativar em um fork:** vá em *Settings → Pages → Source* e selecione
> **Branch: `main` / Folder: `/docs`**.

---

## Opção 2 — Google Colab

<a href="https://colab.research.google.com/github/marstival/tesourodireto/blob/main/src/TesouroPrecoTaxa.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

Clique no badge, execute *Runtime → Run all* e use os menus para explorar.

---

## Opção 3 — Jupyter local

```bash
git clone https://github.com/marstival/tesourodireto.git
cd tesourodireto

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

jupyter notebook src/TesouroPrecoTaxa.ipynb
```

Execute *Kernel → Restart & Run All* e use os menus interativos.

---

## Gerar o JSON de dados manualmente

O script `src/build.py` baixa o CSV e produz `docs/data/tesouro.json`
(usado pelo site GitHub Pages):

```bash
source .venv/bin/activate
python src/build.py
```

O download é ignorado se o arquivo já foi baixado hoje.

---

## Estrutura do projeto

```
src/
  build.py                  # pipeline: CSV → docs/data/tesouro.json
  TesouroPrecoTaxa.ipynb    # notebook interativo
  tesouro.py                # script pontual (gera src/fig1.html)
docs/
  index.html                # site estático (GitHub Pages)
  data/
    tesouro.json            # dados gerados pelo build.py
data/
  PrecoTaxaTesouroDireto.csv  # cache local do CSV
.github/
  workflows/
    update.yml              # Actions: atualiza dados diariamente
```
