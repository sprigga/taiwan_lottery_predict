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
import { ref, computed } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

export default {
  name: 'SuperLotto',
  setup() {
    const loading = ref(false)
    const lotteryData = ref([])
    const error = ref('')
    const selectedDate = ref('')
    const currentPage = ref(1)
    const pageSize = 10

    const paginatedData = computed(() => {
      const start = (currentPage.value - 1) * pageSize
      const end = start + pageSize
      return lotteryData.value.slice(start, end)
    })

    const fetchData = async () => {
      if (!selectedDate.value) {
        ElMessage.warning('請先選擇年月')
        return
      }

      loading.value = true
      error.value = ''
      lotteryData.value = []

      try {
        const [year, month] = selectedDate.value.split('-')
        const response = await axios.get('/api/super_lotto', {
          params: { year, month }
        })
        
        lotteryData.value = response.data
        currentPage.value = 1
        ElMessage.success(`成功載入 ${response.data.length} 筆資料`)
      } catch (err) {
        error.value = err.response?.data?.detail || err.message || '網路連接失敗'
        ElMessage.error(error.value)
      } finally {
        loading.value = false
      }
    }

    const handlePageChange = (page) => {
      currentPage.value = page
    }

    const formatDate = (dateString) => {
      return dateString.substring(0, 10)
    }

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

.loading-section {
  padding: 40px 20px;
}

.data-section {
  padding: 20px 0;
}

.number-group {
  display: flex;
  gap: 5px;
  flex-wrap: wrap;
}

.number-tag {
  font-weight: bold;
  font-size: 14px;
  min-width: 35px;
  text-align: center;
}

.main-number {
  background: linear-gradient(135deg, #409EFF, #1890ff);
  color: white;
  border: none;
}

.special-number {
  background: linear-gradient(135deg, #F56C6C, #ff4757);
  color: white;
  border: none;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.error-section,
.initial-section {
  padding: 40px 20px;
  text-align: center;
}

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