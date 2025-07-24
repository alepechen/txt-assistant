from flask import Flask, render_template, request, jsonify
from next_word_prediction import GPT2
from spellchecker import SpellChecker
import contractions
import re
import string

app = Flask(__name__)

gpt2 = GPT2()

spell = SpellChecker()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict',methods=["POST"])
def predict():
    text = request.form.get('text', '')
    prediction = (gpt2.predict_next(text,3))
    filtered_prediction = [word for word in prediction if word not in string.punctuation]
    prediction = "\t\t\t".join(filtered_prediction)
    response = {
        'prediction': prediction
    }
    return jsonify(response)

@app.route('/complete', methods=["POST"])
def complete():
    input_text = request.form.get('formData', '').strip()
    text = input_text.split('.')
    last_sentence = text[-1]
    word = gpt2.predict_next(last_sentence,1)[0]
    text = " ".join(text[:-1])
    res = text + last_sentence + " " + word
    return res

@app.route('/fix_current', methods=['POST'])    
def fix_current():
    input_text = request.form.get('text','')
    misspelled = spell.unknown([input_text])
    corrected = None
    if misspelled:
        corrected = spell.correction(input_text)

    if corrected:
        return corrected
    return input_text


@app.route('/fix_all', methods=['POST'])
def fix_all():
    input_text = request.form.get('text','')
    misspelled = spell.unknown(input_text.split())
    for word in misspelled:
        correction = spell.correction(word)
        if correction != word:
            input_text = input_text.replace(word, correction)

    return input_text

if __name__ == '__main__':
    app.run()