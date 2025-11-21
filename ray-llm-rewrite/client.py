import ray
from typing import Dict, List
import json
import os
from openai import OpenAI
from loguru import logger
from prompt import rewrite_option, sim_option, PromptOption

class OpenAIClient:
    def __init__(self, base_url: str = "http://localhost:8000/v1", api_key: str = "fake-key", retry:int = 8):
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.retry = retry
    
    def call(self, prompt: str, option: PromptOption, model: str = 'ray') -> str:
        for attempt in range(self.retry):
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    timeout=600,
                    messages=[
                        {"role": "user", "content": str(prompt)},
                    ],
                    stream=False
                )
                response_content = response.choices[0].message.content
                offset = response_content.find('</think>')
                if offset >= 0:
                    response_content = response_content[offset + len('</think>'):]
                
                return option.parser(response_content)
            except Exception as e:
                logger.error(f"Error calling OpenAI API: {e}")
                if 'Invalid' in str(e):
                    logger.info(prompt)
                    # with open('test.json', 'w') as f:
                    #     json_str =  json.dumps({"role": "user", "content": prompt}, ensure_ascii=False, indent=2)
                    #     f.write(json_str)
                if attempt < self.retry - 1:
                    continue
        return option.default


def do_transform(row: Dict[str, str]) -> Dict[str, str]:
    client = OpenAIClient()

    messages = row['messages']
    source = row['source']

    # if 'math' in source or 'coding' in source:
    if 'math' in source or 'coding' in source:
        row['r_question'] = ''
        row['r_answer'] = ''
        row['sim_question'] = 0
        row['sim_answer'] = 0
        return row
    
    question = messages[0]['content']
    answer = messages[1]['content']

    prompt = rewrite_option.template.format(question=question, answer=answer)
    rewrite_question, rewrite_answer = client.call(prompt, rewrite_option)
    row['r_question'] = rewrite_question
    row['r_answer'] = rewrite_answer

    if not rewrite_question or not rewrite_answer:
        row['sim_question'] = 0
        row['sim_answer'] = 0
    else:
        prompt = sim_option.template.format(content1=rewrite_question, content2=question)
        row['sim_question'] = client.call(prompt, sim_option)
        prompt = sim_option.template.format(content1=rewrite_answer, content2=answer)
        row['sim_answer'] = client.call(prompt, sim_option)
    
    with open('train1.jsonl', 'a', encoding='utf-8') as f:
        json_str = json.dumps(row, ensure_ascii=False)
        f.write(json_str + "\n")
    return row

def work(input_paths:List[str], output_path: str):
    if os.path.exists(output_path):
        logger.info(f"Output file {output_path} already exists, skipping processing.")
        return
    ds = ray.data.read_json(input_paths)
    # ds = ds.limit(1)
    # ds.show(limit=1)

    # Apply the transformation to our dataset
    transformed_ds = ds.map(
        do_transform,
        concurrency=256,  # 并行度
    )
    transformed_ds.take_all()

if __name__ == "__main__":
    # ray.init(address="auto")
    work(input_paths=["/data/khj/workspace/train-data/seedllm_train_openai_format.jsonl", "/data/khj/workspace/train-data/seedllm_val_openai_format.jsonl"], output_path="train1.jsonl")
