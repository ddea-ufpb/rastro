# ADR-0001 · Identificar o favorecido só pelo CNPJ e tratar nome parecido como sugestão

- **Status:** aceita
- **Contexto:** A pergunta "quem recebeu?" (FI-01 §4.2, feature 2) depende de juntar pagamentos da mesma entidade. A fonte escreve a mesma entidade de vários jeitos, e nomes iguais pertencem a entidades diferentes. Na coleta do Trabalho 2 (22/11/2026), cada CNPJ veio com um nome só, mas 71 CNPJs se chamam `FUNDO MUNICIPAL DE ASSISTENCIA SOCIAL`, um por município, e 32 raízes de CNPJ têm mais de uma filial. Unir duas entidades por engano faz o sistema afirmar em público que uma delas recebeu dinheiro que não recebeu (FI-01 §3.2, §8.2).
- **Opções consideradas:**
  1. Unir por nome normalizado (sem acento, caixa, abreviações).
  2. Unir por nome com similaridade alta e revisão posterior.
  3. Identificar só pelo CNPJ; nome parecido com CNPJ de outra raiz vira `SugestaoMesmaEntidade`, revisável e nunca somada.
- **Decisão:** Opção 3. `Favorecido.cnpj` é `UNIQUE NOT NULL` (REQ-21). Grafias diferentes do mesmo CNPJ ficam em `NomeFavorecido` (REQ-22). Filiais da mesma raiz são agrupadas só para exibição (REQ-27). Sugestões são geradas na publicação, só dentro do mesmo município (REQ-36), aparecem com rótulo próprio (REQ-39) e nunca entram em soma (REQ-37). A revisão do operador muda o rótulo, não o total (REQ-38).
- **Consequências:**
  - \+ Nenhuma fusão invisível: todo total é a soma de CNPJs que a fonte publicou.
  - \+ O jornalista ainda vê o parentesco provável, com o rótulo de que é sugestão.
  - \+ Cria o recurso compartilhado da concorrência (a linha do CNPJ), tratado no ADR-0007.
  - − Uma entidade que trocou de CNPJ aparece em dois lugares. Aceito: é o que a fonte diz.
  - Opções 1 e 2 descartadas: o caso dos 71 fundos municipais mostra que nome igual não é entidade igual.
