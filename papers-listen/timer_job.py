import requests
import time
from paper import RedisStorage, Paper
# import xml.etree.ElementTree as ET
# import feedparser
import arxiv
import multiprocessing
import requests
import xml.etree.ElementTree as ET
import markdown
import requests
import xml.etree.ElementTree as ET
import markdown
import pdb
import re
from xunfei_tts import create_tts_task, query_and_download, TaskRecord

def check_update(domain):
    # 创建 arXiv 客户端
    client = arxiv.Client()

    # 构造搜索对象，搜索 cs.CL 领域的论文
    search = arxiv.Search(
        query=domain,
        max_results = 10,
        sort_by=arxiv.SortCriterion.LastUpdatedDate,
        sort_order=arxiv.SortOrder.Descending
    )

    rs = RedisStorage()

    results = client.results(search)
    for result in results:
        entry_id = result.entry_id
        pos = entry_id.rfind('/')
        if pos == -1:
            raise Exception('cannot parse {}'.format(result))
            continue

        arxiv_id = entry_id[pos+1:]
        paper = rs.get_paper(arxiv_id)
        if paper is None:
            paper = Paper(
                arxiv_id=arxiv_id,
                title=result.title,
                brief="",
                status="init",
                mp3_url="",
                note=""
            )
            print(paper)
            rs.save_paper(paper)


def check_arxiv_update_per_day():
    domains = ['cs.CL']

    while True:
        for domain in domains:
            check_update(domain)
        time.sleep(3600 * 24)

def convert_papers_cool_to_html(url):
    # 获取内容
    # 1. 移除 xml 壳
    # 2. 移除 markdown 壳
    response = requests.get(url)
    response.raise_for_status()  # 确保请求成功
    html_content = response.text

    pattern_q = r"<p class=\"faq-q\"><strong>Q</strong>: (.*?)<\/p>"
    pattern_a = r"<p class=\"faq-a\"><strong>A</strong>: (.*?)<\/p>"


    # 打印匹配项
    qs = []
    _as = []
    for match in re.findall(pattern_q, html_content, re.DOTALL):
        qs.append(match)

    for match in re.findall(pattern_a, html_content, re.DOTALL):
        _as.append(match)
    
    pairs = []
    size = max(1, min(len(qs), len(_as)))

    text = ''
    for i in range(size - 1):
        text += qs[i]
        text += '\n'
        text += _as[i]
        text += '\n'
        # pairs.append(qs[i], _as[i])
    text = text.strip()
    return text

def gen_mp3(paper, record):
    arxiv_id = paper.arxiv_id
    txt_path = '{}/{}.txt'.format(paper.dir, paper.arxiv_id)
    mp3_path = '{}/{}.mp3'.format(paper.dir, paper.arxiv_id)

    if not os.path.exists(txt_path):
        with open(txt_path, 'w') as f:
            f.write(paper.title)
            f.write('\n')
            f.write(paper.brief)

    if not os.path.exists(mp3_path):
        print(f'{mp3_path} not found')
        if not record.get(arxiv_id):
            # 拿任务 ID
            task_id = create_tts_task(txt_path)
            if task_id is None:
                return Exception('{} create_fail'.format(arxiv_id))

            record.add(arxiv_id, task_id)
            query_and_download(task_id, mp3_path)
        else:
            # 第二次过来，尝试问结果
            task_id, create_time = record.get(arxiv_id)
            if time.time() - create_time > 3600:
                # 过时任务，返回失败
                print(f'{arxiv_id} timeout')
            else:
                query_and_download(task_id, mp3_path)

    if os.path.exists(mp3_path):
        return None
    return Exception('continue')

def check_work():

    record = TaskRecord()
    while True:
        rs = RedisStorage()
        while True:
            arxiv_id = rs.fetch_task()
            if arxiv_id is None:
                break

            paper.brief = paper.title + brief
            if paper.status == 'tts':
                # 检查下载情况
                code = gen_mp3(paper, record)
                if code is not None:
                    if 'continue' in str(code):
                        # 加回去等待
                        rs.add_task(arxiv_id)
                else:
                    # 成功
                    paper.mp3_url = 'http://101.133.161.204:23333/{}/{}.mp3'.format(paper.dir, arxiv_id) 
                    rs.save_paper(paper)
                continue
            
            # hook papers.cool
            index = arxiv_id.rfind('v')
            clean_id = arxiv_id[0:index]

            rs.update_paper_status(arxiv_id, 'processing')

            try:
                papers_cool_url = "https://papers.cool/arxiv/kimi?paper={}".format(clean_id)
                brief = convert_papers_cool_to_html(papers_cool_url)

                if len(brief) < 1:
                    # hook 一下苏神吧 qaq
                    progresss_url = "https://papers.cool/arxiv/progress?paper={}".format(clean_id)
                    import pdb
                    pdb.set_trace()
                    _ = requests.get(progresss_url)
                    rs.add_task(arxiv_id)
                    continue

            except Exception as e:
                print(str(e) + " " + papers_cool_url)

            paper.brief = paper.title + brief
            paper.status = 'tts'
            # 已获取文本,开始 tts
            rs.save_paper(paper)

            code = gen_mp3(paper, record)
            if code is not None:
                if 'continue' in str(code):
                    # 加回去等待
                    rs.add_task(arxiv_id)
            else:
                # 成功
                paper.mp3_url = 'http://101.133.161.204:23333/{}/{}.mp3'.format(paper.dir, arxiv_id) 
                rs.save_paper(paper)

        time.sleep(120)

if __name__ == "__main__":
    arxiv_check = multiprocessing.Process(target=check_arxiv_update_per_day)
    arxiv_check.start()

    check_work()

    arxiv_check.join()