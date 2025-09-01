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
            <p>運用 Google Gemini AI 分析半年歷史資料，快速獲取兩組推薦號碼</p>
            <el-button 
              type="primary" 
              @click="getQuickPrediction"
              :loading="quickLoading"
            >
              {{ quickLoading ? '分析中...' : '智能選號' }}
            </el-button>
            
            <!-- 快速選號結果 -->
            <div v-if="quickPrediction" class="quick-prediction">
              <el-divider />
              <div class="quick-numbers">
                <div v-if="quickPrediction.recommended_sets" class="number-sets">
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
                <el-button 
                  type="info" 
                  size="small" 
                  @click="$router.push('/lotto649')"
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
    const quickLoading = ref(false)
    const quickPrediction = ref(null)

    const getQuickPrediction = async () => {
      quickLoading.value = true
      quickPrediction.value = null

      try {
        const response = await axios.get('http://localhost:8000/api/lotto649/predict')
        if (response.data.status === 'success') {
          quickPrediction.value = response.data
          console.log('Quick prediction data:', quickPrediction.value)
          ElMessage.success('快速選號完成！')
        } else {
          ElMessage.error(response.data.error || '獲取推薦號碼失敗')
        }
      } catch (err) {
        ElMessage.error(err.response?.data?.detail || err.message || '網路連接失敗')
        console.error('Quick prediction error:', err)
      } finally {
        quickLoading.value = false
      }
    }

    return {
      quickLoading,
      quickPrediction,
      getQuickPrediction
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