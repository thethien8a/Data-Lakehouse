# 🦆 DuckDB và Cách Lưu Trữ Dữ Liệu Trong Dự Án Này

## Tổng Quan Về DuckDB

DuckDB là một **cơ sở dữ liệu phân tích nội bộ (in-memory analytical database)** được thiết kế cho các truy vấn phân tích hiệu suất cao. Khác với các hệ quản trị cơ sở dữ liệu truyền thống, DuckDB có một số đặc điểm lưu trữ dữ liệu riêng biệt.

## Cách DuckDB Lưu Trữ Dữ Liệu Trong Dự Án Này

### 1. **Không Lưu Trực Tiếp Dữ Liệu Trong Giai Đoạn Hiện Tại**

Hiện tại, trong dự án này:
- **Dữ liệu thô (Bronze layer)** được lưu trữ trong **MinIO** dưới dạng các file **Parquet**
- **DuckDB** chưa được tích hợp vào pipeline để lưu trữ dữ liệu cố định
- DuckDB sẽ được sử dụng chủ yếu trong **giai đoạn sau** để truy vấn dữ liệu từ MinIO

### 2. **Cách DuckDB Tương Tác Với Dữ Liệu**

Khi DuckDB được tích hợp vào hệ thống (theo kế hoạch trong `documents/plan.md`), nó sẽ:

- **Truy vấn trực tiếp từ MinIO** thông qua giao thức S3 API
- **Không lưu bản sao dữ liệu** vào ổ đĩa cục bộ
- **Xử lý dữ liệu trong bộ nhớ** trong quá trình truy vấn
- **Tạo các bản chuyển đổi (transformations)** và có thể lưu kết quả trở lại MinIO

### 3. **Các Tùy Chọn Lưu Trữ DuckDB**

DuckDB có thể hoạt động theo nhiều cách:

#### A. **In-Memory Mode (Chế độ bộ nhớ)**
- Dữ liệu được tải vào RAM
- Không lưu vào ổ đĩa
- Rất nhanh nhưng dữ liệu mất khi tắt ứng dụng

#### B. **Persistent Mode (Chế độ lưu trữ bền vững)**
- Dữ liệu có thể được lưu vào file `.db` trên ổ đĩa
- Giữ lại dữ liệu giữa các phiên làm việc
- Tuy nhiên, trong dự án này, **chưa sử dụng chế độ này**

### 4. **Tích Hợp DuckDB Với MinIO (Theo Kế Hoạch)**

Theo `documents/plan.md`, DuckDB sẽ được sử dụng trong các giai đoạn:

1. **Silver Layer**: Chuyển đổi dữ liệu từ Bronze → Silver
2. **Gold Layer**: Tạo các bảng tổng hợp cho phân tích
3. **Truy vấn phân tích**: Hỗ trợ BI và phân tích dữ liệu

Ví dụ truy vấn:
```sql
-- Truy vấn trực tiếp từ MinIO (S3)
SELECT * FROM read_parquet('s3://bronze/online_retail_ii/*.parquet');
```

### 5. **Lợi Ích Của Cách Thiết Kế Này**

- **Tách biệt lưu trữ và tính toán**: MinIO cho lưu trữ, DuckDB cho xử lý
- **Khả năng mở rộng**: Có thể mở rộng lưu trữ và tính toán riêng biệt
- **Hiệu suất**: DuckDB tối ưu cho truy vấn phân tích, MinIO tối ưu cho lưu trữ đối tượng
- **Chi phí**: Tránh lưu trữ dữ liệu trùng lặp

## Kết Luận

**Trong giai đoạn hiện tại của dự án này, DuckDB không lưu trữ bất kỳ dữ liệu nào một cách cố định.** DuckDB hoạt động như một công cụ truy vấn và xử lý dữ liệu, lấy dữ liệu trực tiếp từ MinIO (lưu trữ dữ liệu thô) và sẽ tạo ra các bản chuyển đổi để lưu trở lại MinIO theo kiến trúc Bronze → Silver → Gold.

Dữ liệu thực tế được lưu trữ trong:
- **MinIO** (Bronze, Silver, Gold layers) - dưới dạng các file Parquet
- **DuckDB** chỉ tạm giữ dữ liệu trong RAM trong quá trình xử lý truy vấn