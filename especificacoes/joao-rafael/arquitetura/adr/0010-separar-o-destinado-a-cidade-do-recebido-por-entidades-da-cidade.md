# ADR-0010 · Separar no município o destinado à cidade do recebido por entidades da cidade

- **Status:** aceita
- **Contexto:** "O que foi destinado à minha cidade" tem duas leituras na fonte. Uma emenda tem um local de destino (`Código Município IBGE`), mas muitas emendas da PB têm destino estadual ou `MÚLTIPLO` e pagam entidades sediadas num município (ADR-0008 da Sarah; T2 R-RECORTE). Somar as duas leituras conta o mesmo real duas vezes quando a emenda é da cidade e paga uma entidade da cidade.
- **Opções consideradas:**
  1. Mostrar só as emendas com destino na cidade.
  2. Somar destino e recebido num total da cidade.
  3. Mostrar dois blocos separados, cada um com rótulo e fonte próprios, sem total comum.
- **Decisão:** Opção 3 (REQ-40, REQ-42). "Destinado à cidade" vem de `Emenda.municipio_ibge`; "Recebido por entidades da cidade" vem de `Pagamento` cujo `Favorecido.municipio_ibge` é a cidade, qualquer que seja o destino da emenda.
- **Consequências:**
  - \+ Nenhum valor contado duas vezes.
  - \+ A prefeitura que recebeu por emenda de destino estadual aparece.
  - − Dois números para a mesma cidade pedem uma explicação curta em P02.
  - Opção 1 descartada: some quase metade do dinheiro da PB. Opção 2 descartada: dupla contagem.
