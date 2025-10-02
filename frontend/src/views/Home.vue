<template>
  <div class="home">
    <el-row :gutter="20">
      <el-col :span="24">
        <div class="hero-section">
          <h1>🎯 AI 智能選號系統</h1>
          <p class="subtitle">基於歷史資料分析，提供大樂透與威力彩的智能號碼推薦</p>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="feature-cards">
      <el-col :xs="24" :sm="12" :md="8">
        <el-card class="feature-card" shadow="hover">
          <div class="card-content">
            <el-icon class="card-icon" size="48" color="#409EFF">
              <TrendCharts />
            </el-icon>
            <h3>智能選號</h3>
            <p>運用 Google Gemini AI 分析半年歷史資料，快速獲取三組推薦號碼</p>
            <el-button 
              type="primary" 
              @click="getQuickPrediction"
              :loading="quickLoading"
            >
              {{ quickLoading ? '分析中...' : '智能選號' }}
            </el-button>
            
            <!-- 快速選號結果 -->
            <div v-if="quickPrediction || predictionError" class="quick-prediction">
              <el-divider />
              <div class="quick-numbers">
                <!-- 推薦號碼區域 -->
                <div v-if="quickPrediction && quickPrediction.recommended_sets && quickPrediction.recommended_sets.length > 0" 
                     class="number-sets">
                  <div 
                    v-for="(set, index) in quickPrediction.recommended_sets" 
                    :key="index"
                    class="number-set"
                  >
                    <h4>第{{ index + 1 }}組</h4>
                    <div class="numbers-group">
                      <el-tag 
                        v-for="num in set.regular_numbers" 
                        :key="`regular-${num}`"
                        class="number-tag regular" 
                        size="large"
                      >
                        {{ num }}
                      </el-tag>
                      <span class="plus">+</span>
                      <el-tag 
                        class="number-tag special" 
                        size="large" 
                        type="danger"
                      >
                        {{ set.special_number }}
                      </el-tag>
                    </div>
                  </div>
                </div>
                
                <!-- 當 AI 分析完成但沒有推薦號碼時的提示 -->
                <div v-else-if="quickPrediction && quickPrediction.status === 'success' && (!quickPrediction.recommended_sets || quickPrediction.recommended_sets.length === 0)" 
                     class="no-numbers-hint">
                  <el-alert 
                    title="AI 分析完成，但未能生成推薦號碼" 
                    type="warning" 
                    :closable="false"
                    show-icon>
                    <template #default>
                      <p>AI 已完成資料分析，但未能解析出具體的推薦號碼組合。請稍後再試，或查看詳細分析了解更多資訊。</p>
                    </template>
                  </el-alert>
                </div>
                
                <!-- 錯誤狀態提示 -->
                <div v-else-if="predictionError" class="error-hint">
                  <el-alert 
                    title="獲取推薦號碼失敗" 
                    type="error" 
                    :closable="false"
                    show-icon>
                    <template #default>
                      <p>{{ predictionError }}</p>
                      <p>請稍後再試，或檢查網路連線狀態。</p>
                    </template>
                  </el-alert>
                </div>
                
                <!-- 按鈕區域 -->
                <el-button 
                  v-if="quickPrediction"
                  type="info" 
                  size="small" 
                  @click="navigateToDetail"
                  class="detail-button"
                >
                  查看詳細分析
                </el-button>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="8">
        <el-card class="feature-card" shadow="hover">
          <div class="card-content">
            <el-icon class="card-icon" size="48" color="#67C23A">
              <DataAnalysis />
            </el-icon>
            <h3>頻率統計</h3>
            <p>詳細的號碼出現頻率統計，了解熱門與冷門號碼分佈</p>
            <el-button type="success" @click="$router.push('/history')">
              查看統計
            </el-button>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="8">
        <el-card class="feature-card" shadow="hover">
          <div class="card-content">
            <el-icon class="card-icon" size="48" color="#E6A23C">
              <Money />
            </el-icon>
            <h3>多彩種支援</h3>
            <p>支援大樂透、威力彩等多種彩券的歷史資料查詢</p>
            <el-button type="warning" @click="$router.push('/super-lotto')">
              威力彩
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="info-section">
      <el-col :span="24">
        <el-alert
          title="免責聲明"
          type="warning"
          description="本系統僅供娛樂參考，彩券投注涉及風險，請理性投注，量力而為。"
          :closable="false"
          show-icon
        />
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { TrendCharts, DataAnalysis, Money } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

export default {
  name: 'Home',
  components: {
    TrendCharts,
    DataAnalysis,
    Money
  },
  setup() {
    const router = useRouter()
    const quickLoading = ref(false)
    const quickPrediction = ref(null)
    const predictionError = ref(null)
    let currentRequest = null

    const getQuickPrediction = async () => {
      // 防止重複請求
      if (quickLoading.value) {
        console.log('Request already in progress, ignoring...')
        return
      }

      // 如果已有請求在進行，取消它
      if (currentRequest) {
        currentRequest.abort()
        console.log('Cancelled previous request')
      }

      quickLoading.value = true
      predictionError.value = null // 清除之前的錯誤
      
      // 創建可取消的請求
      const controller = new AbortController()
      currentRequest = controller

      try {
        const response = await axios.get('/api/lotto649/predict', {
          signal: controller.signal
        })
        
        if (response.data.status === 'success') {
          quickPrediction.value = response.data
          console.log('Quick prediction data:', quickPrediction.value)
          ElMessage.success('快速選號完成！')
        } else {
          predictionError.value = response.data.error || '獲取推薦號碼失敗'
          ElMessage.error(predictionError.value)
        }
      } catch (err) {
        if (axios.isCancel(err)) {
          console.log('Request was cancelled')
          return
        }
        predictionError.value = err.response?.data?.detail || err.message || '網路連接失敗'
        ElMessage.error(predictionError.value)
        console.error('Quick prediction error:', err)
      } finally {
        currentRequest = null
        quickLoading.value = false
      }
    }

    const navigateToDetail = () => {
      console.log('Navigate to detail called, quickPrediction:', quickPrediction.value)
      if (quickPrediction.value) {
        // Pass prediction data through sessionStorage
        const predictionData = JSON.stringify(quickPrediction.value)
        console.log('Storing prediction data:', predictionData)
        sessionStorage.setItem('lotto649_prediction', predictionData)
        router.push('/lotto649')
      } else {
        console.log('No prediction data available, navigating without data')
        router.push('/lotto649')
      }
    }

    return {
      quickLoading,
      quickPrediction,
      predictionError,
      getQuickPrediction,
      navigateToDetail
    }
  }
}
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
}

.hero-section {
  text-align: center;
  padding: 60px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 10px;
  margin-bottom: 40px;
}

.hero-section h1 {
  font-size: 48px;
  margin: 0 0 20px 0;
  font-weight: bold;
}

.subtitle {
  font-size: 18px;
  margin: 0;
  opacity: 0.9;
}

.feature-cards {
  margin-bottom: 40px;
}

.feature-card {
  height: 100%;
  transition: transform 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
}

.card-content {
  text-align: center;
  padding: 20px;
}

.card-icon {
  margin-bottom: 20px;
}

.card-content h3 {
  font-size: 24px;
  margin: 0 0 15px 0;
  color: #333;
}

.card-content p {
  font-size: 16px;
  color: #666;
  line-height: 1.6;
  margin-bottom: 25px;
}

.info-section {
  margin-top: 40px;
}

/* 快速選號樣式 */
.quick-prediction {
  margin-top: 15px;
}

.number-sets {
  margin-bottom: 15px;
}

.number-set {
  margin-bottom: 15px;
}

.number-set h4 {
  color: #409EFF;
  margin: 0 0 8px 0;
  font-size: 14px;
}

.numbers-group {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
  justify-content: center;
}

.number-tag {
  font-weight: bold;
  font-size: 14px;
  min-width: 32px;
  text-align: center;
}

.number-tag.regular {
  background: linear-gradient(135deg, #409EFF, #1890ff);
  color: white;
  border: none;
}

.number-tag.special {
  background: linear-gradient(135deg, #F56C6C, #ff4757);
  color: white;
  border: none;
}

.plus {
  font-weight: bold;
  color: #666;
  margin: 0 2px;
}

.detail-button {
  width: 100%;
  margin-top: 10px;
}

/* 新增的提示區域樣式 */
.no-numbers-hint {
  margin-bottom: 15px;
}

.error-hint {
  margin-bottom: 15px;
}

.no-numbers-hint .el-alert,
.error-hint .el-alert {
  margin-bottom: 0;
}

.no-numbers-hint .el-alert__content p,
.error-hint .el-alert__content p {
  margin: 0;
  line-height: 1.5;
}

.no-numbers-hint .el-alert__content p + p,
.error-hint .el-alert__content p + p {
  margin-top: 8px;
}

@media (max-width: 768px) {
  .hero-section h1 {
    font-size: 32px;
  }
  
  .subtitle {
    font-size: 16px;
  }
  
  .numbers-group {
    gap: 4px;
  }
}
</style>