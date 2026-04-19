"""
Phase 303: AI 知识库 (RAG 增强)
向量化存储历史决策/研报/笔记，检索增强回答
"""

import os
import json
import hashlib
from typing import Dict, List, Optional
from datetime import datetime
from flask import Blueprint, request
from src.web.response_helpers import ok, error, bad_request

ai_knowledge_bp = Blueprint('ai_knowledge', __name__)

# 简单向量存储 (内存)
_knowledge_base = {
    'documents': [],
    'index': {},
}
_kb_lock = None  # lazy init


def _get_lock():
    global _kb_lock
    if _kb_lock is None:
        import threading
        _kb_lock = threading.Lock()
    return _kb_lock


def _simple_hash(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()[:8]


def _simple_embed(text: str) -> List[float]:
    """简单文本嵌入模拟 (生产环境应使用 embedding 模型)"""
    import random
    random.seed(hash(text) % (2**32))
    return [random.gauss(0, 1) for _ in range(64)]


def _cosine_sim(a: List[float], b: List[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0
    return dot / (norm_a * norm_b)


@ai_knowledge_bp.route('/api/ai/knowledge/add', methods=['POST'])
def api_knowledge_add():
    """添加知识文档"""
    data = request.get_json(silent=True) or {}
    title = data.get('title', '')
    content = data.get('content', '')
    category = data.get('category', 'general')  # stock/research/note/decision
    tags = data.get('tags', [])

    if not content:
        return bad_request(message='内容不能为空')

    doc_id = _simple_hash(title + content[:50])
    embedding = _simple_embed(content)

    doc = {
        'id': doc_id,
        'title': title,
        'content': content[:500],
        'full_content': content,
        'category': category,
        'tags': tags,
        'embedding': embedding,
        'created_at': datetime.now().isoformat(),
    }

    with _get_lock():
        _knowledge_base['documents'].append(doc)
        _knowledge_base['index'][doc_id] = doc

    return ok(data={'id': doc_id, 'title': title}, message='知识已添加')


@ai_knowledge_bp.route('/api/ai/knowledge/search', methods=['POST'])
def api_knowledge_search():
    """检索知识"""
    data = request.get_json(silent=True) or {}
    query = data.get('query', '')
    category = data.get('category')
    top_k = data.get('top_k', 5)

    if not query:
        return bad_request(message='查询词不能为空')

    query_embed = _simple_embed(query)
    results = []

    with _get_lock():
        for doc in _knowledge_base['documents']:
            if category and doc.get('category') != category:
                continue
            sim = _cosine_sim(query_embed, doc['embedding'])
            results.append({
                'id': doc['id'],
                'title': doc['title'],
                'content': doc['content'][:200],
                'category': doc['category'],
                'tags': doc['tags'],
                'score': round(sim, 3),
            })

    results.sort(key=lambda x: x['score'], reverse=True)
    return ok(data={'results': results[:top_k], 'total': len(results)})


@ai_knowledge_bp.route('/api/ai/knowledge/qa', methods=['POST'])
def api_knowledge_qa():
    """RAG 增强问答: 检索 + AI 回答"""
    data = request.get_json(silent=True) or {}
    question = data.get('question', '')

    if not question:
        return bad_request(message='问题不能为空')

    # 1. 检索相关知识
    search_data = {'query': question, 'top_k': 3}
    search_resp = api_knowledge_search()
    search_results = search_resp.get_json().get('data', {}).get('results', [])

    context = '\n\n'.join([f"【{r['title']}】{r['content']}" for r in search_results])

    # 2. AI 回答
    answer = '根据现有知识库，暂未找到相关信息。'
    if search_results:
        try:
            from src.ai.llm_engine import get_llm_engine
            import asyncio
            engine = get_llm_engine()
            if engine.is_available():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    prompt = f"""请根据以下参考资料回答问题。

参考资料:
{context}

问题: {question}

请基于参考资料回答，如果资料不足请说明。（200字以内）"""
                    messages = [
                        {'role': 'system', 'content': '你是基于知识库的智能助手。请仅基于提供的参考资料回答问题。'},
                        {'role': 'user', 'content': prompt},
                    ]
                    result = loop.run_until_complete(engine.provider.chat(messages, temperature=0.3, max_tokens=500))
                    answer = result.get('content', answer)
                finally:
                    loop.close()
        except:
            pass

    return ok(data={
        'answer': answer,
        'sources': search_results,
        'question': question,
    })


@ai_knowledge_bp.route('/api/ai/knowledge/list', methods=['GET'])
def api_knowledge_list():
    """列出所有知识文档"""
    category = request.args.get('category')
    with _get_lock():
        docs = _knowledge_base['documents']
        if category:
            docs = [d for d in docs if d.get('category') == category]
    return ok(data={
        'documents': [{'id': d['id'], 'title': d['title'], 'category': d['category'], 'tags': d['tags']} for d in docs],
        'total': len(docs),
    })


@ai_knowledge_bp.route('/api/ai/knowledge/stats', methods=['GET'])
def api_knowledge_stats():
    """知识库统计"""
    with _get_lock():
        docs = _knowledge_base['documents']
        categories = {}
        for d in docs:
            cat = d.get('category', 'other')
            categories[cat] = categories.get(cat, 0) + 1
    return ok(data={
        'total_documents': len(docs),
        'categories': categories,
    })
