from flask import Flask, request, render_template, jsonify, send_from_directory
import os
from datetime import datetime
import torch
import pretty_midi
from midi_lstm_gan_sample import lstmGenerator, data_to_midi, save_midi

app = Flask(__name__)

MIDI_OUTPUT_DIR = "static/music/generated"
os.makedirs(MIDI_OUTPUT_DIR, exist_ok=True)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/generate_music', methods=['POST'])
def generate_music():
    data = request.get_json()
    model_name = data.get("model")

    if not model_name:
        return jsonify({"error": "Model name is required."}), 400

    try:
        model_path = f"models/{model_name}.pth"
        input_size = 4
        hidden_size = 64
        num_layers = 1
        seq_len = 500
        generate_batch_size = 1

        generator = lstmGenerator(input_size=input_size, hidden_size=hidden_size,
                                  seq_len=seq_len, num_layers=num_layers)
        generator.load_state_dict(torch.load(model_path, map_location=torch.device("cpu"), weights_only=True))
        generator.eval()

        noise = torch.randn(generate_batch_size, seq_len, input_size)
        with torch.no_grad():
            generated_notes = generator(noise).squeeze(0).cpu().detach().tolist()

        midi = data_to_midi(generated_notes)

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{model_name}_{timestamp}"
        saved_file = save_midi(midi, midi_dir=MIDI_OUTPUT_DIR, filename=filename)

        return jsonify({"generatedFiles": [filename + ".mid"]})

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route('/music/<filename>')
def serve_midi(filename):
    return send_from_directory(MIDI_OUTPUT_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True)
