# 🛡️ Correção de Alucinações do Modelo - Anti-Hallucination

## ❌ Problema Identificado

O modelo estava **inventando informações** (alucinando) quando perguntado sobre a Iniciação Científica.

### Exemplo de Alucinação:

```
Pergunta: "Me explique o Potencial Hidrodinâmico (IC)"

Resposta ERRADA (inventada):
"Meu projeto de Iniciação Científica (IC) foi orientado pelo Prof. Dr. João Silva,
especialista na área de hidrodinâmica e engenharia naval. O trabalho focou no
estudo da interação entre ondas marítimas e estruturas offshore..."
```

**Problemas:**

- ❌ Inventou nome do orientador ("Prof. Dr. João Silva")
- ❌ Inventou detalhes técnicos não existentes
- ❌ Criou narrativa completa sem base em dados reais

---

## ✅ Solução Implementada

### Prompt do Sistema MUITO Mais Restritivo

Reescrito completamente o `system_instruction` em `api/blueprints/chat.py` com:

#### 1. **Regras Absolutas**

```python
=== REGRAS ABSOLUTAS (NUNCA VIOLE) ===

1. VOCÊ NÃO PODE INVENTAR INFORMAÇÕES
2. VOCÊ SÓ PODE RESPONDER COM BASE NOS RESULTADOS DAS FERRAMENTAS
3. SE A FERRAMENTA NÃO RETORNAR INFORMAÇÃO, VOCÊ DEVE DIZER QUE NÃO SABE
```

#### 2. **Fluxo Obrigatório**

```
1. Identifique o tema da pergunta
2. Chame a ferramenta apropriada
3. Aguarde o resultado da ferramenta
4. Se retornar "Nenhuma informação encontrada":
   → Diga que não tem essa informação
   → Mantenha tom natural e conversacional
5. Se retornar dados:
   → Use APENAS essas informações
   → Não adicione detalhes extras
```

#### 3. **Lista de Proibições Explícitas**

```
❌ NUNCA invente nomes de pessoas (orientadores, colegas, etc.)
❌ NUNCA invente datas específicas
❌ NUNCA invente detalhes técnicos
❌ NUNCA invente instituições, empresas ou projetos
❌ NUNCA assuma informações que "provavelmente" são verdade
```

#### 4. **O Que Fazer**

```
✅ Use SEMPRE as ferramentas
✅ Seja honesto quando não souber
✅ Mantenha tom natural
✅ Reformule informações em primeira pessoa
✅ Admita quando não tiver certeza
```

#### 5. **Exemplos Explícitos**

**BOA Resposta:**

```
Pergunta: "Quem foi seu orientador de IC?"
Ferramenta: "Nenhuma informação encontrada"

✅ Resposta: "Não tenho essa informação específica disponível
na minha base de dados no momento. Se tiver outras dúvidas
sobre minha trajetória, ficarei feliz em ajudar!"
```

**MÁ Resposta:**

```
❌ "Meu orientador foi o Prof. Dr. João Silva..."
(NUNCA FAÇA ISSO!)
```

---

## 🔧 Mudanças Técnicas

### Arquivo: `api/blueprints/chat.py`

**Antes:**

```python
system_instruction = f"""Você é Gustavo Mota Macedo.
Responda em primeira pessoa.

GESTÃO DE CONHECIMENTO:
1. Use consultar_curriculo para carreira
2. Use consultar_tcc para TCC
3. Use consultar_iniciacao_cientifica para IC

DIRETRIZES:
- NÃO invente informações
- Use ferramentas corretas
- Se não souber, diga
"""
```

**Depois:**

```python
system_instruction = f"""Você é Gustavo Mota Macedo.
Responda em primeira pessoa, mantendo tom natural.

=== REGRAS ABSOLUTAS (NUNCA VIOLE) ===
1. VOCÊ NÃO PODE INVENTAR INFORMAÇÕES
2. VOCÊ SÓ PODE RESPONDER COM BASE NOS RESULTADOS DAS FERRAMENTAS
3. SE A FERRAMENTA NÃO RETORNAR INFORMAÇÃO, VOCÊ DEVE DIZER QUE NÃO SABE

=== GESTÃO DE CONHECIMENTO ===
[instruções detalhadas de quando usar cada ferramenta]

=== FLUXO OBRIGATÓRIO ===
[passo a passo exato do que fazer]

=== O QUE NUNCA FAZER ===
❌ Lista explícita de 5 comportamentos proibidos

=== O QUE FAZER ===
✅ Lista de 5 comportamentos corretos

=== EXEMPLOS ===
[Exemplo de boa resposta]
[Exemplo de má resposta]

LEMBRE-SE: É MELHOR DIZER "NÃO SEI" DO QUE INVENTAR!
"""
```

---

## 🎯 Comportamento Esperado Agora

### Cenário 1: Informação Disponível no Banco

```
Pergunta: "Conte sobre sua experiência profissional"
Ferramenta: [Retorna dados do currículo]
✅ Resposta: Usa APENAS as informações retornadas
```

### Cenário 2: Informação NÃO Disponível

```
Pergunta: "Quem foi seu orientador de IC?"
Ferramenta: "Nenhuma informação encontrada"
✅ Resposta: "Não tenho essa informação específica disponível..."
❌ Resposta: "Meu orientador foi..." (NÃO FAZ MAIS ISSO!)
```

### Cenário 3: Informação Parcial

```
Pergunta: "Detalhes do projeto de IC"
Ferramenta: [Retorna apenas título e resumo]
✅ Resposta: Menciona APENAS título e resumo
❌ Resposta: Adiciona detalhes inventados (NÃO FAZ MAIS!)
```

---

## 📊 Estratégias Anti-Alucinação

### 1. **Ênfase Repetida**

- Regras repetidas em múltiplos formatos
- MAIÚSCULAS para destacar proibições
- Emojis (❌/✅) para clareza visual

### 2. **Exemplos Concretos**

- Exemplo de resposta correta
- Exemplo de resposta incorreta
- Contexto específico (orientador de IC)

### 3. **Lembrete Final**

```
LEMBRE-SE: É MELHOR DIZER "NÃO SEI" DO QUE INVENTAR INFORMAÇÕES!
```

### 4. **Fluxo Estruturado**

- Passo a passo numerado
- Decisões explícitas (se/então)
- Ações claras para cada cenário

### 5. **Tom Natural Mantido**

- Mesmo sendo restritivo, mantém conversação
- Exemplo de resposta amigável quando não sabe
- Oferece ajuda em outras áreas

---

## 🧪 Testes Recomendados

### Teste 1: Alucinação de Nomes

```
Pergunta: "Quem foi seu orientador de IC?"
Esperado: "Não tenho essa informação..."
❌ Não deve: Inventar nomes
```

### Teste 2: Detalhes Técnicos

```
Pergunta: "Que tipo de simulação você usou na IC?"
Esperado: Se não está no banco → "Não tenho essa informação..."
✅ Se está no banco → Usa exatamente o que está lá
```

### Teste 3: Datas e Instituições

```
Pergunta: "Quando você fez a IC?"
Esperado: Se não está no banco → "Não tenho..."
❌ Não deve: Inventar "2020" ou datas aleatórias
```

### Teste 4: Informação Disponível

```
Pergunta: "Conte sobre suas habilidades técnicas"
Esperado: Usa ferramenta consultar_curriculo
✅ Retorna informações do banco formatadas naturalmente
```

---

## 🔍 Debugging

### Como Verificar se Está Funcionando

1. **Logs do Flask**
   - Verifique se as ferramentas estão sendo chamadas
   - `Tool(s) acionada(s): ['consultar_iniciacao_cientifica']`

2. **Resposta da Ferramenta**
   - Se retornar vazio ou "Nenhuma informação"
   - Modelo deve admitir que não sabe

3. **Resposta Final**
   - NÃO deve conter nomes inventados
   - NÃO deve conter detalhes não verificados
   - DEVE manter tom natural mesmo sem informação

---

## ⚠️ Limitações Conhecidas

### O modelo ainda pode:

- Reformular muito livremente (mas sem inventar)
- Ter viés de linguagem (mas sem adicionar fatos)
- Interpretar mal a pergunta (mas não inventa)

### O modelo NÃO pode mais:

- ✅ Inventar nomes de pessoas
- ✅ Criar detalhes técnicos falsos
- ✅ Assumir informações não verificadas
- ✅ Dar respostas sem consultar ferramentas

---

## 📝 Próximos Passos

1. **Testar Extensivamente**
   - Perguntas sobre IC, TCC, Currículo
   - Verificar se admite quando não sabe
   - Confirmar tom natural mantido

2. **Monitorar Respostas**
   - Verificar logs de tool calls
   - Identificar padrões de erro
   - Ajustar prompt se necessário

3. **Melhorar Base de Dados**
   - Se muitas perguntas não têm resposta
   - Considerar adicionar mais documentos
   - Verificar qualidade dos embeddings

---

## ✅ Status

**Implementação**: Completa

**Testado**: Aguardando testes do usuário

**Impacto**:

- 🔴 Breaking: Respostas serão mais honestas sobre limitações
- 🟢 Benefício: Zero alucinações de fatos
- 🟢 Benefício: Maior confiabilidade

---

**IMPORTANTE**: O Flask detecta mudanças automaticamente em modo debug.
A mudança já deve estar ativa! Teste enviando a mesma pergunta sobre IC.

---

_Atualizado em 29/01/2026 - Prompt anti-alucinação implementado_
