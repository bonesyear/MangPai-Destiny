"""飞书自建应用 API 客户端（stdlib urllib，零新依赖）。

凭证从环境变量读：FEISHU_APP_ID / FEISHU_APP_SECRET（不硬编码）。
tenant_access_token 进程内缓存，到期前 60s 刷新。
测试可注入 http_post(url, payload, headers) -> dict 替换真实网络。
"""
from __future__ import annotations

import json
import os
import time
import urllib.request

BASE = 'https://open.feishu.cn/open-apis'


class FeishuError(RuntimeError):
    """飞书 API 调用失败（code != 0 或凭证缺失）。"""


class FeishuClient:
    def __init__(self, app_id=None, app_secret=None, timeout=10.0, http_post=None):
        self.app_id = (app_id or os.environ.get('FEISHU_APP_ID', '')).strip()
        self.app_secret = (app_secret or os.environ.get('FEISHU_APP_SECRET', '')).strip()
        if not self.app_id or not self.app_secret:
            raise FeishuError('FEISHU_APP_ID / FEISHU_APP_SECRET 未配置（读环境变量，勿硬编码）')
        self.timeout = timeout
        self._http_post = http_post or self._urllib_post
        self._token = None
        self._token_expire = 0.0

    def _urllib_post(self, url, payload, headers=None):
        req = urllib.request.Request(
            url, data=json.dumps(payload).encode('utf-8'), method='POST',
            headers={'Content-Type': 'application/json; charset=utf-8', **(headers or {})})
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            return json.loads(resp.read().decode('utf-8'))

    def tenant_access_token(self):
        """取 tenant_access_token，进程内缓存（飞书 expire 通常 7200s）。"""
        if self._token and time.time() < self._token_expire - 60:
            return self._token
        data = self._http_post(f'{BASE}/auth/v3/tenant_access_token/internal',
                               {'app_id': self.app_id, 'app_secret': self.app_secret})
        if data.get('code') != 0:
            raise FeishuError(f"获取 tenant_access_token 失败: code={data.get('code')} {data.get('msg')}")
        self._token = data['tenant_access_token']
        self._token_expire = time.time() + int(data.get('expire', 7200))
        return self._token

    def _api(self, path, payload):
        data = self._http_post(f'{BASE}{path}', payload,
                               {'Authorization': f'Bearer {self.tenant_access_token()}'})
        if data.get('code') != 0:
            raise FeishuError(f"飞书 API {path} 失败: code={data.get('code')} {data.get('msg')}")
        return data

    @staticmethod
    def build_content(msg_type, text):
        """msg_type: text / post / interactive（markdown 卡片，lark_md 渲染）。"""
        if msg_type == 'text':
            body = {'text': text}
        elif msg_type == 'post':
            body = {'zh_cn': {'title': '', 'content': [[{'tag': 'text', 'text': text}]]}}
        elif msg_type == 'interactive':
            body = {'config': {'wide_screen_mode': True},
                    'elements': [{'tag': 'div', 'text': {'tag': 'lark_md', 'content': text}}]}
        else:
            raise ValueError(f'不支持的消息类型: {msg_type!r}')
        return json.dumps(body, ensure_ascii=False)

    def send(self, receive_id, msg_type, text, receive_id_type='chat_id'):
        """主动发消息（text/post/interactive-markdown）。"""
        return self._api(f'/im/v1/messages?receive_id_type={receive_id_type}', {
            'receive_id': receive_id, 'msg_type': msg_type,
            'content': self.build_content(msg_type, text)})

    def reply(self, message_id, msg_type, text):
        """回复原消息（引用回复）。"""
        return self._api(f'/im/v1/messages/{message_id}/reply', {
            'msg_type': msg_type, 'content': self.build_content(msg_type, text)})
