import pytest
import os
import json
from unittest.mock import patch, MagicMock
from app import app
from database import init_db, get_db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    # Usar um banco de dados em memória ou arquivo temporário para testes
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:' 
    
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client

def test_chat_history_empty(client):
    """Testa se o histórico retorna vazio para uma nova sessão."""
    response = client.get('/api/chat/history?session_id=nova_sessao_123')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'history' in data
    assert data['history'] == []

def test_chat_missing_message(client):
    """Testa o comportamento da API quando a mensagem não é enviada."""
    response = client.post('/api/chat', json={"session_id": "123"})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

@patch('langgraph.graph.StateGraph.compile')
def test_chat_flow_without_tools(mock_compile, client):
    """Testa fluxo de chat simples onde o LLM não precisa chamar nenhuma ferramenta."""
    
    # Mock do retorno do compile()
    mock_app = MagicMock()
    mock_compile.return_value = mock_app
    
    # Mock do retorno do app.invoke()
    from langchain_core.messages import AIMessage
    mock_app.invoke.return_value = {"messages": [AIMessage(content="Olá! Tudo bem, sou Gustavo.")]}

    response = client.post('/api/chat', json={"message": "Oi, quem é você?"})
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'response' in data
    assert "Gustavo" in data['response']
    assert 'session_id' in data

def test_chat_tempo_experiencia_tool(client):
    """Testa a nova ferramenta de tempo de experiência isoladamente."""
    from blueprints.chat import obter_tempo_experiencia
    
    # Testa ano simples chamando o invoke da tool
    resultado_ano = obter_tempo_experiencia.invoke("2020")
    assert "ano" in resultado_ano
    
    # Testa mês e ano
    resultado_mes = obter_tempo_experiencia.invoke("01/2021")
    assert "ano" in resultado_mes or "mês" in resultado_mes

