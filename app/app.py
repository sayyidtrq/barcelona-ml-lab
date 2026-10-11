"""Gradio app untuk Hugging Face Spaces (stub). Jalankan lokal: python app/app.py"""

import gradio as gr


def predict(opponent: str, is_home: bool):
    # TODO: ganti dengan barca_ml.models.predict setelah model tersedia
    return {"Win": 0.0, "Draw": 0.0, "Lose": 0.0}


demo = gr.Interface(
    fn=predict,
    inputs=[gr.Textbox(label="Lawan"), gr.Checkbox(label="Barcelona main kandang")],
    outputs=gr.Label(label="Probabilitas hasil"),
    title="Barca Match Predictor",
    description=(
        "Prediksi probabilitas hasil laga Barcelona. Untuk hiburan dan analitik, bukan taruhan."
    ),
)

if __name__ == "__main__":
    demo.launch()
