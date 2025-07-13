import "./App.css";
import { perguntar } from "../src/API/perguntar.tsx";
import { useState } from "react";

function App() {
  const [mensagem, setMensagem] = useState();
  const [isFirstQuest, setIsFirstQuest] = useState(true);
  const [respostas, setRespostas] = useState([]);
  const [perguntas, setPerguntas] = useState([]);
  const [ultimo_filme, setUltimoFilme] = useState(null);

  const handleClick = async () => {
    if (!mensagem) return;

    try {
      if (isFirstQuest) {
        setIsFirstQuest(false);
      }

      // Chama a API e armazena a resposta
      const data = await perguntar(mensagem);

      if (data.ultimo_filme) {
        setUltimoFilme(data.ultimo_filme);
      }

      // Atualiza o estado mantendo as respostas anteriores
      setRespostas((prev) => [...prev, data]);
      setPerguntas((prev) => [...prev, mensagem]);

      return data;
    } catch (error) {
      console.error("Erro ao buscar resposta:", error);
      // Você pode adicionar o erro ao array se quiser:
      // setRespostas(prev => [...prev, { error: error.message }]);
      throw error;
    } finally {
      setMensagem("");
    }
  };

  console.log(respostas);
  return (
    <div className="App">
      {isFirstQuest ? (
        <header
          className="App-header"
          style={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
          }}
        >
          <div
            style={{
              marginBottom: 40,
              fontSize: "2rem",
              fontWeight: "bold",
            }}
          >
            Vamos falar sobre filmes?
          </div>

          <div
            style={{
              marginBottom: 60,
              fontSize: "1.2rem",
              opacity: 0.8,
            }}
          >
            Como posso te ajudar hoje?
          </div>

          <div
            style={{
              display: "flex",
              width: 500,
              maxWidth: 600,
              gap: 10,
            }}
          >
            <input
              placeholder="Digite sua pergunta..."
              style={{
                borderRadius: "12px",
                flex: 1,
                padding: "12px 16px",
                border: "1px solid rgba(255,255,255,0.2)",
                backgroundColor: "rgba(0,0,0,0.2)",
                color: "white",
                fontSize: "1rem",
                outline: "none",
              }}
              onChange={(e) => {
                setMensagem(e.target.value);
              }}
            />
            <button
              style={{
                borderRadius: "12px",
                padding: "0 20px",
                border: "none",
                backgroundColor: "#1e88e5",
                color: "white",
                fontWeight: "bold",
                cursor: "pointer",
                fontSize: "1rem",
              }}
              disabled={!mensagem}
              onClick={() => {
                handleClick(mensagem);
              }}
            >
              Enviar
            </button>
          </div>
        </header>
      ) : (
        <div
          style={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
          }}
        >
          <div style={{ flex: 1, overflowY: "auto", padding: "20px" }}>
            {respostas?.map((item, index) => (
              <div
                key={index}
                style={{ display: "flex", flexDirection: "column" }}
              >
                {/* Balão da PERGUNTA (alinhado à direita) */}
                <div
                  style={{
                    alignSelf: "flex-start",
                    maxWidth: "80%",
                    background: "#616161",
                    marginBottom: 12,
                    padding: "12px 16px",
                    borderRadius: "12px",
                    borderBottomRightRadius: "4px",
                    wordWrap: "break-word",
                    whiteSpace: "pre-wrap",
                  }}
                >
                  {perguntas[index]}
                </div>

                {/* Balão da RESPOSTA ou ERRO (alinhado à esquerda) */}
                {item.erro ? (
                  <div
                    style={{
                      alignSelf: "flex-end",
                      maxWidth: "80%",
                      background: "#ff6b6b",
                      color: "white",
                      padding: "12px 16px",
                      borderRadius: "12px",
                      borderBottomLeftRadius: "4px",
                      marginBottom: 20,
                      wordWrap: "break-word",
                    }}
                  >
                    Erro: {item.erro}
                  </div>
                ) : (
                  <div
                    style={{
                      alignSelf: "flex-end",
                      maxWidth: "80%",
                      background: "#414158",
                      padding: "12px 16px",
                      borderRadius: "12px",
                      borderBottomLeftRadius: "4px",
                      marginBottom: 20,
                      wordWrap: "break-word",
                      whiteSpace: "pre-wrap",
                    }}
                  >
                    {typeof item.resposta === "object"
                      ? JSON.stringify(item.resposta, null, 2)
                      : item.resposta}
                  </div>
                )}
              </div>
            ))}
          </div>

          <header
            className="App-header"
            style={{
              padding: "50px",
            }}
          >
            <div
              style={{
                display: "flex",
                width: "100%",
                margin: "0 auto",
                gap: 10,
              }}
            >
              <input
                placeholder="Digite sua pergunta..."
                value={mensagem}
                style={{
                  borderRadius: "12px",
                  flex: 1,
                  padding: "12px 16px",
                  border: "1px solid rgba(255,255,255,0.2)",
                  backgroundColor: "rgba(0,0,0,0.2)",
                  color: "white",
                  fontSize: "1rem",
                  outline: "none",
                }}
                onChange={(e) => {
                  setMensagem(e.target.value);
                }}
              />
              <button
                style={{
                  borderRadius: "12px",
                  padding: "0 20px",
                  border: "none",
                  backgroundColor: "#1e88e5",
                  color: "white",
                  fontWeight: "bold",
                  cursor: "pointer",
                  fontSize: "1rem",
                }}
                onClick={() => {
                  handleClick(mensagem);
                }}
              >
                Enviar
              </button>
            </div>
          </header>
        </div>
      )}
    </div>
  );
}

export default App;
