const form = document.getElementById('uploadForm');
const fileInput = document.getElementById('imagemInput');
const resultDiv = document.getElementById('uploadResult');

function sanitizeLatex(latex) {
  if (!latex) return '';
  return latex
    .replace(/\\(?:leftrightarrow|Longleftrightarrow|longleftrightarrow|Rightarrow|Leftarrow|iff|implies|impliedby|leftharpoonup|rightharpoonup|xrightarrow|xleftarrow)\b/g, '')
    .replace(/[⇄⇆⇔⇐⇒⇔←→↔↕⟷⟹⟸]/g, '')
    .replace(/\s{2,}/g, ' ')
    .trim();
}

fileInput.addEventListener('change', () => {
  if (fileInput.files.length > 0) {
    form.requestSubmit();
  }
});

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  if (!fileInput.files.length) {
    resultDiv.textContent = 'Selecione uma imagem antes de enviar.';
    return;
  }

  const data = new FormData(form);
  resultDiv.textContent = 'Enviando imagem...';

  try {
    const response = await fetch('/upload', {
      method: 'POST',
      body: data,
    });

    if (!response.ok) {
      const erro = await response.text();
      resultDiv.textContent = `Erro: ${erro}`;
      return;
    }

    const result = await response.json();
    if (result.solution) {
      const cleaned = sanitizeLatex(result.latex || '');
      resultDiv.innerHTML = `
        <div id='math-render'></div>
        <div class='solution-result'>Resultado: ${result.solution}</div>
      `;
      if (window.katex && cleaned) {
        katex.render(cleaned, document.getElementById('math-render'), {throwOnError: false});
      }
    } else if (result.error) {
      resultDiv.textContent = `Erro: ${result.error}`;
    } else {
      resultDiv.textContent = 'Não foi possível obter um resultado da equação.';
    }
  } catch (err) {
    resultDiv.textContent = `Erro de conexão: ${err.message}`;
  }
});
