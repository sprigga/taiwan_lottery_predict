<template>
  <div id="app">
    <el-container class="layout-container">
      <!-- 頂部導航 -->
      <el-header class="header">
        <div class="header-content">
          <div class="logo">
            <h1>🎰 台灣彩券 AI 選號系統</h1>
          </div>
          <el-menu
            mode="horizontal"
            :default-active="$route.path"
            class="navigation"
            router
          >
            <el-menu-item index="/">首頁</el-menu-item>
            <el-menu-item index="/lotto649">大樂透</el-menu-item>
            <el-menu-item index="/super-lotto">威力彩</el-menu-item>
            <el-menu-item index="/history">歷史資料</el-menu-item>
          </el-menu>
        </div>
      </el-header>

      <!-- 主要內容 -->
      <el-main class="main-content">
        <router-view />
      </el-main>

      <!-- 底部 -->
      <el-footer class="footer">
        <p>&copy; 2025 台灣彩券 AI 選號系統 | 僅供娛樂參考，投注請謹慎</p>
      </el-footer>
    </el-container>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style scoped>
.layout-container {
  min-height: 100vh;
}

.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  height: 100%;
}

.logo h1 {
  margin: 0;
  font-size: 24px;
  font-weight: bold;
}

.navigation {
  background: transparent;
  border-bottom: none;
}

.navigation .el-menu-item {
  color: white;
  border-bottom: 2px solid transparent;
}

.navigation .el-menu-item:hover,
.navigation .el-menu-item.is-active {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border-bottom-color: white;
}

.main-content {
  background: #f8f9fa;
  min-height: calc(100vh - 120px);
  padding: 20px;
}

.footer {
  background: #333;
  color: white;
  text-align: center;
  padding: 20px;
}

.footer p {
  margin: 0;
}

/* 全域樣式 */
:global(body) {
  margin: 0;
  padding: 0;
  font-family: 'Helvetica Neue', Arial, sans-serif;
}
</style>