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
├── agent_graph.py         # LangGraph 工作流
├── agent_model.py         # 模型调用与消息格式转换
├── agent_tools.py         # search_knowledge 工具
├── agent_state.py         # Agent 状态定义
├── vector_index.py        # 向量索引、缓存与检索
├── embedding_client.py    # Embedding API 调用
├── qwen_client.py         # Qwen API 调用
├── rag_files.py           # 知识库读取与文本切分
├── agent_history.py       # Agent 历史记录保存
├── knowledge.txt          # 本地知识库
├── requirements.txt       # Python 依赖
└── .env.example           # 环境变量示例
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

## 配置 API Key

仅在当前 PowerShell 窗口中设置：

```powershell
$env:DASHSCOPE_API_KEY="你的_API_Key"
```

## 更新知识库

修改 `knowledge.txt` 后，下一次检索会比较知识库哈希值：

- 哈希值一致：直接加载 `vector_index.json`
- 哈希值不同：自动重新生成向量索引
- 索引文件缺失或格式不符合要求：重新构建索引

## 关键设计

### 向量检索

知识库文本会按段落切分为多个 chunk。每个 chunk 和用户问题都会通过 Embedding API 转换为向量，再通过余弦相似度计算相关程度。

检索结果按分数从高到低排序，只保留满足最低相似度阈值的结果，避免无关资料进入模型上下文。

### Agent 工具调用

`search_knowledge` 是 Agent 可调用的工具。它负责加载知识库、获取向量索引、执行向量检索，并将相关资料作为 `ToolMessage` 返回给模型。

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
