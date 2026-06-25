# Personal Knowledge Agent

一个基于 LangGraph、Qwen 和向量检索的个人知识库 Agent。

它会根据用户问题调用知识库检索工具，将检索到的资料交给大模型，再生成基于资料的回答。

## 核心能力

- 读取 `knowledge.txt` 并按段落切分知识片段
- 调用 Embedding API 将文本转换为向量
- 使用余弦相似度进行语义检索
- 使用相似度阈值过滤无关资料
- 使用知识库哈希自动判断向量索引是否过期
- 使用 LangGraph 管理模型调用和工具调用流程
- 显示检索来源 chunk 编号
- 保存 Agent 运行历史

## Agent 流程

```text
用户问题
→ HumanMessage
→ Qwen 决定调用 search_knowledge
→ Embedding 向量检索
→ ToolMessage 返回检索资料
→ Qwen 基于资料生成最终回答
→ 输出回答、来源和运行记录
```

## 项目结构

```text
personal_knowledge_agent/
├── main.py                # 命令行入口与结果展示
├── api.py                 # FastAPI 接口
├── agent_service.py        # Agent 服务层
├── agent_graph.py          # LangGraph 工作流
├── agent_model.py          # 模型调用与消息格式转换
├── agent_tools.py          # search_knowledge 工具
├── agent_state.py          # Agent 状态定义
├── vector_index.py         # 向量索引、缓存与检索
├── embedding_client.py     # Embedding API 调用
├── qwen_client.py          # Qwen API 调用
├── rag_files.py            # 知识库读取与文本切分
├── agent_history.py        # Agent 历史记录保存
├── knowledge.txt           # 本地知识库
├── requirements.txt        # Python 依赖
└── .env.example            # 环境变量示例
```

## 环境要求

- Python 3.12 或更高版本
- DashScope API Key
- 可访问 DashScope Embedding 和 Qwen 接口的网络环境

## 安装依赖

在项目目录中创建并启用虚拟环境：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## 配置环境变量

项目使用 `settings.py` 集中读取环境变量。本地开发时可以只设置必需项，其他配置会使用默认值。

仅在当前 PowerShell 窗口中设置 API Key：

```powershell
$env:DASHSCOPE_API_KEY="你的_API_Key"
```

如果需要调整运行数据目录、模型、超时时间或检索参数，可以参考 `.env.example`：

```env
DATA_DIR=/data
DASHSCOPE_API_KEY=your_api_key_here

CHAT_API_URL=https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions
CHAT_MODEL_NAME=qwen-plus
CHAT_REQUEST_TIMEOUT=60

EMBEDDING_API_URL=https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings
EMBEDDING_MODEL_NAME=text-embedding-v4
EMBEDDING_REQUEST_TIMEOUT=60

VECTOR_SEARCH_TOP_K=3
MIN_SIMILARITY_SCORE=0.3

MAX_RETRIES=3
RETRY_SLEEP_SECONDS=2
```

配置说明：

| 环境变量 | 作用 |
| --- | --- |
| `DATA_DIR` | 运行数据目录。Docker 中建议设为 `/data`，本地不设置时默认使用项目目录。 |
| `DASHSCOPE_API_KEY` | DashScope API Key，必须由运行环境提供，不要写入代码。 |
| `CHAT_API_URL` | Qwen 对话接口地址。 |
| `CHAT_MODEL_NAME` | Qwen 对话模型名称。 |
| `CHAT_REQUEST_TIMEOUT` | Qwen 请求超时时间，单位为秒。 |
| `EMBEDDING_API_URL` | Embedding 接口地址。 |
| `EMBEDDING_MODEL_NAME` | Embedding 模型名称。 |
| `EMBEDDING_REQUEST_TIMEOUT` | Embedding 请求超时时间，单位为秒。 |
| `VECTOR_SEARCH_TOP_K` | 向量检索最多返回的 chunk 数量。 |
| `MIN_SIMILARITY_SCORE` | 最低相似度阈值，低于该值的 chunk 不进入模型上下文。 |
| `MAX_RETRIES` | 外部 API 请求失败后的最大重试次数。 |
| `RETRY_SLEEP_SECONDS` | 每次重试前等待的秒数。 |

## 更新知识库

修改 `knowledge.txt` 后，下一次检索会比较知识库哈希值：

- 哈希值一致：直接加载 `vector_index.json`
- 哈希值不同：自动重新生成向量索引
- 索引文件缺失或格式不符合要求：重新构建索引

## API 使用

启动 FastAPI 服务：

```powershell
.\.venv\Scripts\python.exe -m uvicorn api:app --reload
```

启动后可访问接口文档：

```text
http://127.0.0.1:8000/docs
```

### 健康检查

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health"
```

预期响应：

```json
{
  "status": "ok"
}
```

### 提问

```python
import requests

response = requests.post(
    "http://127.0.0.1:8000/chat",
    json={"question": "什么是 RAG？"},
    timeout=120
)

print(response.status_code)
print(response.json())
```

成功响应格式：

```json
{
  "answer": "RAG 是检索增强生成……",
  "sources": [2],
  "step_count": 2
}
```

### 常见状态码

- `200`：请求成功，返回 Agent 回答。
- `422`：请求参数不合法，例如 `question` 为空或超过 500 个字符。
- `503`：Qwen 或 Embedding 等外部服务暂时不可用，可稍后重试。
- `500`：未预期的服务端错误，需要查看服务日志排查。

## Docker 运行

### 构建镜像

在 `personal_knowledge_agent` 目录中执行：

```powershell
docker build -t personal-knowledge-agent:latest .
```

### 设置 API Key

仅在当前 PowerShell 窗口中设置：

```powershell
$env:DASHSCOPE_API_KEY="你的_API_Key"
```

### 启动容器

```powershell
docker run `
  --name personal-knowledge-agent-api `
  -p 8000:8000 `
  -e DATA_DIR=/data `
  -e DASHSCOPE_API_KEY=$env:DASHSCOPE_API_KEY `
  -v agent-data:/data `
  personal-knowledge-agent:latest
```

参数说明：

- `-p 8000:8000`：将容器内的 `8000` 端口映射到宿主机本地 `8000` 端口。
- `-e DATA_DIR=/data`：让运行数据写入容器内 `/data` 目录。
- `-e DASHSCOPE_API_KEY=$env:DASHSCOPE_API_KEY`：将宿主机 PowerShell 中的 API Key 传入容器。
- `-v agent-data:/data`：将 Docker 命名卷 `agent-data` 挂载到容器内 `/data`，用于保存运行数据。

### 检查服务

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health"
```

预期响应：

```json
{
  "status": "ok"
}
```

### 调用问答接口

建议使用 Python `requests` 验证响应，避免 PowerShell 中文显示乱码影响判断：

```powershell
..\.venv\Scripts\python.exe -c "import requests; r=requests.post('http://127.0.0.1:8000/chat', json={'question':'什么是 RAG？'}, timeout=120); print('状态码：', r.status_code); print(r.content.decode('utf-8'))"
```

预期响应示例：

```json
{
  "answer": "RAG 是检索增强生成，它会先查找资料，再让大模型基于资料回答。",
  "sources": [2],
  "step_count": 2
}
```

### 数据持久化

容器内目录分工：

```text
/app  ：项目代码和 knowledge.txt
/data ：运行数据
```

`knowledge.txt` 属于镜像内的固定知识库文件。向量索引和历史记录属于运行数据，会写入 `DATA_DIR` 指向的目录。

当前 Docker 命令中：

```text
DATA_DIR=/data
agent-data:/data
```

表示以下文件会保存在 Docker 命名卷 `agent-data` 中：

```text
vector_index.json
agent_history.json
rag_history.json
```

只删除容器不会删除 `agent-data` 卷；只要继续挂载同一个卷，运行数据可以继续复用。

## 关键设计

### 向量检索

知识库文本会按段落切分为多个 chunk。每个 chunk 和用户问题都会通过 Embedding API 转换为向量，再通过余弦相似度计算相关程度。

检索结果按分数从高到低排序，只保留满足最低相似度阈值的结果，避免无关资料进入模型上下文。

### 向量索引缓存

向量索引保存在 `vector_index.json` 中，避免每次提问都重新请求 Embedding API。

索引文件同时保存知识库内容的 MD5 哈希值：

- 哈希值一致：直接加载已有索引
- 哈希值不同：知识库已变化，重新构建索引
- 索引文件缺失或格式不符合要求：重新构建索引

### 运行数据目录

项目通过 `DATA_DIR` 区分固定知识库和运行数据：

- `knowledge.txt`：固定知识库文件，随镜像一起打包，仍从项目代码目录读取。
- `vector_index.json`：向量索引缓存，属于运行数据。
- `agent_history.json`：Agent 运行历史，属于运行数据。
- `rag_history.json`：RAG 历史记录，属于运行数据。

本地开发时如果未设置 `DATA_DIR`，运行数据默认保存在项目目录中。Docker 运行时建议设置 `DATA_DIR=/data`，并挂载 Docker 命名卷保存运行数据。

### Agent 工具调用

`search_knowledge` 是 Agent 可调用的工具。它负责加载知识库、获取向量索引、执行向量检索，并将相关资料作为 `ToolMessage` 返回给模型。

Agent 使用 LangGraph 管理执行流程：

```text
HumanMessage
  -> AIMessage（请求调用 search_knowledge）
  -> ToolMessage（工具返回检索资料）
  -> AIMessage（基于资料生成最终回答）
```

### 来源展示

程序从 `ToolMessage` 中提取 `[chunk 编号]`，在最终回答后显示参考来源。来源表示检索阶段提供给模型的知识片段，不代表逐句引用。

## 运行项目

```powershell
python main.py
```

## 已知限制

- 知识库目前使用本地 `knowledge.txt`，适合较小规模的文本资料。
- 向量索引保存为 JSON 文件，不适合大规模数据。
- 模型和 Embedding 调用依赖网络及 DashScope API。
- 相似度阈值和 Top-K 数量需要随知识库内容逐步调整。
- 当前 Agent 只提供知识库检索工具。
