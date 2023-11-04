from pathlib import Path

docs = Path.cwd() / 'docs'
# print(docs)
# print(*docs.glob('*.*.md'))
print(*docs.glob('*.*.*.md'))


def format_doc(version):
    with open(f'docs/{version}.md', 'r', encoding='utf8') as f, open('docs/temple.md', 'r', encoding='utf8') as t:
        return t.read() + f'\n<h3>V{version}更新</h3>\n' + f.read() + '\n<h3>History</h3>' + '\n'.join(
            f'<div><a href="/doc/{i.name}">{i.stem}</a></div>' for i in docs.glob('*.*.*.md'))
