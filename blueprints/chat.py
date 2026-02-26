import os
import json
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify
import logging # Adicionar Import
from sqlalchemy import or_

# Configuração de Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition
from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages

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
    A busca abrange todos os arquivos de currículo disponíveis (ex: backend e fullstack).
    """
    try:
        db = next(get_db())
        query_vector = embeddings.embed_query(query)
        
        # Filtra por arquivos que contenham "curriculo" no nome (case-insensitive)
        # Usando ilike com curingas para capturar variações como 'Currículo' ou 'curriculo'
        results = db.query(DocumentEmbedding).filter(
            or_(
                DocumentEmbedding.source.ilike('%curriculo%'),
                DocumentEmbedding.source.ilike('%currículo%')
            )
        ).order_by(
            DocumentEmbedding.embedding.l2_distance(query_vector)
        ).limit(10).all()
        
        if not results:
            logger.warning(f"Curriculo: Nenhuma informação encontrada para query: {query}")
            return "Nenhuma informação encontrada nos currículos sobre esse tema."
            
        logger.info(f"Curriculo: {len(results)} chunks encontrados para query: {query}")
        return "\n\n".join([doc.content for doc in results])
    except Exception as e:
        logger.error(f"Erro ao consultar Curriculo: {e}", exc_info=True)
        return f"Erro ao consultar Currículos: {str(e)}"
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

@tool
def obter_tempo_experiencia(data_inicio: str) -> str:
    """
    Ferramenta OBRIGATÓRIA para calcular o tempo exato de experiência em anos e meses.
    O formato de data_inicio deve ser 'MM/AAAA' ou apenas o ano 'AAAA'. 
    Use esta ferramenta sempre que precisar calcular há quanto tempo o candidato trabalha com certa tecnologia ou em certo cargo, baseado na data de hoje.
    """
    try:
        agora = datetime.now()
        mes_atual = agora.month
        ano_atual = agora.year
        
        if "/" in data_inicio:
            mes_str, ano_str = data_inicio.split("/")
            mes_inicio = int(mes_str)
            ano_inicio = int(ano_str)
        else:
            ano_inicio = int(data_inicio)
            mes_inicio = 1 # Assume Janeiro se apenas o ano for fornecido
            
        meses_totais = (ano_atual - ano_inicio) * 12 + (mes_atual - mes_inicio)
        anos = meses_totais // 12
        meses = meses_totais % 12
        
        resultado = []
        if anos > 0:
            resultado.append(f"{anos} ano{'s' if anos > 1 else ''}")
        if meses > 0:
            resultado.append(f"{meses} mês{'es' if meses > 1 else ''}")
            
        if not resultado:
            return "Menos de 1 mês"
            
        return " e ".join(resultado)
    except Exception as e:
        logger.error(f"Erro ao calcular tempo de experiência: {e}")
        return "Erro ao calcular o tempo de experiência. Verifique o formato da data."

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
        now = datetime.now()
        data_extenso = now.strftime("%d/%m/%Y")
        dia_semana = now.strftime("%A")
        
        system_instruction = f"""Você é Gustavo Mota Macedo.
### CONTEXTO TEMPORAL CRÍTICO ###
- Data de Hoje: {data_extenso} ({dia_semana})
- Sua Localização Atual: São Paulo, Brasil (Fuso Horário BRT)

### DIRETRIZES DE RACIOCÍNIO (ReAct) ###
Ao receber uma pergunta, você deve pensar passo a passo:
1. **Thought (Raciocínio):** O que eu preciso saber para responder isso? Qual ferramenta devo usar?
2. **Action (Ação):** Acionar a ferramenta necessária. Você pode acionar várias em sequência se a primeira não retornar tudo que precisa.
3. **Observation (Observação):** O resultado me permite responder completamente? Se o usuário fala MÚLTIPLOS TÓPICOS, busque todos.
4. **Considerar o Tempo**: Se o usuário perguntar "há quanto tempo", chame OBRIGATORIAMENTE a ferramenta `obter_tempo_experiencia` passando a data que encontrou para que o cálculo seja exato, baseado na Data de Hoje.
5. **Priorizar o Recente**: Dê mais peso a informações recentes (próximas a {now.year}) ou atuações descritas como 'Atual'.

=== REGRAS DE IDIOMA (ESTRITAS E INVIOLÁVEIS) ===
VOCÊ ESTÁ PROIBIDO DE FALAR QUALQUER IDIOMA QUE NÃO SEJA PORTUGUÊS OU INGLÊS.
SE O USUÁRIO FALAR ESPANHOL, FRANCÊS, ITALIANO, ETC:
-> IGNORE O IDIOMA DELE E RESPONDA DIRETO EM INGLÊS.
        
=== REGRAS DE CONTEÚDO (NUNCA VIOLE) ===
1. VOCÊ NÃO PODE INVENTAR INFORMAÇÕES
2. VOCÊ SÓ PODE RESPONDER COM BASE NOS RESULTADOS DAS FERRAMENTAS
3. SE A FERRAMENTA NÃO RETORNAR INFORMAÇÃO, VOCÊ DEVE DIZER QUE NÃO SABE

=== DIRETRIZES DE VENDAS E RECRUTAMENTO (PRIORIDADE MÁXIMA) ===
Se você identificar que o usuário é um **Recrutador** ou **Cliente Potencial**:
1. **Adote uma postura proativa e entusiasta.**
2. **REDIRECIONE PARA O WHATSAPP IMEDIATAMENTE.**
Exemplo: "Isso soa ótimo! Como hoje é {dia_semana} e estou em São Paulo, se você me chamar no WhatsApp agora, é provável que eu te responda rapidamente! Vamos conversar?"
Link direto: `https://wa.me/5573998061168`

=== GESTÃO DE CONHECIMENTO ===
- **Curriculo, habilidades, experiência profissional e contato**: `consultar_curriculo`
- **TCC, Monografia, trabalho de conclusão**: `consultar_tcc`
- **IC (Iniciação Científica), Hidrodinâmica, pesquisa**: `consultar_iniciacao_cientifica`
- **Orçamento de software, estimativas, preço**: `calcular_orcamento_software`
- **Cálculo de tempo de experiência**: `obter_tempo_experiencia`

LEMBRE-SE: É MELHOR DIZER "NÃO SEI" DO QUE INVENTAR INFORMAÇÕES!
"""
        
        # Construir estado inicial do LangGraph
        messages = [SystemMessage(content=system_instruction)] + context_messages + [HumanMessage(content=user_message)]
        
        # Configurar Agent
        tools = [consultar_curriculo, consultar_tcc, consultar_iniciacao_cientifica, calcular_orcamento_software, obter_tempo_experiencia]
        llm_with_tools = llm.bind_tools(tools)
        
        # Criar nós do Grafo
        class GraphState(TypedDict):
            messages: Annotated[list, add_messages]
            
        def chatbot(state: GraphState):
            return {"messages": [llm_with_tools.invoke(state["messages"])]}
            
        # Compilar o LangGraph
        graph_builder = StateGraph(GraphState)
        graph_builder.add_node("chatbot", chatbot)
        
        tool_node = ToolNode(tools=tools)
        graph_builder.add_node("tools", tool_node)
        
        graph_builder.add_conditional_edges("chatbot", tools_condition)
        graph_builder.add_edge("tools", "chatbot")
        graph_builder.set_entry_point("chatbot")
        
        app = graph_builder.compile()
        
        # Executar a rede (O loop ReAct)
        final_state = app.invoke({"messages": messages})
        
        # O último message será do assistente
        response_content = final_state["messages"][-1].content
        
        # Salvar resposta do assistente no banco
        ai_msg_db = ChatMessage(session_id=session_id, role="assistant", content=response_content)
        db.add(ai_msg_db)
        db.commit()
        
        return jsonify({
            "response": response_content,
            "session_id": session_id
        })
    except Exception as e:
        logger.critical(f"Erro crítico ao processar mensagem: {e}", exc_info=True)
        return jsonify({"error": "Erro interno", "details": str(e)}), 500
    finally:
        db.close()


