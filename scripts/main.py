from pathlib import Path

from flask import Flask, request, jsonify
from pix2text import Pix2Text

ROOT_DIR = Path(__file__).resolve().parent.parent
app = Flask(__name__, static_folder=str(ROOT_DIR), static_url_path='')
UPLOAD_FOLDER = ROOT_DIR / 'uploads'
UPLOAD_FOLDER.mkdir(exist_ok=True)

p2t = Pix2Text.from_config()


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


def try_parse_latex(text):
    from sympy.parsing.latex import parse_latex

    replacements = {
        '\\cdot': '*',
        '\\times': '*',
        '\\div': '/',
        '\\left': '',
        '\\right': '',
        '\\,': '',
        '\\;': '',
        '\\!': '',
        '\\ ': '',
        '\\mathrm': '',
        '\\text': '',
        '\\left(': '(',
        '\\right)': ')',
    }

    cleaned = text
    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new)

    cleaned = cleaned.replace('^ ', '^').replace('_ ', '_')
    return parse_latex(cleaned)


def solve_equation(latex):
    try:
        from sympy import Eq, solve
        from sympy.parsing.latex import parse_latex
    except Exception as exc:
        return None, f'Sympy não disponível ou parser LaTeX não instalado: {exc}'

    cleaned = sanitize_latex(latex)
    try:
        expr = parse_latex(cleaned)
    except Exception:
        try:
            expr = try_parse_latex(cleaned)
        except Exception as exc:
            return None, f'Não foi possível interpretar a equação: {exc}'

    if not getattr(expr, 'is_Relational', False):
        from sympy import Eq

        expr = Eq(expr, 0)

    symbols = list(expr.free_symbols)
    if not symbols:
        return None, 'A equação não contém variáveis reconhecíveis a resolver.'

    try:
        solutions = solve(expr, symbols)
    except Exception as exc:
        return None, f'Erro ao resolver a equação: {exc}'

    if not solutions:
        return 'Sem soluções reais ou não é uma equação univariada.', None

    return str(solutions), None


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

    resultado = p2t.recognize_formula(str(save_path))
    latex = extract_latex(resultado)
    cleaned_latex = sanitize_latex(latex)
    solution, error = solve_equation(cleaned_latex)
    if error:
        return jsonify({'error': error, 'latex': cleaned_latex})

    return jsonify({'latex': cleaned_latex, 'solution': solution})


if __name__ == '__main__':
    app.run(debug=True)
