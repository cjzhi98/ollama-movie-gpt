import gradio as gr
from utils import run_conversation


def chatbot(input_text):
    return run_conversation(input_text)


iface = gr.Interface(
    title="Ollama Movies Recommendation Chatbot",
    fn=chatbot,
    inputs=gr.Textbox(lines=2, placeholder="Type something here..."),
    outputs="text",
)

iface.launch()
