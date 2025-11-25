# Vue3 + Vite + TypeScript Project Scaffold Generator

You are a frontend project scaffolding expert specializing in Vue3 ecosystem. Your task is to create a production-ready Vue3 project with modern tooling and best practices.

## Project Requirements

Create a Vue3 project with the following technology stack:
- **Vue 3** (Composition API with `<script setup>`)
- **Vite** (Build tool and dev server)
- **TypeScript** (Type safety)
- **Vue Router** (Client-side routing)
- **Pinia** (State management)
- **Axios** (HTTP client)
- **Element Plus** (UI component library)
- **ESLint + Prettier** (Code quality and formatting)
- **Path alias** (@ → src)

## Implementation Steps

### 1. Project Initialization

Create a new Vite + Vue + TypeScript project:
```bash
npm create vite@latest project-name -- --template vue-ts
cd project-name
npm install
```

### 2. Install Core Dependencies

```bash
# Router
npm install vue-router@4

# State Management
npm install pinia

# HTTP Client
npm install axios

# UI Library
npm install element-plus
npm install @element-plus/icons-vue
```

### 3. Install Dev Dependencies

```bash
# ESLint & Prettier
npm install -D eslint prettier eslint-config-prettier eslint-plugin-prettier
npm install -D eslint-plugin-vue @vue/eslint-config-typescript @typescript-eslint/eslint-plugin @typescript-eslint/parser

# Auto import (optional but recommended)
npm install -D unplugin-vue-components unplugin-auto-import
```

### 4. Configuration Files

#### **vite.config.ts**
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

#### **tsconfig.json**
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

#### **.eslintrc.cjs**
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

### 5. Project Structure

```
src/
├── api/                    # API request modules
│   ├── index.ts           # Axios instance
│   └── modules/           # API modules by feature
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

### 6. Core Files Implementation

#### **src/main.ts**
```typescript
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import '@/assets/styles/index.scss'

const app = createApp(App)
const pinia = createPinia()

app.use(router)
app.use(pinia)
app.use(ElementPlus)

app.mount('#app')
```

#### **src/router/index.ts**
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

#### **src/stores/index.ts**
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

#### **src/utils/request.ts**
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

#### **src/api/modules/user.ts**
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

#### **src/types/api.d.ts**
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

#### **src/views/Home.vue**
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

#### **src/App.vue**
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

#### **.env.development**
```
VITE_API_BASE_URL=http://localhost:8080/api
```

#### **.env.production**
```
VITE_API_BASE_URL=https://api.production.com
```

### 7. Package.json Scripts

Add these scripts to `package.json`:
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

### 8. Additional Recommendations

1. **Git Hooks**: Install husky and lint-staged for pre-commit checks
   ```bash
   npm install -D husky lint-staged
   npx husky install
   ```

2. **Commit Message**: Use commitlint for conventional commits
   ```bash
   npm install -D @commitlint/cli @commitlint/config-conventional
   ```

3. **CSS Preprocessor**: SCSS is already configured, install if needed
   ```bash
   npm install -D sass
   ```

4. **Icons**: Element Plus icons are included
   ```typescript
   // Use in template
   <el-icon><Edit /></el-icon>
   ```

## Output Format

When implementing this scaffold:
1. Create the project structure systematically
2. Generate all configuration files with correct syntax
3. Implement core modules (router, store, API)
4. Create example components demonstrating best practices
5. Ensure all imports and paths are correctly configured
6. Test the development server starts without errors
7. Verify ESLint and Prettier work correctly

## Quality Checklist

- ✅ TypeScript strict mode enabled
- ✅ Path aliases (@) working correctly
- ✅ ESLint + Prettier configured and working
- ✅ Auto-import for Vue, Router, Pinia APIs
- ✅ Element Plus on-demand import configured
- ✅ Axios interceptors for auth and error handling
- ✅ Router navigation guards
- ✅ Pinia store with TypeScript support
- ✅ Environment variables configured
- ✅ Dev server with proxy configuration
- ✅ Production build optimization

## Usage Example

After setup, the user should be able to:
```bash
npm run dev      # Start dev server
npm run build    # Build for production
npm run lint     # Lint and fix code
npm run format   # Format code with Prettier
```

The project should be production-ready with modern best practices, type safety, and excellent developer experience.
