export const perguntar = async (pergunta) => {
  try {
    const resposta = await fetch("http://localhost:5000/perguntar", {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        pergunta: pergunta,
      }),
    });

    if (!resposta.ok) {
      const erroData = await resposta.json();
      throw new Error(erroData.erro || `Erro HTTP: ${resposta.status}`);
    }

    return await resposta.json();
  } catch (error) {
    console.error("Erro na chamada API:", error);
    throw error;
  }
};
