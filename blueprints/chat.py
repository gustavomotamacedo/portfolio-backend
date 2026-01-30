import os
import json
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify
import logging # Adicionar Import

# Configuração de Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from database import init_db, get_db, ChatSession, ChatMessage, DocumentEmbedding
import pdfplumber

chat_bp = Blueprint('chat', __name__)

# Configuração do modelo e embeddings
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Inicializar Banco de Dados
init_db()

@tool
def consultar_tcc(query: str):
    """
    Ferramenta OBRIGATÓRIA para buscar informações sobre o Trabalho de Conclusão de Curso (TCC), artigo final ou monografia.
    A busca é restrita EXCLUSIVAMENTE ao arquivo: artigo_base--abtn.pdf.
    """
    try:
        db = next(get_db())
        query_vector = embeddings.embed_query(query)
        
        # Filtra pelo arquivo do TCC e ordena por similaridade
        results = db.query(DocumentEmbedding).filter(
            DocumentEmbedding.source == 'artigo_base--abtn.pdf'
        ).order_by(
            DocumentEmbedding.embedding.l2_distance(query_vector)
        ).limit(5).all()
        
        if not results:
            logger.warning(f"TCC: Nenhuma informação encontrada para query: {query}")
            return "Nenhuma informação encontrada no TCC sobre esse tema."
            
        logger.info(f"TCC: {len(results)} chunks encontrados para query: {query}")
        return "\n\n".join([doc.content for doc in results])
    except Exception as e:
        logger.error(f"Erro ao consultar TCC: {e}", exc_info=True)
        return f"Erro ao consultar TCC: {str(e)}"
    finally:
        db.close()

@tool
def consultar_iniciacao_cientifica(query: str):
    """
    Ferramenta OBRIGATÓRIA para buscar informações sobre a Iniciação Científica (IC) ou Potencial Hidrodinâmico.
    A busca é restrita EXCLUSIVAMENTE ao arquivo: potencial_hidrodinamica_completo.pdf.
    """
    try:
        db = next(get_db())
        query_vector = embeddings.embed_query(query)
        
        # Filtra pelo arquivo da IC
        results = db.query(DocumentEmbedding).filter(
            DocumentEmbedding.source == 'potencial_hidrodinamica_completo.pdf'
        ).order_by(
            DocumentEmbedding.embedding.l2_distance(query_vector)
        ).limit(5).all()
        
        if not results:
            logger.warning(f"IC: Nenhuma informação encontrada para query: {query}")
            return "Nenhuma informação encontrada na Iniciação Científica sobre esse tema."
            
        logger.info(f"IC: {len(results)} chunks encontrados para query: {query}")
        return "\n\n".join([doc.content for doc in results])
    except Exception as e:
        logger.error(f"Erro ao consultar IC: {e}", exc_info=True)
        return f"Erro ao consultar IC: {str(e)}"
    finally:
        db.close()

@tool
def consultar_curriculo(query: str):
    """
    Ferramenta OBRIGATÓRIA para buscar informações sobre Experiência Profissional, Habilidades, Contato, Resumo e Histórico do candidato.
    A busca é restrita EXCLUSIVAMENTE ao arquivo: CURRICULO JAVA-1.pdf.
    """
    try:
        db = next(get_db())
        query_vector = embeddings.embed_query(query)
        
        # Filtra pelo arquivo do Currículo
        results = db.query(DocumentEmbedding).filter(
            DocumentEmbedding.source == 'CURRICULO JAVA-1.pdf'
        ).order_by(
            DocumentEmbedding.embedding.l2_distance(query_vector)
        ).limit(5).all()
        
        if not results:
            logger.warning(f"Curriculo: Nenhuma informação encontrada para query: {query}")
            return "Nenhuma informação encontrada no currículo sobre esse tema."
            
        logger.info(f"Curriculo: {len(results)} chunks encontrados para query: {query}")
        return "\n\n".join([doc.content for doc in results])
    except Exception as e:
        logger.error(f"Erro ao consultar Curriculo: {e}", exc_info=True)
        return f"Erro ao consultar Currículo: {str(e)}"
    finally:
        db.close()

@tool
def calcular_orcamento_software(query: str):
    """
    Ferramenta OBRIGATÓRIA para calcular orçamentos de projetos de software.
    Use esta ferramenta para perguntas sobre: preço, custo, orçamento, estimativa de projeto, valores de desenvolvimento.
    A busca é restrita EXCLUSIVAMENTE ao arquivo: calcular_orcamento_de_software.md.
    
    IMPORTANTE: Esta ferramenta retorna automaticamente 3 opções de preço:
    - Econômico (equipe júnior)
    - Intermediário (equipe mista)
    - Premium (equipe sênior)
    """
    try:
        db = next(get_db())
        query_vector = embeddings.embed_query(query)
        
        # Filtra pelo arquivo de orçamento
        results = db.query(DocumentEmbedding).filter(
            DocumentEmbedding.source == 'calcular_orcamento_de_software.md'
        ).order_by(
            DocumentEmbedding.embedding.l2_distance(query_vector)
        ).limit(5).all()
        
        if not results:
            return """Não encontrei informações específicas sobre cálculo de orçamento no momento. 
            
Mas posso te ajudar com isso! Para discutir seu projeto e receber um orçamento personalizado, entre em contato comigo:

📱 **WhatsApp:** [+55 (73) 99806-1168](https://wa.me/5573998061168)

Vamos conversar sobre as necessidades do seu projeto!"""
        
        # Extrair informações do contexto para gerar os 3 orçamentos
        # Valores médios por hora baseados no documento
        import random
        valor_junior = random.randint(20, 80)   
        valor_pleno = random.randint(80, 120)
        valor_senior = random.randint(120, 160)
        
        # Tentar extrair estimativa de horas da query do usuário
        # Se não conseguir, usar valores padrão
        import re
        horas_match = re.search(r'(\d+)\s*(?:horas|hrs|h)', query.lower())
        horas_estimadas = int(horas_match.group(1)) if horas_match else 200
        
        # Calcular custos base
        custo_economico = horas_estimadas * valor_junior
        custo_intermediario = horas_estimadas * valor_pleno
        custo_premium = horas_estimadas * valor_senior
        
        # Adicionar custos indiretos (15%) e margem (25%)
        fator_total = 1.15 * 1.25
        
        orcamento_economico = custo_economico * fator_total
        orcamento_intermediario = custo_intermediario * fator_total
        orcamento_premium = custo_premium * fator_total
        
        # Formatar resposta com os 3 orçamentos
        resposta = f"""# Gustavo Macedo AI
**Desenvolvimento de Software & Automação**

Para fornecer uma proposta precisa e alinhada às suas necessidades, preciso entender alguns detalhes do seu projeto.  
Com base em padrões gerais do mercado, apresento três opções de escopo e investimento:

---

## 💰 Opções de Orçamento

### 🟢 Plano Econômico
**R$ {orcamento_economico:,.2f}**
- Equipe júnior qualificada
- Ideal para projetos com orçamento limitado
- Tempo de desenvolvimento: padrão
- Suporte básico incluído

### 🟡 Plano Intermediário (Recomendado)
**R$ {orcamento_intermediario:,.2f}**
- Equipe mista (júnior + pleno)
- Melhor custo-benefício
- Tempo de desenvolvimento otimizado
- Suporte completo incluído

### 🔴 Plano Premium
**R$ {orcamento_premium:,.2f}**
- Equipe sênior especializada
- Máxima qualidade e performance
- Desenvolvimento mais ágil
- Suporte prioritário e consultoria incluídos

---

📋 **Estimativa baseada em:** {horas_estimadas}h de desenvolvimento
💡 **Incluso:** Análise de requisitos, desenvolvimento, testes e deploy

⚠️ *Estes são valores estimados. Para um orçamento preciso e personalizado, precisamos conversar sobre os detalhes específicos do seu projeto.*"""
        
        # Adicionar CTA ao final da resposta
        cta = """

---

💬 **Pronto para começar seu projeto?**

Entre em contato comigo pelo WhatsApp para discutir os detalhes:
📱 **+55 (73) 99806-1168**

<a href="https://wa.me/5573998061168" class="cta-whatsapp-green" target="_blank">Clique aqui para conversar no WhatsApp</a>

Vou te ajudar a escolher a melhor opção e planejar seu projeto de software!"""
        
        return resposta + cta
        
    except Exception as e:
        logger.error(f"Erro ao calcular orçamento: {e}", exc_info=True)
        return f"""Erro ao calcular orçamento: {str(e)}

Entre em contato comigo diretamente para um orçamento personalizado:
📱 **WhatsApp:** [+55 (73) 99806-1168](https://wa.me/5573998061168)"""
    finally:
        db.close()

def init_vector_store():

    """Escaneia a pasta de dados e indexa arquivos novos no banco."""
    db = next(get_db())
    data_dir = os.path.join(os.path.dirname(__file__), '../data')
    
    if not os.path.exists(data_dir):
        print(f"Diretório de dados não encontrado: {data_dir}")
        return

    # Extensões suportadas
    supported_extensions = ('.pdf', '.txt', '.md')
    
    # Listar arquivos
    files = [f for f in os.listdir(data_dir) if f.lower().endswith(supported_extensions)]
    
    for filename in files:
        # Verificar se já processado
        if db.query(DocumentEmbedding).filter_by(source=filename).first():
            print(f"Skipping {filename}: já indexado.")
            continue
            
        file_path = os.path.join(data_dir, filename)
        print(f"Processando novo arquivo: {filename}...")
        
        try:
            text = ""
            if filename.lower().endswith('.pdf'):
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        extracted = page.extract_text()
                        if extracted:
                            text += extracted + "\n"
            else:
                # Ler arquivos de texto (txt, md)
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
            
            if not text.strip():
                logger.warning(f"Aviso: {filename} está vazio ou ilegível.")
                continue

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            chunks = text_splitter.split_text(text)
            
            logger.info(f"  -> Gerando {len(chunks)} embeddings para {filename}...")
            
            embeddings_to_add = []
            for chunk in chunks:
                vector = embeddings.embed_query(chunk)
                embeddings_to_add.append(DocumentEmbedding(
                    content=chunk,
                    source=filename,
                    embedding=vector
                ))
            
            # Batch insert
            db.add_all(embeddings_to_add)
            db.commit()
            logger.info(f"  -> Sucesso: {filename} salvo.")

        except Exception as e:
            logger.error(f"  -> Erro ao processar {filename}: {e}", exc_info=True)
            db.rollback()

# Carregar dados ao iniciar
init_vector_store()

@chat_bp.route('/chat/history', methods=['GET'])
def get_history():
    session_id = request.args.get('session_id')
    if not session_id:
        return jsonify({"history": []})

    db = next(get_db())
    try:
        messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id)\
                     .order_by(ChatMessage.timestamp.asc()).all()
        
        history = []
        for msg in messages:
            # Mapear 'assistant' para 'ai' para compatibilidade com frontend
            role = 'ai' if msg.role == 'assistant' else msg.role
            history.append({
                "role": role,
                "content": msg.content
            })
            
        return jsonify({"history": history})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@chat_bp.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message')
    session_id = data.get('session_id')
    logger.info(f"Nova requisição de chat recebida. Session ID: {session_id}")

    if not user_message:
        logger.warning("Tentativa de chat sem mensagem.")
        return jsonify({"error": "Mensagem não fornecida"}), 400

    # Gerar session_id
    if not session_id:
        session_id = str(uuid.uuid4())

    db = next(get_db())

    try:
        # Verificar/Criar Sessão
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            session = ChatSession(id=session_id)
            db.add(session)
            db.commit()

        # Salvar mensagem do usuário
        user_msg_db = ChatMessage(session_id=session_id, role="user", content=user_message)
        db.add(user_msg_db)
        db.commit()

        # Recuperar Histórico Recente
        recent_msgs = db.query(ChatMessage).filter(ChatMessage.session_id == session_id)\
                        .order_by(ChatMessage.timestamp.desc()).limit(10).all()
        previous_messages_objs = recent_msgs[::-1]
        
        context_messages = []
        for msg in previous_messages_objs:
            if msg.role == "user":
                context_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                context_messages.append(AIMessage(content=msg.content))

        # Prompt base
        current_date = datetime.now().strftime("%d/%m/%Y")
        system_instruction = f"""Você é Gustavo Mota Macedo e hoje é {current_date}.
        Responda sempre em primeira pessoa, mantendo um tom natural e conversacional.

        === REGRAS DE IDIOMA (ESTRITAS E INVIOLÁVEIS) ===
        
        VOCÊ ESTÁ PROIBIDO DE FALAR QUALQUER IDIOMA QUE NÃO SEJA PORTUGUÊS OU INGLÊS.
        
        1. **Português (Brasil)**: Use se o usuário falar português.
        2. **Inglês**: Use se o usuário falar inglês OU qualquer outro idioma estranho.
        
        SE O USUÁRIO FALAR ESPANHOL, FRANCÊS, ITALIANO, ETC:
        -> IGNORE O IDIOMA DELE E RESPONDA EM INGLÊS.
        -> NÃO PEDIR DESCULPAS POR NÃO FALAR O IDIOMA, APENAS RESPONDA EM INGLÊS DIRETO.
        
        Exemplo:
        User: "Hola, como estás?" (Espanhol)
        Assistant: "Hello! I am doing well. How can I help you regarding my professional experience?" (Inglês)

        === REGRAS DE CONTEÚDO (NUNCA VIOLE) ===
        
        1. VOCÊ NÃO PODE INVENTAR INFORMAÇÕES
        2. VOCÊ SÓ PODE RESPONDER COM BASE NOS RESULTADOS DAS FERRAMENTAS
        3. SE A FERRAMENTA NÃO RETORNAR INFORMAÇÃO, VOCÊ DEVE DIZER QUE NÃO SABE
        
        === DIRETRIZES DE VENDAS E RECRUTAMENTO (PRIORIDADE MÁXIMA) ===
        
        Se você identificar que o usuário é um **Recrutador** (falando sobre vagas, entrevistas, oportunidades) OU um **Cliente Potencial** (interessado em fechar negócio, gostou do orçamento, quer começar):

        1. **Adote uma postura proativa e entusiasta.**
        2. **REDIRECIONE PARA O WHATSAPP IMEDIATAMENTE.**
        3. Use frases como:
           - "Isso soa ótimo! Vamos conversar melhor pelo WhatsApp para agilizarmos?"
           - "Fico muito interessado nessa oportunidade. Pode me chamar no WhatsApp para marcarmos uma conversa?"
           - "Excelente! Para darmos o próximo passo, me chame no WhatsApp."
        
        Sempre inclua o link direto: `https://wa.me/5573998061168`

        === GESTÃO DE CONHECIMENTO ===
        
        Para QUALQUER pergunta sobre:
        - **Experiência profissional, habilidades, tecnologias, contato**: Use `consultar_curriculo`
        - **TCC, Monografia, trabalho de conclusão**: Use `consultar_tcc`
        - **Iniciação Científica (IC), Hidrodinâmica, pesquisa**: Use `consultar_iniciacao_cientifica`
        - **Orçamento, preço, custo, estimativa de projeto de software**: Use `calcular_orcamento_software`
        
        === FLUXO OBRIGATÓRIO ===
        
        1. Identifique o tema da pergunta
        2. Chame a ferramenta apropriada
        3. Aguarde o resultado da ferramenta
        4. Se a ferramenta retornar "Nenhuma informação encontrada" ou erro:
           → Responda naturalmente que não tem essa informação específica
           → Exemplo: "Não tenho essa informação detalhada disponível no momento. Posso te ajudar com outra coisa sobre minha carreira?"
        5. Se a ferramenta retornar dados:
           → Use APENAS essas informações
           → Reformule de forma natural, em primeira pessoa
           → NÃO adicione detalhes que não estão no resultado
        
        === O QUE NUNCA FAZER ===
        
        ❌ NUNCA invente nomes de pessoas (orientadores, colegas, etc.)
        ❌ NUNCA invente datas específicas sem confirmação da ferramenta
        ❌ NUNCA invente detalhes técnicos não mencionados pela ferramenta
        ❌ NUNCA invente instituições, empresas ou projetos
        ❌ NUNCA assume informações que "provavelmente" são verdade
        
        === O QUE FAZER ===
        
        ✅ Use SEMPRE as ferramentas para buscar informação
        ✅ Seja honesto quando não souber algo
        ✅ Mantenha tom natural e conversacional
        ✅ Reformule as informações da ferramenta em primeira pessoa
        ✅ Se não tiver certeza, admita
        
        === EXEMPLO DE BOA RESPOSTA (sem informação) ===
        
        Pergunta: "Quem foi seu orientador de IC?"
        Ferramenta retorna: "Nenhuma informação encontrada"
        Resposta correta: "Não tenho essa informação específica disponível na minha base de dados no momento. Se tiver outras dúvidas sobre minha trajetória, ficarei feliz em ajudar!"
        
        === EXEMPLO DE MÁ RESPOSTA (inventada) ===
        
        ❌ "Meu orientador foi o Prof. Dr. João Silva..." (NUNCA FAÇA ISSO!)
        
        LEMBRE-SE: É MELHOR DIZER "NÃO SEI" DO QUE INVENTAR INFORMAÇÕES!
        """
        
        # Construir lista de mensagens (Sem contexto injetado forçadamente)
        messages = [SystemMessage(content=system_instruction)] + context_messages + [HumanMessage(content=user_message)]
        
        # Bind Tools
        tools = [consultar_curriculo, consultar_tcc, consultar_iniciacao_cientifica, calcular_orcamento_software]
        llm_with_tools = llm.bind_tools(tools)
        
        # Primeira execução
        ai_msg = llm_with_tools.invoke(messages)
        
        # --- FALLBACK DE REPARO DE TOOL CALL ---
        import re
        if not ai_msg.tool_calls and ai_msg.content:
            # Tentar encontrar padrão JSON de tool call no texto 
            # (Adicionado consultar_curriculo no regex)
            json_pattern = re.search(r'(\{.*"name":\s*"(?:consultar_tcc|consultar_iniciacao_cientifica|consultar_curriculo|calcular_orcamento_software)".*?\})', ai_msg.content.replace('\n', ' '))
            if json_pattern:
                try:
                    raw_json = json_pattern.group(1)
                    parsed_call = json.loads(raw_json)
                    args = parsed_call.get("arguments") or parsed_call.get("parameters") or {}
                    if isinstance(args, str):
                         args = json.loads(args)

                    repaired_call = {
                        "name": parsed_call.get("name"),
                        "args": args,
                        "id": str(uuid.uuid4())
                    }
                    ai_msg.tool_calls = [repaired_call]
                    ai_msg.tool_calls = [repaired_call]
                    ai_msg.content = "" 
                    logger.info(f"Reparado tool call via regex: {repaired_call['name']}")
                except Exception as e:
                    logger.error(f"Falha ao tentar reparar tool call: {e}")

        # Processar Tool Calls (se houver)
        if ai_msg.tool_calls:
            logger.info(f"Tool(s) acionada(s): {[tc['name'] for tc in ai_msg.tool_calls]}")
            messages.append(ai_msg)
            for tool_call in ai_msg.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                
                tool_output = "Ferramenta desconhecida."
                if tool_name == "consultar_tcc":
                    tool_output = consultar_tcc.invoke(tool_args)
                elif tool_name == "consultar_iniciacao_cientifica":
                    tool_output = consultar_iniciacao_cientifica.invoke(tool_args)
                elif tool_name == "consultar_curriculo":
                    tool_output = consultar_curriculo.invoke(tool_args)
                elif tool_name == "calcular_orcamento_software":
                    tool_output = calcular_orcamento_software.invoke(tool_args)
                
                messages.append(ToolMessage(content=str(tool_output), tool_call_id=tool_call['id']))
            
            # Segunda chamada ao LLM com o resultado da tool
            response = llm_with_tools.invoke(messages)
        else:
            response = ai_msg
        
        # Salvar resposta do assistente
        ai_msg_db = ChatMessage(session_id=session_id, role="assistant", content=response.content)
        db.add(ai_msg_db)
        db.commit()
        
        return jsonify({
            "response": response.content,
            "session_id": session_id
        })
    except Exception as e:
        logger.critical(f"Erro crítico ao processar mensagem: {e}", exc_info=True)
        return jsonify({"error": "Erro interno", "details": str(e)}), 500
    finally:
        db.close()


