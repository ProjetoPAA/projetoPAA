from knowledgebase import KnowledgeBase
from engine import EnhancedQAEngine
from flask import Flask, request, jsonify, session
from flask_cors import CORS

# Configuração inicial do Flask
app = Flask(__name__)
app.secret_key = 'estigma'
CORS(
    app,
    supports_credentials=True,
    origins=["http://localhost:3000"],
    methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"]
)

# =============================================
#  INICIALIZAÇÃO DO SISTEMA
# =============================================
kb = KnowledgeBase()
qa_engine = EnhancedQAEngine(kb)

# =============================================
#  ROTAS DA API
# =============================================
@app.route('/perguntar', methods=['POST'])
def responder():
    data = request.get_json()
    
    if not data or 'pergunta' not in data:
        return jsonify({'erro': 'Campo "pergunta" é obrigatório'}), 400
    
    pergunta = data['pergunta']
    
    try:
        pergunta_processada = qa_engine.preprocessor.preprocess(pergunta)
        pergunta_processada = qa_engine.expand_synonyms(pergunta_processada)
        
        titulo_filme, score = qa_engine.find_most_similar(pergunta_processada)
        
        if score < 0.2:
            return jsonify({'resposta': "Não tenho informações suficientes sobre esse filme."})
        
        filme = kb.get_filme(titulo_filme)
        if not filme:
            return jsonify({'resposta': "Filme não encontrado na base de dados."})
        
        question_type = qa_engine.identificar_tipo_pergunta(pergunta)
        resposta = qa_engine.gerar_resposta_avancada(filme, question_type)

        session['ultimo_filme'] = titulo_filme
        
        return jsonify({
            'pergunta': pergunta,
            'resposta': resposta,
            'filme': titulo_filme,
            'score': float(score),
            'ultimo_filme': session.get('ultimo_filme')
        })
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/debug_sessao', methods=['GET'])
def debug_sessao():
    return jsonify({
        'session_id': session.sid,
        'ultimo_filme': session.get('ultimo_filme'),
        'todos_dados': dict(session)
    })

if __name__ == '__main__':
    import nltk
    nltk.download('stopwords')
    app.run(debug=True)