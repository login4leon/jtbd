from openai import OpenAI

from app01 import models

class LLMUtil():
    def __init__(self, agent):
        row_object = models.Agents.objects.filter(id=agent).first()
        if not row_object:
            raise Exception('agent not found')
        self.system_prompt = row_object.system_prompt
        self.user_prompt = row_object.user_prompt
        self.name = row_object.description

    def chat(self):
        # 生成完整提示词
        if self.system_prompt:
            self.messages = [{'role': 'system', 'content': '%s' % self.system_prompt}]
            self.messages.append({'role': 'user', 'content': '%s' % self.user_prompt})
        else:
            self.messages = [{'role': 'user', 'content': '%s' % self.user_prompt}]
        # 与LLM沟通
        client = OpenAI(api_key="sk-d0727e25ef7f4d6f9a480a3070107fff", base_url="https://api.deepseek.com")
        response = client.chat.completions.create(
            model="deepseek-reasoner",
            messages=self.messages,
            temperature=1.5,
            stream=False
        )
        output = {}
        output['content'] = response.choices[0].message.content
        output['reasoning_content'] = response.choices[0].message.reasoning_content
        return output
