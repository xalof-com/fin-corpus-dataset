<center>
    <h1>Corpus/Dataset Tiếng Việt Về Tài Chính Dùng Trong Việc Training Mô Hình Transformer</h1>
</center>

# Nguồn Dữ Liệu
Dữ liệu được crawl từ nguồn cafef.vn, thời gian từ 01/01/2021 đến 02/06/2024. Bao gồm 4 chuyên mục:
* Chứng Khoán
* Tài Chính
* Bất Động Sản
* Doanh Nghiệp

Tổng cộng có `85.586` bài báo.

# Raw Dataset
Là các file chứa dữ liệu gồm các câu, mỗi câu là một dòng được chứa trong thư mục `dataset`, gồm:

[Download tại: https://drive.google.com/drive/folders/1pndKI3wCjjmZkxlnmOdcbAUxRbTlpIBe?usp=sharing]

* `fin_tai-chinh_479976_sentences.txt.zip`: tất cả các câu trong tất cả các bài báo thuộc section `Tài Chính`
* `fin_chung-khoan_488480_sentences.txt.zip`: tất cả các câu trong tất cả các bài báo thuộc section `Chứng Khoán`
* `fin_bat-dong-san_825747_sentences.txt.zip`: tất cả các câu trong tất cả các bài báo thuộc section `Bất Động Sản`
* `fin_doanh-nghiep_599138_sentences.txt.zip`: tất cả các câu trong tất cả các bài báo thuộc section `Doanh Nghiệp`
* `fin_all_2393341_sentences.txt.zip`: tất cả các câu trong tất cả các bài báo của 4 section trên

Cấu trức tên file: fin_{section}_{number-of-sentences}_sentences.txt.zip


# Corpus
Bao gồm 2 file chứa trong thư mục `corpus` (mình tạo sẳn để dùng. Các bạn có thể tạo lại theo cấu trúc của riêng mình bằng 1 trong 5 file zip trong `dataset`):

[Download tại: https://drive.google.com/drive/folders/1pndKI3wCjjmZkxlnmOdcbAUxRbTlpIBe?usp=sharing]

* `fin_all_word_tokenized_sencentences.txt.zip`: mỗi dòng của file này là một json string như sau:

<pre>
{"sentence": ["Chứng khoán", "VNDirect", "đi", "vay", "10.000", "tỷ", "đồng", "."], "word_count": 8}
{"sentence": ["Công ty", "CP", "Chứng khoán", "VNDirect", "thông qua", "việc", "sử dụng", "vốn", "vay", ",", "bảo lãnh", "tại", "VietinBank", "với", "tổng", "hạn mức", "10.000", "tỷ", "đồng", "để", "bổ sung", "nguồn", "vốn", ",", "đầu tư", "vào", "các", "giấy tờ", "có giá", "trên", "thị trường", ",", "bảo lãnh", "phát hành", "chứng khoán", "."], "word_count": 36}
{"sentence": ["Tuần", "qua", ",", "chỉ số", "VN-Index", "giảm", "0,21", "điểm", "xuống", "1.261,72 điểm", "."], "word_count": 11}
{"sentence": ["Thanh khoản", "trên", "sàn", "HoSE", "đạt", "hơn", "109.520", "tỷ", "đồng", ",", "giảm", "gần", "21", "so", "với", "tuần", "trước", "."], "word_count": 18}
{"sentence": ["Chỉ số", "HNX-Index kết", "tuần", "ở", "mức", "243,09 điểm", ",", "tăng", "1,37 điểm", "."], "word_count": 10}
...
</pre>

* `fin_all_vocab.json.zip`: là file chứa tất cả các từ (unique) được tổng hợp từ file `fin_all_word_tokenized_sencentences.txt`, có dạng:

<pre>
{
    "size": 422539,
    "tokens": {
        "&lt;SOS&gt;": 0,
        "&lt;EOS&gt;": 1,
        "&lt;PAD&gt;": 2,
        "&lt;UNK&gt;": 3,
        "04/6": 4,
        "Hệ Sinh thái": 5,
        "18006821": 6,
        "Tân Long đóng": 7,
        "Bàu Lâm": 8,
        "Samco": 9,
        "VinFast Philippines": 10,
        "2.758.000 cp": 11,
        "quý kế tiếp": 12,
        "Hanwha Master": 13,
        ...
    }
}
</pre>

