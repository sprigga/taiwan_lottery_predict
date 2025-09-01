<template>
  <div class="lotto649">
    <el-page-header @back="$router.push('/')" content="大樂透 AI 選號" />
    
    <el-row :gutter="20" class="main-content">
      <el-col :span="24">
        <div class="prediction-section">
          <el-card class="prediction-card" shadow="always">
            <template #header>
              <div class="card-header">
                <span>🎯 AI 智能推薦號碼</span>
                <el-button 
                  type="primary" 
                  @click="getPrediction" 
                  :loading="loading"
                  :disabled="loading"
                >
                  {{ loading ? '分析中...' : '獲取推薦' }}
                </el-button>
              </div>
            </template>

            <!-- 載入中狀態 -->
            <div v-if="loading" class="loading-section">
              <el-skeleton :rows="5" animated />
              <p class="loading-text">正在使用 AI 分析半年歷史資料，請稍候...</p>
            </div>

            <!-- 推薦結果 -->
            <div v-else-if="prediction" class="prediction-result">
              <!-- 推薦號碼組合 -->
              <div v-if="prediction.recommended_sets" class="recommended-sets">
                <h3>🎯 推薦號碼</h3>
                <el-row :gutter="20">
                  <el-col 
                    v-for="(set, index) in prediction.recommended_sets" 
                    :key="index"
                    :xs="24" 
                    :md="12"
                  >
                    <el-card class="number-set-card" shadow="hover">
                      <template #header>
                        <span>第{{ index + 1 }}組推薦 - {{ set.type }}</span>
                      </template>
                      <div class="number-display">
                        <div class="regular-numbers">
                          <el-tag 
                            v-for="num in set.regular_numbers" 
                            :key="`set${index}-${num}`"
                            class="number-tag regular-big" 
                            size="large"
                          >
                            {{ num }}
                          </el-tag>
                        </div>
                        <div class="special-section">
                          <span class="plus-sign">+</span>
                          <el-tag 
                            class="number-tag special-big" 
                            size="large"
                          >
                            {{ set.special_number }}
                          </el-tag>
                        </div>
                      </div>
                      <div class="set-reason">
                        <p>{{ set.reason }}</p>
                      </div>
                    </el-card>
                  </el-col>
                </el-row>
              </div>

              <el-divider />

              <!-- AI 推薦內容 -->
              <div class="ai-prediction">
                <h3>🤖 AI 分析結果</h3>
                <div class="prediction-text">
                  <pre>{{ prediction.ai_prediction }}</pre>
                </div>
              </div>

              <!-- 統計資料 -->
              <el-divider />
              <div v-if="prediction.data" class="statistics">
                <h3>📊 資料統計</h3>
                <el-row :gutter="20">
                  <el-col :xs="24" :sm="12" :md="6">
                    <el-statistic 
                      title="分析期數" 
                      :value="prediction.data.total_periods"
                      suffix="期"
                    />
                  </el-col>
                  <el-col :xs="24" :sm="12" :md="6">
                    <el-statistic 
                      title="最新期別" 
                      :value="prediction.data.latest_period"
                    />
                  </el-col>
                  <el-col :xs="24" :sm="12" :md="6">
                    <el-statistic 
                      title="資料起始" 
                      :value="prediction.data.date_range.start"
                    />
                  </el-col>
                  <el-col :xs="24" :sm="12" :md="6">
                    <el-statistic 
                      title="資料結束" 
                      :value="prediction.data.date_range.end"
                    />
                  </el-col>
                </el-row>
              </div>

              <!-- 頻率分析 -->
              <el-divider />
              <div v-if="prediction.data?.frequency_analysis" class="frequency-analysis">
                <h3>🔥 號碼頻率分析</h3>
                <el-row :gutter="20">
                  <el-col :xs="24" :md="12">
                    <el-card class="analysis-card hot-numbers">
                      <template #header>
                        <span>🔥 熱門號碼 (前10名)</span>
                      </template>
                      <div class="number-list">
                        <div 
                          v-for="[num, freq] in prediction.data.frequency_analysis.hot_numbers" 
                          :key="`hot-${num}`"
                          class="number-item hot"
                        >
                          <span class="number">{{ num }}</span>
                          <span class="frequency">{{ freq }}次</span>
                        </div>
                      </div>
                    </el-card>
                  </el-col>
                  <el-col :xs="24" :md="12">
                    <el-card class="analysis-card cold-numbers">
                      <template #header>
                        <span>❄️ 冷門號碼 (後10名)</span>
                      </template>
                      <div class="number-list">
                        <div 
                          v-for="[num, freq] in prediction.data.frequency_analysis.cold_numbers" 
                          :key="`cold-${num}`"
                          class="number-item cold"
                        >
                          <span class="number">{{ num }}</span>
                          <span class="frequency">{{ freq }}次</span>
                        </div>
                      </div>
                    </el-card>
                  </el-col>
                </el-row>
              </div>
            </div>

            <!-- 錯誤狀態 -->
            <div v-else-if="error" class="error-section">
              <el-alert
                title="獲取預測失敗"
                :description="error"
                type="error"
                show-icon
              />
            </div>

            <!-- 初始狀態 -->
            <div v-else class="initial-section">
              <el-empty description="點擊上方按鈕開始 AI 分析">
                <template #image>
                  <el-icon size="100" color="#409EFF">
                    <TrendCharts />
                  </el-icon>
                </template>
              </el-empty>
            </div>
          </el-card>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { ref } from 'vue'
import axios from 'axios'
import { TrendCharts } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

export default {
  name: 'Lotto649',
  components: {
    TrendCharts
  },
  setup() {
    const loading = ref(false)
    const prediction = ref(null)
    const error = ref('')

    const getPrediction = async () => {
      loading.value = true
      error.value = ''
      prediction.value = null

      try {
        const response = await axios.get('http://localhost:8000/api/lotto649/predict')
        if (response.data.status === 'success') {
          prediction.value = response.data
          ElMessage.success('AI 分析完成！')
        } else {
          error.value = response.data.error || '獲取預測失敗'
          ElMessage.error(error.value)
        }
      } catch (err) {
        error.value = err.response?.data?.detail || err.message || '網路連接失敗'
        ElMessage.error(error.value)
      } finally {
        loading.value = false
      }
    }

    return {
      loading,
      prediction,
      error,
      getPrediction
    }
  }
}
</script>

<style scoped>
.lotto649 {
  max-width: 1200px;
  margin: 0 auto;
}

.main-content {
  margin-top: 20px;
}

.prediction-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
  font-size: 18px;
}

/* 推薦號碼卡片樣式 */
.recommended-sets h3 {
  color: #409EFF;
  margin-bottom: 20px;
}

.number-set-card {
  margin-bottom: 20px;
  height: 100%;
}

.number-display {
  text-align: center;
  margin-bottom: 15px;
}

.regular-numbers {
  display: flex;
  gap: 8px;
  justify-content: center;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.special-section {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.plus-sign {
  font-size: 20px;
  font-weight: bold;
  color: #666;
}

.number-tag.regular-big {
  background: linear-gradient(135deg, #409EFF, #1890ff);
  color: white;
  border: none;
  font-weight: bold;
  font-size: 16px;
  min-width: 45px;
  height: 45px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.number-tag.special-big {
  background: linear-gradient(135deg, #F56C6C, #ff4757);
  color: white;
  border: none;
  font-weight: bold;
  font-size: 16px;
  min-width: 45px;
  height: 45px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.set-reason {
  background: #f8f9fa;
  border-radius: 6px;
  padding: 12px;
}

.set-reason p {
  margin: 0;
  font-size: 14px;
  line-height: 1.5;
  color: #666;
}

.loading-section {
  text-align: center;
  padding: 40px 20px;
}

.loading-text {
  margin-top: 20px;
  color: #666;
  font-size: 16px;
}

.prediction-result {
  padding: 20px 0;
}

.ai-prediction h3 {
  color: #409EFF;
  margin-bottom: 15px;
}

.prediction-text {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 20px;
  font-family: monospace;
}

.prediction-text pre {
  white-space: pre-wrap;
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
}

.statistics h3 {
  color: #67C23A;
  margin-bottom: 20px;
}

.frequency-analysis h3 {
  color: #E6A23C;
  margin-bottom: 20px;
}

.analysis-card {
  height: 100%;
}

.number-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 10px;
}

.number-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  border-radius: 6px;
  font-weight: bold;
}

.number-item.hot {
  background: linear-gradient(135deg, #ff6b6b, #ee5a52);
  color: white;
}

.number-item.cold {
  background: linear-gradient(135deg, #74b9ff, #0984e3);
  color: white;
}

.number {
  font-size: 16px;
}

.frequency {
  font-size: 12px;
  opacity: 0.9;
}

.error-section,
.initial-section {
  padding: 40px 20px;
  text-align: center;
}

@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    gap: 10px;
    text-align: center;
  }
}
</style>