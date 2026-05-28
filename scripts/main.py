from pix2text import Pix2Text

img_fp = 'assets/img/equacao.jpg'
p2t = Pix2Text.from_config()
outs = p2t.recognize_formula(img_fp)
print(outs)