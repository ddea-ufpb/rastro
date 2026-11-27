# Relatório de auditoria do plano

**Plano:** `modulos/ingestao/.paul/phases/01-etapa1-contrato/01-01-PLAN.md`
**Auditado em:** 2026-11-27
**Veredito:** aceitável com condições → pronto para APPLY depois das melhorias abaixo

---

## 1. Veredito

Aceitável com condições. A troca de nomes é mecânica e protegida por uma verificação de equivalência. Mas o plano original enviava para um repositório público sem portão de privacidade e não provava, a partir do git, o critério do professor ("apago o corpus, rodo o coletor e obtenho um arquivo equivalente"). A pasta local tem o zip completo (ignorado pelo git), então rodar de novo ali não prova que a árvore versionada se basta. As duas falhas foram corrigidas no plano.

## 2. O que está sólido (não mudar)

- As fronteiras congelam as regras de recorte e de descarte e o bruto: a troca de nomes não muda quais itens entram no corpus.
- A equivalência é conferida contra um hash imutável (`24017d4`), não contra memória ou só contagens.
- Dinheiro continua inteiro (REQ-24 do T1), sem float no caminho. O estorno negativo tem teste.
- Commits separados (original, alinhamento, `.paul/`) geram a evidência de processo que a disciplina avalia.
- O `.gitattributes` já fixa as quebras de linha (`bruto/*.csv -text`, `*.jsonl eol=lf`), então o sha256 é estável no Windows.
- Dentro do módulo, a `main` só tem `modulos/ingestao/.paul/.gitkeep`, e o `24017d4` não toca `.paul/`. O rebase tem pouco risco de conflito.

## 3. Lacunas encontradas

1. **Sem portão de privacidade antes de um push público irreversível.** LGPD é restrição do projeto. Depois do push, um CPF dentro de `razao_social` fica no histórico do git e nos forks.
2. **Reprodutibilidade não provada a partir do git.** O `obter()` reaproveita o extrato quando ele existe, mas o plano só rodava de novo na pasta de trabalho, onde estão o zip e os arquivos não versionados.
3. **Sem referência de volta antes do rebase.** O rebase reescreve o hash da única cópia da E1, que nunca foi enviada.
4. **Verificação de tipos fraca na equivalência.** Só "×100" não pega valor que continuou string ou float, contagem errada nem `cnpj_raiz` errado.
5. **Mudança de contrato não comunicada.** `*_centavos` ainda é [decidir] no PR #5, e os nomes antigos aparecem no cofre e em anotações.
6. Um `assert` protege a invariante "um nome por CNPJ", e o `python -O` o remove (já existia antes deste plano).
7. O `municipio_ibge` do modelo do T1 não é produzido.

## 4. Melhorias aplicadas ao plano

### Obrigatórias (bloqueiam a entrega)

| # | Lacuna | Seção do plano | Mudança aplicada |
|---|---------|----------------------|----------------|
| 1 | Sem portão de privacidade antes do push | AC-6, Task 3, verificação | Varredura de CPF e de zip sobre `git diff origin/main..HEAD`; se falhar, não há push |
| 2 | Reprodutibilidade não provada a partir do git | AC-5, Task 3, verificação | Um `git worktree` no scratchpad, sem o zip, regera o corpus com o mesmo sha256 |

### Fortemente recomendadas

| # | Lacuna | Seção do plano | Mudança aplicada |
|---|---------|----------------------|----------------|
| 1 | Sem referência de volta | ação da Task 3 | `git branch backup/t2-e1-24017d4 24017d4` antes do rebase |
| 2 | Verificação de tipos fraca | ação da Task 2 | Confere int (não bool, float nem str), contagens e `cnpj_raiz` |
| 3 | Mudança de contrato não comunicada | Task 2, Task 3 | Tabela de nomes antigo → novo no REGRAS.md e no PR, com pedido explícito sobre `*_centavos` |

### Adiadas (podem esperar)

| # | Lacuna | Por que pode esperar |
|---|---------|----------------------|
| 1 | `assert` removido pelo `-O` | O plano congela as regras e o coletor nunca roda com `-O`. Rever quando o coletor virar a ingestão definitiva |
| 2 | `municipio_ibge` | Precisa da tabela do IBGE e do casamento por nome (ADR-0010). É da ingestão definitiva, não do corpus do T2. Já está nos limites de escopo |

## 5. Prontidão para auditoria

- **Evidência:** a saída do script de equivalência, os dois sha256, o sha256 do checkout limpo e o resultado da varredura LGPD vão para o SUMMARY.
- **Falha silenciosa:** os portões bloqueiam o push. A equivalência falha com qualquer diferença de contagem, tipo ou valor.
- **Reconstrução:** o `24017d4` fica guardado numa branch, e o bruto e o manifesto são cópia byte a byte.
- **Responsabilidade:** o autor é João Rafael. O merge é do grupo (o plano proíbe mesclar).

## 6. Critério final de entrega

- Antes do push: os testes passam, o corpus é equivalente, o checkout limpo o reproduz e a varredura LGPD sai limpa.
- Risco que fica: o grupo pode escolher reais em vez de centavos no PR #5. Isso exigiria um plano novo para renomear `*_centavos` de novo.
- Com os portões no lugar, eu assinaria.

---

**Resumo:** aplicadas 2 melhorias obrigatórias e 3 fortemente recomendadas. 2 adiadas.
**Situação do plano:** atualizado e pronto para APPLY

---
*Auditoria feita pelo PAUL Enterprise Audit Workflow*
*Versão do modelo de auditoria: 1.0*
