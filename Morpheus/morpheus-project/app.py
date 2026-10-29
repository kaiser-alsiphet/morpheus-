"""Morpheus detector UI. Run: python app.py"""
import gradio as gr
from src.predict import DISCLAIMER, available_models, predict_text

MODELS = available_models()
MODEL = MODELS.get("transformer") or MODELS.get("baseline")


def analyze(text: str):
    result = predict_text(text, MODEL)
    if result["error"]:
        return "", "", "", result["error"], ""

    info = f'{result["chars"]} characters · {result["words"]} words · model: {result["model"]}'
    warnings = " ".join([result["message"]] + result["warnings"])
    return (
        f'{result["p_ai"]:.1%} likelihood',
        f'{result["p_human"]:.1%} likelihood',
        result["label"],
        warnings,
        info,
    )


CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@700&family=JetBrains+Mono&family=Lexend&display=swap');

:root {
  --ivory: #fffdf5;
  --paper: #ffffff;
  --ink: #181818;
  --muted: #716c5d;
  --line: #ded8c8;
  --yellow: #f4c542;
  --yellow-dark: #aa7f00;
  --soft: #fff1a8;
}

.gradio-container {
  max-width: 1120px !important;
  margin: 0 auto !important;
  background: var(--ivory) !important;
  color: var(--ink) !important;
  font-family: Lexend, system-ui, sans-serif !important;
}

body { background: var(--ivory) !important; }

#brand h1, h1, h2, h3, button, label span {
  font-family: "Chakra Petch", system-ui, sans-serif !important;
  color: var(--ink) !important;
}

#brand h1 {
  font-size: clamp(3.5rem, 9vw, 7rem) !important;
  line-height: .88 !important;
  letter-spacing: -.04em !important;
  margin: 0 !important;
}

#brand p, .disclaimer { color: var(--muted) !important; }

.panel, .result-panel {
  background: var(--paper) !important;
  border: 1px solid var(--line) !important;
  border-radius: 6px !important;
  box-shadow: 0 4px 20px rgba(40,35,20,.05) !important;
}

textarea, input {
  background: var(--paper) !important;
  color: var(--ink) !important;
  border: 1px solid var(--line) !important;
  border-radius: 5px !important;
  font-family: Lexend, system-ui, sans-serif !important;
}

textarea:focus, input:focus {
  border-color: var(--yellow-dark) !important;
  box-shadow: 0 0 0 2px var(--soft) !important;
}

button.primary {
  background: var(--yellow) !important;
  color: var(--ink) !important;
  border: 1px solid var(--yellow-dark) !important;
  border-radius: 5px !important;
  font-weight: 700 !important;
}

button.primary:hover { background: #eabb32 !important; }

.output-label, .label-wrap span, .block-label span {
  color: var(--muted) !important;
  font-family: "JetBrains Mono", monospace !important;
  text-transform: uppercase;
  letter-spacing: .04em;
}

footer { display: none !important; }
"""

with gr.Blocks(title="Morpheus", css=CUSTOM_CSS, theme=gr.themes.Base()) as demo:
    gr.Markdown(
        "# MORPHEUS\n"
        "### A likelihood estimate for patterns commonly associated with AI-generated writing.\n\n"
        f"<p class='disclaimer'>{DISCLAIMER}</p>",
        elem_id="brand",
    )

    with gr.Column(elem_classes="panel"):
        box = gr.Textbox(
            lines=12,
            label="Paste your text",
            placeholder="Paste an article, paragraph, or essay here...",
        )
        btn = gr.Button("RUN DETECTOR", variant="primary")

    with gr.Column(elem_classes="result-panel"):
        gr.Markdown("## Result")
        outs = [
            gr.Textbox(label=label, interactive=False)
            for label in [
                "AI likelihood",
                "Human likelihood",
                "Prediction",
                "Confidence and warnings",
                "Input details",
            ]
        ]

    btn.click(analyze, inputs=box, outputs=outs)
    gr.Markdown(
        "**Privacy:** Text is processed on this server for analysis and is not stored by this app. "
        "Do not use this estimate as the sole basis for decisions about a person."
    )


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
