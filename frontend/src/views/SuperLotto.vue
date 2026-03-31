<template>
  <div class="super-lotto">
    <el-page-header @back="$router.push('/')" content="威力彩資料查詢" />
    
    <el-row :gutter="20" class="main-content">
      <el-col :span="24">
        <el-card class="data-card" shadow="always">
          <template #header>
            <div class="card-header">
              <span>🎰 威力彩歷史資料</span>
              <div class="header-controls">
                <el-date-picker
                  v-model="selectedDate"
                  type="month"
                  placeholder="選擇年月"
                  format="YYYY-MM"
                  value-format="YYYY-MM"
                  @change="fetchData"
                />
                <el-button 
                  type="primary" 
                  @click="fetchData" 
                  :loading="loading"
                >
                  查詢
                </el-button>
              </div>
            </div>
          </template>

          <!-- 載入中 -->
          <div v-if="loading" class="loading-section">
            <el-skeleton :rows="8" animated />
          </div>

          <!-- 資料表格 -->
          <div v-else-if="lotteryData.length > 0" class="data-section">
            <el-table :data="paginatedData" stripe style="width: 100%">
              <el-table-column prop="期別" label="期別" width="100" />
              <el-table-column prop="開獎日期" label="開獎日期" width="120">
                <template #default="scope">
                  {{ formatDate(scope.row.開獎日期) }}
                </template>
              </el-table-column>
              <el-table-column label="第一區號碼" min-width="200">
                <template #default="scope">
                  <div class="number-group">
                    <el-tag
                      v-for="num in scope.row.第一區"
                      :key="num"
                      class="number-tag main-number"
                      size="large"
                    >
                      {{ num }}
                    </el-tag>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="第二區" width="80">
                <template #default="scope">
                  <el-tag class="number-tag special-number" size="large" type="danger">
                    {{ scope.row.第二區 }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>

            <!-- 分頁 -->
            <div class="pagination-wrapper">
              <el-pagination
                v-model:current-page="currentPage"
                :page-size="pageSize"
                :total="lotteryData.length"
                layout="prev, pager, next, jumper"
                @current-change="handlePageChange"
              />
            </div>
          </div>

          <!-- 無資料狀態 -->
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
            <el-empty description="請選擇年月並點擊查詢按鈕">
              <template #image>
                <el-icon size="100" color="#409EFF">
                  <Calendar />
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
import { useLotteryFetch } from '../composables/useLotteryFetch'
import { formatDate } from '../utils/dateFormat'

export default {
  name: 'SuperLotto',
  setup() {
    // [原始] const loading = ref(false)
    // [原始] const lotteryData = ref([])
    // [原始] const error = ref('')
    // [原始] const currentPage = ref(1)
    // [原始] const pageSize = 10
    const selectedDate = ref('')

    // 使用 composable 共用 loading、error、currentPage、pageSize、paginatedData、fetchData
    const { data: lotteryData, loading, error, currentPage, pageSize, paginatedData, fetchData: _fetchData, handlePageChange } = useLotteryFetch('/api/super_lotto')

    // [原始] const paginatedData = computed(() => {
    // [原始]   const start = (currentPage.value - 1) * pageSize
    // [原始]   const end = start + pageSize
    // [原始]   return lotteryData.value.slice(start, end)
    // [原始] })

    // [原始] const fetchData = async () => {
    // [原始]   if (!selectedDate.value) {
    // [原始]     ElMessage.warning('請先選擇年月')
    // [原始]     return
    // [原始]   }
    // [原始]   loading.value = true
    // [原始]   error.value = ''
    // [原始]   lotteryData.value = []
    // [原始]   try {
    // [原始]     const [year, month] = selectedDate.value.split('-')
    // [原始]     const response = await axios.get('/api/super_lotto', {
    // [原始]       params: { year, month }
    // [原始]     })
    // [原始]     lotteryData.value = response.data
    // [原始]     currentPage.value = 1
    // [原始]     ElMessage.success(`成功載入 ${response.data.length} 筆資料`)
    // [原始]   } catch (err) {
    // [原始]     error.value = err.response?.data?.detail || err.message || '網路連接失敗'
    // [原始]     ElMessage.error(error.value)
    // [原始]   } finally {
    // [原始]     loading.value = false
    // [原始]   }
    // [原始] }
    // fetchData 改由 useLotteryFetch composable 提供，此 wrapper 傳入 selectedDate
    const fetchData = () => _fetchData(selectedDate.value)

    // [原始] const handlePageChange = (page) => {
    // [原始]   currentPage.value = page
    // [原始] }
    // handlePageChange 改由 useLotteryFetch composable 提供

    // [原始] const formatDate = (dateString) => {
    // [原始]   return dateString.substring(0, 10)
    // [原始] }
    // formatDate 改由 utils/dateFormat.js 提供

    return {
      loading,
      lotteryData,
      paginatedData,
      error,
      selectedDate,
      currentPage,
      pageSize,
      fetchData,
      handlePageChange,
      formatDate
    }
  }
}
</script>

<style scoped>
.super-lotto {
  max-width: 1200px;
  margin: 0 auto;
}

.main-content {
  margin-top: 20px;
}

.data-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
  font-size: 18px;
}

.header-controls {
  display: flex;
  gap: 10px;
  align-items: center;
}

/* [原始] .loading-section { padding: 40px 20px; } */
/* .loading-section 已移至 lottery-common.css 共享 */

.data-section {
  padding: 20px 0;
}

/* [原始] .number-group, .number-tag, .main-number, .special-number, .pagination-wrapper, .error-section, .initial-section */
/* 以上樣式已移至 lottery-common.css 共享 */

@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }

  .header-controls {
    flex-direction: column;
    width: 100%;
  }

  .header-controls > * {
    width: 100%;
  }
}
</style>