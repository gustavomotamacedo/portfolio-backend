# 🔧 Configuração de CORS - API Flask

## ✅ O Que Foi Feito

### 1. **Instalação do flask-cors**

```bash
pip install flask-cors
```

### 2. **Configuração no app.py**

Adicionada a configuração de CORS para permitir requisições do frontend Next.js:

```python
from flask_cors import CORS

# Configurar CORS para permitir requisições do frontend
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})
```

### 3. **Atualização do requirements.txt**

```
flask
flask-cors
```

## 🚀 Como Aplicar as Mudanças

### Opção 1: Reiniciar o servidor Flask manualmente

```bash
# Parar o servidor (Ctrl+C no terminal)
# Depois executar novamente:
flask run
# ou
python app.py --debug
```

### Opção 2: O Flask pode detectar mudanças automaticamente

Se estiver rodando com `--debug` ou `debug=True`, o Flask deve detectar as mudanças e reiniciar automaticamente.

## 🔍 Verificar se Funcionou

### 1. Checar logs do Flask

Você deve ver algo como:

```
* Restarting with stat
* Debugger is active!
* Running on http://localhost:5000
```

### 2. Testar no Frontend

Abra http://localhost:3000 e envie uma mensagem. O erro de CORS deve desaparecer!

### 3. Console do Navegador

**ANTES (com erro):**

```
❌ Requisição cross-origin bloqueada: A diretiva Same Origin...
❌ Código de status: 200
```

**DEPOIS (funcionando):**

```
✅ POST http://localhost:5000/api/chat 200 OK
✅ Resposta recebida com sucesso
```

## 📋 Configuração CORS Explicada

```python
CORS(app, resources={
    r"/api/*": {                                    # Aplica a todas as rotas /api/*
        "origins": [
            "http://localhost:3000",                # Frontend Next.js
            "http://127.0.0.1:3000"                 # Alternativa localhost
        ],
        "methods": [                                 # Métodos HTTP permitidos
            "GET", "POST", "PUT", "DELETE", "OPTIONS"
        ],
        "allow_headers": [                          # Headers permitidos
            "Content-Type", "Authorization"
        ],
        "supports_credentials": True                # Permite cookies/sessões
    }
})
```

## 🎯 Próximos Passos

1. **Reiniciar servidor Flask** (se ainda não fez)
2. **Testar chat no frontend** - http://localhost:3000
3. **Verificar se mensagens são enviadas e recebidas**
4. **Verificar se histórico é recuperado**

## 🐛 Troubleshooting

### Problema: Ainda aparece erro de CORS

**Solução:**

1. Verificar se o servidor Flask foi reiniciado
2. Verificar se flask-cors foi instalado corretamente
3. Limpar cache do navegador (Ctrl+Shift+R)

### Problema: ImportError: No module named 'flask_cors'

**Solução:**

```bash
# Ativar ambiente virtual (se estiver usando)
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar flask-cors
pip install flask-cors
```

### Problema: Servidor não reinicia automaticamente

**Solução:**

```bash
# Parar servidor (Ctrl+C)
# Iniciar novamente:
python app.py --debug
```

## ✨ Arquivos Modificados

- ✅ `api/app.py` - Adicionado CORS
- ✅ `api/requirements.txt` - Adicionado flask-cors

---

**Status**: ✅ CORS CONFIGURADO - Aguardando reinício do servidor Flask
