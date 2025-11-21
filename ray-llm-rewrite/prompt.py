import ray
from typing import Dict, List, Tuple, Any
from loguru import logger
import json

class PromptOption:
    def __init__(self, template:str, parser:callable, default: Any):
        self.template = template
        self.parser = parser
        self.default = default

def rewrite_parser(response_content: str) -> Tuple[str, str]:
    response_content = response_content.strip()
    if response_content.startswith('```json'):
        response_content = response_content[7:].strip()
    if response_content.endswith('```'):
        response_content = response_content[:-3].strip()

    jsonobj = None
    try:
        jsonobj = json.loads(response_content)
    except Exception:
        raise ValueError(f"Invalid JSON {response_content}")
    
    if not isinstance(jsonobj, dict):
        raise Exception(f"JSON not dict {response_content}")
    
    if 'question' not in jsonobj or 'answer' not in jsonobj:
        raise Exception(f"Key not exists {response_content}")
        
    return jsonobj['question'].strip(), jsonobj['answer'].strip()

template_rewrite = """You are a helpful text expert. Give a question and answer, please rewrite the answer in a more concise way, and make sure the answer is correct.

## question

```text
{question}
```

## answer
```text
{answer}
```

## 输出要求
- 重写后的 question 和 answer 用 json 表达
- question 的 json key 为 "question"
- answer 的 json key 为 "answer"

## 输出实例
以下是输出示例

```json
{{
  "question": "who are you?",
  "answer": "I am a helpful assistant"
}}
```

## 注意事项
- 你的任务是重新表述问题和答案，你不会缺失任何信息
- 重写后的 question 和原始 question 意义相同，但文字不同（可以只是调整问法）
- 你不会缺少原始 question 和 answer 中的任何信息
- 你可以把 question 和 answer 重写成更详细、更有结构的形式
- 你可以把 question 和 answer 重写成英文或中文
- 你会直接输出重写后的 json，不需要任何其他内容
"""

rewrite_option = PromptOption(
    template=template_rewrite,
    parser=rewrite_parser,
    default=('', '')
)

template_sim = """You are a helpful text expert. 给定两段描述，请判断它们是否相似，并给出一个 0~100 的得分。

## 描述1

```text
{content1}
```

## 描述2

```text
{content2}
```

## 输出要求
- 输出一个整数，表示描述1和描述2的相似度得分，范围 0~100
- 最终直接给分数即可

## 注意事项
- 只需要对比内容含义是否相似，你不关注语法和拼写错误
- 你不会关注中英文的语言差异
- 你会直接给出分数
"""

def sim_checker(response_content: str) -> bool:
    response_content = response_content.strip()
    return response_content.isdigit() and 0 <= int(response_content) <= 100

def sim_parser(response_content: str) -> int:
    response_content = response_content.strip()
    if not response_content.isdigit() and 0 <= int(response_content) <= 100:
        raise ValueError(f"Invalid response content: {response_content}")
    return int(response_content.strip())

sim_option = PromptOption(
    template=template_sim,
    parser=sim_parser,
    default=0
)
