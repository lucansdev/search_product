from langchain.agents import AgentType,Tool,initialize_agent
from langchain.utilities import SerpAPIWrapper
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import os 
import dotenv
from openai import OpenAI
import base64

dotenv.load_dotenv()

llm = ChatOpenAI(api_key=os.getenv("openaiKey"),model="gpt-4.1-mini")


def search_results(query):
    """busca resultado de varias pesquisas e retorna os resultados:precisa ser passado o que quer pesquisar no query"""

    params = {
        "no_cache":True,
        "gl":"br",
        "hl":"pt"

    }
    search = SerpAPIWrapper(serpapi_api_key=os.getenv("searpAPI"),params=params)
    resultado = search.results(f"{query} preço")

    contexto_para_chatgpt = ""
    if 'organic_results' in resultado:
        for i, result in enumerate(resultado['organic_results'][:3]): # Pega os 3 primeiros, por exemplo
            contexto_para_chatgpt += f"Resultado {i+1}:\n"
            contexto_para_chatgpt += f"  Título: {result.get('title', 'N/A')}\n"
            contexto_para_chatgpt += f"  Link: {result.get('link', 'N/A')}\n"
            contexto_para_chatgpt += f"  Resumo: {result.get('snippet', 'N/A')}\n\n"
    if isinstance(resultado, dict) and 'answer_box' in resultado:
     # Às vezes a resposta direta vem em 'answer_box' ou similar
        contexto_para_chatgpt += f"Resposta Direta Encontrada:\n"
        contexto_para_chatgpt += f"  Título: {resultado['answer_box'].get('title', 'N/A')}\n"
        contexto_para_chatgpt += f"  Link: {resultado['answer_box'].get('link', 'N/A')}\n"
        contexto_para_chatgpt += f"  Resposta: {resultado['answer_box'].get('snippet', resultado['answer_box'].get('answer', 'N/A'))}\n\n"

    return result 


tools =[
    Tool(
        name="Pesquisa de Preços",
        func=search_results,
        description="busca o preço de vários produtos em diferentes sites e retorna os valores.",
        k=5
    )
]

client = OpenAI(api_key=os.getenv("openaiKey"))

def response_image(image_path_origin):

    def enconde():
        with open(image_path_origin,"rb") as file_final:
            return base64.b64encode(file_final.read()).decode("utf-8")


    base64_encode = enconde()

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{
            "role":"user",
            "content":[
                {"type":"text","text":"o que tem na imagem,pega o que mais se destaca na imagem e tente detalhar.se souber o nome do produto pode retornar."},
                {"type":"image_url",
                "image_url":{
                    "url":f"data:image/jpeg;base64,{base64_encode}"
                }}
            ]
        }]
    )

    result = response.choices[0].message.content


    final_result = response_write(result)

    return final_result


def response_write(response):
    prompt = """
    Você é um assistente de precisão. Padronize o termo abaixo para busca em lojas online.
    Inclua detalhes como modelo, cor, capacidade (se aplicável).

    Termo: {product_category}
    Exemplo: 
    - Se a entrada for "iPhone", retorne "iPhone 15 Pro Max 256GB".
    - Se for "Tênis Nike", retorne "Tênis Nike Air Max Preto".

    IMPORTANTE:
        se no detalhe sobre o produto ele descrever o design a cena pode descartar apenas procure pelo nome do produto ou apenas a descrição do produto.
        exemplo:
            nome do produto:iphone 15 pro max
            descrição do produto:mochila preta com design futurista

    """


    prompt = PromptTemplate.from_template(prompt)




    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        agent_kwargs={"prompt":prompt}
    )

    resposta = agent.invoke({"input":f"qual o menor preco para isso {response},me retorne o link do produto  e o preço."})
    
    return resposta["output"]





