#导入langchain的tool
from langchain.agents import tool
from pydantic import BaseModel, Field
import base64
import cv2 as cv
import requests
 

# # Define the input schema
# class OpenMeteoInput(BaseModel):
#     latitude: cv.typing.MatLike = Field(..., description="Image that you captured")

#添加tool装饰器
# @tool(args_schema=OpenMeteoInput)
@tool()
def Eyes() -> str:
    """Capture an image from the your eyes and describe the visual context in the image. Only use this tool when it is explicitly required. For example, when the user asks about the things in front of you."""

    cap = cv.VideoCapture(0)

    # 跳过前10帧
    for i in range(10):
        ret, frame = cap.read()

    prompt = """
This is the scene in front of the user's eyes. Please describe the content in the picture so that we can communicate better. 
Please make sure the description is brief and to the point."""

    max_tokens = 3000

    if not ret:
        return "Failed to capture image"
    
    # 将图片缩小一半
    frame = cv.resize(frame, (frame.shape[1]//2, frame.shape[0]//2))
    # 将图片转换为jpeg格式
    frame = cv.imencode('.jpg', frame)[1].tobytes()

    base64_image = base64.b64encode(frame).decode('utf-8')

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Authorization"
    }
    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": max_tokens
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    res = response.json()

    cap.release()

    return res['choices'][0]['message']["content"]

 
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

#创建函数描述变量
functions = [
    convert_to_openai_function(f) for f in [
        Eyes
    ]
]

import env
#设置环境变量
env.openai_api_key()

def get_vision(text):
    #定义llm
    model = ChatOpenAI(temperature=0).bind(functions=functions)
    
    #创建prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are helpful but sassy assistant"),
        ("user", "{input}"),
    ])
    

    from langchain.agents.output_parsers import ToolsAgentOutputParser
    #定义chain
    chain = prompt | model
    #调用chain
    tool_use = chain.invoke({"input": text}).additional_kwargs
    print(tool_use)
    if tool_use == {}:
        return ''
    else:
        if tool_use['function_call']['name'] == 'Eyes':
            return Eyes.run({})
    return ''

if __name__ == "__main__":
    
    print(get_vision("what can you see in front of you?"))
    print(get_vision("hello"))