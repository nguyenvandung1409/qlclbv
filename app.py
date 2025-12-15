from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DB_NAME = "chatluongbenhvien.db"

# 1. Khởi tạo Database và Dữ liệu mẫu
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Bảng danh mục tiêu chí (Ví dụ: A1.1, A1.2...)
    c.execute('''CREATE TABLE IF NOT EXISTS criteria (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    section TEXT
                )''')
    
    # Bảng điểm số (Lưu theo Năm, Tiêu chí, Điểm, Link minh chứng)
    c.execute('''CREATE TABLE IF NOT EXISTS scores (
                    year INTEGER,
                    criteria_id TEXT,
                    score INTEGER,
                    evidence_link TEXT,
                    PRIMARY KEY (year, criteria_id)
                )''')

    # Danh mục 83 tiêu chí đầy đủ theo Quyết định 6858/QĐ-BYT (Phiên bản 2.0)
    # Định dạng: (Mã tiêu chí, Tên tiêu chí, Phần)
    sample_criteria = [
        # PHẦN A: HƯỚNG ĐẾN NGƯỜI BỆNH
        ('A1.1', 'Chỉ dẫn, thủ tục, quy trình KBCB', 'A'),
        ('A1.2', 'An toàn người bệnh và tài sản', 'A'),
        ('A1.3', 'Thời gian chờ đợi của người bệnh', 'A'),
        ('A2.1', 'Nhân viên y tế giao tiếp, ứng xử', 'A'),
        ('A2.2', 'Tiếp cận người bệnh, người nhà để lắng nghe, thấu hiểu', 'A'),
        ('A3.1', 'Đánh giá, bảo đảm quyền lợi người bệnh', 'A'),
        ('A3.2', 'Tôn trọng và bảo mật thông tin', 'A'),
        ('A3.3', 'Hỗ trợ xã hội và tâm lý cho người bệnh', 'A'),
        ('A4.1', 'Thực hiện tư vấn, giáo dục sức khỏe', 'A'),
        ('A4.2', 'Quản lý hồ sơ, tài liệu tư vấn/giáo dục', 'A'),
        ('A5.1', 'Bảo đảm an toàn môi trường', 'A'),
        ('A5.2', 'Quản lý chất thải, vệ sinh môi trường', 'A'),
        ('A6.1', 'Thông tin rõ ràng về chi phí và thanh toán', 'A'),
        ('A6.2', 'Hỗ trợ giải quyết thắc mắc, khiếu nại', 'A'),

        # PHẦN B: PHÁT TRIỂN NGUỒN NHÂN LỰC
        ('B1.1', 'Quy trình tuyển dụng và phân công công việc', 'B'),
        ('B1.2', 'Bảo đảm năng lực hành nghề', 'B'),
        ('B2.1', 'Chương trình đào tạo và phát triển chuyên môn', 'B'),
        ('B2.2', 'Đánh giá hiệu quả đào tạo', 'B'),
        ('B3.1', 'Quản lý sức khỏe và an toàn lao động', 'B'),
        ('B3.2', 'Môi trường làm việc thân thiện', 'B'),

        # PHẦN C: HOẠT ĐỘNG CHUYÊN MÔN
        ('C1.1', 'Tiếp nhận, đánh giá ban đầu', 'C'),
        ('C1.2', 'Quyết định điều trị, nhập/chuyển khoa', 'C'),
        ('C2.1', 'Hồ sơ bệnh án đầy đủ, kịp thời', 'C'),
        ('C2.2', 'Quản lý thông tin y tế (HIS, LIS, PACS)', 'C'),
        ('C3.1', 'Kiểm soát nhiễm khuẩn cơ bản', 'C'),
        ('C3.2', 'Giám sát, báo cáo nhiễm khuẩn', 'C'),
        ('C4.1', 'Quản lý, sử dụng thuốc an toàn', 'C'),
        ('C4.2', 'Theo dõi, báo cáo phản ứng có hại của thuốc (ADR)', 'C'),
        ('C5.1', 'Quản lý thiết bị y tế, vật tư tiêu hao', 'C'),
        ('C5.2', 'Bảo trì, hiệu chuẩn thiết bị', 'C'),
        ('C6.1', 'An toàn phẫu thuật và thủ thuật', 'C'),
        ('C6.2', 'Chăm sóc sau phẫu thuật', 'C'),
        ('C7.1', 'Quản lý máu và truyền máu', 'C'),
        ('C7.2', 'Theo dõi phản ứng truyền máu', 'C'),
        ('C8.1', 'Thực hiện xét nghiệm đúng quy trình', 'C'),
        ('C8.2', 'Kiểm soát chất lượng xét nghiệm (Nội kiểm, Ngoại kiểm)', 'C'),
        ('C9.1', 'Quy trình chẩn đoán hình ảnh (CĐHA)', 'C'),
        ('C9.2', 'Bảo đảm an toàn bức xạ', 'C'),
        ('C10.1', 'Hồi sức cấp cứu và chống độc', 'C'),
        ('C10.2', 'Vận chuyển cấp cứu nội, ngoại viện', 'C'),
        ('C11.1', 'Dinh dưỡng lâm sàng', 'C'),
        ('C11.2', 'Phối hợp dinh dưỡng và điều trị', 'C'),
        ('C12.1', 'Phục hồi chức năng và hoạt động trị liệu', 'C'),

        # PHẦN D: CẢI TIẾN CHẤT LƯỢNG
        ('D1.1', 'Cấu trúc hệ thống QLCL', 'D'),
        ('D1.2', 'Phân tích và sử dụng dữ liệu QLCL', 'D'),
        ('D2.1', 'Quản lý sự cố y khoa', 'D'),
        ('D2.2', 'Phân tích nguyên nhân và hành động khắc phục', 'D'),
        ('D3.1', 'Quản lý rủi ro và an toàn người bệnh', 'D'),
        ('D3.2', 'Văn hóa an toàn người bệnh', 'D'),
        ('D4.1', 'Nghiên cứu khoa học và cải tiến kỹ thuật', 'D'),
        ('D4.2', 'Ứng dụng kết quả nghiên cứu', 'D'),

        # PHẦN E: TIÊU CHÍ ĐẶC THÙ (TÙY CHỌN)
        ('E1.1', 'Sản khoa: Chăm sóc thai nghén, chuyển dạ, sinh đẻ', 'E'),
        ('E1.2', 'Sản khoa: Cấp cứu sản khoa', 'E'),
        ('E2.1', 'Nhi khoa: Sàng lọc và chăm sóc trẻ sơ sinh', 'E'),
        ('E2.2', 'Nhi khoa: Cấp cứu và hồi sức nhi', 'E')
    ]
    c.executemany('INSERT OR IGNORE INTO criteria VALUES (?,?,?)', sample_criteria)
    conn.commit()
    conn.close()

# Chạy khởi tạo DB ngay khi start app
init_db()

# 2. Các Route (Đường dẫn trang web)

@app.route('/')
def index():
    # Lấy năm từ thanh địa chỉ, mặc định là 2025
    selected_year = request.args.get('year', 2025, type=int)
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Lấy danh sách tiêu chí và điểm của năm được chọn (Left Join để lấy cả tiêu chí chưa chấm)
    query = '''
        SELECT c.id, c.name, c.section, s.score, s.evidence_link
        FROM criteria c
        LEFT JOIN scores s ON c.id = s.criteria_id AND s.year = ?
        ORDER BY c.id
    '''
    c.execute(query, (selected_year,))
    data = c.fetchall()
    
    # Tính điểm trung bình
    total_score = sum([row[3] for row in data if row[3] is not None])
    count_rated = sum([1 for row in data if row[3] is not None])
    avg_score = round(total_score / count_rated, 2) if count_rated > 0 else 0
    
    conn.close()
    
    return render_template('index.html', data=data, year=selected_year, avg=avg_score)

@app.route('/update', methods=['POST'])
def update():
    year = request.form.get('year')
    criteria_id = request.form.get('criteria_id')
    score = request.form.get('score')
    evidence = request.form.get('evidence')
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Lưu hoặc cập nhật điểm (Upsert)
    c.execute('''INSERT OR REPLACE INTO scores (year, criteria_id, score, evidence_link)
                 VALUES (?, ?, ?, ?)''', (year, criteria_id, score, evidence))
    
    conn.commit()
    conn.close()
    return redirect(url_for('index', year=year))

if __name__ == '__main__':
    app.run(debug=True)