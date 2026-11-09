# SEOGEOAuditor API

`app.py` 提供轻量级 SEO / GEO 审计基础类 `SEOGEOAuditor`。抓取过程是本地模拟，不会发起网络请求。评分只使用文本启发式规则，不会调用外部搜索引擎。

## SEOGEOAuditor

```python
from app import SEOGEOAuditor

auditor = SEOGEOAuditor()
```

无构造参数。

### analyze_url(url: str) -> dict

模拟抓取页面，并分析 title、meta、H1/H2 与关键词密度。

参数：

- `url`：绝对地址，协议必须是 `http` 或 `https`，且必须包含主机名。

返回字段：

| 字段 | 说明 |
| --- | --- |
| `url` | 去除首尾空白后的地址 |
| `source` | 固定为 `simulated` |
| `title` | 页面标题 |
| `meta.description` | description meta |
| `meta.keywords` | keywords meta |
| `meta.robots` | robots meta |
| `headings.h1` | H1 文本列表 |
| `headings.h2` | H2 文本列表 |
| `word_count` | 可见文本的词数 |
| `keyword_density` | 最多 8 个关键词，每项含 `keyword`、`count`、`density` |

`density` 是该词次数除以可见文本总词数，保留 4 位小数。停用词不进入排名。

异常：

- `TypeError`：`url` 不是字符串。
- `ValueError`：空字符串、缺少协议、非 http(s)、缺少主机，或地址中含空白/控制字符。

示例：

```python
report = auditor.analyze_url("https://example.com/seo-geo-audit")
report["headings"]["h1"]  # ["Seo Geo Audit"]
```

### evaluate_geo_score(content: str) -> dict

评估一段文本在 Perplexity、SearchGPT 等 AI 搜索引擎中的基础可引用度。

参数：

- `content`：待评估的纯文本。空白内容合法，分数为 0。

返回字段：

| 字段 | 说明 |
| --- | --- |
| `score` | 0 到 100 的整数 |
| `citability` | `low`（0–39）、`medium`（40–69）、`high`（70–100） |
| `signals.substance` | 篇幅是否适合被引用，0–25 |
| `signals.structure` | 段落、列表和句子长度，0–25 |
| `signals.specificity` | 数字、年份、比例和例证，0–25 |
| `signals.answer_readiness` | 是否先给出定义、原因和直接回答，0–25 |
| `notes` | 可改进项；没有问题时为空列表 |

四项信号之和等于 `score`。

异常：

- `TypeError`：`content` 不是字符串。

示例：

```python
result = auditor.evaluate_geo_score(
    "What is GEO?\n\nGEO is writing that answer engines can cite because it states a definition and a 2024 statistic."
)
result["citability"]
```
