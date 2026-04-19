"""
Phase 277: AI 大模型引擎
支持多 LLM 提供商，用于智能问答、研报生成、行情解读
"""

import os
import json
import httpx
from typing import Dict, List, Optional
from datetime import datetime


class LLMProvider:
    """LLM 提供商抽象"""
    
    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
    
    async def chat(self, messages: List[Dict], temperature: float = 0.7, max_tokens: int = 2000) -> Dict:
        """发送对话请求"""
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}',
        }
        payload = {
            'model': self.model,
            'messages': messages,
            'temperature': temperature,
            'max_tokens': max_tokens,
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(f'{self.base_url}/chat/completions', json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return {
                'content': data['choices'][0]['message']['content'],
                'usage': data.get('usage', {}),
                'model': data.get('model', self.model),
            }


class LLMEngine:
    """
    AI 大模型引擎
    支持多提供商切换，负责研报生成、行情解读、智能问答
    """
    
    # 系统提示词模板
    PROMPT_STOCK_ANALYSIS = """你是专业的量化金融分析师。请基于以下数据对股票进行分析：
股票: {code}
名称: {name}
最新价: {price}
涨跌幅: {change}%
评分: {score}/100
请给出简短的投资建议（200字以内），包含风险提示。"""

    PROMPT_REPORT_GENERATE = """你是一位资深金融研究员。请根据以下信息生成一份简短的个股研报：
{context}
要求：格式清晰，包含基本面、技术面、风险提示，500字以内。"""

    PROMPT_MARKET_SUMMARY = """你是首席策略师。请根据以下市场数据生成今日市场总结：
{context}
要求：150字以内，涵盖大盘走势、板块热点、资金流向。"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.provider = self._create_provider()
        self.history: List[Dict] = []
    
    def _create_provider(self) -> Optional[LLMProvider]:
        """创建 LLM 提供商实例"""
        api_key = os.getenv('LLM_API_KEY', self.config.get('api_key', ''))
        base_url = os.getenv('LLM_BASE_URL', self.config.get('base_url', 'https://api.openai.com/v1'))
        model = os.getenv('LLM_MODEL', self.config.get('model', 'gpt-3.5-turbo'))
        
        if not api_key:
            return None
        return LLMProvider(api_key, base_url, model)
    
    def is_available(self) -> bool:
        """检查 AI 是否可用"""
        return self.provider is not None
    
    def get_config(self) -> Dict:
        """获取配置信息"""
        return {
            'available': self.is_available(),
            'model': self.provider.model if self.provider else 'none',
            'base_url': self.provider.base_url if self.provider else 'none',
        }
    
    async def analyze_stock(self, stock_data: Dict) -> Dict:
        """分析个股"""
        if not self.is_available():
            return {'error': 'AI 服务未配置，请设置 LLM_API_KEY'}
        
        prompt = self.PROMPT_STOCK_ANALYSIS.format(
            code=stock_data.get('code', ''),
            name=stock_data.get('name', ''),
            price=stock_data.get('price', 0),
            change=stock_data.get('change', 0),
            score=stock_data.get('score', 50),
        )
        
        messages = [
            {'role': 'system', 'content': '你是专业的量化金融分析师。'},
            {'role': 'user', 'content': prompt},
        ]
        
        result = await self.provider.chat(messages, temperature=0.5, max_tokens=500)
        self.history.append({'type': 'stock_analysis', 'code': stock_data.get('code'), 'result': result})
        return result
    
    async def generate_report(self, context: str) -> Dict:
        """生成研报"""
        if not self.is_available():
            return {'error': 'AI 服务未配置'}
        
        prompt = self.PROMPT_REPORT_GENERATE.format(context=context)
        messages = [
            {'role': 'system', 'content': '你是一位资深金融研究员。'},
            {'role': 'user', 'content': prompt},
        ]
        
        result = await self.provider.chat(messages, temperature=0.6, max_tokens=1000)
        self.history.append({'type': 'report', 'result': result})
        return result
    
    async def market_summary(self, context: str) -> Dict:
        """市场总结"""
        if not self.is_available():
            return {'error': 'AI 服务未配置'}
        
        prompt = self.PROMPT_MARKET_SUMMARY.format(context=context)
        messages = [
            {'role': 'system', 'content': '你是首席策略师。'},
            {'role': 'user', 'content': prompt},
        ]
        
        result = await self.provider.chat(messages, temperature=0.5, max_tokens=300)
        self.history.append({'type': 'market_summary', 'result': result})
        return result
    
    async def chat(self, question: str, history: Optional[List[Dict]] = None) -> Dict:
        """通用智能问答"""
        if not self.is_available():
            return {'error': 'AI 服务未配置'}
        
        messages = history or []
        messages.append({'role': 'user', 'content': question})
        
        result = await self.provider.chat(messages, temperature=0.7, max_tokens=1000)
        return result
    
    def get_history(self, limit: int = 50) -> List[Dict]:
        """获取调用历史"""
        return self.history[-limit:]
    
    def clear_history(self):
        """清空历史"""
        self.history.clear()


# 全局实例
_llm_engine = None

def get_llm_engine(config: Optional[Dict] = None) -> LLMEngine:
    """获取全局 LLM 引擎实例"""
    global _llm_engine
    if _llm_engine is None:
        _llm_engine = LLMEngine(config)
    return _llm_engine
