import { ref, computed } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

export function useLotteryFetch(apiEndpoint, defaultData = []) {
  const data = ref(defaultData)
  const loading = ref(false)
  const error = ref('')
  const currentPage = ref(1)
  const pageSize = 10

  const paginatedData = computed(() => {
    const start = (currentPage.value - 1) * pageSize
    const end = start + pageSize
    return data.value.slice(start, end)
  })

  const fetchData = async (selectedDate, options = {}) => {
    if (!selectedDate) {
      ElMessage.warning(options.warningMessage || '請先選擇年月')
      return
    }

    loading.value = true
    error.value = ''
    data.value = []

    try {
      const [year, month] = selectedDate.split('-')
      const response = await axios.get(apiEndpoint, {
        params: { year, month }
      })

      data.value = response.data
      currentPage.value = 1
      const lotteryName = options.lotteryName || ''
      ElMessage.success(
        lotteryName
          ? `成功載入 ${response.data.length} 筆 ${lotteryName} 資料`
          : `成功載入 ${response.data.length} 筆資料`
      )
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

  const reset = () => {
    data.value = defaultData
    loading.value = false
    error.value = ''
    currentPage.value = 1
  }

  return {
    data,
    loading,
    error,
    currentPage,
    pageSize,
    paginatedData,
    fetchData,
    handlePageChange,
    reset
  }
}
