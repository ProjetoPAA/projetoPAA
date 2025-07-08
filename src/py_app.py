from flask import Flask, request, jsonify
from src import data_base, engine

# =============================================
# INICIALIZAÇÃO DO SISTEMA
# =============================================
kb = data_base.KnowledgeBase()
qa_engine = engine.QAEngine(kb)
# Configuração inicial do Flask
app = Flask(__name__)


@app.route('/perguntar', methods=['POST'])
def responder():
    data = request.get_json()
    
    if not data or 'pergunta' not in data:
        return jsonify({'erro': 'Campo "pergunta" é obrigatório'}), 400
    
    pergunta = data['pergunta']
    
    try:
        # Pré-processamento
        pergunta_processada = qa_engine.preprocessor.preprocess(pergunta)
        pergunta_processada = qa_engine.expand_synonyms(pergunta_processada)
        
        # Identificação do filme
        titulo_filme, score = qa_engine.find_most_similar(pergunta_processada)
        
        if score < 0.2:
            return jsonify({'resposta': "Não tenho informações suficientes sobre esse filme."})
        
        # Obtenção da resposta
        filme = kb.get_filme(titulo_filme)
        if not filme:
            return jsonify({'resposta': "Filme não encontrado na base de dados."})
        
        question_type = qa_engine.identify_question_type(pergunta)
        resposta = qa_engine.generate_answer(filme, question_type)
        
        return jsonify({
            'pergunta': pergunta,
            'resposta': resposta,
            'filme': titulo_filme,
            'score': float(score)
        })
    except Exception as e:
        return jsonify({'erro': str(e)}), 500