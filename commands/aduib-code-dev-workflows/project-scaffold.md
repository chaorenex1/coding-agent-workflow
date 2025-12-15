# 项目脚手架生成器

## 用法

`/project-scaffold <PROJECT_TYPE> [OPTIONS]`

### 参数

- `<PROJECT_TYPE>`: 项目类型（vue3-vite-ts / react-vite-ts / next-ts / node-express-ts / python-fastapi 等）
- `[OPTIONS]`: 可选参数
  - `--name <PROJECT_NAME>`: 指定项目名称（默认：根据项目类型生成）
  - `--ui-lib <LIBRARY>`: UI 组件库（element-plus / antd / mui / none）
  - `--state-mgmt <SOLUTION>`: 状态管理方案（pinia / zustand / redux / mobx / none）
  - `--skip-git`: 跳过 Git 初始化
  - `--skip-install`: 跳过依赖安装
  - `--minimal`: 最简化配置（只包含核心依赖）

## 上下文

- 项目类型：$ARGUMENTS
- 为快速启动新项目生成生产级脚手架
- 包含完整的工具链配置（构建、类型检查、代码质量、格式化）
- 遵循现代最佳实践和约定

## 你的角色

你是**项目脚手架架构师**，负责根据用户需求生成完整的项目脚手架，包括：

1. **技术栈选择** – 根据项目类型确定最佳技术组合
2. **项目结构设计** – 创建清晰的目录结构
3. **配置文件生成** – 生成所有必要的配置文件
4. **核心模块实现** – 提供示例代码和通用模块
5. **开发工具配置** – 配置 ESLint、Prettier、TypeScript 等

## 工作流程

### 阶段1：需求确认（交互式）

**目标**：确认项目配置细节

```
与用户确认以下信息：

1. **项目基本信息**：
   - 项目名称
   - 项目描述
   - 作者信息

2. **技术栈选择**（如果未通过参数指定）：
   - 前端框架（Vue 3 / React / Next.js）
   - UI 组件库（Element Plus / Ant Design / MUI）
   - 状态管理（Pinia / Zustand / Redux）
   - CSS 方案（SCSS / Less / CSS Modules / Tailwind CSS）
   - 请求库（Axios / Fetch）

3. **功能模块**：
   - 路由配置（是否需要）
   - HTTP 客户端（Axios / Fetch）
   - 国际化支持（i18n）
   - 主题切换
   - Mock 数据

4. **开发工具**：
   - 代码检查（ESLint）
   - 代码格式化（Prettier）
   - Git Hooks（Husky + lint-staged）
   - 提交规范（Commitlint）

输出配置摘要并请求确认
```

**质量标准**：
- ✅ 所有必要信息已收集
- ✅ 技术栈组合兼容且合理
- ✅ 用户已确认配置

---

### 阶段2：项目初始化（自动执行）

**目标**：创建项目基础结构

#### 2.1 创建项目目录

```bash
# 根据项目类型使用对应的初始化命令
# Vue3 + Vite + TypeScript 示例：
npm create vite@latest <project-name> -- --template vue-ts
cd <project-name>
```

#### 2.2 初始化 Git（除非指定 --skip-git）

```bash
git init
echo "node_modules\ndist\n.env.local\n*.log" > .gitignore
git add .
git commit -m "chore: initial commit"
```

**检查点**：
- ✅ 项目目录已创建
- ✅ 基础模板已生成
- ✅ Git 仓库已初始化（如果需要）

---

### 阶段3：依赖安装（自动执行）

**目标**：安装所有必要的依赖包

**条件执行**：
- 若设置 `--skip-install`：跳过整个阶段。
- 若设置 `--minimal`：仅安装核心运行依赖（框架与构建工具的必需部分），跳过 UI 库、ESLint/Prettier、Git Hooks 等可选项。

#### 3.1 安装核心依赖

```bash
# 根据用户选择安装核心功能依赖（以下以 Vue 3 为例）
# 必需：路由/状态/HTTP（按参数选择）
# - 当 --state-mgmt=pinia 时安装 pinia
# - 当 --ui-lib=element-plus 时安装 element-plus 及图标

# 路由与 HTTP
npm install vue-router@4 axios

# 状态管理（可选）
# 当 --state-mgmt=pinia 时：
npm install pinia

# UI 组件库（可选）
# 当 --ui-lib=element-plus 时：
npm install element-plus @element-plus/icons-vue
```

#### 3.2 安装开发依赖

```bash
# TypeScript 相关
npm install -D typescript @types/node

# 构建工具插件（Vue 项目）
npm install -D unplugin-auto-import unplugin-vue-components

# 代码质量工具
npm install -D eslint prettier eslint-config-prettier eslint-plugin-prettier
npm install -D eslint-plugin-vue @vue/eslint-config-typescript
npm install -D @typescript-eslint/eslint-plugin @typescript-eslint/parser

# CSS 预处理器（如果需要）
npm install -D sass

# Git Hooks（可选）
npm install -D husky lint-staged @commitlint/cli @commitlint/config-conventional
```

#### 3.3 配置 Git Hooks（可选）

```bash
npx husky install
npx husky add .husky/pre-commit "npx lint-staged"
npx husky add .husky/commit-msg "npx --no -- commitlint --edit $1"
```

**检查点**：
- ✅ 所有依赖安装成功
- ✅ package.json 包含正确的依赖列表
- ✅ Git Hooks 已配置（如果需要）

#### 3.4 最简模式说明（当 --minimal）

- 保留：框架与构建工具核心（Vue/React/Next 等基础包、Vite 或框架内建工具、TypeScript）。
- 跳过：UI 组件库、按需自动导入插件、ESLint/Prettier、Git Hooks、示例性 Axios 拦截器与多余演示模块。
- 生成：最小的 `vite.config.ts`、基础入口与示例页面，确保开箱即跑。

---

### 阶段4：配置文件生成（自动执行）

**目标**：生成所有必要的配置文件

#### 4.1 构建工具配置

**vite.config.ts**（Vue 3 + Vite 示例）
```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    // 当 --ui-lib=element-plus 时启用下列 Resolver；否则删除 resolvers 字段或整段插件
    AutoImport({
      resolvers: [ElementPlusResolver()],
      imports: ['vue', 'vue-router', 'pinia'],
      dts: 'src/types/auto-imports.d.ts',
    }),
    Components({
      resolvers: [ElementPlusResolver()],
      dts: 'src/types/components.d.ts',
    }),
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 3000,
    open: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
```

#### 4.2 TypeScript 配置

**tsconfig.json**
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "module": "ESNext",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,

    /* Bundler mode */
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "preserve",

    /* Linting */
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,

    /* Path Alias */
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["src/**/*.ts", "src/**/*.d.ts", "src/**/*.tsx", "src/**/*.vue"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

**tsconfig.node.json**
```json
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
```

#### 4.3 代码质量配置

**.eslintrc.cjs**
```javascript
module.exports = {
  root: true,
  env: {
    browser: true,
    es2021: true,
    node: true,
  },
  extends: [
    'eslint:recommended',
    'plugin:vue/vue3-recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:prettier/recommended',
  ],
  parser: 'vue-eslint-parser',
  parserOptions: {
    ecmaVersion: 'latest',
    parser: '@typescript-eslint/parser',
    sourceType: 'module',
  },
  plugins: ['vue', '@typescript-eslint', 'prettier'],
  rules: {
    'vue/multi-word-component-names': 'off',
    '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
    '@typescript-eslint/no-explicit-any': 'warn',
    'prettier/prettier': 'error',
  },
}
```

#### **.prettierrc.json**
```json
{
  "semi": false,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 100,
  "arrowParens": "always",
  "endOfLine": "auto"
}
```

#### **.eslintignore**
```
node_modules
dist
*.d.ts
```

#### **.prettierignore**
```
node_modules
dist
*.d.ts
```

#### 4.4 环境变量配置

**.env.development**
```
VITE_API_BASE_URL=http://localhost:8080/api
VITE_APP_TITLE=My App
```

**.env.production**
```
VITE_API_BASE_URL=https://api.production.com
VITE_APP_TITLE=My App
```

#### 4.5 Git Hooks 配置（可选）

**package.json** 添加 lint-staged 配置：
```json
{
  "lint-staged": {
    "*.{js,jsx,ts,tsx,vue}": [
      "eslint --fix",
      "prettier --write"
    ],
    "*.{css,scss,less,html,md}": [
      "prettier --write"
    ]
  }
}
```

**commitlint.config.js**
```javascript
module.exports = {
  extends: ['@commitlint/config-conventional']
}
```

**检查点**：
- ✅ 所有配置文件已生成
- ✅ 配置文件语法正确
- ✅ 配置项符合项目需求

---

### 阶段5：项目结构搭建（自动执行）

**目标**：创建标准化的目录结构和核心模块

#### 5.1 创建目录结构

**Vue 3 项目标准结构**：
```
src/
├── api/                    # API 请求模块
│   ├── index.ts           # Axios 实例配置
│   └── modules/           # 按功能划分的 API 模块
│       └── user.ts
├── assets/                # Static resources
│   ├── images/
│   └── styles/
│       └── index.scss
├── components/            # Reusable components
│   └── HelloWorld.vue
├── composables/           # Composition functions
│   └── useRequest.ts
├── layouts/               # Layout components
│   └── DefaultLayout.vue
├── router/                # Router configuration
│   └── index.ts
├── stores/                # Pinia stores
│   ├── index.ts
│   └── modules/
│       └── user.ts
├── types/                 # TypeScript types
│   ├── api.d.ts
│   ├── auto-imports.d.ts
│   └── components.d.ts
├── utils/                 # Utility functions
│   ├── request.ts
│   └── storage.ts
├── views/                 # Page components
│   ├── Home.vue
│   └── About.vue
├── App.vue
├── main.ts
└── vite-env.d.ts
```

**检查点**：
- ✅ 所有目录已创建
- ✅ 目录结构清晰合理
- ✅ 符合框架约定

---

### 阶段6：核心模块实现（自动执行）

**目标**：生成核心功能模块的示例代码

#### 6.1 应用入口

**src/main.ts**
```typescript
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import pinia from '@/stores'
// 若未选择 Element Plus，请移除以下两行
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import '@/assets/styles/index.scss'

const app = createApp(App)

app.use(router)
app.use(pinia)
// 若未选择 Element Plus，请移除此行
app.use(ElementPlus)

app.mount('#app')
```

#### 6.2 路由配置

**src/router/index.ts**
```typescript
import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: {
      title: 'Home',
    },
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('@/views/About.vue'),
    meta: {
      title: 'About',
    },
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// Navigation guard
router.beforeEach((to, from, next) => {
  document.title = (to.meta.title as string) || 'Vue App'
  next()
})

export default router
```

#### 6.3 状态管理

**src/stores/index.ts**
```typescript
import { createPinia } from 'pinia'

const pinia = createPinia()

export default pinia
```

#### **src/stores/modules/user.ts**
```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

interface UserInfo {
  id: number
  name: string
  email: string
}

export const useUserStore = defineStore('user', () => {
  const userInfo = ref<UserInfo | null>(null)
  const token = ref<string>('')

  const isLoggedIn = computed(() => !!token.value)

  const setUserInfo = (info: UserInfo) => {
    userInfo.value = info
  }

  const setToken = (newToken: string) => {
    token.value = newToken
  }

  const logout = () => {
    userInfo.value = null
    token.value = ''
  }

  return {
    userInfo,
    token,
    isLoggedIn,
    setUserInfo,
    setToken,
    logout,
  }
})
```

#### 6.4 HTTP 请求封装

**src/utils/request.ts**
```typescript
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'

const service: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
service.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor
service.interceptors.response.use(
  (response: AxiosResponse) => {
    const { code, data, message } = response.data

    if (code === 200) {
      return data
    } else {
      ElMessage.error(message || 'Request failed')
      return Promise.reject(new Error(message || 'Error'))
    }
  },
  (error) => {
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 401:
          ElMessage.error('Unauthorized, please login')
          break
        case 403:
          ElMessage.error('Access denied')
          break
        case 404:
          ElMessage.error('Resource not found')
          break
        case 500:
          ElMessage.error('Server error')
          break
        default:
          ElMessage.error(data.message || 'Request failed')
      }
    } else {
      ElMessage.error('Network error')
    }
    
    return Promise.reject(error)
  }
)

export default service
```

#### 6.5 API 模块示例

**src/api/modules/user.ts**
```typescript
import request from '@/utils/request'

export interface LoginParams {
  username: string
  password: string
}

export interface UserInfo {
  id: number
  name: string
  email: string
}

export const userApi = {
  login(data: LoginParams) {
    return request({
      url: '/auth/login',
      method: 'post',
      data,
    })
  },

  getUserInfo() {
    return request<UserInfo>({
      url: '/user/info',
      method: 'get',
    })
  },

  logout() {
    return request({
      url: '/auth/logout',
      method: 'post',
    })
  },
}
```

#### 6.6 TypeScript 类型定义

**src/types/api.d.ts**
```typescript
export interface ApiResponse<T = any> {
  code: number
  data: T
  message: string
}

export interface PageParams {
  page: number
  pageSize: number
}

export interface PageResult<T> {
  list: T[]
  total: number
  page: number
  pageSize: number
}
```

#### 6.7 示例页面组件

**src/views/Home.vue**
```vue
<template>
  <div class="home">
    <h1>{{ title }}</h1>
    <el-button type="primary" @click="handleClick">Click Me</el-button>
    <p>Count: {{ count }}</p>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const title = ref('Welcome to Vue 3 + TypeScript + Vite')
const count = ref(0)

const handleClick = () => {
  count.value++
  ElMessage.success('Button clicked!')
}
</script>

<style scoped lang="scss">
.home {
  padding: 20px;
  text-align: center;

  h1 {
    color: #42b983;
  }
}
</style>
```

#### 6.8 根组件

**src/App.vue**
```vue
<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup lang="ts">
// App logic here
</script>

<style lang="scss">
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style>
```

**检查点**：
- ✅ 所有核心模块已实现
- ✅ 代码符合 TypeScript 规范
- ✅ 示例代码可运行

---

### 阶段7：Package.json 配置（自动执行）

**目标**：配置 npm 脚本和项目元信息

在 `package.json` 中添加/更新以下内容：
```json
{
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext .vue,.js,.jsx,.cjs,.mjs,.ts,.tsx,.cts,.mts --fix",
    "format": "prettier --write ."
  }
}
```

**检查点**：
- ✅ 所有必要的脚本已配置
- ✅ 项目元信息完整
- ✅ 脚本可正常执行

---

### 阶段8：验证测试（自动执行）

**目标**：确保项目可以正常启动和构建

#### 8.1 依赖安装验证

```bash
# 检查依赖是否正确安装
npm list --depth=0

# 检查是否有依赖冲突
npm audit
```

#### 8.2 TypeScript 类型检查

```bash
npx vue-tsc --noEmit
```

**预期结果**：
- ✅ 无类型错误
- ✅ 路径别名正常工作

#### 8.3 代码检查

```bash
npm run lint
```

**预期结果**：
- ✅ 无 ESLint 错误
- ✅ 代码风格一致

#### 8.4 开发服务器启动

```bash
npm run dev
```

**预期结果**：
- ✅ 开发服务器成功启动
- ✅ 可在浏览器中访问
- ✅ 热更新正常工作

#### 8.5 生产构建测试

```bash
npm run build
```

**预期结果**：
- ✅ 构建成功完成
- ✅ dist 目录生成
- ✅ 无警告或错误

**质量门禁**：
```typescript
interface ValidationChecks {
  dependencies_installed: boolean;    // 必须: true
  typescript_check: boolean;          // 必须: true
  lint_check: boolean;                // 必须: true
  dev_server_start: boolean;          // 必须: true
  build_success: boolean;             // 必须: true
}

// 如果任何检查失败，报告详细错误并提供修复建议
```

---

### 阶段9：文档生成（自动执行）

**目标**：生成项目文档和使用说明

#### 9.1 生成 README.md

```markdown
# ${PROJECT_NAME}

## 项目简介

基于 Vue 3 + Vite + TypeScript 的现代化前端项目。

## 技术栈

- **Vue 3** - 渐进式 JavaScript 框架
- **Vite** - 下一代前端构建工具
- **TypeScript** - JavaScript 的超集
- **Vue Router** - 官方路由管理器
- **Pinia** - Vue 状态管理库
- **Element Plus** - Vue 3 组件库
- **Axios** - HTTP 客户端
- **ESLint + Prettier** - 代码质量和格式化

## 快速开始

### 安装依赖
\`\`\`bash
npm install
\`\`\`

### 开发模式
\`\`\`bash
npm run dev
\`\`\`

### 生产构建
\`\`\`bash
npm run build
\`\`\`

### 代码检查
\`\`\`bash
npm run lint
\`\`\`

### 代码格式化
\`\`\`bash
npm run format
\`\`\`

## 项目结构

\`\`\`
src/
├── api/          # API 请求模块
├── assets/       # 静态资源
├── components/   # 可复用组件
├── composables/  # 组合式函数
├── layouts/      # 布局组件
├── router/       # 路由配置
├── stores/       # 状态管理
├── types/        # TypeScript 类型
├── utils/        # 工具函数
├── views/        # 页面组件
├── App.vue       # 根组件
└── main.ts       # 应用入口
\`\`\`

## 开发规范

- 使用 Composition API + `<script setup>`
- 遵循 ESLint 和 Prettier 配置
- 使用 TypeScript 进行类型检查
- 组件名使用 PascalCase
- 文件名使用 kebab-case
```

#### 9.2 生成 .claude/project-info.md

记录项目脚手架的详细信息，供后续开发参考：
- 技术栈版本
- 已安装的依赖包
- 配置说明
- 开发建议

**检查点**：
- ✅ README.md 已生成
- ✅ 文档内容完整
- ✅ 包含使用说明

---

## 输出总结

完成所有阶段后，输出以下信息：

```
✅ 项目脚手架生成成功！

📦 项目信息：
- 名称：${PROJECT_NAME}
- 类型：${PROJECT_TYPE}
- 位置：${PROJECT_PATH}

🛠️ 技术栈：
- ${TECH_STACK_LIST}

📝 后续步骤：
1. cd ${PROJECT_NAME}
2. npm install (如果未自动安装)
3. npm run dev

📚 文档：
- README.md - 项目说明
- .claude/project-info.md - 项目详细信息

⚠️  注意事项：
- 请根据实际 API 地址修改环境变量文件
- 建议配置 Git Hooks 提升代码质量
```

## 质量标准

### 必须满足
- ✅ TypeScript strict 模式启用
- ✅ 路径别名（@）正常工作
- ✅ ESLint + Prettier 配置正确
- ✅ 开发服务器可正常启动
- ✅ 生产构建成功无错误
- ✅ 所有配置文件语法正确
- ✅ 核心模块示例代码可运行

### 推荐满足
- ✅ 自动导入 Vue/Router/Pinia API
- ✅ UI 组件库按需导入
- ✅ Axios 拦截器配置完整
- ✅ 路由导航守卫示例
- ✅ Git Hooks 配置
- ✅ 环境变量配置
- ✅ 代理服务器配置

## 错误处理

如果在任何阶段遇到错误：
1. 立即停止流程
2. 输出详细错误信息
3. 提供具体的修复建议
4. 询问用户是否继续

## 扩展说明

### 支持的项目类型

- `vue3-vite-ts` - Vue 3 + Vite + TypeScript
- `react-vite-ts` - React + Vite + TypeScript
- `next-ts` - Next.js + TypeScript
- `node-express-ts` - Node.js + Express + TypeScript
- `python-fastapi` - Python + FastAPI
- `spring-boot` - Spring Boot + Java

### 自定义配置

用户可以通过参数自定义：
- UI 组件库选择
- 状态管理方案
- CSS 预处理器
- 是否包含 Git Hooks
- 是否包含测试框架

---

**最后提醒**：生成的脚手架是生产级的起点，应根据具体项目需求进行调整和扩展。
