# Makefile para RAG Project

# Comandos
API_CMD = uvicorn api.main:app --host 0.0.0.0 --port 8005 --reload --log-level debug
# Ajuste: O caminho correto para o arquivo é streamlit/admin_frontend.py
STREAMLIT_CMD = streamlit run streamlit/admin_frontend.py

.PHONY: start stop logs clean

start:
	@echo "🚀 Iniciando a API em background..."
	@# Inicia a API, redireciona logs para api.log e salva o PID
	@nohup $(API_CMD) > api.log 2>&1 & echo $$! > api.pid
	
	@echo "🚀 Iniciando o Streamlit em background..."
	@# Inicia o Streamlit, redireciona logs para streamlit.log e salva o PID
	@nohup $(STREAMLIT_CMD) > streamlit.log 2>&1 & echo $$! > streamlit.pid
	
	@echo "✅ Sistema Online!"
	@echo "   📄 API Docs: http://localhost:8005/docs"
	@echo "   💻 Frontend: http://localhost:8502"
	@echo "   📝 Para ver os logs, use: make logs"

stop:
	@echo "🛑 Parando serviços..."
	@# Verifica se existe o arquivo PID da API e mata o processo
	@if [ -f api.pid ]; then \
		kill `cat api.pid` && rm api.pid && echo "   - API parada"; \
	else \
		echo "   - API não parece estar rodando (arquivo pid não encontrado)"; \
	fi
	
	@# Verifica se existe o arquivo PID do Streamlit e mata o processo
	@if [ -f streamlit.pid ]; then \
		kill `cat streamlit.pid` && rm streamlit.pid && echo "   - Streamlit parado"; \
	else \
		echo "   - Streamlit não parece estar rodando (arquivo pid não encontrado)"; \
	fi
	@echo "✅ Tudo desligado."

logs:
	@echo "👀 Acompanhando logs (Ctrl+C para sair)..."
	@tail -f api.log streamlit.log

clean: stop
	@echo "🧹 Limpando arquivos de log e cache..."
	@rm -f api.log streamlit.log
	@find . -type d -name "__pycache__" -exec rm -rf {} +