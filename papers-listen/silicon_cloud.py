from openai import OpenAI

def call_silicon_cloud(arxiv_id):

    client = OpenAI(api_key="sk-", base_url="https://api.siliconflow.cn/v1")

    response = client.chat.completions.create(
        model='alibaba/Qwen1.5-110B-Chat',
        messages=[
            {'role': 'user', 'content': "抛砖引玉是什么意思呀"}
        ],
        stream=False
    )

    print(response.choices[0].message.content)
