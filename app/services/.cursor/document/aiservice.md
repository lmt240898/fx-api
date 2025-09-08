# Kiến trúc Dịch vụ AI (AIService)

Tài liệu này mô tả kiến trúc và cách sử dụng module dịch vụ AI, được thiết kế để tương tác với các nhà cung cấp mô hình ngôn ngữ lớn (LLM) một cách linh hoạt và dễ bảo trì.

## 1. Tổng quan kiến trúc

Hệ thống được xây dựng dựa trên **Strategy Design Pattern** để tách biệt logic nghiệp vụ khỏi chi tiết triển khai của từng nhà cung cấp API (ví dụ: OpenRouter, OpenAI, Google).

Các thành phần chính bao gồm:

-   **`AIService` (`ai_service.py`)**: Là class chính mà ứng dụng sẽ tương tác. Nó đóng vai trò là "Context" trong Strategy Pattern.
-   **`AIProviderStrategy` (`ai_providers/base.py`)**: Là một Abstract Base Class (ABC) định nghĩa "giao diện" chung mà tất cả các nhà cung cấp phải tuân theo.
-   **Các Provider cụ thể (ví dụ: `OpenRouterProvider`)**: Là các class kế thừa từ `AIProviderStrategy` và triển khai logic gọi API cụ thể cho từng nhà cung cấp.
-   **Pydantic Models (`models/ai_config.py`)**: Dùng để đọc và xác thực file cấu hình `config/ai_config.json`, đảm bảo an toàn dữ liệu và cung cấp auto-completion.
-   **Configuration (`config/ai_config.json`)**: File JSON để định nghĩa các "chiến lược" model, nhà cung cấp, và model mặc định.

## 2. Cách sử dụng

### Khởi tạo

Bạn có thể khởi tạo `AIService` theo hai cách:

**a. Sử dụng model mặc định (được định nghĩa trong `use_model` của file JSON):**

```python
from app.services.ai_service import AIService

ai_service = AIService()
```

**b. Chỉ định một model cụ thể (dựa trên key trong `strategies` của file JSON):**

```python
ai_service = AIService(strategy_key='gpt-4-1')
```

### Tạo phản hồi

Sau khi khởi tạo, chỉ cần gọi phương thức `generate_response`.

```python
prompt = "Your generated prompt here..."
response_text = await ai_service.generate_response(prompt)

print(response_text)
```

## 3. Triển khai

### Cấu hình (`config/ai_config.json`)

File này là trung tâm điều khiển.

-   `strategies`: Một dictionary chứa các cấu hình model. Key của mỗi entry (ví dụ: `"gemini-2-5-pro"`) được dùng làm `strategy_key`.
-   `model`: Tên model đầy đủ sẽ được gửi đến API provider.
-   `provider`: (Optional) Cấu hình dành riêng cho provider (ví dụ: `order` cho OpenRouter).
-   `use_model`: `strategy_key` mặc định sẽ được sử dụng nếu không có key nào được truyền vào lúc khởi tạo.

### Thêm một Nhà cung cấp (Provider) mới

Để thêm một provider mới (ví dụ: `DirectOpenAIProvider`), hãy làm theo các bước sau:

1.  **Tạo file mới**: `app/services/ai_providers/direct_openai.py`.
2.  **Tạo class mới**:
    ```python
    from .base import AIProviderStrategy
    # ... import các thư viện cần thiết ...

    class DirectOpenAIProvider(AIProviderStrategy):
        @retry(...) # Thêm retry logic
        async def generate(self, model_name: str, provider_config: AIProviderConfig | None, prompt: str) -> str:
            # Viết logic gọi API của OpenAI tại đây
            pass
    ```
3.  **Đăng ký provider mới trong `AIService`**:
    Mở file `app/services/ai_service.py` và thêm provider mới vào dictionary `_strategies`.
    ```python
    class AIService:
        _strategies = {
            "openrouter": OpenRouterProvider(),
            "openai": DirectOpenAIProvider() # Thêm dòng này
        }
        # ...
    ```

## 4. Xử lý lỗi và Retry

Hệ thống sử dụng thư viện `tenacity` để tự động retry khi gọi API thất bại. Logic này được triển khai bằng decorator `@retry` ngay trên phương thức `generate` của mỗi provider. Nó sẽ tự động thử lại 3 lần với thời gian chờ tăng dần (exponential backoff).

---
