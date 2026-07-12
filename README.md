#  通达信量化 说明文档

## 一、必要条件

1、主要适用于 `QwenPaw` **开源 Agent**，如果你适用于靠积分充值、Ai 编辑器、则效果大打折扣！因为缺少：人格、价值观、底线、行为边界、流程、权限、长期记忆、多Agent、子Agent等；

2、务必安装 Agent 的核心三件套：`IDENTITY.md`、`SOUL.md`、`AGENTS.md`，它们最终决定 Ai Agent的产出质量；

3、如果你是量化新手，在`IDENTITY.md`文件中，告知你当前的状况，比如
```
我是一个量化新手，在跟我交流的时候，尽可能阐述的更简单、详细一些
```
除此之外，不建议修改核心三件套，如果你有丰富的量化经验，可以进行适当的修改；

## 二、总目录

### TdxQuant 量化智能体 — 人设文件

本目录包含为 **TdxQuant（通达信量化平台）** 定制的 **QwenPaw 智能体人设文件**。

### 文件说明

| 文件 | 用途 | 说明 |
|------|------|------|
| **AGENTS.md** | 工作规则与操作指南 | 定义智能体的工作流程、能力边界、安全规范、作答习惯 |
| **SOUL.md** | 核心身份与行为原则 | 定义智能体的价值观、风格、语气、行为准则 |
| **PROFILE.md** | 身份信息与用户资料 | 记录智能体的专长领域、参考资源、用户画像框架 |
| **WORKING_MEMORY.md** | 工作记忆 | 智能体运行时自动维护 |
| **agent.json** | QwenPaw 智能体配置模板（可选） | 可导入 QwenPaw 的 config.json 的 `agents.profiles` 中注册智能体 |
| **Skills/** | 当前智能体真正要用到的技能目录 |

### 技能目录
详细参见：skills\TQ-Python\README.md
```
skills/                      # 工作区文件夹
│   └── TQ-Python/           # 当前技能根目录
│       ├── SKILL.md         # 【核心文件】技能的主指令、元数据
│       ├── scripts/         # 可执行脚本目录
│       │   ├── *.py         # Python 脚本
│       │   ├── *.sh         # Shell 脚本
│       │   ├── *.js         # JavaScript 脚本
│       │   └── ...          # 其他可执行文件
│       ├── references/      # 【参考文档】存放规则、API等文档，AI按需查阅
│       │   ├── *.md         # Markdown 文档
│       │   ├── *.txt        # 纯文本文件
│       │   └── ...          # 其他文本文件
│       └── assets/          # 【静态资源】存放模板、图片、配置文件等
│           ├── templates/   # 模板文件（如报告模板）
│           ├── ...          # 其他静态资源
│           └── origin.json  # 技能其它信息（下载地址、安装时间）
```

## 三、在 QwenPaw 中使用

### 方式一：直接克隆项目到QwenPaw工作区（推荐）

### 方式二：通过控制台创建

1. 启动 QwenPaw，在控制台进入 **设置 → 智能体管理**
2. 点击 **创建智能体**
3. 填写：
   - **名称：** TdxQuant 量化助手
   - **描述：** 通达信 TdxQuant 量化投研平台的 Python 策略开发技术伙伴：行情数据、策略开发、回测分析、模拟/实盘交易
   - **ID：** `TdxQuant`（或自定义）
4. 创建后，在 **工作区 → 文件** 页面，将本目录的 `AGENTS.md`、`SOUL.md`、`PROFILE.md` 上传或粘贴覆盖
5. 在 **工作区 → 技能** 页面，按需启用所需技能

### 方式三：通过配置文件注册

将 `agent.json` 的内容合并到 `~/.qwenpaw/config.json` 的 `agents.profiles` 中：

```json
{
  "agents": {
    "profiles": {
      "TdxQuant": {
        "id": "TdxQuant",
        "name": "TdxQuant 量化助手",
        "description": "通达信 TdxQuant 量化投研平台的 Python 策略开发技术伙伴",
        "workspace_dir": "~/.qwenpaw/workspaces/TdxQuant"
      }
    }
  }
}
```

然后将人设文件放入 `~/.qwenpaw/workspaces/TdxQuant/` 目录。

## 四、依赖检查

为了能够正常运行量化分析、回测、实盘；**<font color="yellow">在初次使用的时候，Agent会自动监测必要环境依赖</font>**;

### 1、通达信软件的安装

我们修改了 通达信官方的技能文件，原因是：

1、里面太多对公司介绍的句子。多余。并且影响上下文和记忆。

2、默认会监测你本地是否安装了通达信，但是我们不会让 Agent 自动安装，原因是：如果并没有正确检测到的时候，他就会多给你安装一个通达信，多余，并且影响上下文和记忆。所以，务必自己手动已经安装了通达信X64。

### 2、Python 库

比如：`Pandas`、`numpy`、`talib`、`vectorbt`为必备第三方标准库！量化的必选！
| 库      | 说明 |
| ----------- | ----------- |
| pandas      | 最流行的Python数据分析库|
| numpy   | Python的科学计算基础库|
| talib   | 技术分析指标库，也可用于指定其它指标，如<font color="red"> **帝法指标**  </font>|
| vectorbt   | 它通过创新的 向量化计算 和 即时编译技术，<font color="red">**实现了极高的回测速度**</font> |

> :memo: **警告** 其中 `vectorbt` 的 `vbt.Portfolio.from_signals` 在通达信中不支持分红送股等权益变动，如果使用 `vectorbt` 可能不精确，如果追求更高效、更高级的量化，推荐使用我们开源的**金字塔量化**；

#### 2-1、安装库 可能遇到的问题

Agent 在安装过程中，可能出现超时报错等情况，这是因为第三方库的镜像源默认在国外，受网络因素的影响较大。建议大家在安装时，让 Agent 使用国内镜像源下载(牛逼的模型会自己知道这样干)。或自行安装必要的库；

2-1-1、国内镜像源

清华：https://pypi.tuna.tsinghua.edu.cn/simple/

阿里云：http://mirrors.aliyun.com/pypi/simple/

中国科技大学 https://pypi.mirrors.ustc.edu.cn/simple/

华中理工大学：http://pypi.hustunique.com/

山东理工大学：http://pypi.sdutlinux.org/

豆瓣：http://pypi.douban.com/simple/

以使用清华镜像源安装pandas为例，安装命令如下，
```
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pandas
```

#### 2-2、查看安装的库

通过命令查看在cmd中输入`pip list`

## 其它说明

鉴当前股市网络环境、政策等原因，公开的项目，暂时不提供策略源码。如果你已经加入 24krmb-Fans 组织，优先从 组织仓库 `https://github.com/24krmb-Fans` 拉取或克隆、下载项目，组织项目包含各类量化、选股等源码供你参考学习交流；

## 致谢

- [QwenPaw](https://github.com/agentscope-ai/QwenPaw) — 阿里 agentscope 团队出品的 Agent
- [通达信](https://www.tdx.com.cn/) — 深圳市财富趋势科技股份有限公司
- [24KRMB.COM](https://www.24krmb.com/) — 技术支持与社区

## 开许可证

[MIT](LICENSE)