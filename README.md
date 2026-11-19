# Radar KRL de Supply Chain (demonstração)

Projeto demonstrativo de Kelvin Raial (Kelvin Barbosa da Silva). **KRL é uma empresa fictícia.** Câmbio, juros e inflação vêm do Banco Central e se atualizam sozinhos em dias úteis; as notícias são exemplos estáticos, com fonte e data em cada card.

## Estrutura

| Caminho | Função |
| --- | --- |
| `index.html` | Página do site (HTML, CSS e JavaScript) |
| `data.json` | Dados da edição; a página lê este arquivo ao abrir |
| `img/` | Fotos, logo e ícone |
| `scripts/coletar_indicadores.py` | Busca as séries do Banco Central e atualiza o `data.json` |
| `.github/workflows/atualizar.yml` | Roda o script em dias úteis às 7h40 (Brasília) e salva o resultado |
| `.nojekyll` | Faz o GitHub Pages servir os arquivos como estão |

## Publicar no GitHub (cerca de 10 minutos, tudo pelo navegador)

1. Crie uma conta em github.com, se ainda não tiver.
2. Clique em **New repository**. Nome sugerido: `radar-supply-chain`. Marque **Public** e crie.
3. Na página do repositório, clique em **uploading an existing file** e arraste **todo o conteúdo** desta pasta, inclusive as pastas `img`, `scripts` e `.github`. Clique em **Commit changes**.
   - Se o navegador não mostrar a pasta `.github` (pastas que começam com ponto ficam ocultas), use **Add file → Create new file**, digite o nome `.github/workflows/atualizar.yml` e cole o conteúdo do arquivo.
4. Vá em **Settings → Pages**. Em *Source*, escolha **Deploy from a branch**, branch **main**, pasta **/ (root)**, e salve. Em 1 a 2 minutos o site fica no ar em `https://SEU-USUARIO.github.io/radar-supply-chain/`.
5. Vá em **Settings → Actions → General → Workflow permissions** e marque **Read and write permissions**. Sem isso, a atualização automática não consegue salvar os dados.
6. Teste a atualização: aba **Actions → Atualizar indicadores → Run workflow**. Ao terminar (ícone verde), recarregue o site: a data da edição e o câmbio devem mudar.

A partir daí, o GitHub roda sozinho de segunda a sexta. Custo: zero (repositório público).

## Observações

- O GitHub pode atrasar execuções agendadas em alguns minutos; isso é normal.
- Depois de 60 dias sem nenhum commit no repositório, o GitHub pausa os agendamentos. Como o próprio fluxo faz um commit por dia útil, isso só acontece se a coleta falhar por muito tempo.
- Para notícias automáticas seria preciso uma chave de API de IA (com custo); não está incluída nesta versão.
