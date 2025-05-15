import gradio as gr
from back import response_image,response_write


with gr.Blocks() as app:
    gr.Markdown("# PESQUISA DE PRODUTOS")
    with gr.Tab(label="pesquisar por imagem"):
        file = gr.Image(type="filepath")
        buton_imagem = gr.Button()
        text_image = gr.TextArea(label="resposta")

        button_output = buton_imagem.click(
            fn=response_image,
            inputs=[file],
            outputs=[text_image]
        )

        

    with gr.Tab(label="pesquisar por escrita"):
        text_escrita = gr.Textbox(label="escreva o nome do produto")
        buton_escrita = gr.Button()
        text_resposta_escrita = gr.TextArea(label="resposta")


        buton_escrita.click(
            fn=response_write,
            inputs=[text_escrita],
            outputs=[text_resposta_escrita]
        )

app.launch()