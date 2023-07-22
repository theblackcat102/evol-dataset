import os
from jinja2 import Environment, FileSystemLoader, select_autoescape


current_directory = os.path.dirname(os.path.abspath(__file__))
# Specify the templates directory

env = Environment(
    loader=FileSystemLoader(os.path.join(current_directory, 'instructions')),
    autoescape=select_autoescape(['txt'])
)

def load_template(template_name):
    return env.get_template(template_name)

def render_template(template, context):
    return template.render(context)


def elimination_response(response):
    if len(response) < 30:
        return True
    if 'sorry' in response.lower() or '抱歉' in response.lower():
        return True
    if response.lower()[:10] == 'modify the':
        return True

    copy_keywords = ['given prompt',  'new prompt',
                     'modified prompt', 'translated prompt',
                     'rewritten prompt', '##Given Prompt', 
                     'Created Prompt', '#Rewritten Prompt', 
                     'replace a commonly used requirement',
                     'if the original problem can be solved with only a',
                     'modify the given programming', 'updated prompt',
                     'propose higher time or space complexity',
                     'modify the programming test']
    for keyword in copy_keywords:
        if keyword.lower() in response.lower():
            return True
    return False

if __name__ == "__main__":
    temp = load_template('concretizing.txt')
    out = render_template(temp, {'prompt': 'Hi how are you'})
    print(out)