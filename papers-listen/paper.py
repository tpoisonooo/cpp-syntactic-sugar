import redis
import json
import pdb
from datetime import datetime
import os

def ymd():
    now = datetime.now()
    # 格式化时间为年月日字符串
    date_string = now.strftime("%Y-%m-%d")
    if not os.path.exists(date_string):
        os.makedirs(date_string)
    return date_string

class Paper:
    def __init__(self, arxiv_id, title, brief, status, mp3_url, note):
        self.arxiv_id = arxiv_id
        self.title = title
        self.brief = brief
        self.status = status
        self.mp3_url = mp3_url
        self.note = note
        self.dir = ymd()

    def to_dict(self):
        return {
            "arxiv_id": self.arxiv_id,
            "title": self.title,
            "brief": self.brief,
            "status": self.status,
            "mp3_url": self.mp3_url,
            "note": self.note
        }

    @staticmethod
    def from_dict(data):
        return Paper(
            arxiv_id=data["arxiv_id"],
            title=data["title"],
            brief=data["brief"],
            status=data["status"],
            mp3_url=data["mp3_url"],
            note=data["note"]
        )

class RedisStorage:
    def __init__(self, host='101.133.161.204', port=6380, password='hxd123'):
        self.redis = redis.Redis(host=host, port=port, password=password, decode_responses=True)

    def save_paper(self, paper):
        data = paper.to_dict()
        self.redis.hset(paper.arxiv_id, mapping=data)

    def get_paper(self, arxiv_id):
        data = self.redis.hgetall(arxiv_id)
        if data:
            return Paper.from_dict(data)
        else:
            return None

    def get_top_n(self, n=50):
        all_keys = self.redis.keys('*')
        keys = all_keys[:50]  # 返回最近 50 条论文的 ID
        
        papers = []
        for key in keys:
            p = self.get_paper(arxiv_id=key)
            papers.append(p)
        return papers

    def add_task(self, arxiv_id):
        self.redis.lpush('work', arxiv_id)

    def fetch_task(self):
        data = self.redis.rpop(queue_name)
        return data

    def update_paper_status(self, arxiv_id, new_status):
        paper = self.get_paper(arxiv_id)
        if paper:
            paper.status = new_status
            self.save_paper(paper)
            return True
        return False

    def delete_paper(self, arxiv_id):
        self.redis.delete(arxiv_id)

# 使用示例
if __name__ == "__main__":
    storage = RedisStorage()

    # 创建一个 Paper 对象
    paper = Paper(
        arxiv_id="arXiv123",
        title="Example Paper",
        brief="A brief description of the paper.",
        status="pending",
        mp3_url="http://example.com/mp3",
        note="Note about the paper."
    )

    # 存储 Paper 对象
    storage.save_paper(paper)

    # 获取 Paper 对象
    retrieved_paper = storage.get_paper("arXiv123")
    print(retrieved_paper.to_dict())

    # 更新 Paper 状态
    storage.update_paper_status("arXiv123", "completed")

    # 获取更新后的 Paper 对象
    updated_paper = storage.get_paper("arXiv123")
    print(updated_paper.to_dict())

    # 删除 Paper 对象
    # storage.delete_paper("arXiv123")