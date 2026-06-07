import json

import os

from pathlib import Path



from dotenv import load_dotenv

from flask import Flask, jsonify, request

from openai import OpenAI



load_dotenv()



ROOT_DIR = Path(__file__).resolve().parent.parent

app = Flask(__name__, static_folder=str(ROOT_DIR), static_url_path='')

UPLOAD_FOLDER = ROOT_DIR / 'uploads'

UPLOAD_FOLDER.mkdir(exist_ok=True)



p2t = None

CATEGORIES = [

    'Álgebra (Equações e Manipulação)',

    'Geometria',

    'Funções e Gráficos',

    'Estatística e Probabilidade',

    'Trigonometria',

    'Cálculo',

    'Logaritmos',

    'Exponenciais',

]





def heuristic_classify(latex: str) -> str:

    text = (latex or '').lower()



    if any(token in text for token in ('sin(', 'cos(', 'tan(', 'cot(', 'sec(', 'csc(', 'arcsin', 'arccos', 'arctan')):

        return 'Trigonometria'

    if any(token in text for token in ('log(', 'ln(', 'log_')):

        return 'Logaritmos'

    if any(token in text for token in ('e^', '^x', 'exp(', 'e^{')):

        return 'Exponenciais'

    if any(token in text for token in ('∫', 'integral', 'derivada', 'lim ', 'd/dx', 'dx', 'dy/dx')):

        return 'Cálculo'

    if any(token in text for token in ('media', 'desvio', 'variância', 'probabilidade', 'binomial', 'normal', 'σ', 'μ', 'p(x)', 'e(x)')):

        return 'Estatística e Probabilidade'

    if any(token in text for token in ('f(x)', 'y=', 'graf', 'plt.', 'plot(', 'domínio', 'imagem')):

        return 'Funções e Gráficos'

    if any(token in text for token in ('triângulo', 'ângulo', 'círculo', 'raio', 'diâmetro', 'área', 'perímetro', 'paralelo', 'perpendicular')):

        return 'Geometria'

    return 'Álgebra (Equações e Manipulação)'





def classify_latex(latex: str):

    api_key = os.getenv('OPENAI_API_KEY') or os.getenv('OPENAI_APIKEY')

    if not api_key:

        return heuristic_classify(latex), 'heurística'



    try:

        client = OpenAI(api_key=api_key)

        response = client.chat.completions.create(

            model='gpt-4o-mini',

            temperature=0,

            messages=[

                {

                    'role': 'system',

                    'content': (

                        'Você classifica equações matemáticas em exatamente uma destas categorias: '

                        + ', '.join(CATEGORIES)

                        + '. Responda apenas em JSON no formato {"categoria": "..."}.'

                    ),

                },

                {

                    'role': 'user',

                    'content': f'Equação em LaTeX: {latex or "(sem LaTeX detectado)"}',

                },

            ],

        )

        content = response.choices[0].message.content or '{}'

        payload = json.loads(content)

        categoria = str(payload.get('categoria', '')).strip()

        if categoria in CATEGORIES:

            return categoria, 'IA'

    except Exception as exc:

        app.logger.exception('Falha na classificação via IA: %s', exc)



    return heuristic_classify(latex), 'heurística'





def get_pix2text():

    global p2t

    if p2t is not None:

        return p2t

    try:

        from pix2text import Pix2Text

        p2t = Pix2Text.from_config()

    except Exception as exc:

        app.logger.exception('Falha ao inicializar Pix2Text: %s', exc)

        p2t = None

    return p2t



def extract_latex(resultado):

    if isinstance(resultado, list):

        return resultado[0].get('latex', str(resultado)) if resultado else ''

    if isinstance(resultado, dict):

        return resultado.get('latex', str(resultado))

    return str(resultado)



def sanitize_latex(latex):

    if latex is None:

        return ''

    arrow_patterns = [

        '\\leftrightarrow', '\\Longleftrightarrow', '\\longleftrightarrow',

        '\\Rightarrow', '\\Leftarrow', '\\iff', '\\implies', '\\impliedby',

        '\\leftharpoonup', '\\rightharpoonup', '\\xrightarrow', '\\xleftarrow',

        '\\Leftrightarrow', '\\Rightarrow', '\\Leftarrow', '\\leftrightarrow',

    ]

    cleaned = latex.replace('\n', ' ')

    for pattern in arrow_patterns:

        cleaned = cleaned.replace(pattern, '')

    cleaned = cleaned.replace('⇄', '')

    cleaned = cleaned.replace('⇆', '')

    cleaned = cleaned.replace('⇔', '')

    cleaned = cleaned.replace('←', '')

    cleaned = cleaned.replace('→', '')

    cleaned = cleaned.replace('↔', '')

    cleaned = cleaned.replace('↕', '')

    while '  ' in cleaned:

        cleaned = cleaned.replace('  ', ' ')

    return cleaned.strip()



@app.route('/')

def index():

    return app.send_static_file('home.html')



@app.route('/upload', methods=['POST'])

def upload():

    arquivo = request.files.get('imagem')

    if arquivo is None or arquivo.filename == '':

        return jsonify({'error': 'Nenhum arquivo enviado'}), 400

    save_path = UPLOAD_FOLDER / arquivo.filename

    arquivo.save(save_path)

    p2t_instance = get_pix2text()

    if p2t_instance is None:

        return jsonify({'error': 'OCR não disponível. Verifique a instalação de pix2text/ANTLR/omegaconf.'}), 500

    resultado = p2t_instance.recognize_formula(str(save_path))

    latex = extract_latex(resultado)

    cleaned_latex = sanitize_latex(latex)

    categoria, fonte = classify_latex(cleaned_latex)

    return jsonify({

        'latex': cleaned_latex,

        'categoria': categoria,

        'fonte': fonte,

    })



if __name__ == '__main__':

    app.run(debug=True)

