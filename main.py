from flask import Flask, jsonify
import random
import datetime

app = Flask(__name__)

@app.route("/gerar-sinal")
def gerar_sinal():
    ativos = ["EURUSD", "GBPUSD", "USDJPY"]
    direcoes = ["CALL", "PUT"]
    tempos = ["1M", "5M"]

    agora = datetime.datetime.now().strftime("%H:%M")

    sinal = {
        "ativo": random.choice(ativos),
        "direcao": random.choice(direcoes),
        "tempo": random.choice(tempos),
        "horario": agora
    }

    return jsonify(sinal)

if __name__ == "__main__":
    app.run(debug=True)