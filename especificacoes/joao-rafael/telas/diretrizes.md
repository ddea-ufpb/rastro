# Diretrizes globais da interface — Rastro

Valem para todas as fichas. As fichas não repetem estas diretrizes; registram só o que é próprio de cada tela.

## Público

| Quem | Situação de uso | O que espera da interface |
| :-- | :-- | :-- |
| Morador | Ouviu falar de uma emenda para a cidade; abre no celular, muitas vezes por link compartilhado | Achar a cidade em um passo e ler a fase numa frase ("O dinheiro foi reservado e ainda não foi pago"), com o termo técnico ao lado |
| Jornalista / controle social | Investiga por dias no computador; precisa citar | Números exatos, a linha do arquivo de onde cada valor saiu, export em CSV e a API |
| Gestor municipal | Rotina mensal na prefeitura | Ver o que está empenhado e não pago para o município e receber aviso por e-mail quando a fase mudar |
| Operador de dados | Terminal, uma vez por dia ou quando a fonte muda | Saber se a importação foi publicada, por que falhou e o que precisa revisar |

## Plataforma e orientação

- **Interface web** (telas P e S): SPA responsiva (ADR-0008).
  - Celular em retrato a partir de 360 px, prioridade do morador.
  - Desktop a partir de 1280 px, prioridade do jornalista.
  - Tabelas largas rolam dentro do próprio contêiner no celular.
- **E-mail** (S03): texto simples + HTML, legível sem imagens, largura máxima 600 px.
- **Terminal** (telas O): 80 colunas, legível sem cor, saída `--json`.
- Toda consulta tem URL estável com os filtros na query string (`/emendas?municipio_ibge=2507507&fase=empenhada`), para compartilhar e citar.

## Tom de voz

- **Factual.** Verbos do registro: "reservou", "conferiu a entrega", "pagou", "recebeu". Nunca as palavras do REQ-82.
- **Primeiro o simples, depois o técnico.** "O dinheiro foi reservado e ainda não foi pago (empenhada)".
- **Neutro com pessoas e entidades.** Nomes como a fonte publica, sem adjetivo, sem cor de alarme, sem posição.
- **Diz o que não sabe.** "A fonte não informa o município" em vez de esconder a linha.
- Frases curtas, voz ativa, segunda pessoa quando fala com o usuário.

## Princípios verificáveis

1. **Todo valor leva à linha de origem.** Cada valor monetário abre, em um toque, o painel "Origem" com fonte, arquivo, linha, data de extração, importação e link do download oficial; toda tela com dado mostra a faixa de proveniência (REQ-29, REQ-75). *Verificação:* `e2e/proveniencia.spec.ts` percorre os valores das telas P.
2. **Nada é somado com o que não é igual.** Etapas (empenhado, liquidado, pago), "destinado à cidade" e "recebido por entidades da cidade", e CNPJs de uma sugestão aparecem sempre separados, sem rótulo "Total" que os junte (REQ-37, REQ-42, ADR-0010). *Verificação:* `e2e/sem-soma.spec.ts`.
3. **Fase em linguagem simples, termo técnico ao lado, texto vindo da API.** A interface não tem nenhuma frase de fase no código; mostra `texto_simples`, `termo_oficial` e "tradução v`traducao_versao`" com link para P10 (REQ-31, ADR-0005). *Verificação:* `e2e/traducao.spec.ts`.
4. **Nada some sem explicação.** Onde há resultado, há a contagem de linhas da fonte que não entraram e o motivo (REQ-26, REQ-47, ADR-0009). "Nenhuma emenda" nunca aparece sem "N linhas descartadas" ao lado quando N > 0. *Verificação:* `e2e/descartes.spec.ts`.
5. **Nenhuma conclusão que o dado não sustenta.** O aviso do REQ-83 está em toda tela com valores; nenhuma lista de parlamentares é ordenada por valor (REQ-52); nenhuma palavra do REQ-82 aparece. *Verificação:* `e2e/linguagem.spec.ts`.

## Referência visual

- **Ideia central: o recibo.** Cada valor é uma linha de recibo: rótulo à esquerda, valor à direita em algarismos tabulares, e um pequeno carimbo "Origem" que abre a proveniência. Blocos que não se somam ficam em recibos separados, com um corte serrilhado entre eles.
- **Tipografia:** IBM Plex Sans (interface) e IBM Plex Mono (código da emenda, CNPJ, hash, CLI). Corpo de 16 px; escala 13/16/20/25/31/39.
- **Paleta:** papel `#FAF8F3`, tinta `#1B1F23`, texto secundário `#4A5560`, ação e link `#0B5563`, foco `#C2410C` (anel de 3 px). Fases usam um ícone e o rótulo escrito; a cor de fundo da etiqueta é só reforço (WCAG 1.4.1). Contrastes conferidos em `../verificar.py` (texto ≥ 4,5:1 sobre o papel).
- **Inspira:** a clareza de sites públicos de dados (GOV.UK Design System para formulários e erros; tabelas numéricas alinhadas à direita).
- **Evitar:** velocímetros, pizzas, mapas de calor; vermelho ligado a pessoas; listas de "maiores"; emoji; gradientes.
- **Gráficos:** só barras simples, sempre com a tabela equivalente.
- **Layout fino:** fica para a implementação. As fichas especificam intenção, não pixel.

## Idioma e formatos

- pt-BR em toda a interface (`<html lang="pt-BR">`).
- Moeda: `R$ 1.234.567,89`; abreviada `R$ 1,2 mi` só em cartões, com o valor exato no rótulo acessível.
- Datas `dd/mm/aaaa`; mês de pagamento `mm/aaaa`; data e hora `dd/mm/aaaa, hh:mm`.
- Código da emenda (12 dígitos) e CNPJ (`00.000.000/0000-00`) em fonte monoespaçada, com botão "copiar".
- Nomes de autores, favorecidos e municípios como publicados; município em caixa de título na exibição ("Campina Grande").

## Acessibilidade (piso: WCAG 2.2 AA, REQ-80)

- Contraste de texto ≥ 4,5:1; componentes e gráficos ≥ 3:1.
- Teclado completo, foco visível, ordem de foco igual à visual, link "Pular para o conteúdo".
- Alvos ≥ 24×24 px (44 px no celular).
- Cor nunca é o único meio: fase tem ícone e texto.
- Gráfico tem tabela equivalente e resumo em texto.
- Mensagens de estado por `aria-live="polite"`.
- Formulários com rótulo visível, erro junto ao campo e resumo de erros no topo.
- `prefers-reduced-motion` e `prefers-color-scheme` respeitados.
- CLI: rótulos `OK`/`AVISO`/`ERRO`, `NO_COLOR`, `--json`.

## Convenção para o campo "Ações"

Toda ação termina apontando o contrato que ela aciona, numa destas formas:

| Forma | Quando | Exemplo |
| :-- | :-- | :-- |
| (`operação`) | Chama a API na própria tela | "Mudar o filtro de fase → (`listar_emendas`)" |
| → Pxx (`operação`) | Navega; a operação é a que a tela de destino chama ao abrir | "Nome da cidade → P02 (`obter_municipio`)" |
| (`cli:comando`) ou (`email:modelo`) | Terminal ou e-mail | "Enter → (`cli:sugestoes`)" |
| ação local · sem chamada à API (REQ-81) | Copiar, exportar o já carregado, voltar, abrir link externo | "Copiar CNPJ → ação local · sem chamada à API (REQ-81)" |

Operação que cada tela chama ao abrir: P01 `obter_status` · P02 `obter_municipio` · P03 `listar_emendas` · P04 `obter_emenda` · P05 `listar_pagamentos_emenda` · P06 `obter_favorecido` · P07 `obter_agregacoes` · P08 `obter_parlamentar` · P09 `listar_importacoes` · P10 `listar_traducoes` · S01 `listar_municipios` · S02 `confirmar_assinatura` (link de confirmação) ou `obter_assinatura` (link de gestão) · S03 `email:alerta` · O01 `cli:importar` · O02 `cli:sugestoes`.

## Elementos comuns das telas web

- **Cabeçalho:** marca (→ P01), "Emendas" (P03), "Comparar" (P07), "Dados" (P09), "Receber alertas" (S01) e a busca "Cidade, código da emenda ou CNPJ" (atalho `/`): nome de município → P02; 12 dígitos → P04; 14 dígitos → P06; outro texto → P01 com os resultados.
- **Faixa de proveniência** logo abaixo do cabeçalho (REQ-75), de `obter_status`: "Portal da Transparência · atualizado pela fonte em dd/mm/aaaa · importado em dd/mm/aaaa (importação #n) · Ver origem" → P09.
- **Rodapé:** aviso do REQ-83, link para P10 ("Como traduzimos as fases"), para P09 e para o repositório.
- **Estados comuns**, citados nas fichas:
  - carregando: esqueleto com `aria-busy` (REQ-76);
  - vazio: mensagem própria (REQ-77);
  - erro: mensagem, `request_id` e "Tentar de novo" (REQ-78);
  - offline: "Sem conexão. Nada abaixo está atualizado." e nenhum valor guardado (REQ-79);
  - sem permissão: as telas P são públicas; o único "sem permissão" é o limite por IP, "Muitas consultas seguidas. Tente de novo em N s." (REQ-58); nas telas S, token inválido (REQ-63);
  - sem importação publicada: "Os dados ainda não foram importados." (REQ-56).
