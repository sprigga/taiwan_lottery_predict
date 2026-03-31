<template>
  <div class="history">
    <el-page-header @back="$router.push('/')" content="歷史資料查詢" />
    
    <el-row :gutter="20" class="main-content">
      <el-col :span="24">
        <el-card class="query-card" shadow="always">
          <template #header>
            <span>📊 彩券歷史資料查詢</span>
          </template>

          <!-- 查詢條件 -->
          <div class="query-form">
            <el-row :gutter="20">
              <el-col :xs="24" :sm="8">
                <el-select v-model="selectedLottery" placeholder="選擇彩券類型" style="width: 100%">
                  <el-option label="大樂透" value="lotto649" />
                  <el-option label="威力彩" value="super_lotto" />
                  <el-option label="今彩539" value="daily_cash" />
                </el-select>
              </el-col>
              <el-col :xs="24" :sm="8">
                <el-date-picker
                  v-model="selectedDate"
                  type="month"
                  placeholder="選擇年月"
                  format="YYYY-MM"
                  value-format="YYYY-MM"
                  style="width: 100%"
                />
              </el-col>
              <el-col :xs="24" :sm="8">
                <el-button 
                  type="primary" 
                  @click="fetchData" 
                  :loading="loading"
                  style="width: 100%"
                >
                  查詢資料
                </el-button>
              </el-col>
            </el-row>
          </div>

          <!-- 載入中 -->
          <div v-if="loading" class="loading-section">
            <el-skeleton :rows="6" animated />
            <p class="loading-text">正在載入歷史資料...</p>
          </div>

          <!-- 資料表格 -->
          <div v-else-if="historyData.length > 0" class="data-section">
            <!-- 統計資訊 -->
            <div class="statistics-bar">
              <el-row :gutter="20">
                <el-col :xs="12" :sm="6">
                  <el-statistic title="總筆數" :value="historyData.length" suffix="筆" />
                </el-col>
                <el-col :xs="12" :sm="6">
                  <el-statistic title="彩券類型" :value="getLotteryName(selectedLottery)" />
                </el-col>
                <el-col :xs="12" :sm="6">
                  <el-statistic title="查詢年月" :value="selectedDate" />
                </el-col>
                <el-col :xs="12" :sm="6">
                  <el-statistic title="最新期別" :value="historyData[0]?.期別 || '-'" />
                </el-col>
              </el-row>
            </div>

            <el-divider />

            <!-- 大樂透表格 -->
            <el-table 
              v-if="selectedLottery === 'lotto649'" 
              :data="paginatedData" 
              stripe 
              style="width: 100%"
            >
              <el-table-column prop="期別" label="期別" width="100" />
              <el-table-column prop="開獎日期" label="開獎日期" width="120">
                <template #default="scope">
                  {{ formatDate(scope.row.開獎日期) }}
                </template>
              </el-table-column>
              <el-table-column label="獎號" min-width="250">
                <template #default="scope">
                  <div class="number-group">
                    <el-tag
                      v-for="num in scope.row.獎號"
                      :key="num"
                      class="number-tag lotto-number"
                      size="large"
                    >
                      {{ num }}
                    </el-tag>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="特別號" width="80">
                <template #default="scope">
                  <el-tag class="number-tag special-number" size="large" type="danger">
                    {{ scope.row.特別號 }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>

            <!-- 威力彩表格 -->
            <el-table 
              v-else-if="selectedLottery === 'super_lotto'" 
              :data="paginatedData" 
              stripe 
              style="width: 100%"
            >
              <el-table-column prop="期別" label="期別" width="100" />
              <el-table-column prop="開獎日期" label="開獎日期" width="120">
                <template #default="scope">
                  {{ formatDate(scope.row.開獎日期) }}
                </template>
              </el-table-column>
              <el-table-column label="第一區" min-width="250">
                <template #default="scope">
                  <div class="number-group">
                    <el-tag
                      v-for="num in scope.row.第一區"
                      :key="num"
                      class="number-tag super-number"
                      size="large"
                    >
                      {{ num }}
                    </el-tag>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="第二區" width="80">
                <template #default="scope">
                  <el-tag class="number-tag power-number" size="large" type="warning">
                    {{ scope.row.第二區 }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>

            <!-- 今彩539表格 -->
            <el-table 
              v-else-if="selectedLottery === 'daily_cash'" 
              :data="paginatedData" 
              stripe 
              style="width: 100%"
            >
              <el-table-column prop="期別" label="期別" width="100" />
              <el-table-column prop="開獎日期" label="開獎日期" width="120">
                <template #default="scope">
                  {{ formatDate(scope.row.開獎日期) }}
                </template>
              </el-table-column>
              <el-table-column label="獎號" min-width="300">
                <template #default="scope">
                  <div class="number-group">
                    <el-tag
                      v-for="num in scope.row.獎號"
                      :key="num"
                      class="number-tag cash-number"
                      size="large"
                    >
                      {{ num }}
                    </el-tag>
                  </div>
                </template>
              </el-table-column>
            </el-table>

            <!-- 分頁 -->
            <div class="pagination-wrapper">
              <el-pagination
                v-model:current-page="currentPage"
                :page-size="pageSize"
                :total="historyData.length"
                layout="total, prev, pager, next, jumper"
                @current-change="handlePageChange"
              />
            </div>
          </div>

          <!-- 錯誤狀態 -->
          <div v-else-if="!loading && error" class="error-section">
            <el-alert
              title="查詢失敗"
              :description="error"
              type="error"
              show-icon
            />
          </div>

          <!-- 初始狀態 -->
          <div v-else class="initial-section">
            <el-empty description="請選擇彩券類型和年月，然後點擊查詢">
              <template #image>
                <el-icon size="100" color="#409EFF">
                  <DataAnalysis />
                </el-icon>
              </template>
            </el-empty>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { ref } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useLotteryFetch } from '../composables/useLotteryFetch'
import { formatDate } from '../utils/dateFormat'

export default {
  name: 'History',
  setup() {
    // [原始] const loading = ref(false)
    // [原始] const historyData = ref([])
    // [原始] const error = ref('')
    // [原始] const currentPage = ref(1)
    // [原始] const pageSize = 10
    // 使用 composable 共用 loading、error、currentPage、pageSize、paginatedData
    // 注意：保留原始 fetchData，因為它有動態 endpoint 邏輯（依據 selectedLottery 決定 API 路徑）
    const { data: historyData, loading, error, currentPage, pageSize, paginatedData, handlePageChange } = useLotteryFetch('')
    const selectedLottery = ref('')
    const selectedDate = ref('')

    // [原始] const paginatedData = computed(() => {
    // [原始]   const start = (currentPage.value - 1) * pageSize
    // [原始]   const end = start + pageSize
    // [原始]   return historyData.value.slice(start, end)
    // [原始] })

    const fetchData = async () => {
      if (!selectedLottery.value || !selectedDate.value) {
        ElMessage.warning('請選擇彩券類型和年月')
        return
      }

      loading.value = true
      error.value = ''
      historyData.value = []

      try {
        const [year, month] = selectedDate.value.split('-')
        const response = await axios.get(`/api/${selectedLottery.value}`, {
          params: { year, month }
        })
        
        historyData.value = response.data
        currentPage.value = 1
        ElMessage.success(`成功載入 ${response.data.length} 筆 ${getLotteryName(selectedLottery.value)} 資料`)
      } catch (err) {
        error.value = err.response?.data?.detail || err.message || '網路連接失敗'
        ElMessage.error(error.value)
      } finally {
        loading.value = false
      }
    }

    // [原始] const handlePageChange = (page) => {
    // [原始]   currentPage.value = page
    // [原始] }
    // handlePageChange 改由 useLotteryFetch composable 提供

    // [原始] const formatDate = (dateString) => {
    // [原始]   return dateString.substring(0, 10)
    // [原始] }
    // formatDate 改由 utils/dateFormat.js 提供

    const getLotteryName = (type) => {
      const names = {
        'lotto649': '大樂透',
        'super_lotto': '威力彩',
        'daily_cash': '今彩539'
      }
      return names[type] || type
    }

    return {
      loading,
      historyData,
      paginatedData,
      error,
      selectedLottery,
      selectedDate,
      currentPage,
      pageSize,
      fetchData,
      handlePageChange,
      formatDate,
      getLotteryName
    }
  }
}
</script>

<style scoped>
.history {
  max-width: 1200px;
  margin: 0 auto;
}

.main-content {
  margin-top: 20px;
}

.query-card {
  margin-bottom: 20px;
}

.query-form {
  padding: 20px 0;
}

/* [原始] .loading-section { text-align: center; padding: 40px 20px; } */
/* .loading-section 已移至 lottery-common.css 共享 */

.loading-text {
  margin-top: 20px;
  color: #666;
  font-size: 16px;
}

.data-section {
  margin-top: 30px;
}

.statistics-bar {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

/* [原始] .number-group, .number-tag, .lotto-number, .super-number, .cash-number, .special-number, .power-number, .pagination-wrapper, .error-section, .initial-section */
/* 以上樣式已移至 lottery-common.css 共享 */

@media (max-width: 768px) {
  .query-form .el-col {
    margin-bottom: 10px;
  }

  .statistics-bar .el-col {
    margin-bottom: 10px;
  }
}
</style>