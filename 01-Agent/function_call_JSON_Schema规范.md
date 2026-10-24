# Function Calling 的 JSON Schema 规范

> 适用对象：用 Chat Completions / Responses API 给模型挂工具的开发者。
>
> 覆盖内容：`tools[].function.parameters` 这一份 JSON Schema 的**写法、约束、strict 模式规则、常见错误与自检方法**。
>
> 一句话结论：**function calling 的 `parameters` 不是"随便一个 JSON"，而是一份以 `{"type":"object"}` 为根、每个对象都闭合（`additionalProperties:false`）、每个属性都写 `description` 的 JSON Schema。**

---

## 目录

1. [它在请求里的位置](#1-它在请求里的位置)
2. [外层包装：tool 对象字段表](#2-外层包装tool-对象字段表)
3. [parameters：真正的 JSON Schema](#3-parameters真正的-json-schema)
4. [strict 模式的硬规则](#4-strict-模式的硬规则)
5. [Python 类型 → Schema 映射](#5-python-类型--schema-映射)
6. [场景化示例](#6-场景化示例)
7. [常见错误清单](#7-常见错误清单)
8. [校验与调试](#8-校验与调试)
9. [tool_choice / parallel_tool_calls 的交互](#9-tool_choice--parallel_tool_calls-的交互)
10. [跨厂商对照](#10-跨厂商对照)
11. [提交前 Checklist](#11-提交前-checklist)
12. [参考资料](#12-参考资料)

---

## 1. 它在请求里的位置

```
POST /v1/chat/completions
{
  "model": "...",
  "messages": [...],
  "tools": [                      ← 工具列表
    {
      "type": "function",         ← 目前只有这一种
      "function": {               ← 注意：是对象，不是数组
        "name": "...",            ← 必填
        "description": "...",     ← 强烈建议
        "parameters": {           ← 必填：JSON Schema，根必须是 object
          "type": "object",
          "properties": {...},
          "required": [...],
          "additionalProperties": false
        },
        "strict": true            ← 可选：开启严格模式
      }
    }
  ],
  "tool_choice": "auto"
}
```

模型不会返回"函数调用"本身，而是返回一段**字符串形式的 JSON**：

```json
{
  "role": "assistant",
  "content": null,
  "tool_calls": [
    {
      "id": "call_abc123",
      "type": "function",
      "function": {
        "name": "getWeather",
        "arguments": "{\"city\":\"北京\"}"
      }
    }
  ]
}
```

约定：`arguments` 是 **JSON 字符串**（要 `json.loads`），`id` 必须原样回填到 `role:"tool"` 消息的 `tool_call_id`。每个 `tool_call` 对应**一条** tool 消息，少一条下一轮就会 400。

---

## 2. 外层包装：tool 对象字段表

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `type` | string | 是 | 固定 `"function"` |
| `function.name` | string | 是 | 函数名，`^[a-zA-Z0-9_-]{1,64}$`；**和代码里注册表的 key 完全一致** |
| `function.description` | string | 强烈建议 | 模型靠它决定"什么时候调"；写触发条件，不写实现细节 |
| `function.parameters` | object | 是 | JSON Schema，见第 3 节 |
| `function.strict` | bool | 否 | `true` 时服务端保证 `arguments` 通过该 schema 校验（规则见第 4 节） |

命名建议：

- 用 `snake_case` 或 `camelCase`，**全仓库统一**；中文、空格、点号都不行。
- 名字要动词开头（`get_weather` / `search_docs` / `create_order`），不要 `tool1`。
- 名字是路由键，改名等于破坏兼容，先想清楚再定。

`description` 的三段式写法（比"查询天气"有效得多）：

> 作用 + 触发条件 + 边界。
>
> 例：`查询指定城市当前天气。当用户询问某城市气温、是否下雨、要不要带伞时使用。只支持中国大陆城市，不要用于历史天气或未来预报。`

---

## 3. parameters：真正的 JSON Schema

### 3.1 根节点必须是 object

`parameters` 描述的是"一次调用的参数集合"，所以：

```json
{ "type": "object", "properties": {}, "additionalProperties": false }
```

- 根是 `array`、`string` 或 `anyOf` 都会报错（根不能用 `anyOf`）。
- 没有参数的工具也要写成空对象：`{"type":"object","properties":{},"additionalProperties":false}`。
- `parameters` 是 **JSON 对象**，不是字符串。把 schema 先 `json.dumps` 再塞进去 = 双重编码，必 400。

### 3.2 类型表

| `type` | 说明 | 对应 Python |
|---|---|---|
| `string` | 字符串 | `str` |
| `number` | 任意数值（含小数） | `float` |
| `integer` | 整数 | `int` |
| `boolean` | 布尔 | `bool` |
| `object` | 对象，需 `properties` | `dict` / `BaseModel` |
| `array` | 数组，需 `items` | `list` / `tuple` |
| `null` | 仅用于联合/可空 | `None` |

**没有 `str`、`int`、`float`、`bool`、`dict`、`list` 这些"Python 类型名"**——写 `"type": "str"` 是最常见的翻车点之一。

### 3.3 关键字速查

| 关键字 | 作用 | 备注 |
|---|---|---|
| `type` | 类型 | 必填（`$ref` 节点除外） |
| `properties` | 对象属性表 | 每个属性是**一份子 schema** |
| `required` | 必填属性名数组 | **strict 下必须是全部属性** |
| `description` | 自然语言说明 | 给模型看的，越具体越好 |
| `enum` | 枚举值 | 与 `type` 搭配，值类型一致 |
| `const` | 单值常量 | 支持，但一般用 `enum: [x]` 更直观 |
| `items` | 数组元素 schema | `array` 必填 |
| `additionalProperties` | 是否允许额外键 | **strict 下每层都必须 `false`** |
| `$defs` / `$ref` | 定义与引用 | `$ref` 用 `#/$defs/名字` |
| `anyOf` | 多选一（并集） | 唯一受支持的组合关键字 |
| `default` | 默认值 | 不影响 `required`，模型仍会填 |
| `title` | 人类标题 | 允许但基本被忽略 |

不推荐/不支持的关键字见第 4.4 节。

### 3.4 属性名与语义

- 属性名同样受 `^[a-zA-Z0-9_-]+$` 约束，别用中文键。
- 属性顺序即模型输出顺序（部分平台按 schema 顺序生成），把最重要的放前面。
- 每个属性**都要写 `description`**：枚举要写"每个值什么意思"，数字要写单位，字符串要写格式示例。

```json
{
  "type": "object",
  "properties": {
    "city": {
      "type": "string",
      "description": "城市名，使用中文，例如 北京、上海。不要带“市”后缀"
    },
    "unit": {
      "type": "string",
      "description": "温度单位，c 表示摄氏度，f 表示华氏度",
      "enum": ["c", "f"]
    },
    "days": {
      "type": "integer",
      "description": "查询未来几天的天气，取值 1-7"
    }
  },
  "required": ["city"],
  "additionalProperties": false
}
```

> 上例把 `unit`、`days` 留作可选，是**非 strict** 写法；一旦开 `"strict": true`，这三个属性必须全部进 `required`（把可选表达成 `anyOf[..., {"type":"null"}]`，见 §4.2）。

---

## 4. strict 模式的硬规则

开 `"strict": true` 后，服务端会做**结构化输出**级别的约束：保证模型吐出的 `arguments` 一定合法。代价是 schema 必须落在受支持的子集内，否则请求直接 400。

### 4.1 三条必守规则

1. **根必须是 object**，且根上也要 `additionalProperties: false`。
2. **所有属性都必须在 `required` 里**（把"可选"表达成可空类型，见 4.2）。
3. **每一个 `object` 层级都要 `additionalProperties: false`**——包括嵌套对象、数组元素对象、`$defs` 里的对象。只写根一层是不够的，这是报错率最高的一条。

典型 400 长这样：

```
Invalid schema for function 'getWeather': In context=(), 'required' is required
to be supplied and to be an array including every key in properties.
Missing 'unit'.
```

### 4.2 "可选参数"怎么写

strict 下没有真正的 optional，只能"允空"：

```json
{
  "type": "object",
  "properties": {
    "city": { "type": "string", "description": "城市名" },
    "unit": {
      "anyOf": [{ "type": "string", "enum": ["c", "f"] }, { "type": "null" }],
      "description": "温度单位；不确定时传 null，表示使用默认摄氏度"
    }
  },
  "required": ["city", "unit"],
  "additionalProperties": false
}
```

要点：

- `anyOf: [T, {"type":"null"}]` 是标准写法，`"type": ["string","null"]` 在部分平台也接受（Azure 文档明确支持），但 `anyOf` 兼容性最好。
- 关键：**在 `description` 里告诉模型"不确定时传 null"**，否则它会硬猜一个值。
- 不开 strict 时，可选参数就是不写进 `required`，模型可能省略该键——此时代码里必须 `args.get("unit", "c")` 兜底。

### 4.3 规模限制

- 整个 schema 最多 **100 个 object 属性**，嵌套最多 **5 层**。
- 递归 schema 已被支持（如树形结构用 `"$ref": "#"` 或 `#/$defs/node` 自引用），但各平台支持进度不一，深度也受运行时限制，业务上别指望无限深。
- schema 本身计入 prompt token，工具一多，光 schema 就可能几千 token——精简 `description`、砍掉用不上的工具。

### 4.4 不支持的关键字（strict 下）

| 类型 | 不支持 |
|---|---|
| string | `minLength`、`maxLength`、`pattern`、`format` |
| number | `minimum`、`maximum`、`multipleOf` |
| object | `patternProperties`、`unevaluatedProperties`、`propertyNames`、`minProperties`、`maxProperties` |
| array | `unevaluatedItems`、`contains`、`minContains`、`maxContains`、`minItems`、`maxItems`、`uniqueItems` |
| 通用 | `oneOf`、`allOf`、`not`、`if/then/else`、`dependencies`（用 `anyOf` 替代） |

也就是说：**长度、范围、正则这些约束不能靠 schema 表达**，必须落到 `description` 里 + 代码里二次校验：

```json
{
  "type": "object",
  "properties": {
    "phone": {
      "type": "string",
      "description": "11 位中国大陆手机号，纯数字，不带 +86"
    }
  },
  "required": ["phone"],
  "additionalProperties": false
}
```

服务端不校验，拿到后自己用正则验一遍，不合格就把错误信息塞回 tool 消息让模型重来。

### 4.5 strict 与并行调用

部分平台（如 Azure OpenAI）在 `strict: true` 时**不支持并行工具调用**，需要显式 `"parallel_tool_calls": false`。用之前查一下目标平台文档；DeepSeek/第三方兼容端点对 `strict` 的支持也不一致，**不支持时会静默忽略**，所以代码侧的校验不能省。

---

## 5. Python 类型 → Schema 映射

手写 schema 时对照下表，或用 Pydantic 自动生成。

| Python | JSON Schema |
|---|---|
| `str` | `{"type": "string"}` |
| `int` | `{"type": "integer"}` |
| `float` | `{"type": "number"}` |
| `bool` | `{"type": "boolean"}` |
| `list[str]` | `{"type": "array", "items": {"type": "string"}}` |
| `dict[str, str]` | `{"type": "object", "additionalProperties": {"type": "string"}}` |
| `Literal["a", "b"]` | `{"type": "string", "enum": ["a", "b"]}` |
| `Optional[str] = None` | strict：`{"anyOf": [{"type":"string"},{"type":"null"}]}` |
| `Union[int, str]` | `{"anyOf": [{"type": "integer"}, {"type": "string"}]}`（联合越多，模型越容易摇摆，能拆字段就别联合） |
| `datetime` | `{"type": "string", "format": "date-time"}` → strict 不支持 `format`，退化为 `string` + description 说明格式 |
| `Enum` 子类 | `{"type": "string", "enum": [...]}` |
| `BaseModel` | 嵌套 object，Pydantic v2 用 `$defs` + `$ref` 复用 |

Pydantic v2 生成与适配：

```python
from pydantic import BaseModel, Field
from typing import Literal

class GetWeatherArgs(BaseModel):
    city: str = Field(description="中文城市名，如 北京")
    unit: Literal["c", "f"] = Field(default="c", description="温度单位")

schema = GetWeatherArgs.model_json_schema()
```

注意 Pydantic 默认**不会**生成 `additionalProperties: false`，也**不会**把所有字段塞进 `required`（有默认值的字段会缺席）。用 OpenAI SDK 的 `openai.pydantic_function_tool(GetWeatherArgs)` 或自己补两步：

```python
schema["additionalProperties"] = False
schema["required"] = list(schema["properties"].keys())
```

---

## 6. 场景化示例

以下每个 `parameters` 都是可直接使用的完整 schema。

### 6.1 单参数（最小可用）

```json
{
  "type": "object",
  "properties": {
    "city": {
      "type": "string",
      "description": "城市名，使用中文，例如 北京、上海"
    }
  },
  "required": ["city"],
  "additionalProperties": false
}
```

### 6.2 多参数 + 枚举 + 可空

```json
{
  "type": "object",
  "properties": {
    "city": {
      "type": "string",
      "description": "城市名，使用中文"
    },
    "unit": {
      "type": "string",
      "enum": ["c", "f"],
      "description": "温度单位：c 摄氏度，f 华氏度"
    },
    "days": {
      "anyOf": [{ "type": "integer" }, { "type": "null" }],
      "description": "查询未来几天，1-7；用户没说就传 null"
    }
  },
  "required": ["city", "unit", "days"],
  "additionalProperties": false
}
```

### 6.3 数组参数

```json
{
  "type": "object",
  "properties": {
    "keywords": {
      "type": "array",
      "items": { "type": "string" },
      "description": "搜索关键词列表，2-5 个，互相独立；中文关键词"
    },
    "doc_ids": {
      "type": "array",
      "items": { "type": "string" },
      "description": "限定检索的文档 ID 列表，为空表示全库检索"
    }
  },
  "required": ["keywords", "doc_ids"],
  "additionalProperties": false
}
```

数组长度（`minItems`/`maxItems`）strict 不支持，写进 description，代码里截断。

### 6.4 数组套对象（批量操作）

```json
{
  "type": "object",
  "properties": {
    "items": {
      "type": "array",
      "description": "要创建的订单行，至少 1 条",
      "items": {
        "type": "object",
        "properties": {
          "sku": { "type": "string", "description": "商品编码，如 SKU-1001" },
          "qty": { "type": "integer", "description": "数量，正整数" },
          "note": {
            "anyOf": [{ "type": "string" }, { "type": "null" }],
            "description": "备注，没有就传 null"
          }
        },
        "required": ["sku", "qty", "note"],
        "additionalProperties": false
      }
    }
  },
  "required": ["items"],
  "additionalProperties": false
}
```

注意 `items` 里的 object **也有** `additionalProperties: false` 和完整 `required`。

### 6.5 嵌套对象

```json
{
  "type": "object",
  "properties": {
    "hotel": {
      "type": "object",
      "description": "酒店预订信息",
      "properties": {
        "name": { "type": "string", "description": "酒店名称" },
        "check_in": { "type": "string", "description": "入住日期，格式 YYYY-MM-DD" },
        "check_out": { "type": "string", "description": "离店日期，格式 YYYY-MM-DD" },
        "guests": { "type": "integer", "description": "入住人数" }
      },
      "required": ["name", "check_in", "check_out", "guests"],
      "additionalProperties": false
    }
  },
  "required": ["hotel"],
  "additionalProperties": false
}
```

### 6.6 anyOf 联合类型

金额既可能是数字也可能是字符串时：

```json
{
  "type": "object",
  "properties": {
    "amount": {
      "description": "金额，优先给数字；带币种符号时给字符串",
      "anyOf": [
        { "type": "number" },
        { "type": "string" }
      ]
    }
  },
  "required": ["amount"],
  "additionalProperties": false
}
```

更稳的做法是**拆成两个字段**（`amount: number` + `currency: enum`），联合类型会降低模型的稳定性。

### 6.7 `$defs` 复用 + 递归

```json
{
  "type": "object",
  "properties": {
    "root": { "$ref": "#/$defs/node" }
  },
  "$defs": {
    "node": {
      "type": "object",
      "properties": {
        "name": { "type": "string", "description": "节点名称" },
        "children": {
          "type": "array",
          "description": "子节点，没有则空数组",
          "items": { "$ref": "#/$defs/node" }
        }
      },
      "required": ["name", "children"],
      "additionalProperties": false
    }
  },
  "required": ["root"],
  "additionalProperties": false
}
```

---

## 7. 常见错误清单

| # | 现象 / 写法 | 原因 | 修法 |
|---|---|---|---|
| 1 | `"function": [ {...} ]` | 把 function 当成数组 | 改成对象 `{...}` |
| 2 | `"type": "str"` / `"int"` | 混入 Python 类型名 | `string` / `integer` |
| 3 | 模型总是漏参数 | 漏写 `required`，或参数不在 `required` 里 | 补齐 `required` |
| 4 | strict 报 400 `additionalProperties` | 只在根写了，嵌套层没写 | **每一层 object 都写** |
| 5 | strict 报 400 `Missing 'x'` | 有默认值/可空字段没进 `required` | 全部列进 `required` |
| 6 | 400 `parameters must be an object` | schema 被 `json.dumps` 成字符串 | 传 dict |
| 7 | 400 `root must be object` | 根写成 array/anyOf | 包一层 object |
| 8 | 模型的 `arguments` 不是合法 JSON | 未开 strict + 复杂 schema | 开 strict，或解析失败时把错误回灌重试 |
| 9 | `tool_call_id` 对不上 | 少回填 / 顺序错 | 每个 `tool_call` 回填一条，用 `tc.id` |
| 10 | 400 `unsupported keyword: minLength` | 用了 strict 不支持的约束 | 删掉，改 description + 代码校验 |
| 11 | 模型该调不调、乱调 | `description` 只写"查询天气" | 写清触发条件与边界 |
| 12 | 参数名中英混用、camel/snake 混用 | 没有约定 | 统一命名，一次定死 |
| 13 | 工具太多导致答非所问 | 20+ 工具 + 长描述挤占上下文 | 按场景裁剪工具集 |
| 14 | `enum` 与 `type` 不一致 | `"type":"integer","enum":["1","2"]` | 值类型对齐 |
| 15 | 用 `oneOf` 表达互斥 | strict 不支持 | 改 `anyOf`，或拆字段 |

> 本仓库 `01-Agent/00-llm_function_call/llm_function_call_bymself.py` 目前同时命中了 #1 和 #2：`"function"` 写成了数组，且 `"type"` 写成了 `"str"`。

---

## 8. 校验与调试

### 8.1 先在本地验证 schema 合法

```python
import json
from jsonschema import Draft202012Validator

schema = {
    "type": "object",
    "properties": {"city": {"type": "string", "description": "城市名"}},
    "required": ["city"],
    "additionalProperties": False,
}
Draft202012Validator.check_schema(schema)  # 抛异常即 schema 本身非法
```

### 8.2 运行时校验模型给的参数

```python
import json
from jsonschema import Draft202012Validator

args = json.loads(tc.function.arguments or "{}")  # 一定是字符串
errors = sorted(Draft202012Validator(schema).iter_errors(args), key=lambda e: e.path)
if errors:
    result = "参数不合法：" + "; ".join(f"{list(e.path)} {e.message}" for e in errors)
else:
    result = fn(**args)
```

把校验错误原样回灌给模型（作为 tool 消息内容），它通常能自我修正——这是比"直接抛异常"有效得多的兜底。

### 8.3 用 Pydantic 做类型安全调用

```python
from typing import Literal
from pydantic import BaseModel

class GetWeatherArgs(BaseModel):
    city: str
    unit: Literal["c", "f"] = "c"

args = GetWeatherArgs.model_validate_json(tc.function.arguments)
result = getWeather(**args.model_dump())
```

### 8.4 排查三步法

1. `curl` 原始请求 → 看 400 的 message 里到底指向哪个 keyword。
2. 把 `tools` 单独打印成 JSON，肉眼检查缩进层级（一半问题出在层级错位）。
3. 只留一个工具、只留一个必填参数，通了再逐个加回。

---

## 9. tool_choice / parallel_tool_calls 的交互

| 参数 | 取值 | 效果 |
|---|---|---|
| `tool_choice` | `"auto"` | 模型自行决定调不调（默认） |
| | `"none"` | 禁止调用，只回答 |
| | `"required"` | 必须调用某个工具 |
| | `{"type":"function","function":{"name":"getWeather"}}` | 强制调用指定工具 |
| `parallel_tool_calls` | `true` / `false` | 是否允许一次返回多个 `tool_calls`；strict 场景常需 `false` |

`tool_choice="required"` + `parallel_tool_calls=false` 是"必须产出结构化参数"的常用组合，用来做信息抽取也很顺手。

---

## 10. 跨厂商对照

| | OpenAI Chat Completions | OpenAI Responses | Anthropic Messages | Gemini（原生） |
|---|---|---|---|---|
| 工具数组 | `tools[]` | `tools[]` | `tools[]` | `tools[].functionDeclarations[]` |
| 名称字段 | `function.name` | `name` | `name` | `name` |
| 描述字段 | `function.description` | `description` | `description` | `description` |
| Schema 字段 | `function.parameters` | `parameters` | `input_schema` | `parameters` |
| 严格模式 | `function.strict` | `strict` | 部分模型支持 `strict` | 不支持，靠 `responseSchema` |
| Schema 方言 | JSON Schema 子集 | 同左 | JSON Schema | OpenAPI 3.0 子集（`type` 大写、`nullable`） |

DeepSeek 等 OpenAI 兼容端点：请求形状与 OpenAI 相同，但 `strict` 未必生效、并行调用支持不一，**代码侧校验必须自己兜**。走兼容层（如 Gemini 的 OpenAI 兼容端点）时按 OpenAI 形状传，兼容层负责转换。

---

## 11. 提交前 Checklist

- [ ] `function` 是对象，不是数组
- [ ] `parameters.type == "object"`
- [ ] 所有 `type` 用 JSON Schema 名称（`string`/`integer`/`number`/`boolean`/`object`/`array`）
- [ ] 每个属性都有 `description`，且写清了单位、格式、取值含义
- [ ] `required` 覆盖所有属性（strict）或准确表达可选项（非 strict）
- [ ] **每一层** object 都有 `additionalProperties: false`
- [ ] 数组都有 `items`
- [ ] 没有 `minLength`/`pattern`/`format`/`oneOf`/`allOf` 等不支持关键字
- [ ] 嵌套不超过 5 层、属性总数不超过 100
- [ ] 工具名与代码注册表 key 完全一致
- [ ] `json.loads(tc.function.arguments)` 有 try/except
- [ ] 每个 `tool_call` 都回填了一条 `role:"tool"` 且 `tool_call_id` 一致

---

## 12. 参考资料

- JSON Schema 官方：[What is JSON Schema?](https://json-schema.org/overview/what-is-jsonschema)、[Understanding JSON Schema](https://json-schema.org/understanding-json-schema)
- OpenAI Structured Outputs 文档（含受支持 schema 子集与限制）：<https://platform.openai.com/docs/guides/structured-outputs>
- Azure OpenAI Structured Outputs（同源规范的中文友好版，含完整不支持关键字表）：<https://learn.microsoft.com/azure/ai-foundry/openai/how-to/structured-outputs>
- Anthropic Tool use：<https://docs.anthropic.com/en/docs/build-with-claude/tool-use>
- Gemini Function calling：<https://ai.google.dev/gemini-api/docs/function-calling>

---

## 附录 A：最小可跑骨架（复制即用）

请求体关键部分：

```json
{
  "model": "deepseek-flash",
  "messages": [{ "role": "user", "content": "北京多少度？" }],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "getWeather",
        "description": "查询指定城市当前天气。当用户询问某城市气温、是否下雨、要不要带伞时使用。",
        "parameters": {
          "type": "object",
          "properties": {
            "city": {
              "type": "string",
              "description": "城市名，使用中文，例如 北京、上海"
            }
          },
          "required": ["city"],
          "additionalProperties": false
        },
        "strict": true
      }
    }
  ],
  "tool_choice": "auto",
  "parallel_tool_calls": false
}
```

执行循环（补全 §1 的协议约定）：

```python
import json
from openai import OpenAI

client = OpenAI(base_url="...", api_key="...")
TOOLS = [ ... ]                     # 上面的 tools 数组
TOOL_REGISTRY = {"getWeather": getWeather}

messages = [{"role": "user", "content": "北京多少度？"}]

for _ in range(5):
    resp = client.chat.completions.create(
        model="deepseek-flash",
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
    )
    msg = resp.choices[0].message

    if not msg.tool_calls:                     # 没有工具调用 = 收敛
        print(msg.content)
        break

    messages.append(msg.model_dump(exclude_none=True))   # ① assistant 那条必须回填

    for tc in msg.tool_calls:                             # ② 一个都不能少
        fn = TOOL_REGISTRY[tc.function.name]
        try:
            args = json.loads(tc.function.arguments or "{}")
            out = fn(**args)
        except Exception as e:
            out = f"调用失败：{e}"
        messages.append({
            "role": "tool",
            "tool_call_id": tc.id,             # 必须与 tc.id 完全一致
            "content": json.dumps(out, ensure_ascii=False),
        })
else:
    print("超过 5 轮仍未收敛")
```
