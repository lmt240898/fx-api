def get_timeframe_config(main_tf_desc):
    """
    Tạo cấu hình phân tích đa khung thời gian (higher, lower, main) một cách logic
    dựa trên khung thời gian giao dịch chính được người dùng lựa chọn.

    Hàm này được tách riêng để module hóa logic, giúp prompt chính trở nên gọn gàng
    và dễ bảo trì. Mỗi cấu hình đều được xây dựng dựa trên nguyên tắc phân tích
    Top-Down, kết hợp giữa xác nhận xu hướng và tối ưu hóa điểm vào lệnh.

    Args:
        main_tf_desc (int): Một số nguyên đại diện cho khung thời gian chính
                            (ví dụ: 2 cho H2, 4 cho H4, 24 cho D1).

    Returns:
        dict: Một dictionary chứa cấu hình chi tiết cho các khung thời gian để
              cung cấp cho AI, bao gồm tên khung và vai trò chiến lược của chúng.
    """

    if main_tf_desc == "H2":  # Trade chính trên H2
        """
        --- TRADE CHÍNH: H2 (Giao dịch lướt sóng Chiến thuật / Tactical Swing/Day Trading) ---
        Mục tiêu: Bắt các con sóng chính trong ngày theo xu hướng lớn hơn.
        - higher_timeframe (D1): Cung cấp "bức tranh lớn" và xu hướng chủ đạo của cả tuần. Nó trả lời câu hỏi: "Tôi nên đứng về phe Mua hay phe Bán?". Tránh được rủi ro chống lại xu hướng của các tổ chức lớn.
        - main_timeframe (H2): Là khung tìm kiếm THIẾT LẬP (setup). Sau khi có xu hướng từ D1, ta tìm các điểm pullback về vùng giá trị (MA, S/R...) trên H2.
        - lower_timeframe (M30): Đóng vai trò "kính ngắm" để TINH CHỈNH ĐIỂM VÀO LỆNH. Nó giúp tìm tín hiệu xác nhận (nến, phân kỳ), cho phép đặt stop-loss chặt và tối ưu R:R.
        => Logic: D1 (Xu hướng) → H2 (Thiết lập) → M30 (Vào lệnh). Cấu trúc kinh điển, tách biệt rõ ràng vai trò, từ vĩ mô đến vi mô.
        """
        return {
            "lower_timeframe": "M30",
            "higher_timeframe": "D1",
            "main_timeframe": "H2",
            "main_role": "Tactical Setup Identification: Identifies pullback zones and patterns that align with the Daily trend.",
            "higher_role": "Strategic Trend Context: Defines the dominant daily/weekly trend to establish a directional bias.",
            "lower_role": "Entry Trigger & Refinement: Pinpoints precise entry triggers on micro-patterns for optimal Risk/Reward."
        }

    elif main_tf_desc == "H4":  # Trade chính trên H4
        """
        --- TRADE CHÍNH: H4 (Giao dịch trong ngày Chiến lược / Strategic Swing) ---
        Mục tiêu: Bắt các con sóng kéo dài từ 1-3 ngày, cân bằng giữa tín hiệu và nhiễu.
        - higher_timeframe (W1): Thiết lập "xu hướng của tháng". Nó đảm bảo rằng lệnh trên H4 đang đi thuận theo xu hướng vĩ mô, tăng xác suất thành công đáng kể.
        - main_timeframe (H4): Đây là "khung thời gian vàng", nơi các tín hiệu và mô hình giá có độ tin cậy cao, là nơi tìm kiếm THIẾT LẬP.
        - lower_timeframe (H1): Đóng vai trò "tinh chỉnh điểm vào lệnh". Sau khi một vùng thiết lập xuất hiện trên H4, ta "zoom" vào H1 để tìm tín hiệu xác nhận, giúp cải thiện tỷ lệ Rủi ro:Lợi nhuận.
        => Logic: W1 (Xu hướng) → H4 (Thiết lập) → H1 (Vào lệnh). Cấu trúc Swing Trading kinh điển và mạnh mẽ.
        """
        return {
            "lower_timeframe": "H1",
            "higher_timeframe": "W1", # Sử dụng W1 để có bối cảnh lớn thực sự cho H4
            "main_timeframe": "H4",
            "main_role": "Strategic Setup Identification: Identifies robust patterns that align with the weekly market bias.",
            "higher_role": "Weekly Bias Definition: Establishes the major weekly trend direction and key structural levels.",
            "lower_role": "Entry Refinement & Trigger: Used to fine-tune entry points and find confirmation signals, minimizing risk."
        }

    elif main_tf_desc == "H8":  # Trade chính trên H8
        """
        --- TRADE CHÍNH: H8 (Giao dịch Swing Ngắn hạn / Short-term Swing) ---
        Mục tiêu: Lọc bỏ nhiễu trong ngày, tập trung vào cấu trúc của từng phiên giao dịch lớn.
        - higher_timeframe (W1): Cung cấp xu hướng chủ đạo của tuần/tháng. Bắt buộc đối với khung H8 để không bị lạc trong các biến động ngắn hạn của D1.
        - main_timeframe (H8): Cung cấp một cái nhìn rõ ràng về cuộc chiến trong mỗi phiên lớn, nơi tìm kiếm các THIẾT LẬP swing.
        - lower_timeframe (H2): Đóng vai trò "tinh chỉnh và xác nhận". Khi H8 vào vùng thiết lập, H2 giúp xác nhận động lượng và tìm một điểm vào lệnh có cấu trúc rõ ràng.
        => Logic: Tuân thủ nghiêm ngặt nguyên tắc Top-Down. W1 (Xu hướng) → H8 (Thiết lập) → H2 (Vào lệnh).
        """
        return {
            "lower_timeframe": "H2",
            "higher_timeframe": "W1",
            "main_timeframe": "H8",
            "main_role": "Session-Based Setup Trading: Identifies setups based on session-to-session structure for multi-day moves.",
            "higher_role": "Weekly Bias Confirmation: Confirms the prevailing weekly trend and highlights critical weekly-level structures.",
            "lower_role": "Tactical Fine-tuning & Entry: Provides more granular entry timing and confirms momentum within a single trading session."
        }
        
    elif main_tf_desc == "D1": # Trade chính trên D1
        """
        --- TRADE CHÍNH: D1 (Giao dịch Swing Trung hạn / Core Swing Trading) ---
        Mục tiêu: Bắt các con sóng lớn của tuần/tháng, dựa trên dữ liệu cuối ngày có độ tin cậy cao nhất.
        - higher_timeframe (MN1): Cung cấp "bối cảnh vĩ mô" của cả quý/năm. Nó cho biết xu hướng chính của thị trường dài hạn. W1 cũng có thể dùng, nhưng MN1 là lý tưởng nhất.
        - main_timeframe (D1): Là "khung của vua" trong swing trading. Nơi tìm kiếm THIẾT LẬP dựa trên hành động giá cuối ngày.
        - lower_timeframe (H4): Đóng vai trò "tối ưu hóa điểm vào". Khi D1 hình thành tín hiệu, ta quan sát H4 để tìm điểm kết thúc của cú điều chỉnh trong ngày, giúp vào lệnh với rủi ro thấp hơn nhiều.
        => Logic: Một setup kinh điển của trader chuyên nghiệp. MN1/W1 (Xu hướng vĩ mô) → D1 (Thiết lập) → H4 (Vào lệnh).
        """
        return {
            "lower_timeframe": "H4",
            "higher_timeframe": "W1", # W1 là tiêu chuẩn, MN1 là lý tưởng cho position trading
            "main_timeframe": "D1",
            "main_role": "Core Swing Setup Identification: Identifies high-probability trades based on clean end-of-day price action.",
            "higher_role": "Macro Trend Direction: Determines the multi-month macro trend and identifies critical long-term structural zones.",
            "lower_role": "Intraday Entry Refinement: Used after the D1 signal to fine-tune entry points on intraday pullbacks."
        }

    else: # Fallback - Cấu hình mặc định an toàn
        """
        Nếu một khung thời gian không xác định được truyền vào, hệ thống sẽ mặc định
        sử dụng cấu hình của H4. Đây là lựa chọn an toàn nhất vì H4 là khung thời gian
        rất cân bằng, được sử dụng rộng rãi và có logic phân tích vững chắc.
        """
        print(f"Warning: Unknown timeframe description '{main_tf_desc}'. Falling back to robust H4 configuration.")
        # Gọi lại chính nó với giá trị mặc định để tránh lặp code, sử dụng config đã sửa
        return get_timeframe_config(4)