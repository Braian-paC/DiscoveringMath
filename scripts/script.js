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

function getCategoryPage(category) {
  const pages = {
    'Álgebra (Equações e Manipulação)': 'pages/1_algebra.html',
    'Geometria': 'pages/2_geometria.html',
    'Funções e Gráficos': 'pages/3_funcoesegraficos.html',
    'Estatística e Probabilidade': 'pages/4_estatisticaprobabilidade.html',
    'Trigonometria': 'pages/5_trigonometria.html',
    'Cálculo': 'pages/6_calculo.html',
    'Logaritmos': 'pages/7_logaritmos.html',
    'Exponenciais': 'pages/8_exponenciais.html',
  };

  return pages[category] || '';
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
    const cleaned = sanitizeLatex(result.latex || '');
    const categoria = result.categoria || 'Categoria não identificada';
    const pageHref = getCategoryPage(categoria);
    const linkHtml = pageHref
      ? `<a href="${pageHref}" class="btn btn-sm btn-outline-primary mt-2" target="_blank" rel="noopener noreferrer">Abrir página de ${categoria}</a>`
      : '';

    if (window.katex && cleaned) {
      resultDiv.innerHTML = `
        ${linkHtml}
        <div id='math-render'></div>
      `;
      katex.render(cleaned, document.getElementById('math-render'), {throwOnError: false});
    } else if (result.latex) {
      resultDiv.innerHTML = `
        ${linkHtml}
        <pre class='mb-0'>${result.latex}</pre>
      `;
    } else {
      resultDiv.textContent = 'Não foi possível obter a equação lida da imagem.';
    }
  } catch (err) {
    resultDiv.textContent = `Erro de conexão: ${err.message}`;
  }
});
