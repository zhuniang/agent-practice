# `__new__`、`__init__` 与 `__post_init__`：Python 对象创建全流程

> 阅读前提：知道 `@dataclass` 会自动生成 `__init__` 就够了。
> 本文所有代码都在 Python 3.12 上跑过，输出直接标在代码下方。

---

## 0. 速查表

| 钩子 | 归属 | 何时被调用 | 拿到的参数 | 返回值要求 |
|---|---|---|---|---|
| `__new__(cls, ...)` | 普通类 / 不可变类型子类 | `type.__call__` 的第一步，**真正创建实例** | 与 `__init__` 相同的构造参数 | 必须是实例；返回非 `cls` 实例时 `__init__` 被跳过 |
| `__init__(self, ...)` | 普通类（dataclass 自动生成） | `__new__` 返回 `cls` 实例之后 | 构造参数 | 必须返回 `None` |
| `__post_init__(self, ...)` | **dataclass 专属** | 生成的 `__init__` 最后一行 | `InitVar` 字段（按声明顺序） | 无要求（返回值被忽略） |
| `__call__(cls, ...)` | 元类 | 比 `__new__` 更外层，拦截整个实例创建 | 构造参数 | 返回对象 |

一句话：**`__call__` → `__new__` → `__init__` → `__post_init__`**。

---

## 1. 实例创建的完整顺序

Python 把一个对象"造出来"分成两件事：

- **创建**：分配内存、返回一个实例 —— `__new__`
- **初始化**：给这个实例填属性 —— `__init__`

当你写 `Foo(1, 2)` 时，真正执行的是 `type(Foo).__call__(Foo, 1, 2)`。它的逻辑可以近似写成：

```python
def __call__(cls, *args, **kwargs):
    obj = cls.__new__(cls, *args, **kwargs)   # 1. 创建
    if isinstance(obj, cls):                  # 2. 只有还是这个类的实例才初始化
        type(obj).__init__(obj, *args, **kwargs)   # 注意：按 obj 的实际类型分派
    return obj
```

所以 **`__new__` 永远会被调用**，哪怕你只写了 `__init__`——因为 `object.__new__` 在那里兜底。反之，只写 `__new__` 不写 `__init__` 也完全合法。

```python
class Log:
    def __new__(cls, *args, **kwargs):
        print("  __new__", cls.__name__, args, kwargs)
        return super().__new__(cls)

    def __init__(self, *args, **kwargs):
        print("  __init__", self.__class__.__name__, args)
        self.args = args

Log(1, 2, k="v")
```

```
  __new__ Log (1, 2) {'k': 'v'}
  __init__ Log (1, 2)
```

注意 `__new__` 的 kwargs 收到了完整的 `k='v'`，`__init__` 里我只打印了位置参数——两者拿到的是**同一组参数**，`type.__call__` 原样转发。

---

## 2. `__new__`

### 2.1 签名与"隐式 staticmethod"

```python
def __new__(cls, *args, **kwargs):
    return super().__new__(cls)
```

- 第一个参数是 **`cls`（类本身）**，不是 `self`。
- 它定义在类里，但被 Python **自动包装成 `staticmethod`**，所以你不需要（也不应该）写 `@staticmethod`：

```python
class S:
    def __new__(cls, *a):
        return super().__new__(cls)

print(type(S.__dict__["__new__"]).__name__)   # staticmethod
print(S.__new__)                              # <function S.__new__ at ...>，不会绑定成方法
```

- `super().__new__(cls)` 是标准写法，等价于 `object.__new__(cls)`（在单继承、无特殊元类的情况下）。**不要写 `super().__new__(cls, *args)`**，`object.__new__` 不接受多余参数（见 2.3）。

#### 为什么 `class Log:` 没写父类，却能用 `super()`

```python
class Log:          # 等价于 class Log(object):
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

print(Log.__bases__)   # (<class 'object'>,)
print(Log.__mro__)     # (Log, object)
```

- **所有类都隐式继承 `object`**，它就是 MRO 的终点，所以 `super()` 永远有"下一个"可找。
- 无参 `super()` 展开成 `super(当前类, 当前方法的第一个参数)`。在 `__new__` 里第一个参数是 `cls`，所以这里就是 `super(Log, cls)`，`super().__new__` 解析到 `object.__new__`。
- `super()` 返回的不是父类本身，而是一个**按 MRO 向后查找的代理对象**，每次属性访问都重新解析。
- `object.__new__(cls)` 才是真正分配内存、返回一个空实例的内置函数；`cls` 必须显式传，因为 `__new__` 是静态方法，不会自动绑定。
- 写成 `super()` 而不是硬编码 `object.__new__(cls)`，是为了以后加 mixin 或改继承关系时能自动走到正确的下一个类（比如 mixin 也定义了 `__new__`）。
- **这个返回值不能丢**：`__new__` 的返回值就是构造结果，漏写 `return` 等于返回 `None`，`Log()` 会得到 `None` 且 `__init__` 不执行。

### 2.2 返回值决定 `__init__` 跑不跑

`type.__call__` 里有一个 `isinstance(obj, cls)` 判断，规则如下：

| `__new__` 返回 | `__init__` 是否调用 |
|---|---|
| `cls` 的新实例 | 调用 |
| `cls` 的**子类**实例 | 调用（`isinstance` 成立） |
| 完全不相干的其他对象 | 不调用 |
| `None` / `int` 等非实例 | 不调用，`Foo(...)` 直接返回这个值 |

> 注意两件事：
> 1. 判断用的是 `isinstance(obj, cls)`，不是 `type(obj) is cls`——返回 `cls` 的**子类**实例也算数。
> 2. `__init__` 是在 `type(obj)` 上按 MRO 查找的，不是硬编码调用 `cls.__init__`。所以子类自己定义了 `__init__` 时，执行的是子类那份；子类没定义才落到父类那份。

```python
class Base:
    def __init__(self):
        print("  Base.__init__ 被执行")

class Sub(Base):
    def __new__(cls):
        if cls is Sub:
            print("  Sub.__new__ 返回一个 Base 实例")
            return Base()          # 不是 Sub 的实例
        return super().__new__(cls)

s = Sub()
print("  type(s) =", type(s).__name__)
```

```
  Sub.__new__ 返回一个 Base 实例
  Base.__init__ 被执行          ← 这是 Base() 自己触发的
  type(s) = Base
```

这里 `Sub.__init__` 从头到尾没执行；屏幕上那行 `Base.__init__` 是 `Base()` 内部的。

再看一个更细的点：子类自己定义了 `__init__` 时，跑的是子类那份。

```python
class Parent:
    def __new__(cls):
        class Child(Parent):
            def __init__(self):
                print("  Child.__init__ 执行, type(self) =", type(self).__name__)
        return object.__new__(Child)      # 返回子类实例

    def __init__(self):
        print("  Parent.__init__ 执行, type(self) =", type(self).__name__)

Parent()
```

```
  Child.__init__ 执行, type(self) = Child
```

`type(obj)` 是 `Child`，所以按 `Child` 的 MRO 找到 `Child.__init__`。如果 `Child` 不定义 `__init__`，查找会落到 `Parent.__init__`——函数是 `Parent` 里写的，但 `self` 仍是 `Child` 实例，`type(self).__name__` 依然是 `"Child"`。**方法定义在哪个类，和 `self` 的实际类型，是两件事**，Python 从不检查 `type(self) is Parent`。

再把 `__new__` 返回子类实例的情况对比一下：

```python
class Parent:
    def __new__(cls):
        if cls is Parent:
            class Child(Parent):
                pass
            return object.__new__(Child)     # 是 Parent 的子类实例
        return object.__new__(cls)

    def __init__(self):
        print("  Parent.__init__ 调用，self 类型 =", type(self).__name__)

Parent()
```

```
  Parent.__init__ 调用，self 类型 = Child
```

> 这解释了为什么"返回已有实例"的写法能实现单例/缓存：只要返回的仍是 `cls` 的实例，`__init__` 还会再跑一遍（可能不是你想要的，见 2.4）。

### 2.3 `object.__new__` 的参数怪癖

`object.__new__` 只接受一个参数（即 `cls`）。但它的报错行为取决于这个类有没有自定义 `__new__`：

```python
class WithInit:
    def __init__(self, x):
        self.x = x

w = object.__new__(WithInit, 1, 2)   # 不报错！多余参数被静默忽略
print(hasattr(w, "x"))               # False，w 是个没初始化的"半成品"
```

```python
class HasNew:
    def __new__(cls, x):
        return object.__new__(cls)
    def __init__(self, x):
        self.x = x

object.__new__(HasNew, 1)
# TypeError: object.__new__() takes exactly one argument (the type to instantiate)
```

规则：**类自己定义了 `__new__` 时严格校验；没有自定义 `__new__` 但自定义了 `__init__` 时，`object.__new__` 允许并忽略多余参数。** 这是历史遗留行为，实际写代码时不必依赖，记住"自定义 `__new__` 就别把参数传给 `object.__new__`"即可。

### 2.4 `__new__` 的典型用途

**(1) 不可变内置类型的子类**——`int`、`str`、`tuple` 的实例一旦创建就不能改，只能在 `__new__` 阶段做文章：

```python
class AlwaysZero(int):
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, 0)

print(AlwaysZero(999))        # 0
print(type(AlwaysZero(999)))  # <class '__main__.AlwaysZero'>
```

`namedtuple`、`enum.Enum` 也都是靠 `__new__` 实现的，这也是它们不能用普通 `__init__` 定制的原因。

**(2) 单例 / 对象池**：

```python
class Singleton:
    _inst = None
    def __new__(cls):
        if cls._inst is None:
            print("  创建新实例")
            cls._inst = super().__new__(cls)
        else:
            print("  复用已有实例")
        return cls._inst

Singleton()   # 创建新实例
Singleton()   # 复用已有实例
```

> 注意：单例如果还有 `__init__`，每次 `Singleton()` 都会重跑 `__init__`。要彻底只初始化一次，得在 `__init__` 里加标志位，或者干脆不定义 `__init__`。

**(3) 返回缓存对象 / 不可变对象的 intern**：

```python
_cache = {}

class Color:
    def __new__(cls, name):
        if name not in _cache:
            obj = super().__new__(cls)
            obj.name = name
            _cache[name] = obj
        return _cache[name]

Color("red") is Color("red")   # True
```

**(4) 需要在"对象还不存在"时做决策**——比如根据参数决定实际返回哪个子类（工厂模式）。

### 2.5 `__new__` 的坑

```python
class NeedsArg:
    def __new__(cls, v):
        obj = super().__new__(cls)
        obj.v = v
        return obj
    def __init__(self, v):
        pass

import pickle, copy
pickle.loads(pickle.dumps(NeedsArg(9)))
# TypeError: NeedsArg.__new__() missing 1 required positional argument: 'v'
copy.copy(NeedsArg(9))
# TypeError: NeedsArg.__new__() missing 1 required positional argument: 'v'
```

原因：`pickle` 和 `copy` 还原对象时会用 `cls.__new__(cls)` **不带参数**地重建实例。修法是加 `__getnewargs__`：

```python
class NeedsArg2:
    def __new__(cls, v):
        obj = super().__new__(cls)
        obj.v = v
        return obj
    def __getnewargs__(self):
        return (self.v,)

pickle.loads(pickle.dumps(NeedsArg2(3))).v   # 3
```

同理，`copy.copy` 走的是 `__reduce_ex__` 协议，不需要 `__getnewargs__` 时会走 `__new__` + `__dict__` 拷贝。

---

## 3. `__init__`

- 参数：`self` + 构造参数。
- **返回值必须是 `None`**，否则：

```python
class BadInit:
    def __init__(self):
        return 1

BadInit()
# TypeError: __init__() should return None, not 'int'
```

- `__init__` 里抛异常，对象已经创建（`__new__` 已执行），只是不会被返回给调用方，后续会被 GC 掉。
- 什么时候需要自己写 `__init__`？当类不是 dataclass，或者 dataclass 的 `init=False`，或者你需要在初始化里做 dataclass 表达不了的事。

```python
@dataclass
class P:
    x: int
    y: int = 0

import inspect
print(inspect.signature(P.__init__))   # (self, x: int, y: int = 0) -> None
```

dataclass 生成的 `__init__` 做的就是 `self.x = x`、`self.y = y` 这类赋值，**结尾自动调用 `__post_init__`**（如果定义了）。所以 dataclass 本身**不生成 `__new__`**，`__new__` 仍来自 `object`。

### 3.1 通俗版：构造函数到底要哪些参数

把 `@dataclass` 想成「照着类体自动印一张报名表」，规则只有六条：

- `字段名: 类型` → 表上一行，**必填**；
- `字段名: 类型 = 默认值`（或 `field(default=...)` / `default_factory=...`）→ 表上一行，**选填**；
- `字段名: 类型 = field(init=False)` → **不印在表上**，但档案里有，得自己事后填（通常在 `__post_init__`）；
- `字段名: ClassVar[...]` → 贴在墙上的公告，**不是报名项**；
- `字段名: InitVar[...]` → 表上一行，但**传完就扔**，不进档案（不是实例属性）；
- 没有 `: 类型` 的类属性 → 墙上告示，dataclass 根本看不见。

所以判断一个名字要不要传，只问三件事：**有类型注解吗？是 `ClassVar` 吗？是 `init=False` 吗？** 三个条件都满足，才进参数表。

```python
import inspect
from dataclasses import dataclass, field, fields, InitVar
from typing import ClassVar

@dataclass
class Order:
    user: str                          # 必填
    amount: float                      # 必填
    note: str = ""                     # 选填
    tax: float = field(init=False)     # 参数表里没有
    currency: ClassVar[str] = "CNY"    # 参数表里没有
    coupon: InitVar[str] = "-"         # 参数表里有，但不成为属性

    def __post_init__(self, coupon):
        self.tax = round(self.amount * 0.1, 2)
        self.tag = coupon

inspect.signature(Order.__init__)
# (self, user: str, amount: float, note: str = '', coupon: InitVar[str] = '-') -> None
[f.name for f in fields(Order)]
# ['user', 'amount', 'note', 'tax']   ← tax 是字段但不是参数
vars(Order("tom", 100))
# {'user': 'tom', 'amount': 100, 'note': '', 'tax': 10.0, 'tag': '-'}
```

三条硬规则：

1. 参数顺序 = 类体里声明顺序，基类字段排在最前。
2. 有默认值的字段不能排在没默认值的前面 → `TypeError: non-default argument 'b' follows default argument`；3.10+ 用 `field(kw_only=True)` 或类级 `@dataclass(kw_only=True)` 可以绕过。
3. 传了表里没有的参数 → `TypeError: Order.__init__() got an unexpected keyword argument 'z'`。

---

## 4. `__post_init__`

### 4.1 它是什么

`@dataclass` 自动生成的 `__init__` 长这样（伪代码）：

```python
def __init__(self, x, y=0):
    self.x = x
    self.y = y
    self.__post_init__()     # ← 如果类里定义了，就在这里被调用
```

`__post_init__` 是 dataclass 给你的**唯一插入点**：`__init__` 是自动生成的，你没法改；但你可以定义 `__post_init__`，它会在所有字段赋值完成后执行。

### 4.2 能干什么：校验、派生字段、规范化

```python
from dataclasses import dataclass, field

@dataclass
class Rect:
    w: float
    h: float = 0.0
    label: InitVar[str] = "rect"
    area: float = field(init=False)

    def __post_init__(self, label):
        if self.w <= 0 or self.h <= 0:
            raise ValueError("边长必须为正")
        self.area = self.w * self.h
        self.name = f"{label}-{self.w}x{self.h}"

r = Rect(2, 3, "box")
print(r)          # Rect(w=2, h=3, area=6)
print(r.area)     # 6
print(r.name)     # box-2x3
Rect(-1, -1)      # ValueError: 边长必须为正
```

要点：

- `field(init=False)` 的字段不出现构造参数里，只由 `__post_init__` 赋值。
- `__post_init__` 里可以给**没在 dataclass 声明过**的属性赋值（上面的 `name`），没人拦你，但它不会出现在 `repr`/`eq`/`fields()` 里。
- 抛异常即"校验失败"，构造不会成功。

### 4.3 `InitVar`：只做构造参数，不做属性

`InitVar[T]` 表示"这个值只在构造时用一下，不存成字段"：

```python
from dataclasses import dataclass, InitVar, fields

@dataclass
class R:
    w: int
    label: InitVar[str] = "rect"     # 有默认值，位置在 w 之后

    def __post_init__(self, label):  # 按字段声明顺序接收 InitVar
        self.tag = label

r = R(1)
print(vars(r))                  # {'w': 1, 'tag': 'rect'}
print([f.name for f in fields(R)])  # ['w']          ← 不是字段
```

`InitVar` 的三个特点：

1. 出现在 `__init__` 签名里（`(self, w, label='rect')`），也出现在 `__match_args__` 里；
2. **不会成为实例属性**（`'label' not in vars(r)`）；
3. 不会出现在 `repr`、`eq`、`fields()`、`asdict()` 中。

> 小陷阱：如果 `InitVar` 带默认值，**类属性上还留着这个默认值**，所以 `hasattr(r, "label")` 是 `True`（走类属性查找），但 `"label" in r.__dict__` 是 `False`。写代码时用后者判断更准确。

`__post_init__` 的签名必须与所有 `InitVar` 字段一一对应（按声明顺序），否则调用时 TypeError。

### 4.4 `frozen=True` 时必须用 `object.__setattr__`

冻结的 dataclass 会拦截所有属性赋值（生成 `__setattr__`/`__delattr__` 抛 `FrozenInstanceError`），`__post_init__` 里也不例外：

```python
@dataclass(frozen=True)
class FrozenRect:
    w: float
    h: float
    area: float = field(init=False)

    def __post_init__(self):
        object.__setattr__(self, "area", self.w * self.h)

f = FrozenRect(2, 3)
print(f)          # FrozenRect(w=2, h=3, area=6)
f.w = 10          # dataclasses.FrozenInstanceError: cannot assign to field 'w'
```

这是标准做法：`frozen` + `field(init=False)` + `object.__setattr__`。

### 4.5 继承：基类的 `__post_init__` 不会自动调用

```python
@dataclass
class A:
    a: int = 1
    def __post_init__(self):
        print("  A.__post_init__")

@dataclass
class B(A):
    b: int = 2
    def __post_init__(self):
        super().__post_init__()      # ← 必须自己写
        print("  B.__post_init__")

B()
```

```
  A.__post_init__
  B.__post_init__
```

子类覆盖 `__post_init__` 时，不复写 `super().__post_init__()` 就会丢掉父类的逻辑。这和 `__init__` 的 `super()` 规则一致。

另外，`B.__init__` 的签名是 `(self, a: int = 1, b: int = 2)`——基类字段在前。

### 4.6 什么时候**不会**调用

```python
called = []

@dataclass(init=False)
class NoInit:
    x: int = 1
    def __post_init__(self):
        called.append(1)

NoInit()
print(len(called))    # 0
```

`init=False` 时不生成 `__init__`，自然没人调用 `__post_init__`。同理，你手动定义了 `__init__` 并覆盖了 dataclass 生成的版本，也不会自动调用——必须自己写。

### 4.7 `replace()` 会重走一遍

`dataclasses.replace(obj, **changes)` 的语义是"用新参数重新构造"，所以 `__init__` 和 `__post_init__` 都会执行：

```python
from dataclasses import replace

f = FrozenRect(2, 3)
print(replace(f, w=4))    # FrozenRect(w=4, h=3, area=12)
```

注意 `area` 是从 `w`、`h` 重新算出来的（12 而不是 6），因为 `__post_init__` 又跑了一次。这通常是优点（派生字段自动保持一致），但如果你在 `__post_init__` 里做有副作用的事（写日志、注册到全局表），要小心 `replace`/反序列化时会重复触发。

### 4.8 为什么用钩子，而不是在 `__init__` 里写逻辑

因为 dataclass 的 `__init__` 是生成的，你无法在不放弃整个自动 `__init__` 的情况下插入逻辑。`__post_init__` 就是官方给的钩子。对比三种写法：

| 写法 | 优点 | 缺点 |
|---|---|---|
| `__post_init__` | 保留自动 `__init__`，声明式 | 只有"初始化之后"一个时机 |
| 手写 `__init__` | 完全自由 | 丢掉 dataclass 的 `init` 生成，字段多了很啰嗦 |
| `__new__` | 能在创建前决策 | 太底层，参数转发、pickle 都要自己管 |

---

## 5. 完整调用链实验

```python
class Meta(type):
    def __call__(cls, *args, **kwargs):
        print("  Meta.__call__ 拦截，args =", args)
        obj = super().__call__(*args, **kwargs)
        obj.traced = True
        return obj

class Traced(metaclass=Meta):
    def __new__(cls, v):
        print("  Traced.__new__")
        return super().__new__(cls)

    def __init__(self, v):
        print("  Traced.__init__")
        self.v = v

t = Traced(7)
print(t.v, t.traced)
```

```
  Meta.__call__ 拦截，args = (7,)
  Traced.__new__
  Traced.__init__
  7 True
```

所以完整的创建链条是：

```
Foo(...)
 └─ type(Foo).__call__          ← 元类可拦截（最外层，可改返回值/参数）
     ├─ Foo.__new__(cls, ...)   ← 创建实例，决定返回什么
     └─ Foo.__init__(obj, ...)  ← 初始化（仅当 isinstance(obj, Foo)）
         └─ obj.__post_init__() ← dataclass 生成，仅 dataclass 有
```

- 想**换一个对象**返回（工厂）→ 用元类 `__call__` 或 `__new__`。
- 想**控制实例创建**（单例、不可变、缓存）→ `__new__`。
- 想**初始化后补充、校验**→ `__init__`（普通类）或 `__post_init__`（dataclass）。

---

## 6. 容易混进来的其他钩子

这些**不是构造函数**，但经常和上面几个一起被问到：

### 6.1 `__init_subclass__`：子类被定义时触发

```python
class Plugin:
    registry = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Plugin.registry[cls.__name__] = cls

class P1(Plugin): pass
class P2(Plugin): pass

print(list(Plugin.registry))   # ['P1', 'P2']
```

- 触发时机是 **`class P1(Plugin):` 这一行执行时**，跟实例化无关。
- 隐式 classmethod，第一个参数是子类。
- 典型用途：注册表、自动给子类打补丁、`abc`/`Protocol` 的钩子。

### 6.2 `__set_name__`：描述符被绑定时触发

```python
class Desc:
    def __set_name__(self, owner, name):
        print(f"  __set_name__: {owner.__name__}.{name}")
        self.name = name
    def __get__(self, obj, owner=None):
        return self.name.upper()

class UsesDesc:
    foo = Desc()          # 类创建时触发 __set_name__

print(UsesDesc().foo)     # FOO
```

同样是**类创建时**（`type.__new__` 之后、类体执行完）对每个类属性调用一次，和实例创建无关。

### 6.3 `__class_getitem__` / `__getitem__`

`Foo[int]` 走的是 `__class_getitem__`，和 `Foo(...)` 完全是两回事。

### 6.4 `__setattr__` / `__delattr__` / `__slots__`

对象**已经存在之后**，属性赋值/删除时的拦截（`frozen=True` 就生成这两个）。`slots=True` 则是在类创建时重建类、加 `__slots__`，让实例没有 `__dict__`：

```python
@dataclass(slots=True)
class SlotRect:
    w: int
    area: int = field(init=False)
    def __post_init__(self):
        self.area = self.w * self.w

print(SlotRect(3))                      # SlotRect(w=3, area=9)
print(hasattr(SlotRect(3), "__dict__")) # False
```

注意 `slots=True` 时 dataclass 会**返回一个新的类对象**，`isinstance` 判断、`super()` 在极少数动态场景下会受影响。

### 6.5 `__del__`

不是 `__new__` 的对称物（那是 `__init__`），也不是可靠的析构时机——GC 不保证调用、解释器退出时不保证执行。资源清理用 `with` / `try-finally`。

---

## 7. 常见误解 FAQ

**Q：`@dataclass` 会生成 `__new__` 吗？**
不会。只生成 `__init__`（默认）、`__repr__`、`__eq__`，以及按需的 `__hash__`、比较方法、`__setattr__`/`__delattr__`、`__slots__`、`__match_args__`。`__new__` 始终来自 `object`。

**Q：dataclass 的 `__init__` 参数包含所有属性吗？**
不包含。参数集合 ≠ 属性集合，两个方向都有例外：

| 写法 | 进 `__init__` 参数？ | 算字段（进 repr/eq/fields）？ |
|---|---|---|
| `x: int` | 是 | 是 |
| `x: int = 1` | 是（有默认值） | 是 |
| `x: int = field(init=False)` | **否** | 是 |
| `x: InitVar[int]` | **是** | **否** |
| `x: ClassVar[int]` | 否 | 否 |
| `x = 1`（无注解） | 否 | 否 |
| `__post_init__` 里 `self.y = ...` | 否 | 否 |

所以准确说法是：**`__init__` 的参数 = 所有 `init=True` 的字段 + 所有 `InitVar`**，和"类上有哪些属性"没有直接关系。`init=False` 的字段记得在 `__post_init__` 里赋值，否则访问它（包括 `repr`、`==`）会抛 `AttributeError`。

**Q：类变量和实例属性有什么区别？**
Python 只有一种东西叫"属性"（attribute），区别只在于名字存在哪个 `__dict__` 里。类体里直接写的进类的 `__dict__`（俗称类变量），`self.x = ...` 写的进实例的 `__dict__`（实例属性）。

读完的顺序是：先找实例 `__dict__`，没有就沿 `type(实例)` 的 MRO 到类里找。

- `a.kind = "B"` 只是往实例的 `__dict__` 里写一个新项，不会改类；`del a.kind` 之后，读到的又变回类上的值。
- 类体里放的**可变对象**（`items = []`）会被所有实例共享，因为大家拿到的是同一个 list；要每个实例各有一份，用 `field(default_factory=list)` 或 `self.items = []`。
- 在 dataclass 里，只有 `x: ClassVar[int] = ...` 才是真正的类变量；`x: int` / `x: int = 1` 都是实例字段，只是默认值暂存在类上。

**Q：只定义 `__new__` 不定义 `__init__`，对象能正常用吗？**
能。`Foo(...)` 会先创建，再调用继承来的 `object.__init__`——它只做参数检查、不做任何赋值。而且因为类自定义了 `__new__`，它连多余参数都直接忽略：

```python
class OnlyNew:
    def __new__(cls, v):
        obj = super().__new__(cls)
        obj.v = v
        return obj

OnlyNew(5).v    # 5
```

**Q：`__new__` 和 `__init__` 的参数必须一致吗？**
`type.__call__` 会把同一组参数先给 `__new__` 再给 `__init__`。所以自定义 `__new__` 时必须接收（或至少兼容）全部构造参数，否则直接 TypeError。常见写法：

```python
def __new__(cls, *args, **kwargs):
    return super().__new__(cls)     # 只把 cls 交给 object.__new__
```

**Q：`__post_init__` 可以是"第二个构造函数"吗？**
不能。它拿不到普通字段参数（只有 `InitVar`），也不能改变对象身份，更不能阻止对象被创建——它跑的时候 `self` 已经完整赋值了。

**Q：`__post_init__` 里能修改 `frozen` 的字段吗？**
只能通过 `object.__setattr__(self, "字段", 值)`；直接赋值会抛 `FrozenInstanceError`。

**Q：dataclass 的 `__init__` 里字段顺序是什么？**
位置参数按声明顺序、基类字段在前；`kw_only` 字段无论在哪儿声明，一律排到 `*` 之后变成仅关键字参数。所以 kw_only 字段没有"默认值必须靠后"的限制，位置字段才有。

**Q：`__post_init__` 里抛异常，对象还存在吗？**
已经创建（`__new__` 执行过），但构造失败，调用方拿不到引用，很快会被回收。如果 `__new__` 里做了全局注册，记得在异常路径清理，否则会泄漏。

**Q：`replace()` 和 `copy.copy()` 有什么区别？**
`replace` 是"用新参数重新调用 `__init__`"（会重新执行 `__post_init__` 和校验）；`copy.copy` 是浅拷贝，走 `__reduce_ex__`，不重新跑 `__init__`，对 dataclass 字段做逐属性复制。

---

## 8. 一页纸总结

```
实例化 Foo(...)
├─ type(Foo).__call__           元类可拦截
├─ Foo.__new__(cls, ...)        创建；返回非 cls 实例 → 跳过 __init__
├─ Foo.__init__(self, ...)      初始化；必须返回 None
└─ self.__post_init__()         仅 dataclass；frozen 时用 object.__setattr__
```

- **`__new__`**：管"造出来"，不可变类型、单例、缓存才需要碰它；记得 pickle/copy 的 `__getnewargs__`。
- **`__init__`**：管"填属性"，dataclass 自动生成，返回 `None`。
- **`__post_init__`**：dataclass 初始化后的唯一插入点，做校验和派生字段；`InitVar` 是它的专属参数；继承要 `super()`；`init=False` 时不触发。
- **`__init_subclass__` / `__set_name__`**：类创建阶段的钩子，和实例无关。
- **`__call__`（元类）**：比 `__new__` 更外层，能换掉整个返回值。

---

## 附录 A：MRO 是什么

MRO（Method Resolution Order，方法解析顺序）是**一个类到 `object` 的线性查找顺序表**。Python 在类上查找属性/方法时严格按这个顺序走，命中即停。

```python
class A: pass
class B(A): pass
class C(A): pass
class D(B, C): pass

print(D.__mro__)   # (D, B, C, A, object)
```

规则（C3 线性化）：

1. 子类永远排在父类前面；
2. 多个父类按 `class D(B, C)` 里的声明顺序；
3. 保持每个父类自身的 MRO 顺序（单调性）。

`super()` 就是"在 MRO 里取当前类的下一个"，所以合作式多继承能一路串下去：

```python
class A:
    def hi(self): print("A.hi")
class B(A):
    def hi(self):
        print("B.hi")
        super().hi()     # 在 D 的实例上，这里从 C 开始
class C(A):
    def hi(self):
        print("C.hi")
        super().hi()
class D(B, C):
    def hi(self):
        print("D.hi")
        super().hi()

D().hi()   # D.hi / B.hi / C.hi / A.hi
```

`super()` 里的"当前类"由 `__class__` cell 决定，不是 `self` 的类型——所以 `D()` 调 `B.hi()` 时，`B` 里的 `super()` 找的是 `C` 而不是 `A`。

两个父类的顺序打架时会直接报错：

```python
class P: pass
class Q: pass
class X(P, Q): pass
class Y(Q, P): pass
class Z(X, Y): pass
# TypeError: Cannot create a consistent method resolution order (MRO) for bases P, Q
```

- `__mro__` 是只读元组；`mro()` 是方法，元类可以覆盖它。
- `__bases__` 只是直接父类，`__mro__` 才是完整链条。
- 属性查找的实际顺序是：数据描述符 → 实例 `__dict__` → 类 MRO 上的非数据描述符/普通属性。
