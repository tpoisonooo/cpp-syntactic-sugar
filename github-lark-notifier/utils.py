import json

def load(filename, key) -> str:
    with open(filename) as f:
        config = json.load(f)
        if key in config:
            return config [key]
    return None


def lark_webhook():
    return load('config.json', 'lark_webhook')

def issue_comment():
    return load('config.json', 'issue_comment')

def github_token():
    return load('config.json', 'github_token')

if __name__ == "__main__":
    print(lark_webhook())
    print(issue_comment())
    print(github_token())
