import re

ai_text = """根據您提供的半年大樂透中獎資料，我將分析並推薦兩組彩券號碼。

---

### 大樂透半年中獎資料分析摘要

**總體熱門號碼 (獎號):**
*   **9次:** 45
*   **8次:** 2, 15, 20
*   **7次:** 5, 13, 25, 26, 29, 33, 37, 39, 41, 46, 49

**總體冷門號碼 (獎號):**
*   **2次:** 12, 30, 44
*   **3次:** 10, 18, 28, 31, 36, 38

**特別號熱門號碼:**
*   **4次:** 10, 28
*   **3次:** 2, 24, 27, 31

**特別號冷門號碼 (從未出現的特別號):**
*   **0次:** 1, 4, 5, 7, 12, 13, 15, 16, 17, 18, 20, 23, 25, 29, 32, 35, 38, 40, 41, 42, 44, 47, 48

---

### 彩券號碼推薦

**第一組 (冷門號碼組合):**
[10, 12, 18, 30, 31, 44] + 特別號: 38

**選號理由:**
這組號碼的選擇依據是半年內出現頻率最低的號碼：
*   **主獎號:** 我們從出現次數為2次 (12, 30, 44) 和 3次 (10, 18, 31) 的號碼中選取，以確保這些號碼在過去半年中較少被選中。
*   **特別號:** 選擇了38。在半年內的資料中，38曾作為主獎號出現過3次，但從未以特別號的形式出現過，因此它是一個極為冷門的特別號選項，同時也確保不與主獎號重複。

---

**第二組 (熱門號碼組合):**
[2, 5, 15, 20, 33, 45] + 特別號: 10

**選號理由:**
這組號碼的選擇依據是半年內出現頻率最高的號碼：
*   **主獎號:** 我們從出現次數為9次 (45)、8次 (2, 15, 20) 和 7次 (5, 33) 的號碼中選取，這些都是在過去半年中被抽中次數最多的號碼。
*   **特別號:** 選擇了10。在半年內的資料中，10曾以特別號的形式出現過4次，是特別號中出現頻率最高的號碼之一，且不與主獎號重複。

---"""

def parse_ai_prediction(ai_prediction_text):
    if not ai_prediction_text:
        return None
    
    recommended_sets = []
    
    # 使用更寬鬆的正則表達式匹配號碼格式
    pattern = r'\[(\d+(?:,\s*\d+){5})\]\s*\+\s*特別號:\s*(\d+)'
    matches = re.findall(pattern, ai_prediction_text)
    
    print(f"Found {len(matches)} matches with pattern: {pattern}")
    for i, match in enumerate(matches):
        print(f"Match {i+1}: {match}")
    
    if len(matches) >= 2:
        for i, match in enumerate(matches[:2]):
            regular_numbers_str, special_number_str = match
            regular_numbers = [int(x.strip()) for x in regular_numbers_str.split(',')]
            special_number = int(special_number_str)
            
            set_type = "冷門號碼組合" if i == 0 else "熱門號碼組合"
            reason = f"基於歷史資料分析的{set_type}"
            
            recommended_sets.append({
                "type": set_type,
                "regular_numbers": regular_numbers,
                "special_number": special_number,
                "reason": reason
            })
    
    return recommended_sets if recommended_sets else None

result = parse_ai_prediction(ai_text)
print("Parsing result:", result)