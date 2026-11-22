# Fonte e recorte — Trabalho 2 (João Rafael)

**Recorte:** registros de pagamento das emendas parlamentares ligadas à Paraíba, com nome e CNPJ da entidade que recebeu. Entram as linhas de `EmendasParlamentares_PorFavorecido.csv` cuja emenda tem `Código UF IBGE = 2500000` **ou** cujo favorecido tem `UF Favorecido = PB` (mesmo filtro de REQ-52). Só entra pessoa jurídica com CNPJ.

**Etapa 2 (o que o modelo decide):** se dois nomes de entidade são a mesma, e a natureza da entidade (prefeitura, autarquia, hospital, OSC, consórcio).

| Item | Valor |
|---|---|
| Fonte | Portal da Transparência (CGU), emendas parlamentares, arquivo único |
| URL | <https://portaldatransparencia.gov.br/download-de-dados/emendas-parlamentares/UNICO>, que redireciona para `https://dadosabertos-download.cgu.gov.br/PortalDaTransparencia/saida/emendas-parlamentares/EmendasParlamentares.zip` |
| Acesso | Público, sem login e sem chave |
| Licença / termos | Dados abertos (Lei 12.527/2011); uso livre com citação da fonte |
| Data da coleta | 2026-11-22 (`Last-Modified` da fonte: 2026-11-19 22:36 GMT; `ETag` `"2bdb459be7478f908395e357bff86e30-6"`) |
| sha256 do zip | `221c0a3eb2f561d8e7041188d66914314f2be033fd835ebbd7c83e963796faf0` |
| Limite de requisição | Uma requisição por coleta (um arquivo de ~47 MB); sem limite documentado |
| Itens | 836 298 linhas no arquivo original; 31 840 no recorte; 19 647 pagamentos a pessoa jurídica no extrato; **2 353 entidades no corpus** |

## O que fica no repositório

- `bruto/favorecidos-pb-<data>.csv`: as linhas do recorte copiadas **byte a byte** do CSV original (Windows-1252, `;`), só pessoa jurídica. O zip completo fica fora do git (`.gitignore`) porque traz nome e CPF parcial de pessoas físicas.
- `bruto/favorecidos-pb-<data>.manifesto.json`: URL, cabeçalhos HTTP, sha256 do zip, contagens e os descartes feitos na obtenção (só posição no arquivo original e motivo, sem nome).
- `corpus.jsonl`, `descartes.jsonl`: saída do coletor.

## Como reproduzir

```
python coletor.py            # usa o bruto mais recente de bruto/ (sem rede)
python coletor.py --baixar   # baixa de novo e gera um bruto com a data de hoje
python test_coletor.py       # testes das regras
```

Rodar duas vezes gera arquivos idênticos (conferido por sha256).

## Diferenças em relação ao contrato da Sarah (`especificacoes/sarah-araujo/arquitetura/contratos/fonte-portal.md`, 27/10/2026)

- O zip agora tem **6** CSVs (entraram `_Parcerias`, `_PlanodeTrabalhoParcerias` e `_PlanodeTrabalhoTransferenciasEspeciais`). Os três do contrato continuam lá, com o mesmo cabeçalho no de favorecidos.
- `Tipo Favorecido` tem também `Unidade Gestora` (código de 6 dígitos, sem CNPJ) e `Inscrição Genéric` (nome de pessoa estrangeira).
- `Empresário (Individual)` é pessoa: o nome é o dela, às vezes seguido do CPF inteiro. O contrato o põe em `entidade_privada`; aqui ele é descartado como pessoa física (ver REGRAS.md, R-EI). Proposta para o grupo: estender REQ-53 a essa natureza.
